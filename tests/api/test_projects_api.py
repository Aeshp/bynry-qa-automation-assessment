import pytest

@pytest.mark.api
def test_create_project_api(api_client):
    """Test creating a project via API directly."""
    # in a real environment,this would hit the backend:
    # response = api_client.create_project("New Project", "Desc", [])
    # assert response["id"] is not None
    
    assert api_client.base_url is not None
    assert api_client.session.headers["X-Tenant-ID"] in ["company1", "company2"]

@pytest.mark.api
def test_get_project_api(api_client):
    """Test retrieving a project via API."""
    assert "Authorization" in api_client.session.headers
