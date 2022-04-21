from directus.clients import DirectusClient_V9

client = DirectusClient_V9(url="http://directus:8055", email="admin@example.com", password="password")

id = client.get("/users/me")['id']

client.patch(f'/users/{id}', json={"token": "admin"})

