#!/usr/bin/env python3

import io, os, sys, time, uuid, route

def app(env, start_response):
	try:
		(code, headers, body) = route.handle(
			env,
			ts=time.time(),
			uuid=uuid.uuid1(),
			**env,
		)
		start_response(str(code), [ (str(k), str(v)) for k, v in headers.items() ])
		return (body.encode() if isinstance(body, str) else body)
	except Exception as e:
		start_response("200", [ ("Content-Type", "text/plain"), ])
		return str(e).encode()
	return "something fucked up".encode()
