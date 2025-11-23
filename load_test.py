from locust import HttpUser, task, between
import random


class PRReviewerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.team_created = False
        self.user_ids = []
        self.pr_ids = []
    
    @task(1)
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def create_team(self):
        if not self.team_created:
            team_name = f"team_{random.randint(1000, 9999)}"
            members = [
                {"user_id": f"u{i}_{team_name}", "username": f"User{i}", "is_active": True}
                for i in range(1, 6)
            ]
            self.user_ids = [m["user_id"] for m in members]
            
            response = self.client.post("/team/add", json={
                "team_name": team_name,
                "members": members
            })
            
            if response.status_code == 201:
                self.team_created = True
                self.team_name = team_name
    
    @task(5)
    def create_pull_request(self):
        if self.team_created and self.user_ids:
            pr_id = f"pr_{random.randint(10000, 99999)}"
            author_id = random.choice(self.user_ids)
            
            response = self.client.post("/pullRequest/create", json={
                "pull_request_id": pr_id,
                "pull_request_name": f"Feature {pr_id}",
                "author_id": author_id
            })
            
            if response.status_code == 201:
                self.pr_ids.append(pr_id)
    
    @task(2)
    def get_team(self):
        if self.team_created:
            self.client.get(f"/team/get?team_name={self.team_name}")
    
    @task(2)
    def get_user_reviews(self):
        if self.user_ids:
            user_id = random.choice(self.user_ids)
            self.client.get(f"/users/getReview?user_id={user_id}")
    
    @task(1)
    def get_statistics(self):
        self.client.get("/statistics")
    
    @task(2)
    def merge_pull_request(self):
        if self.pr_ids:
            pr_id = random.choice(self.pr_ids)
            self.client.post("/pullRequest/merge", json={"pull_request_id": pr_id})

