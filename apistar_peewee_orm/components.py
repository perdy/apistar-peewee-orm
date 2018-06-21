import logging

import peewee
from apistar import Component
from playhouse.db_url import connect

from apistar_peewee_orm.database import _database

logger = logging.getLogger(__name__)

__all__ = ["PeeweeDatabaseComponent"]


class PeeweeDatabaseComponent(Component):
    def __init__(self, url: str, **kwargs) -> None:
        """
        Configure a new database backend.

        :param url: Database url connection string.
        :param kwargs: Connection args.
        """
        self.database = connect(url, **kwargs)
        _database.initialize(self.database)
        logger.info("Peewee connection created")
        logger.debug("Engine connection to %s", url)

    def resolve(self) -> peewee.Database:
        return self.database
