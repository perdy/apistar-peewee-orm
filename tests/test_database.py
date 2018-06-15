import peewee
import pytest

from apistar_peewee_orm import Model, PeeweeDatabaseComponent

database_component = PeeweeDatabaseComponent(url="sqlite+pool://")


class TestCaseRegisterModel:

    @pytest.fixture
    def register(self):
        old_register = Model.register
        Model.register = set()
        yield Model.register
        Model.register = old_register

    def test_model_registration(self, register):
        class PuppyModel(Model):
            name = peewee.CharField()

        assert register == {PuppyModel}
