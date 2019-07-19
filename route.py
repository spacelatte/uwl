#!/usr/bin/env python3

import re, os, sys, time, json, collections

__routes = collections.OrderedDict({
	"^/$": (lambda *args, **kwargs: (200, {},
		"default route: #{} {}#".format(args, kwargs),
	)),
})

flatten = lambda stuff: (
	(r"/").join([ flatten(part) for part in stuff ])
	if isinstance(stuff, (tuple, list)) else str(stuff)
)

def find(routes, http):
	def function(event, match, callback):
		if callable(callback):
			(status, headers, body) = callback(event, match)
			headers["access-control-allow-origin"] = "*"
			if not isinstance(body, (str, bytes)):
				headers["content-type"] = "application/json"
				body = json.dumps(body, indent='\t')
			return (status, headers, body)
		return (200,
			{ "content-type": "application/json" },
			json.dumps(callback, indent='\t'),
		)
	for k, v in routes.items():
		match = re.match(k, http["path"])
		if not match:
			continue
		if callable(v):
			return function(http, match, v)
		if isinstance(v, dict):
			method = http["method"]
			if method in list(v.keys()):
				return function(http, match, v[method])
			elif "DEF" in v.keys():
				return function(http, match, v["DEF"])
			pass
		if isinstance(v, str):
			return (200, { "content-type": "text/plain" }, v)
		if isinstance(v, list):
			return (200,
				{ "content-type": "application/json" },
				json.dumps(v, indent='\t'),
			)
		if isinstance(v, tuple):
			return v
		continue
	return None

def handle(env, **kwargs):
	return find(__routes, {
		"uri":    (env["REQUEST_URI"]),
		"path":   (env["PATH_INFO"]),
		"query":  (env["QUERY_STRING"]),
		"scheme": (env["REQUEST_SCHEME"]),
		"method": (env["REQUEST_METHOD"]),
		"remote": (env["REMOTE_ADDR"], env["REMOTE_PORT"]),
		"server": (env["SERVER_NAME"], env["SERVER_PORT"]),
		"length": (env["CONTENT_LENGTH"]),
		"type":   (env["CONTENT_TYPE"]),
		"root":   (env["DOCUMENT_ROOT"]),
		"host":   (env["HTTP_HOST"]),
		"agent":  (env["HTTP_USER_AGENT"]),
		"body": (
			env["wsgi.input"].read(int(env["CONTENT_LENGTH"]))
			if env["CONTENT_LENGTH"] else None
		),
	}) or (404, { "Content-Type": "text/plain", }, "404 not found")

def set(methods=None, *args, headers={}, **kwargs):
	"""
	methods  -> str or list of strings or None:
	         -> "GET" or [ "GET", "POST", ... ]
	         -> None means all methods
	*args    -> path or paths, can be regex and nested:
	         -> r"^/hello/world$" or [ r"^", r"hello", r"world$" ]
	headers  -> dict of headers to pass function, you may pass headers
	         -> to response later, for convenience
	**kwargs -> this also passed to your function, for convenience
	"""
	path = flatten(args)
	if not methods:
		methods = "DEF"
	if isinstance(methods, str):
		methods = [ methods ]
	def dec(func):
		if path not in __routes.keys():
			__routes[path] = dict()
		elif callable(__routes[path]):
			__routes[path] = dict(DEF=__routes[path])
		__routes[path].update({ m: func for m in methods })
		return (lambda *args, **kwargs: func(*args, headers=headers, **kwargs))
	return dec
