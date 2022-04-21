# import sys
# sys.path.append('./directus')
from directus.clients import DirectusClient_V9
import pytest, uuid

client = DirectusClient_V9(url="http://directus:8055", token="admin")

@pytest.mark.parametrize(
    "collection_name, pk_type", [
        ()
    ]
)