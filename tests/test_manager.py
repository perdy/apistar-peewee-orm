import pytest
from apistar import App

from apistar_peewee_orm import Model, PeeweeDatabaseComponent
from apistar_peewee_orm.manager import Manager
from mock import Mock, call

app_mock = App(routes=[], components=[PeeweeDatabaseComponent(url="sqlite://")])


class TestCaseManager:
    @pytest.fixture
    def component(self):
        return PeeweeDatabaseComponent(url="sqlite://")

    @pytest.fixture
    def app(self, component):
        return App(routes=[], components=[component])

    @pytest.fixture
    def manager(self, app):
        manager = Manager(app)
        manager.router = Mock()
        manager.component = Mock()
        return manager

    def test_init_app_path(self):
        manager = Manager("tests.test_manager:app_mock")
        assert manager.app == app_mock

    def test_init_app_path_wrong_format(self):
        with pytest.raises(ImportError):
            Manager("wrong-format")

    def test_init_app_path_wrong_path(self):
        with pytest.raises(ImportError):
            Manager("tests.test_manager:wrong_app")

    def test_init_app_without_component(self):
        with pytest.raises(ValueError):
            Manager(App(routes=[]))

    def test_init_app_object(self, app):
        manager = Manager(app)
        assert manager.app == app

    def test_upgrade(self, manager):
        expected_calls = [call("foo", True)]

        manager.upgrade("foo", True)

        assert manager.router.run.call_args_list == expected_calls

    def test_downgrade(self, manager):
        expected_calls = [call("foo")]

        manager.downgrade("foo")

        assert manager.router.rollback.call_args_list == expected_calls

    def test_merge(self, manager):
        expected_calls = [call("foo")]

        manager.merge("foo")

        assert manager.router.merge.call_args_list == expected_calls

    def test_create(self, manager):
        expected_calls = [call("foo", auto="bar")]

        manager.create("foo", "bar")

        assert manager.router.create.call_args_list == expected_calls

    def test_create_tables(self, manager):
        expected_calls = [call(list(Model.register))]

        manager.create_tables()

        assert manager.component.database.create_tables.call_args_list == expected_calls

    def test_drop_tables(self, manager):
        expected_calls = [call(list(Model.register))]

        manager.drop_tables()

        assert manager.component.database.drop_tables.call_args_list == expected_calls

    def test_repr(self, manager):
        pass
