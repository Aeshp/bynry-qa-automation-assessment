import requests


class WorkFlowProAPIClient:
    def __init__(self, base_url: str, tenant_id: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json",
        })

    def create_project(self, name: str, description: str, team_members: list) -> dict:
        resp = self.session.post(
            f"{self.base_url}/projects",
            json={"name": name, "description": description, "team_members": team_members},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_project(self, project_id: int) -> dict:
        resp = self.session.get(f"{self.base_url}/projects/{project_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def delete_project(self, project_id: int) -> None:
        resp = self.session.delete(f"{self.base_url}/projects/{project_id}", timeout=10)
        resp.raise_for_status()
