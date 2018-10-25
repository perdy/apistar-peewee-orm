import logging

import peewee
from apistar import http

logger = logging.getLogger(__name__)

__all__ = ["PeeweeTransactionHook"]


class PeeweeTransactionHook:
    def on_request(self, database: peewee.Database):
        database.atomic().__enter__()

    def on_response(self, response: http.Response, database: peewee.Database, exc: Exception):
        if not database.is_closed():  # pragma: no cover
            if exc is None:
                database.commit()
                logger.debug("Commit")
            else:
                database.rollback()
                logger.debug("Rollback")

            database.__exit__(type(exc), exc, None)

        return response

    def on_error(self, database: peewee.Database):
        if not database.is_closed():  # pragma: no cover
            database.rollback()
            logger.debug("Rollback")
            database.__exit__(None, None, None)
