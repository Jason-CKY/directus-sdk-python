<h1>
    <img src="assets/logo.jpg", width="40", alt="Directus Logo"> Directus Python SDK
</h1>

![.github/workflows/test.yml](https://raw.githubusercontent.com/Jason-CKY/directus-sdk-python/badges/master/test-badge.svg)

## Requirements

- Python 3.6+

## Installation

```bash
pip install -e .
```

## Usage

### Initializa directus client

```python
from directus.clients import DirectusClient_V9

# Create a directus client connection with user static token
client = DirectusClient_V9(url="http://localhost:8055", token="admin-token")

# Or create a directus client connection with email and password
client = DirectusClient_V9(url="http://localhost:8055", email="user@example.com", password="password")
```

### Logging in and out of the client

```python
client = DirectusClient_V9(url="http://localhost:8055", email="user@example.com", password="password")

# Log out and use static token instead
client.logout()
client.static_token = "admin-token"
client.login(email="user2@example.com", password="password2")
```

### Generic API requests

The directus client automatically handles the injection of access token so any [directus API requests](https://docs.directus.io/reference/introduction/) can be simplified like so:

```python
# GET request
collection = client.get(f"/collections/{collection_name}")
item = client.get(f"/items/{collection_name}/1")

# POST request
items = [
    {
        "name": "item1"
    },
    {
        "name": "item2"
    }
]

client.post(f"/items/{collection_name}", json=items)

# PATCH request
client.patch(f"/items/{collection_name}/1", json={
    "name": "updated item1"
})

# DELETE request
client.delete(f"/items/{collection_name}/1")
```

#### Bulk Insert

> **Params:** collection_name: str, items: list

```python
client.bulk_insert(collection_name="test-collection",
                    items=[{"Title": "test"}, {"Title": "test2"}])
```

#### Duplicate Collection

> **Params:** collection_name: str, duplicate_collection_name: str

```python
client.duplicate_collection(collection_name="test-collection", duplicate_collection_name="test_duplication_collection")
```

#### Checks if collection exists

> **Params** collection_name: str, items: list

```python
if client.collection_exists("test"):
    print("test collection exists!")
```

#### Delete all items from a collection

> **Params:** collection_name: str

```python
client.delete_all_items("test")
```

#### Get collection primary key

> **Params:** collection_name: str

```python
pk_field = client.get_pk_field("brands")
```

#### Get all user-created collection names

> **Params:**

```python
print("Listing all user-created collections on directus...")
for name in client.get_all_user_created_collection_names():
    print(name)
```

#### Get all field names of a given collection

> **Params:** collection_name: str

```python
print("Listing all fields in test collection...")
for field in client.get_all_fields("test"):
    print(json.dumps(field, indent=4))
```

#### Get all foreign key fields in directus collection

> **Params:** collection_name: str

```python
print("Listing all foreign key fields in test collection...")
for field in client.get_all_fk_fields("brands"):
    print(json.dumps(field, indent=4))
```

#### Get all relations in directus collection

> **Params:** collection_name: str

```python
import json
print("Listing all relations in test collection...")
for field in client.get_relations("test"):
    print(json.dumps(field, indent=4))
```

#### Create relations

> **Params:** relation: dict

```python
client.post_relation({
    "collection": "books",
    "field": "author",
    "related_collection": "authors"
})
```


## TODOs:

* debug test cases
* add proper pytest