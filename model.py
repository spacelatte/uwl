#!/usr/bin/env python3

import dataclasses, enum, pathlib, typing, re


class HttpMethod(str, enum.Enum):
	ANY    = "*"
	GET    = "GET"
	PUT    = "PUT"
	POST   = "POST"
	PATCH  = "PATCH"
	DELETE = "DELETE"
	TRACE  = "TRACE"

class HttpScheme(str, enum.Enum):
	ANY   = "*"
	FTP   = "ftp"
	HTTP  = "http"
	HTTPS = "https"


@dataclasses.dataclass
class HttpRequest:
	uri:    typing.Union[pathlib.PurePath, str] = dataclasses.field(default="/")
	path:   typing.Union[pathlib.PurePath, str] = dataclasses.field(default="/")
	query:  typing.Optional[typing.Union[typing.Mapping, str]] = None
	scheme: typing.Union[HttpScheme, str] = HttpScheme.ANY
	method: typing.Union[HttpMethod, str] = HttpMethod.ANY
	remote: typing.Tuple[str, str] = ("", "")
	server: typing.Tuple[str, str] = ("", "")
	length: int = 0
	type:   typing.Optional[str] = None
	root:   typing.Optional[str] = None
	host:   typing.Optional[str] = None
	agent:  typing.Optional[str] = None
	head:   typing.Optional[typing.Mapping[str, typing.Union[str, typing.List[str]]]] = None
	body:   typing.Optional[typing.Union[str, bytes]] = None


@dataclasses.dataclass
class HttpResponse:
	status:  int
	headers: typing.Mapping[str, typing.Union[str, typing.Iterable[str]]]
	body:    typing.Optional[typing.Union[str, bytes]]


class HttpCall(typing.Protocol):

	def __call__(self, http: HttpRequest, match: re.Match, *args, **kwargs) -> HttpResponse:
		return HttpResponse(0, dict(), None)


def flatten(paths: typing.Union[pathlib.PurePath, typing.Iterable[typing.Union[pathlib.PurePath, str]], str]) -> pathlib.PurePath:
	if isinstance(paths, (pathlib.Path, pathlib.PurePath, str)):
		return pathlib.PurePath(paths)
	if isinstance(paths, typing.Iterable):
		return pathlib.PurePath(*paths)
	return pathlib.PurePath("/")
