#!/usr/bin/env python3

import time, uuid, typing

from . import route, model


def handle_wsgi(env, **kwargs) -> model.HttpResponse:
	return route.handle(model.HttpRequest(**{
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
	}))


def app(env, start_response: typing.Callable[
	[typing.Union[str, bytes], typing.Union[typing.Dict[str, str], typing.Iterable[typing.Tuple], ...]
], None]):
	try:
		response = handle_wsgi(
			env=env,
			ts=time.time(),
			uuid=uuid.uuid1(),
			#**env,
		)
		start_response(str(response.status), response.headers)
		return (
			response.body.encode()
			if isinstance(response.body, str)
			else response.body
		)
	except Exception as e:
		start_response("500", [ ("Content-Type", "text/plain"), ])
		return str(e) + "\n"
	return "something went wrong".encode()
