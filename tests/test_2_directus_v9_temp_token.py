# import sys
# sys.path.append('./directus')
from directus.clients import DirectusClient_V9
import pytest, uuid
import os

url = os.environ.get("BASE_URL", "http://localhost:8055")

client = DirectusClient_V9(url=url, email="admin@example.com", password="password")

@pytest.mark.parametrize(
    "collection_name, pk_type", [
        ("test_collection", "int"),
        ("test_relations_collection", "int"),
        ("uuid_pk_collection", "uuid")
    ]
)
def test_create_collection(collection_name: str, pk_type: str):
    collection_data = {"collection": collection_name, "schema": {}, "meta": {}}
    if pk_type == 'uuid':
        collection_data['fields'] = [{
            "field": "id",
            "type": "uuid",
            "meta": {
                "hidden": True,
                "readonly": True,
                "interface": "text-input",
                "special": ["uuid"]
            },
            "schema": {
                "is_primary_key": True
            }
        }]
    
    client.post("/collections", json=collection_data)

@pytest.mark.parametrize(
    "collection_name, field_name, field_type", 
    [
        ("test_collection", "name", "string"),
        ("test_collection", "comments", "text"),
        ("test_relations_collection", "uuid_fk", "uuid"),
        ("uuid_pk_collection", "title", "string")
    ]
)
def test_create_field(collection_name: str, field_name: str, field_type: str):
    client.post(
        f"/fields/{collection_name}",
        json={
            "field": field_name,
            "type": field_type
        }
    )

@pytest.mark.parametrize(
    "collection_name, name, comments", 
    [
        ("test_collection", "item1", "delete me!"),
        ("test_collection", "item2", "change me!")
    ]
)
def test_create_items(collection_name: str, name: str, comments: str):
    client.post(
        f"/items/{collection_name}",
        json={
            "name": name,
            "comments": comments
        }
    )

@pytest.mark.parametrize(
    "collection_name, id", 
    [
        ("test_collection", 1)
    ]
)
def test_delete_item(collection_name: str, id: int):
    client.delete(
        f"/items/{collection_name}/{id}"
    )

@pytest.mark.parametrize(
    "collection_name, id, name, comments", 
    [
        ("test_collection", 2, "item2_updated", "I am updated!")
    ]
)
def test_update_items(collection_name: str, id: int, name: str, comments: str):
    client.patch(
        f"/items/{collection_name}/{id}",
        json={
            "name": name,
            "comments": comments
        }
    )

@pytest.mark.parametrize(
    "collection_name, num_of_items", 
    [
        ("test_collection", 100)
    ]
)
def test_bulk_insert(collection_name: str, num_of_items: int):
    items = [{
        "name": str(i) + str(uuid.uuid4()),
        "comments": str(uuid.uuid4())
    } for i in range(num_of_items)]
    client.bulk_insert(collection_name, items)

@pytest.mark.parametrize(
    "original_collection_name, duplicated_collection_name", 
    [
        ("test_collection", "duplicated_collection")
    ]
)
def test_duplicate_collection(original_collection_name: str, duplicated_collection_name: str):
    client.duplicate_collection(original_collection_name, duplicated_collection_name)

@pytest.mark.parametrize(
    "collection_name, exists", 
    [
        ("test_collection", True),
        ("duplicated_collection", True),
        ("no_collection", False)
    ]
)
def test_collection_exists(collection_name: str, exists: bool):
    assert client.collection_exists(collection_name) == exists

@pytest.mark.parametrize(
    "collection_name", 
    [
        ("duplicated_collection")
    ]
)
def test_delete_all_items(collection_name: str):
    client.delete_all_items(collection_name)

@pytest.mark.parametrize(
    "collection_name, data_type", 
    [
        ("test_collection", "integer"),
        ("duplicated_collection", "integer"),
        ("uuid_pk_collection", "uuid")
    ]
)
def test_integer_pk(collection_name: str, data_type: str):
    client.get_pk_field(collection_name)['type'] == data_type

@pytest.mark.parametrize(
    "collection_names", 
    [
        (["test_collection", "duplicated_collection", "uuid_pk_collection", "test_relations_collection"])
    ]
)
def test_get_all_user_created_collection_names(collection_names: list):
    assert sorted(client.get_all_user_created_collection_names()) == sorted(collection_names)

@pytest.mark.parametrize(
    "collection_name, field_names", 
    [
        ("test_collection", ["id", "name", "comments"]),
        ("duplicated_collection", ["id", "name", "comments"]),
        ("test_relations_collection", ["id", "uuid_fk"]),
        ("uuid_pk_collection", ["id", "title"]),
    ]
)
def test_get_all_fields(collection_name: str, field_names: list):
    user_fields = [
        field['field'] for field in client.get_all_fields(collection_name)
    ]

    assert sorted(field_names) == sorted(user_fields)

@pytest.mark.parametrize(
    "collection_name, field, related_collection", 
    [
        ("test_relations_collection", "uuid_fk", "uuid_pk_collection")
    ]
)
def test_post_relations(collection_name: str, field: str, related_collection: str):
    client.post_relation({
        "collection": collection_name,
        "field": field,
        "related_collection": related_collection
    })

@pytest.mark.parametrize(
    "collection_name, fk_field_names", 
    [
        ("test_relations_collection", ["uuid_fk"]),
        ("test_collection", []),
        ("duplicated_collection", []),
        ("uuid_pk_collection", [])
    ]
)
def test_get_fk(collection_name: str, fk_field_names: list):
    fk_fields = [
        field['field'] for field in [
            field for field in client.get_all_fk_fields(collection_name)
            if field['schema']['foreign_key_table'] in 
            client.get_all_user_created_collection_names()
        ]
    ]
    assert sorted(fk_fields) == sorted(fk_field_names)

@pytest.mark.parametrize(
    "collection_name, relations", 
    [
        ("test_relations_collection", [{
            "collection": "test_relations_collection",
            "field": "uuid_fk",
            "related_collection": "uuid_pk_collection"
        }]),
        ("test_collection", []),
        ("duplicated_collection", []),
        ("uuid_pk_collection", [])
    ]
)
def test_get_relations(collection_name: str, relations: list):
    assert client.get_relations(collection_name) == relations

@pytest.mark.parametrize(
    "collection_name", 
    [
        ("test_collection"),
        ("duplicated_collection"),
        ("test_relations_collection"),
        ("uuid_pk_collection")
    ]
)
def test_delete_collection(collection_name: str):
    client.delete(f"/collections/{collection_name}")

