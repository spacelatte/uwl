#!/usr/bin/env python3

import time, uuid, typing, json

from . import route, model


def handle_wsgi(env: dict, **kwargs) -> model.HttpResponse:
	length = int(env.get("CONTENT_LENGTH", 0))
	return route.handle(model.HttpRequest(
		uri    = (env.get("REQUEST_URI", None)),
		path   = (env.get("PATH_INFO", None)),
		query  = (env.get("QUERY_STRING", None)),
		scheme = (env.get("REQUEST_SCHEME") or env.get("wsgi.url_scheme", None)),
		method = (env.get("REQUEST_METHOD", None)),
		remote = (env.get("REMOTE_ADDR", None), env.get("REMOTE_PORT", None)),
		server = (env.get("SERVER_NAME", None), env.get("SERVER_PORT", None)),
		length = (length),
		type   = (env.get("CONTENT_TYPE", None)),
		root   = (env.get("DOCUMENT_ROOT", None)),
		host   = (env.get("HTTP_HOST", None)),
		agent  = (env.get("HTTP_USER_AGENT", None)),
		body   = (env.get("wsgi.input", None).read(length) if length else None),
	))


def app(env: dict, start_response: typing.Callable[
	[typing.Union[str, bytes], typing.Union[typing.Mapping[str, typing.Union[str, typing.Iterable[str]]], typing.Iterable[typing.Tuple]]
], None]):
	try:
		response = handle_wsgi(
			env=env,
			ts=time.time(),
			uuid=uuid.uuid1(),
		)
		start_response(str(response.status), list(response.headers.items()))
		return (
			response.body.encode()
			if isinstance(response.body, str)
			else response.body
		)
	except Exception as error:
		start_response("500", [ ("Content-Type", "text/plain"), ])
		return (str(error) + "\n").encode()
	return "something went wrong".encode()
