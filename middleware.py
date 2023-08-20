#!/usr/bin/env python3

import collections, pathlib, typing

from . import model

default_middleware = lambda *args, **kwargs: (True, print("MiddleWare:", args, kwargs))[0]

__middlewares: typing.OrderedDict[str, typing.Any] = collections.OrderedDict({
	".*": [
		default_middleware,
	],
})


def add(
		methods: typing.Union[typing.Iterable[typing.Union[model.HttpMethod, str]], model.HttpMethod, str, None] = None,
		*route: typing.Union[pathlib.PurePath, typing.Iterable[typing.Union[pathlib.PurePath, str]], str],
		headers: dict = dict(),
		**kwarg: dict,
	):
	path = model.flatten(*route)
	posix = path.as_posix()
	if not methods:
		methods = model.HttpMethod.ANY
	if isinstance(methods,(str, model.HttpMethod)):
		methods = [ methods ]
	def dec(func):
		if posix not in __middlewares.keys():
			__middlewares[posix] = dict()
		elif callable(__middlewares[posix]):
			__middlewares[posix] = dict({ model.HttpMethod.ANY: __middlewares[posix] })
		if methods and isinstance(methods, typing.Iterable):
			__middlewares[posix].update({ m: func for m in methods })
		return (lambda *route, **kwargs: func(*route, headers=headers, **kwargs))
	return dec

