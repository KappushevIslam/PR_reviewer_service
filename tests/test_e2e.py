def test_full_workflow(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    team_data = {
        "team_name": "test_team",
        "members": [
            {"user_id": "t1", "username": "TestUser1", "is_active": True},
            {"user_id": "t2", "username": "TestUser2", "is_active": True},
            {"user_id": "t3", "username": "TestUser3", "is_active": True},
        ],
    }
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 201
    assert response.json()["team"]["team_name"] == "test_team"

    response = client.get("/team/get", params={"team_name": "test_team"})
    assert response.status_code == 200
    assert len(response.json()["members"]) == 3

    pr_data = {"pull_request_id": "test-pr-1", "pull_request_name": "Test PR", "author_id": "t1"}
    response = client.post("/pullRequest/create", json=pr_data)
    assert response.status_code == 201
    pr = response.json()["pr"]
    assert pr["status"] == "OPEN"
    assert len(pr["assigned_reviewers"]) <= 2
    assert "t1" not in pr["assigned_reviewers"]

    response = client.get("/users/getReview", params={"user_id": pr["assigned_reviewers"][0]})
    assert response.status_code == 200
    assert len(response.json()["pull_requests"]) == 1

    response = client.post("/pullRequest/merge", json={"pull_request_id": "test-pr-1"})
    assert response.status_code == 200
    assert response.json()["pr"]["status"] == "MERGED"

    response = client.post("/pullRequest/merge", json={"pull_request_id": "test-pr-1"})
    assert response.status_code == 200
    assert response.json()["pr"]["status"] == "MERGED"

    response = client.get("/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_prs"] >= 1
    assert stats["merged_prs"] >= 1


def test_reassignment_workflow(client):
    team_data = {
        "team_name": "reassign_team",
        "members": [
            {"user_id": "r1", "username": "User1", "is_active": True},
            {"user_id": "r2", "username": "User2", "is_active": True},
            {"user_id": "r3", "username": "User3", "is_active": True},
            {"user_id": "r4", "username": "User4", "is_active": True},
        ],
    }
    client.post("/team/add", json=team_data)

    pr_data = {"pull_request_id": "test-pr-2", "pull_request_name": "Test PR 2", "author_id": "r1"}
    response = client.post("/pullRequest/create", json=pr_data)
    original_reviewers = response.json()["pr"]["assigned_reviewers"]

    reassign_data = {"pull_request_id": "test-pr-2", "old_user_id": original_reviewers[0]}
    response = client.post("/pullRequest/reassign", json=reassign_data)
    assert response.status_code == 200
    new_reviewers = response.json()["pr"]["assigned_reviewers"]
    assert original_reviewers[0] not in new_reviewers
    assert response.json()["replaced_by"] in new_reviewers


def test_error_handling(client):
    response = client.post(
        "/team/add",
        json={"team_name": "error_team", "members": [{"user_id": "e1", "username": "ErrorUser", "is_active": True}]},
    )
    assert response.status_code == 201

    response = client.post(
        "/team/add",
        json={"team_name": "error_team", "members": [{"user_id": "e2", "username": "ErrorUser2", "is_active": True}]},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "TEAM_EXISTS"

    response = client.post(
        "/pullRequest/create",
        json={"pull_request_id": "error-pr", "pull_request_name": "Error PR", "author_id": "nonexistent"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"


def test_deactivate_users(client):
    team_data = {
        "team_name": "deactivate_team",
        "members": [
            {"user_id": "d1", "username": "DeactUser1", "is_active": True},
            {"user_id": "d2", "username": "DeactUser2", "is_active": True},
            {"user_id": "d3", "username": "DeactUser3", "is_active": True},
        ],
    }
    client.post("/team/add", json=team_data)

    client.post(
        "/pullRequest/create",
        json={"pull_request_id": "deact-pr-1", "pull_request_name": "Deact PR", "author_id": "d1"},
    )

    response = client.post("/team/deactivateUsers", json={"team_name": "deactivate_team", "user_ids": ["d2"]})
    assert response.status_code == 200
    assert response.json()["deactivated_users"] >= 1
