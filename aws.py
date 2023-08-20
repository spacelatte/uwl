#!/usr/bin/env python3

import base64

from dataclasses import dataclass
from typing import Optional, Iterable, Mapping, Union

from . import model, route, _aws_events

@dataclass
class AwsLambdaResponse:
	statusCode: int
	headers: Optional[Mapping[str, str]]
	multiValueHeaders: Optional[Mapping[str, Iterable]]
	isBase64Encoded: bool
	body: Optional[Union[str, bytes]]


def _response_transform_lambda(response: model.HttpResponse):
	return AwsLambdaResponse(
		statusCode=response.status,
		headers={
			k: v
			for k, v in response.headers.items()
			if isinstance(v, str)
		},
		multiValueHeaders={
			k: v
			for k, v in response.headers.items()
			if isinstance(v, list)
		},
		isBase64Encoded=False,
		body=response.body,
	)


def handle_lambda_apigw_v2(event: dict, context, *args, **kwargs):
	request = model.HttpRequest(
		path = event["requestContext"]["http"]["path"],
		head = event["headers"],
		body = (
			base64.b64decode(event["body"]).decode()
			if event["isBase64Encoded"]
			else event["body"]
		),
		method = event["requestContext"]["http"]["method"],
		agent  = event["requestContext"]["http"]["userAgent"],
		host   = event["requestContext"]["domainName"],
	)
	return _response_transform_lambda(route.handle(request))


def handle_lambda_apigw_v1(event, context, *args, **kwargs):
	ex_event =  _aws_events.payload_apigw_v1
	request = model.HttpRequest()
	return _response_transform_lambda(route.handle(request))


def handle_lambda_apigw(event, context, *args, **kwargs):
	version_mapping = {
		"2.0": handle_lambda_apigw_v2,
		"1.0": handle_lambda_apigw_v1,
	}
	if "version" in event:
		return version_mapping[event["version"]](event, context)
	return handle_lambda_apigw_v1(event, context)


@dataclass(frozen=True)
class AwsHandlerType:

	LambdaApiGw   = handle_lambda_apigw
	LambdaApiGwV1 = handle_lambda_apigw_v1 # explicit
	LambdaApiGwV2 = handle_lambda_apigw_v2 # explicit
	LambdaFnUrl   = handle_lambda_apigw
