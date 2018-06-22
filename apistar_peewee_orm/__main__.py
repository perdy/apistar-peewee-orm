import logging
import os
import sys

import peewee_migrate
from clinner.command import Type as CommandType
from clinner.command import command
from clinner.exceptions import ImproperlyConfigured
from clinner.run.main import Main as ClinnerMain

from apistar_peewee_orm.manager import Manager

logger = logging.getLogger("apistar_peewee_orm.cli")
logger.addHandler(logging.StreamHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

peewee_migrate.LOGGER = logger  # Redirect peewee_migrate logger to apistar_peewee_orm

sys.path.insert(0, os.getcwd())


@command(command_type=CommandType.PYTHON, parser_opts={"help": "Database migrations and models status."})
def status(*args, **kwargs):
    manager = Manager(os.environ["APISTAR_APP"])
    logger.info(repr(manager))


@command(
    command_type=CommandType.PYTHON,
    args=(
        (("target",), {"help": "Last migration to be applied", "nargs": "?"}),
        (("--fake",), {"help": "Fake migrations"}),
    ),
    parser_opts={"help": "Run database migrations sequentially."},
)
def upgrade(*args, **kwargs):
    Manager(os.environ["APISTAR_APP"]).upgrade(kwargs["target"], fake=kwargs["fake"])


@command(
    command_type=CommandType.PYTHON,
    args=((("target",), {"help": "Last migration to be rollback", "nargs": "?"}),),
    parser_opts={"help": "Rollback database migrations sequentially."},
)
def downgrade(*args, **kwargs):
    Manager(os.environ["APISTAR_APP"]).downgrade(kwargs["target"])


@command(
    command_type=CommandType.PYTHON,
    args=((("name",), {"help": "Result migration name", "nargs": "?"}),),
    parser_opts={"help": "Merge all migrations into a single one."},
)
def merge(*args, **kwargs):
    Manager(os.environ["APISTAR_APP"]).merge(kwargs["name"])


@command(
    command_type=CommandType.PYTHON,
    args=((("name",), {"help": "Migration name"}), (("module",), {"help": "Target module", "nargs": "?"})),
    parser_opts={
        "help": "Create a new migration. If a module is provided then the migration will be automatically generated, "
        "otherwise the migration will be empty."
    },
)
def create(*args, **kwargs):
    Manager(os.environ["APISTAR_APP"]).create(kwargs["name"], kwargs["module"])


@command(command_type=CommandType.PYTHON, parser_opts={"help": "Create tables into database."})
def create_tables(*args, **kwargs):
    Manager(os.environ["APISTAR_APP"]).create_tables()


@command(command_type=CommandType.PYTHON, parser_opts={"help": "Drop tables from database."})
def drop_tables(*args, **kwargs):
    Manager(os.environ["APISTAR_APP"]).drop_tables()


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
