import requests
from urllib3.exceptions import InsecureRequestWarning

class DirectusClient_V9():
    def __init__(self, url: str, token: str = None, email: str = None, password: str = None, verify: bool = False):
        self.verify = verify
        if not self.verify:
            requests.packages.urllib3.disable_warnings(
                category=InsecureRequestWarning
            )

        self.url = url
        if token is not None:
            self.static_token = token
            self.temporary_token = None
        elif email is not None and password is not None:
            self.email = email
            self.password=password
            self.login(email, password)
            self.static_token = None
        else:
            self.static_token = None
            self.temporary_token = None

    def login(self, email: str = None, password: str = None) -> tuple:
        '''
        Login with the /auth/login endpoint. Returns both the access token and refresh token. Updates self.email and self.password 
        if provided email and passwords
        '''
        if email is None or password is None:
            email = self.email
            password = self.password
        else:
            self.email = email
            self.password = password
        
        auth = requests.post(
            f"{self.url}/auth/login",
            json={
                "email": email,
                "password": password
            }
        ).json()['data']

        self.static_token = None
        self.temporary_token = auth['access_token']
        self.refresh_token = auth['refresh_token']

    def logout(self, refresh_token: str = None) -> None:
        '''
        Retrieve new temporary access token and refresh token
        '''
        if refresh_token is None:
            refresh_token = self.refresh_token
        auth = requests.post(
            f"{self.url}/auth/logout",
            json={"refresh_token": refresh_token},
            verify=self.verify
        )
        self.temporary_token = None
        self.refresh_token = None

    def refresh(self, refresh_token: str = None) -> None:
        '''
        Retrieve new temporary access token and refresh token
        '''
        if refresh_token is None:
            refresh_token = self.refresh_token
        auth = requests.post(
            f"{self.url}/auth/refresh",
            json={
                "refresh_token": refresh_token
            },
            verify=self.verify
        ).json()['data']

        self.temporary_token = auth['access_token']
        self.refresh_token = auth['refresh_token']

    def get_token(self):
        '''
        Returns static token if there is any, if not refreshes the temp token.
        '''
        if self.static_token is not None:
            token = self.static_token
        elif self.temporary_token is not None:
            self.refresh()
            token = self.temporary_token
        else:
            token = ""
        return token
    
    def get(self, path, output_type: str = "json", **kwargs):
        data = requests.get(
            f"{self.url}{path}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            verify=self.verify,
            **kwargs
        )
        if 'errors' in data.text:
            raise AssertionError(data.json()['errors'])
        if output_type == 'csv':
            return data.text
        
        return data.json()['data']
    
    def post(self, path, **kwargs):
        x = requests.post(
            f"{self.url}{path}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            verify=self.verify,
            **kwargs
        )
        if x.status_code != 200:
            raise AssertionError(x.text)
        
        return x.json()

    def delete(self, path, **kwargs):
        x = requests.delete(
            f"{self.url}{path}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            verify=self.verify,
            **kwargs
        )
        if x.status_code != 204:
            raise AssertionError(x.text)
        
    def patch(self, path, **kwargs):
        x = requests.patch(
            f"{self.url}{path}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            verify=self.verify,
            **kwargs
        )

        if x.status_code not in [200, 204]:
            raise AssertionError(x.text)
        
        return x.json()

    def bulk_insert(self, collection_name: str, items: list, interval: int = 100, verbose: bool = False) -> None:
        '''
        Post items is capped at 100 items. This function breaks up any list of items more than 100 long and bulk insert
        '''
        length = len(items)
        for i in range(0, length, interval):
            if verbose:
                print(f"Inserting {i}-{min(i+100, length)} out of {length}")
            self.post(f"/items/{collection_name}", json=items[i:i + interval])

    def duplicate_collection(self, collection_name: str, duplicate_collection_name: str) -> None:
        '''
        Duplicate the collection with schema, fields, and data
        '''
        duplicate_collection = self.get(f"/collections/{collection_name}")
        duplicate_collection['collection'] = duplicate_collection_name
        duplicate_collection['meta']['collection'] = duplicate_collection_name
        duplicate_collection['schema']['name'] = duplicate_collection_name
        self.post("/collections", json=duplicate_collection)
        fields = [
            field for field in self.get_all_fields(collection_name) if not field['schema']['is_primary_key']
        ]
        for field in fields:
            self.post(f"/fields/{duplicate_collection_name}", json=field)
        self.bulk_insert(duplicate_collection_name, self.get(f"/items/{collection_name}", params={"limit": -1}))

    def collection_exists(self, collection_name: str):
        '''
        Checks if collection exists in directus
        '''
        collection_schema = [col['collection'] for col in self.get('/collections')]
        return collection_name in collection_schema

    def delete_all_items(self, collection_name: str) -> None:
        '''
        Delete all items from the directus collection. Delete api from directus only able to delete based on ID.
        This helper function helps to delete every item within the collection.
        '''
        pk_name = self.get_pk_field(collection_name)['field']
        item_ids = [data['id'] for data in self.get(f"/items/{collection_name}?fields={pk_name}", params={"limit": -1})]
        if len(item_ids) == 0:
            raise AssertionError("No items to delete!")
        for i in range(0, len(item_ids), 100):
            self.delete(f"/items/{collection_name}", json=item_ids[i:i + 100])

    def get_all_fields(self, collection_name: str) -> list:
        '''
        Return all fields in the directus collection. Remove the id key in metya to avoid errors in inseting this directus field again
        '''
        fields = self.get(f"/fields/{collection_name}")
        for field in fields:
            if 'meta' in field and field['meta'] is not None and 'id' in field['meta']:
                field['meta'].pop('id')

        return fields
    
    def get_pk_field(self, collection_name: str) -> dict:
        '''
        Return the primary key field of the collection
        '''
        return [field for field in self.get(f"/fields/{collection_name}") if field['schema']['is_primary_key']][0]
    
    def get_all_user_created_collection_names(self) -> list:
        '''
        Returns all user created collections. By default Directus GET /collections API will return system collections as well which 
        may not always be useful. 
        '''
        return [ col['collection'] for col in self.get('/collections') if not col['collection'].startswith('directus') ]
    
    def get_all_fk_fields(self, collection_name: str) -> dict:
        '''
        Return all foreign key fields in the directus collection
        '''
        return [ field for field in self.get(f"/fields/{collection_name}") 
            if 'foreign_key_table' in field['schema'].keys()
            and field['schema']['foreign_key_table'] is not None
        ]
    
    def get_relations(self, collection_name: str) -> list:
        '''
        Return all relations in a directus collection in a fixed format. All other keys are usually not necessary
        '''
        return [{
            "collection": relation["collection"],
            "field": relation["field"],
            "related_collection": relation["related_collection"]
        } for relation in self.get(f"/relations/{collection_name}")]

    def post_relation(self, relation: dict) -> None:
        '''
        Keep posting if run into id not unique as sometimes relations are posted with ID, thus not triggering the
        auto-increment of the id field
        '''
        assert set(relation.keys()) == set(['collection', 'field', 'related_collection'])
        try:
            self.post(f"/relations", json=relation)
        except AssertionError as e:
            if '"id" has to be unique' in str(e):
                self.post_relation(relation)
            else:
                raise
