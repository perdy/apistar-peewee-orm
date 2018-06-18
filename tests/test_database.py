import peewee
import pytest

from apistar_peewee_orm import Model


@pytest.fixture
def model():
    old_register = Model.register
    Model.register = set()
    yield Model
    Model.register = old_register


class TestCaseRegisterModel:

    def test_model_registration(self, model):
        class PuppyModel(model):
            name = peewee.CharField()

        assert model.register == {PuppyModel}
