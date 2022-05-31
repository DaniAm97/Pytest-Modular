from typing import Any, Generator

import pytest
from playwright.sync_api import Playwright, APIRequestContext, APIResponse
from uuid import uuid4


@pytest.fixture(scope="session")
def api_request_context(
        playwright: Playwright,
) -> Generator[APIRequestContext, None, None]:
    headers = {
        # We set this header per GitHub guidelines.
        "Accept": "application/vnd.github.v3+json",
        # Add authorization token to all requests.
        # Assuming personal access token available in the environment.
        # "Authorization": f"bearer {TOKEN}"

    }
    request_context = playwright.request.new_context(
        base_url="https://api-dev.hauto.dev/", extra_http_headers=headers
    )
    yield request_context
    request_context.dispose()





def get_random_string():
    return uuid4().hex[:4]


def login_and_return_bearer(api_request_context: APIRequestContext) -> str:
    data_login = {
        "email": "hobeben160@angeleslid.com",
        "password": "123456",
        "org_id": "5edfd39d-d9cd-43dc-ab36-748a03aed01d"
    }

    response = api_request_context.post(f"/api/v1/login", data=data_login)

    bearer = response.json()['access_token']

    return bearer


@pytest.fixture()
def bearer(api_request_context: APIRequestContext):
    return login_and_return_bearer(api_request_context)


@pytest.fixture()
def created_workspace_response(api_request_context: APIRequestContext, bearer) -> APIResponse:
    data_workspace = {

            "name": "dani",
            "org_id": "5edfd39d-d9cd-43dc-ab36-748a03aed01d",
            "type": "recruiting",
            "is_collaboration": False,
            "members": [],
            "topics": []
        }
    response = api_request_context.post("/api/v1/workspaces/", headers={"Authorization": f"bearer {bearer}"},
                                        data=data_workspace)
    print(response.json())
    # return response




@pytest.fixture()
def created_workspace(created_workspace_response: APIResponse):
    print(created_workspace_response.json())


@pytest.fixture()
def refreshed_bearer(api_request_context: APIRequestContext):
    """After creating the workspace this fixture needs to be used to get the brearer token
    to manually refresh the permissions inside the token"""
    return login_and_return_bearer(api_request_context)


def test_create_workspace(created_workspace_response: APIResponse) -> None:
    assert created_workspace_response.status == 201



@pytest.fixture()
def create_topic_response(api_request_context: APIRequestContext, created_workspace: dict[str, Any],
                          refreshed_bearer) -> APIResponse:
    data_topic = {

        "name": f"123456{get_random_string()}"
    }

    ws_id = created_workspace["id"]

    response = api_request_context.post(f"/api/v1/workspaces/{ws_id}/topics/",
                                        headers={"Authorization": f"bearer {refreshed_bearer}"}, data=data_topic)
    return response


@pytest.fixture()
def created_topic(create_topic_response: APIResponse):
    return create_topic_response.json()


def test_create_topic(create_topic_response: APIResponse) -> None:
    assert create_topic_response.status == 201


@pytest.fixture()
def create_skill_response(api_request_context: APIRequestContext, created_workspace: dict[str, Any],
                          create_topic: dict[str, Any], refreshed_bearer) -> APIResponse:
    ws_id = created_workspace['id']
    topic_id = create_topic['id']

    data_skill = {
        "name": "skill",
        "workspace_id": f'{ws_id}',
        "topic_id": f"{topic_id}",
    }
    response = api_request_context.post(f"api/v1/skills/", headers={
        "Authorization": f"bearer {refreshed_bearer}"}, data=data_skill)
    return response


@pytest.fixture()
def created_skill(create_skill_response: APIResponse):
    return create_skill_response.json()


def test_create_skill(create_skill_response: APIResponse):
    return create_skill_response.status == 201


@pytest.fixture()
def create_step_response(api_request_context: APIRequestContext, created_skill
                         , refreshed_bearer) -> APIResponse:
    data_step = {
        "name": "string",
        "display_mode": "progress",
        "widgets": [
            {
                "widget_type": 1,
                "description": "",
                "is_required": False,
                "is_gradeable": False,
                "content": {
                    "source": 101,
                    "type": 1,
                    "data": "string",
                    "data_id": "6d9132b6-7d4b-48aa-b5c7-f341d7b86bfb",
                    "description": "",
                    "options": {
                        "start_at_timestamp": "00:00",
                        "media_duration": 0
                    }
                }
            }
        ],
        "is_shared": False
    }
    skill_id = created_skill['id']

    response = api_request_context.post(f"/api/v1/skills/{skill_id}/steps/",
                                        headers={"Authorization": f"bearer {refreshed_bearer}"}, data=data_step)
    return response


@pytest.fixture()
def created_step(create_step_response: APIResponse):
    return create_step_response.json()


def test_create_step(create_step_response: APIResponse):
    assert create_step_response.status == 201

@pytest.fixture()
def create_widget_response(api_request_context: APIRequestContext,created_skill,created_step,refreshed_bearer) -> APIResponse:
    data_widget = {
        "widget_type": 1,
        "description": "",
        "is_required": False,
        "is_gradeable": False,
        "content": {
            "source": 101,
            "type": 1,
            "data": "string",
            "data_id": "6d9132b6-7d4b-48aa-b5c7-f341d7b86bfb",
            "description": "",
            "options": {
                "start_at_timestamp": "00:00",
                "media_duration": 0
            }
        }
    }
    skill_id = created_skill["id"]
    step_id = created_step["id"]
    response = api_request_context.post(f"/api/v1/skills/{skill_id}/steps/{step_id}/widgets/",
                                        headers={"Authorization": f"bearer {refreshed_bearer}"}, data=data_widget)
    return response

@pytest.fixture()
def created_widget(create_widget_response: APIResponse):
    return create_widget_response.json()


def test_create_widget(create_widget_response: APIResponse):
    assert create_widget_response.status == 201