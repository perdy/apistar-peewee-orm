from typing import List

import peewee
import pytest

from apistar import App, ASyncApp, Route, TestClient, http, types, validators
from apistar_peewee_orm import PeeweeDatabaseComponent, PeeweeTransactionHook


database_component = PeeweeDatabaseComponent(url="sqlite+pool://")


class PuppyModel(peewee.Model):
    name = peewee.CharField()

    class Meta:
        database = database_component.database


class PuppyType(types.Type):
    id = validators.Integer(allow_null=True, default=None)
    name = validators.String()


def list_puppies() -> List[PuppyType]:
    return [PuppyType(puppy) for puppy in PuppyModel.select()]


def create_puppy(puppy: PuppyType, raise_exception: http.QueryParam) -> http.JSONResponse:
    if raise_exception:
        raise Exception

    model = PuppyModel.create(**puppy)
    return http.JSONResponse(PuppyType(model), status_code=201)


components = [database_component]
event_hooks = [PeeweeTransactionHook]
routes = [Route("/puppy/", "POST", create_puppy), Route("/puppy/", "GET", list_puppies)]

app = App(
    routes=routes, components=components, event_hooks=event_hooks, static_dir=None, docs_url=None, schema_url=None
)
async_app = ASyncApp(
    routes=routes, components=components, event_hooks=event_hooks, static_dir=None, docs_url=None, schema_url=None
)


@pytest.fixture(params=[app, async_app])
def client(request):
    with database_component.database:
        database_component.database.create_tables([PuppyModel])
    yield TestClient(request.param)
    with database_component.database:
        database_component.database.drop_tables([PuppyModel])


@pytest.fixture
def puppy():
    return {"name": "canna"}


class TestCaseEndToEnd:

    def test_insert_and_select_success(self, client, puppy):
        # Successfully create a new record
        response = client.post("/puppy/", json=puppy)
        created_puppy = response.json()
        assert response.status_code == 201
        assert created_puppy["name"] == "canna"

        # List all the existing records
        response = client.get("/puppy/")
        assert response.status_code == 200
        assert response.json() == [created_puppy]

    def test_insert_and_select_handled_exception(self, client):
        # Failed to create a new record
        response = client.post("/puppy/", json={})
        assert response.status_code == 400

        # List all the existing records
        response = client.get("/puppy/")
        assert response.status_code == 200
        assert response.json() == []

    def test_insert_and_select_unhandled_exception(self, client, puppy):
        with pytest.raises(Exception):
            # Failed to create a new record
            response = client.post("/puppy/?raise_exception=true", json=puppy)
            assert response.status_code == 500

        # List all the existing records
        response = client.get("/puppy/")
        assert response.status_code == 200
        assert response.json() == []
