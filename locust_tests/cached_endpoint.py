from locust import HttpUser, task, constant


class WebUser(HttpUser):
    wait_time = constant(5)

    @task
    def slow_endpoint(self):
        self.client.get('/playground/slow_endpoint/')
