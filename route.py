#!/usr/bin/env python3

import re, json, collections, enum, dataclasses, typing, pathlib

from . import model

error_default = model.HttpResponse(
	status=404,
	headers={
		"Content-Type": "text/plain",
	},
	body="not found",
)


__routes: typing.OrderedDict[str, typing.Any] = collections.OrderedDict({
	r"^/$": (
		lambda *args, **kwargs: model.HttpResponse(200, {},
			f"default route: args='{args}' kwargs='{kwargs}';"
		)
	),
})

def get(route_matcher: typing.Union[re.Pattern, None]) -> typing.Union[typing.Iterable[str], list]:
	if not route_matcher:
		return __routes.keys()
	filtered = filter(lambda route: re.search(route_matcher, route, re.IGNORECASE | re.MULTILINE), __routes.keys())
	return iter(filtered)

def find(http: typing.Union[model.HttpRequest, typing.Dict, typing.Mapping], routes: typing.OrderedDict = __routes) -> model.HttpResponse:
	"""
	find: Find the given route in the route table. Regex matching is possible
	"""
	if isinstance(http, (dict, typing.Mapping, typing.Dict, typing.OrderedDict)):
		http = model.HttpRequest(**http)
	def function(req, match: re.Match, callback: model.HttpCall) -> model.HttpResponse:
		if callable(callback):
			args = match.groups()
			kwargs = match.groupdict()
			if kwargs:
				resp = callback(req, match, **kwargs)
			else:
				resp = callback(req, match, *args)
			if not isinstance(resp, model.HttpResponse):
				resp = model.HttpResponse(200, dict(), resp)
			if isinstance(resp.headers, (dict, typing.Dict)):
				resp.headers["access-control-allow-origin"] = "*"
			if resp.body and not isinstance(resp.body, (str, bytes)):
				if isinstance(resp.headers, (dict, typing.Dict)):
					resp.headers["content-type"] = "application/json"
				resp.body = json.dumps(resp.body, indent='\t', default=str)
			return resp
		if isinstance(callback, str):
			return model.HttpResponse(
				status=200,
				headers={
					"content-type": "text/plain",
				},
				body=callback,
			)
		return model.HttpResponse(
			status=200,
			headers={ "content-type": "application/json", },
			body=json.dumps(callback, indent='\t', default=str),
		)

	for k, v in routes.items():
		posix = http.path.as_posix() if isinstance(http.path, pathlib.PurePath) else http.path
		match = re.match(k, posix)
		if not match:
			continue
		if isinstance(v, model.HttpResponse):
			print("HttpResponse", v)
			return v
		if callable(v):
			print("callable", v)
			return function(http, match, v)
		if isinstance(v, dict) or isinstance(v, (typing.Mapping, typing.Dict, typing.OrderedDict)):
			if http.method in list(v.keys()):
				return function(http, match, v[http.method])
			if model.HttpMethod.ANY in v.keys():
				return function(http, match, v[model.HttpMethod.ANY])
			raise ValueError(f"Object v='{v}' does not include proper mapping for key='{k}'")
			return error_default
		if isinstance(v, str):
			return model.HttpResponse(200, { "content-type": "text/plain" }, v)
		if isinstance(v, typing.Iterable):
			v = list(v)
			if len(v) == 3:
				return model.HttpResponse(v[0], v[1], v[2])
			if len(v) == 2:
				return model.HttpResponse(v[0], v[1], None)
			if len(v) == 1:
				return model.HttpResponse(v[0], dict(), None)
			return model.HttpResponse(200,
				{ "content-type": "application/json" },
				json.dumps(v, indent='\t'),
			)
		continue
	return error_default


def set(
		methods: typing.Union[typing.Iterable[typing.Union[model.HttpMethod, str]], model.HttpMethod, str, None] = None,
		*route: typing.Union[pathlib.PurePath, typing.Iterable[typing.Union[pathlib.PurePath, str]], str],
		headers: dict = dict(),
		**kwarg: dict,
	):
	"""
	Sets route handling for the function this decorates.

	Example:
	```
		@set(model.HttpMethod.GET, r"^/(?P<name>\\w+)")
		def hello(self: HttpRequest, match: re.Match, name: str, *args, **kwargs):
			headers = {
				"content-type": "text/plain",
			}
			return HttpResponse(200, headers, f"hello {name}!")
	```

	Parameters:
		methods: `"GET"` or `[ "GET", "POST", ... ]` None means all methods
		route: path or paths, can be regex and nested: `r"^/hello/world$"` or `[ r"^", r"hello", r"world$" ]`
		headers: dict of headers to pass function, you may pass headers to response later, for convenience
		kwargs: this also passed to your function, for convenience...

	"""
	path = model.flatten(*route)
	posix = path.as_posix()
	if not methods:
		methods = model.HttpMethod.ANY
	if isinstance(methods,(str, model.HttpMethod)):
		methods = [ methods ]
	def dec(func: model.HttpCall) -> model.HttpCall:
		if posix not in __routes.keys():
			__routes[posix] = dict()
		if callable(__routes[posix]):
			__routes[posix] = dict({ model.HttpMethod.ANY: __routes[posix] })
		if methods and isinstance(methods, typing.Iterable):
			__routes[posix].update({ m: func for m in methods })
		return func
	return dec


def handle(request: typing.Union[model.HttpRequest, typing.Mapping[str, str]]) -> model.HttpResponse:
	response = find(request, __routes) or error_default
	return response
