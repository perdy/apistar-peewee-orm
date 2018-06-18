#!/usr/bin/env python3.6
"""Run script.
"""
import importlib
import logging
import os
import sys
import typing

import apistar
import peewee_moves
from clinner.command import Type as CommandType
from clinner.command import command
from clinner.run.main import Main as ClinnerMain

from apistar_peewee_orm import PeeweeDatabaseComponent, Model

logger = logging.getLogger("cli")
peewee_moves.LOGGER = logger

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
    def from_app(cls, path: str) -> peewee_moves.DatabaseManager:
        return peewee_moves.DatabaseManager(cls.get_database_component(cls.get_app(path)).database)


@command(command_type=CommandType.PYTHON, parser_opts={"help": "Database migrations and models status"})
def status(*args, **kwargs):
    DatabaseManager.from_app(kwargs["app"]).status()
    if len(Model.register) == 0:
        models = "No models found."
    elif len(Model.register) == 1:
        models = f"{len(Model.register)} model found:\n"
    else:
        models = f"{len(Model.register)} models found:\n"

    models += "\n".join([f" - {model.__module__}.{model.__name__}" for model in Model.register])
    logger.info(models)


@command(
    command_type=CommandType.PYTHON,
    args=((("target",), {"help": "Target migration", "nargs": "?"}),),
    parser_opts={"help": "Database migrations upgrade"},
)
def upgrade(*args, **kwargs):
    DatabaseManager.from_app(kwargs["app"]).upgrade(kwargs["target"])


@command(
    command_type=CommandType.PYTHON,
    args=((("target",), {"help": "Target migration", "nargs": "?"}),),
    parser_opts={"help": "Database migrations downgrade"},
)
def downgrade(*args, **kwargs):
    DatabaseManager.from_app(kwargs["app"]).downgrade(kwargs["target"])


@command(
    command_type=CommandType.PYTHON,
    args=((("migration",), {"help": "Migration number"}),),
    parser_opts={"help": "Delete a migration"},
)
def delete(*args, **kwargs):
    DatabaseManager.from_app(kwargs["app"]).delete(kwargs["migration"])


@command(
    command_type=CommandType.PYTHON,
    args=((("model",), {"help": "Target model"}),),
    parser_opts={"help": "Create a new migration"},
)
def create(*args, **kwargs):
    DatabaseManager.from_app(kwargs["app"]).create(kwargs["model"])


class Main(ClinnerMain):

    def add_arguments(self, parser: "argparse.ArgumentParser"):
        super(Main, self).add_arguments(parser)
        parser.add_argument("app", help="API Star application path (<package>.<module>:<variable>)")


def main():
    sys.exit(Main().run())


if __name__ == "__main__":
    main()
