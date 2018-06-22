import importlib
import typing

import apistar
import peewee
from peewee_migrate import Router

from apistar_peewee_orm import Model, PeeweeDatabaseComponent


class Manager:
    def __init__(self, app: typing.Union[str, apistar.App, apistar.ASyncApp]):
        """
        Create a database manager from API Star application.

        :param app: API Star application.
        :return: Manager instance.
        """
        self.app = self.get_app(app) if isinstance(app, str) else app
        self.component = self.get_database_component(self.app)
        self.router = Router(self.component.database)

    @classmethod
    def get_app(cls, path: str) -> typing.Union[apistar.App, apistar.ASyncApp]:
        """
        Get database manager from API Star app path.

        :param path: API Star app path in format <package>.<module>:<variable>
        :return: Database manager.
        """
        try:
            m, c = path.rsplit(":", 1)
            module = importlib.import_module(m)
            app = getattr(module, c)
        except ValueError:
            raise ImportError("Wrong path path, it should be: <package>.<module>:<variable>")
        except (AttributeError, ImportError):
            raise ImportError("API Star path not found '{}'".format(path))

        return app

    @classmethod
    def get_database_component(cls, app: typing.Union[apistar.App, apistar.ASyncApp]) -> PeeweeDatabaseComponent:
        """
        Get database component from API Star application.

        :param app: API Star application.
        :return: Database component
        """
        for component in app.injector.components:
            if isinstance(component, PeeweeDatabaseComponent):
                return component

        raise ValueError("No 'PeeweeDatabaseComponent' found in API Star application")

    def upgrade(self, target: typing.Optional[str] = None, fake: bool = False):
        """
        Apply migrations sequentially to a target.

        :param target: Target migration name.
        :param fake: Fake migrations.
        """
        self.router.run(target, fake)

    def downgrade(self, target: typing.Optional[str] = None):
        """
        Rollback migrations sequentially to a target.

        :param target: Target migration name.
        """
        self.router.rollback(target)

    def merge(self, name: typing.Optional[str] = None):
        """
        Merge all migrations into a single one.

        :param name: Migration name.
        """
        self.router.merge(name)

    def create(self, name: str, module: typing.Optional[str] = None):
        """
        Create a new migration with given name. If module is provided, the migration will be generated automatically.

        :param name: Migration name.
        :param module: Module to infer changes.
        """
        self.router.create(name, auto=module)

    @property
    def models(self) -> typing.List[peewee.Model]:
        """
        Returns a list of registered models.

        :return: List of registered models.
        """
        return list(Model.register)  # noqa

    def create_tables(self):
        """
        Create tables in database.
        """
        self.component.database.create_tables(self.models)

    def drop_tables(self):
        """
        Drop tables from database.
        """
        self.component.database.drop_tables(self.models)

    def __repr__(self):
        migrations = "\n".join([f"[x] {migration}" for migration in self.router.done])
        migrations += "\n".join([f"[ ] {migration}" for migration in self.router.diff])

        if len(Model.register) == 0:
            models = "No models found."
        elif len(Model.register) == 1:
            models = f"{len(Model.register)} model found:\n"
        else:
            models = f"{len(Model.register)} models found:\n"

        models += "\n".join([f" - {model.__module__}.{model.__name__}" for model in Model.register])
        return f"Migrations\n----------\n{migrations}\n\nModels\n------\n{models}"
