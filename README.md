# API Star Peewee ORM
[![Build Status](https://travis-ci.org/PeRDy/apistar-peewee-orm.svg?branch=master)](https://travis-ci.org/PeRDy/apistar-peewee-orm)
[![codecov](https://codecov.io/gh/PeRDy/apistar-peewee-orm/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/apistar-peewee-orm)
[![PyPI version](https://badge.fury.io/py/apistar-peewee-orm.svg)](https://badge.fury.io/py/apistar-peewee-orm)

* **Version:** 0.2.1
* **Status:** Production/Stable
* **Author:** José Antonio Perdiguero López

Peewee integration for API Star.

## Features
This library provides:
 * Event hooks to handle **connections** and **commit/rollback** behavior based on exceptions in your views.
 * **Migrations** support with a command-line interface to interact with them.

## Quick start
Install API Star Peewee ORM:

```bash
pip install apistar-peewee-orm
```

Create an API Star application adding components and event hooks:

```python
from apistar import App
from apistar_peewee_orm import PeeweeDatabaseComponent, PeeweeTransactionHook

routes = []

components = [
    PeeweeDatabaseComponent(url='sqlite://'),
]

event_hooks = [
    PeeweeTransactionHook(),
]

app = App(routes=routes, components=components, event_hooks=event_hooks)
```

Your models now should inherit from a base model defined in this library:

```python
import peewee
from apistar_peewee_orm import Model


class PuppyModel(Model):
    name = peewee.CharField()
```

## Full Example

```python
import typing

import peewee
from apistar import App, http, Route, types, validators
from apistar_peewee_orm import Model, PeeweeDatabaseComponent, PeeweeTransactionHook


class PuppyModel(Model):
    name = peewee.CharField()


class PuppyType(types.Type):
    id = validators.Integer(allow_null=True, default=None)
    name = validators.String()


def list_puppies() -> typing.List[PuppyType]:
    return [PuppyType(puppy) for puppy in PuppyModel.select()]


def create_puppy(puppy: PuppyType, raise_exception: http.QueryParam) -> http.JSONResponse:
    if raise_exception:
        raise Exception

    model = PuppyModel.create(**puppy)
    return http.JSONResponse(PuppyType(model), status_code=201)


routes = [
    Route('/puppy/', 'POST', create_puppy),
    Route('/puppy/', 'GET', list_puppies),
]

components = [
    PeeweeDatabaseComponent(url='sqlite://'),
]

event_hooks = [
    PeeweeTransactionHook(),
]

app = App(routes=routes, components=components, event_hooks=event_hooks)
```

## CLI Application

An application will be installed along with this library to provide full support for migrations and some other features 
of Peewee and API Star.

```bash
$ apistar-peewee-orm --help

usage: apistar-peewee-orm [-h] [-s SETTINGS] [-q | -v] [--dry-run]
                          {status,upgrade,downgrade,merge,create} ... [app]

positional arguments:
  app                   API Star application path
                        (<package>.<module>:<variable>)

optional arguments:
  -h, --help            show this help message and exit
  -s SETTINGS, --settings SETTINGS
                        Module or object with Clinner settings in format
                        "package.module[:Object]"
  -q, --quiet           Quiet mode. No standard output other than executed
                        application
  -v, --verbose         Verbose level (This option is additive)
  --dry-run             Dry run. Skip commands execution, useful to check
                        which commands will be executed and execution order

Commands:
  {status,upgrade,downgrade,merge,create}
    status              Database migrations and models status.
    upgrade             Run database migrations sequentially.
    downgrade           Rollback database migrations sequentially.
    merge               Merge all migrations into a single one.
    create              Create a new migration. If a module is provided then
                        the migration will be automatically generated,
                        otherwise the migration will be empty.
```
