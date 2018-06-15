import peewee

__all__ = ["Model"]


_database = peewee.Proxy()


class Model(peewee.Model):
    register = set()

    def __init_subclass__(cls, **kwargs):
        cls.register.add(cls)

    class Meta:
        database = _database
