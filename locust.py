from locust import HttpUser, task, between

token = 'admin'
class HelloWorldUser(HttpUser):
    wait_time = between(1, 10)

    @task
    def get_data_test(self):
        self.client.get("/items/test_collection", headers={"Authorization": f"Bearer {token}"})

    @task
    def get_data_duplicated(self):
        self.client.get("/items/duplicated_collection", headers={"Authorization": f"Bearer {token}"})
