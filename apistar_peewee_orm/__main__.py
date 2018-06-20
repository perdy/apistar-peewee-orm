#!/usr/bin/env python3.6
"""Run script.
"""
import importlib
import logging
import os
import sys
import typing

import apistar
import peewee_migrate
from clinner.command import Type as CommandType
from clinner.command import command
from clinner.exceptions import ImproperlyConfigured
from clinner.run.main import Main as ClinnerMain

from apistar_peewee_orm import Model, PeeweeDatabaseComponent

logger = logging.getLogger("cli")
peewee_migrate.LOGGER = logger

sys.path.insert(0, os.getcwd())


class DatabaseManager:
    @classmethod
    def get_app(cls, path: str) -> typing.Union[apistar.App, apistar.ASyncApp]:
        """
        Get database manager from API Star app path.

        :param path: API Star app path in format <package>.<module>:<variable>
        :return: Database manager.
        """
        try:
            try:
                m, c = path.rsplit(":", 1)
                module = importlib.import_module(m)
                app = getattr(module, c)
            except ValueError:
                raise ImportError("Wrong path path, it should be: <package>.<module>:<variable>")
        except ImportError:
            raise ImportError("API Star path not found '{}'".format(path))

        return app

    @classmethod
    def get_database_component(cls, app: typing.Union[apistar.App, apistar.ASyncApp]) -> PeeweeDatabaseComponent:
        for component in app.injector.components:
            if isinstance(component, PeeweeDatabaseComponent):
                return component

        raise ValueError("No 'PeeweeDatabaseComponent' found in API Star application")

    @classmethod
    def from_app(cls, path: str) -> peewee_migrate.Router:
        return peewee_migrate.Router(cls.get_database_component(cls.get_app(path)).database)


@command(command_type=CommandType.PYTHON, parser_opts={"help": "Database migrations and models status."})
def status(*args, **kwargs):
    manager = DatabaseManager.from_app(os.environ["APISTAR_APP"])

    migrations = "\n".join([f"[x] {migration}" for migration in manager.done])
    migrations += "\n".join([f"[ ] {migration}" for migration in manager.diff])

    if len(Model.register) == 0:
        models = "No models found."
    elif len(Model.register) == 1:
        models = f"{len(Model.register)} model found:\n"
    else:
        models = f"{len(Model.register)} models found:\n"

    models += "\n".join([f" - {model.__module__}.{model.__name__}" for model in Model.register])
    logger.info(f"Migrations:\n{migrations}\nw\n{models}")


@command(
    command_type=CommandType.PYTHON,
    args=(
        (("target",), {"help": "Last migration to be applied", "nargs": "?"}),
        (("--fake",), {"help": "Fake migrations"}),
    ),
    parser_opts={"help": "Run database migrations sequentially."},
)
def upgrade(*args, **kwargs):
    DatabaseManager.from_app(os.environ["APISTAR_APP"]).run(kwargs["target"], fake=kwargs["fake"])


@command(
    command_type=CommandType.PYTHON,
    args=((("target",), {"help": "Last migration to be rollback", "nargs": "?"}),),
    parser_opts={"help": "Rollback database migrations sequentially."},
)
def downgrade(*args, **kwargs):
    DatabaseManager.from_app(os.environ["APISTAR_APP"]).rollback(kwargs["target"])


@command(
    command_type=CommandType.PYTHON,
    args=((("name",), {"help": "Result migration name", "nargs": "?"}),),
    parser_opts={"help": "Merge all migrations into a single one."},
)
def merge(*args, **kwargs):
    DatabaseManager.from_app(os.environ["APISTAR_APP"]).merge(kwargs["name"])


@command(
    command_type=CommandType.PYTHON,
    args=((("name",), {"help": "Migration name"}), (("module",), {"help": "Target module", "nargs": "?"})),
    parser_opts={
        "help": "Create a new migration. If a module is provided then the migration will be automatically generated, "
        "otherwise the migration will be empty."
    },
)
def create(*args, **kwargs):
    DatabaseManager.from_app(os.environ["APISTAR_APP"]).create(kwargs["name"], auto=kwargs["module"])


class Main(ClinnerMain):
    def add_arguments(self, parser: "argparse.ArgumentParser"):
        super(Main, self).add_arguments(parser)
        parser.add_argument("app", help="API Star application path (<package>.<module>:<variable>)", nargs="?")

    def inject_app(self):
        if self.args.app:
            os.environ.setdefault("APISTAR_APP", self.args.app)

        if "APISTAR_APP" not in os.environ:
            raise ImproperlyConfigured(
                "API Star application not specified, use APISTAR_APP environment variable or command parameter."
            )


def main():
    sys.exit(Main().run())


if __name__ == "__main__":
    main()
