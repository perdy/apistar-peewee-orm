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
                self.transaction.commit()
                logger.debug("Commit")
                self.end(database)
            else:
                self.transaction.rollback()
                logger.debug("Rollback")
                self.end(database)

        return response

    def on_error(self, database: peewee.Database):
        if not database.is_closed():  # pragma: no cover
            self.transaction.rollback()
            logger.debug("Rollback")
            self.end(database)

    def begin(self, database: peewee.Database):
        """
        Create database connection and begin a transaction.

        :param database: Database.
        """
        database.connect(reuse_if_open=True)
        self._atomic = database.atomic()
        self.transaction = self._atomic.__enter__()

    def end(self, database: peewee.Database):
        """
        Ends transaction and closes database connection.

        :param database: Database
        """
        self._atomic.__exit__(None, None, None)
        self._atomic = None
        self.transaction = None
        database.close()
