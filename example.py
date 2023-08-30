#!/usr/bin/env python3

import re

from . import model, route, wsgi


entrypoint = wsgi.app
#entrypoint = lambda *args, **kwargs: wsgi.app(*args, **kwargs)

@route.set(None, r"^/$")
def home(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, "home page, any unsupported method")

@route.set("GET", r"^/$")
def get(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, "hello world!")

@route.set([ "PUT", "POST" ], r"^/$")
def putpost(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, {
		"message": "data you sent is here",
		"data": http.body,
	})

@route.set(None, r"^/([^/]+)$")
def subpath(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, match.groups())

@route.set(None, [ r"^", r"sub", r"sub$" ])
def subsub(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, "array sub")

@route.set(None, [ r"^", r"users", r"(?P<user>[0-9]+)$" ])
def regexsub(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, dict(as_list=match.groups(), as_dict=match.groupdict()))

@route.set(None, [ r"^", r"([a-z]+)", r"tags", r"([0-9]+)$" ])
def regexsubsub(http: model.HttpRequest, match: re.Match, *args, **kwargs):
	return (200, {}, match.groups())

print("some routes for you:", list(route.get(None)))

print(route.handle(route.model.HttpRequest(method="GET", path="/tags")))
