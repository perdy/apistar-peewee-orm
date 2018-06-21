import logging

import peewee
from apistar import http

logger = logging.getLogger(__name__)

__all__ = ["PeeweeTransactionHook"]


class PeeweeTransactionHook:
    def __init__(self):
        self.transaction = None

    def on_request(self, database: peewee.Database):
        self.begin(database)

    def on_response(self, response: http.Response, database: peewee.Database, exc: Exception):
        if not database.is_closed():  # pragma: no cover
            if exc is None:
                database.commit()
                logger.debug("Commit")
                self.end(database)
            else:
                database.rollback()
                logger.debug("Rollback")
                self.end(database)

        return response

    def on_error(self, database: peewee.Database):
        if not database.is_closed():  # pragma: no cover
            database.rollback()
            logger.debug("Rollback")
            self.end(database)

    def begin(self, database: peewee.Database):
        """
        Create database connection and begin a transaction.

        :param database: Database.
        """
        database.connect(reuse_if_open=True)
        self.transaction = database.atomic()
        self.transaction.__enter__()

    def end(self, database: peewee.Database):
        """
        Ends transaction and closes database connection.

        :param database: Database
        """
        self.transaction.__exit__(None, None, None)
        self.transaction = None
        database.close()
