#!/usr/bin/env python3

import route, wsgi

entrypoint = wsgi.app
#entrypoint = lambda *args, **kwargs: wsgi.app(*args, **kwargs)

@route.set(None, r"^/$")
def main(env, match, *args, **kwargs):
	return (200, {}, "main page, unsupported method")

@route.set("GET", r"^/$")
def get(env, match, *args, **kwargs):
	return (200, {}, "hello world!")

@route.set([ "PUT", "POST" ], r"^/$")
def putpost(env, match, *args, **kwargs):
	return (200, {}, {
		"message": "data you sent is here",
		"data": env["body"].decode(),
	})

@route.set(None, r"^/([^/]+)$")
def subpath(env, match, *args, **kwargs):
	return (200, {}, list(match.groups()))

@route.set(None, [ r"^", r"sub", r"sub$" ])
def subsub(env, match, *args, **kwargs):
	return (200, {}, "array sub")

@route.set(None, [ r"^", r"users", r"([0-9]+)$" ])
def regexsub(env, match, *args, **kwargs):
	return (200, {}, list(match.groups()))

@route.set(None, [ r"^", r"([a-z]+)", r"tags", r"([0-9]+)$" ])
def regexsubsub(env, match, *args, **kwargs):
	return (200, {}, list(match.groups()))

print("some routes for you:", list(route.__routes.keys()))
