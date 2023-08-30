#!/usr/bin/env python3

from dataclasses import dataclass, is_dataclass, asdict
from typing import Type


def dataclass_to_dict(cls) -> dict:
	if is_dataclass(cls):
		return asdict(cls)
	return cls.__dict__


from . import aws, middleware, route, wsgi

__all__ = [
	"aws",
	"middleware",
	"route",
	"wsgi",
]

