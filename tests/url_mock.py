import inspect
from collections import namedtuple
from functools import update_wrapper
from http.client import responses as http_reasons
from io import BytesIO
from unittest import mock
from urllib.parse import parse_qsl, urlparse

_exec = getattr(__import__("builtins"), "exec")
unicode = str


Call = namedtuple("Call", ["request", "response"])
Request = namedtuple("Request", ["method", "url", "body", "headers", "scheme", "host", "port"])
_urllib3_import = """\
from %(package)s.response import HTTPResponse
from %(package)s.exceptions import ProtocolError
"""
_wrapper_template = """\
def wrapper%(signature)s:
    with responses:
        return func%(funcargs)s
"""

__all__ = ["Responses"]


def get_wrapped(func, wrapper_template, evaldict):
    # Preserve the argspec for the wrapped function so that testing
    # tools such as pytest can continue to use their fixture injection.
    signature = inspect.signature(func)
    is_bound_method = hasattr(func, "__self__")
    callargs = inspect.signature(func)

    ctx = {"signature": signature, "funcargs": callargs}
    _exec(wrapper_template % ctx, evaldict)

    wrapper = evaldict["wrapper"]

    update_wrapper(wrapper, func)
    if is_bound_method:
        wrapper = wrapper.__get__(func.__self__, type(func.__self__))
    return wrapper


class _FakeHeaders(list):
    def get_all(self, key, default=None):
        key = key.lower()
        return [v for (k, v) in self if k.lower() == key]

    getheaders = get_all


class _FakeResponse(object):
    def __init__(self, headers):
        self.msg = _FakeHeaders(headers)

    def isclosed(self):
        return False


class CallList(list):
    def add(self, request, response):
        self.append(Call(request, response))


class Responses(object):
    ANY = mock.ANY
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"

    def __init__(self, package="urllib3"):
        evaldict = {}
        _exec(_urllib3_import % {"package": package}, evaldict)

        self._package = package
        self._request_class = Request
        self._response_class = evaldict["HTTPResponse"]
        self._error_class = evaldict["ProtocolError"]
        self.reset()

    def reset(self):
        self._urls = []
        self._calls = CallList()

    def add(
        self,
        method,
        url,
        body="",
        match_querystring=False,
        status=200,
        adding_headers=None,
        content_type="text/plain",
    ):
        # body must be bytes
        if isinstance(body, unicode):
            body = body.encode("utf-8")

        self._urls.append(
            {
                "url": url,
                "method": method,
                "return": (status, adding_headers, body),
                "content_type": content_type,
                "match_querystring": match_querystring,
            }
        )

    def add_callback(self, method, url, callback, match_querystring=False, content_type="text/plain"):
        self._urls.append(
            {
                "url": url,
                "method": method,
                "callback": callback,
                "content_type": content_type,
                "match_querystring": match_querystring,
            }
        )

    @property
    def calls(self):
        return self._calls

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        self.reset()

    def activate(self, func):
        evaldict = {"responses": self, "func": func}
        return get_wrapped(func, _wrapper_template, evaldict)

    def _find_match(self, request):
        for match in self._urls:
            if request.method == match["method"] and self._has_url_match(match, request.url):
                return match

    def _has_url_match(self, match, request_url):
        url = match["url"]

        if hasattr(url, "match"):
            return url.match(request_url)
        if match["match_querystring"]:
            return self._has_strict_url_match(url, request_url)

        return url == request_url.partition("?")[0]

    def _has_strict_url_match(self, url, other):
        url_parsed = urlparse(url)
        other_parsed = urlparse(other)

        if url_parsed[:3] != other_parsed[:3]:
            return False

        url_qsl = sorted(parse_qsl(url_parsed.query))
        other_qsl = sorted(parse_qsl(other_parsed.query))
        return url_qsl == other_qsl

    def _urlopen(self, pool, method, url, body=None, headers=None, **kwargs):
        request = self._request_class(method, url, body, headers, pool.scheme, pool.host, pool.port)
        match = self._find_match(request)

        if match is None:
            error_msg = "Connection refused: {0} {1}".format(request.method, request.url)
            response = self._error_class(error_msg)

            self._calls.add(request, response)
            raise response

        headers = [
            ("Content-Type", match["content_type"]),
        ]

        if "callback" in match:  # use callback
            status, r_headers, body = match["callback"](request)
            if isinstance(body, unicode):
                body = body.encode("utf-8")
        else:
            status, r_headers, body = match["return"]

        if isinstance(body, Exception):
            self._calls.add(request, body)
            raise body

        if hasattr(status, "split"):
            status, reason = status.split(None, 1)
            status = int(status)
        else:
            reason = http_reasons.get(status)

        if r_headers:
            if hasattr(r_headers, "items"):
                r_headers = r_headers.items()
            for key, value in r_headers:
                if key.lower() == "content-type":
                    if headers[0][0].lower() == "content-type":
                        del headers[0]  # No duplicate content_type
                headers.append((key, value))

        response = self._response_class(
            status=status,
            reason=reason,
            body=BytesIO(body) if body else BytesIO(),
            headers=headers,
            preload_content=False,
            original_response=_FakeResponse(headers),
        )

        self._calls.add(request, response)
        return response

    def start(self):
        def _urlopen(pool, method, url, body=None, headers=None, **kwargs):
            return self._urlopen(pool, method, url, body=body, headers=headers, **kwargs)

        target = self._package + ".connectionpool.HTTPConnectionPool.urlopen"
        self._patcher = mock.patch(target, _urlopen)
        self._patcher.start()

    def stop(self):
        self._patcher.stop()
