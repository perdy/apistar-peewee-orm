# API Star Peewee ORM
[![Build Status](https://travis-ci.org/PeRDy/apistar-peewee-orm.svg?branch=master)](https://travis-ci.org/PeRDy/apistar-peewee-orm)
[![codecov](https://codecov.io/gh/PeRDy/apistar-peewee-orm/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/apistar-peewee-orm)
[![PyPI version](https://badge.fury.io/py/apistar-peewee-orm.svg)](https://badge.fury.io/py/apistar-peewee-orm)

* **Version:** 0.1.1
* **Status:** Production/Stable
* **Author:** José Antonio Perdiguero López

Peewee integration for API Star.

## Features
This library provides event_hooks to handle connections and commit/rollback behavior based on exceptions in your views.

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
