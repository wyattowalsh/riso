"""Exercise the rendered Python MCP HTTP policy without live network access."""

from __future__ import annotations

import asyncio
import importlib.util
import socket
import ssl
import sys
import tomllib
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from copier._main import Worker

pytestmark = pytest.mark.unit

TEMPLATE = Path(__file__).resolve().parents[2] / "template"
PACKAGE_TEMPLATE = Path("files/python/src/{{ package_name }}")
HTTP_FETCH = (PACKAGE_TEMPLATE / "mcp/tools/http_fetch.py.jinja").as_posix()
PUBLIC_URL = "https://public.example/"
PUBLIC_IPV4 = "93.184.216.34"
PUBLIC_IPV6 = "2606:4700:4700::1111"


@pytest.fixture(scope="module", name="http_fetch_module")
def _http_fetch_module(tmp_path_factory):
    """Import the enabled example from Copier's configured environment."""
    destination = tmp_path_factory.mktemp("python-mcp-http")
    with Worker(src_path=str(TEMPLATE), dst_path=destination, defaults=True) as worker:
        template = worker.jinja_env.get_template(HTTP_FETCH)
        context = {"mcp_module": "enabled", "mcp_languages": ["python"]}
        assert template.render(**context, mcp_example_tools=False) == ""
        rendered = template.render(**context, mcp_example_tools=True)
    path = destination / "http_fetch.py"
    path.write_text(rendered, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("riso_mcp_http_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with pytest.MonkeyPatch.context() as patch:
        patch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
        yield module


@pytest.fixture(name="tool_functions")
def _tool_functions(http_fetch_module):
    """Capture the real handlers without requiring FastMCP in the maintainer env."""
    functions = {}

    def tool():
        def register(fn):
            functions[fn.__name__] = fn
            return fn

        return register

    http_fetch_module.register_http_tools(SimpleNamespace(tool=tool))
    return functions


def test_python_mcp_host_policy(http_fetch_module: ModuleType) -> None:
    """Reject special addresses and aliases without substring false positives."""
    validate = vars(http_fetch_module)["_literal_address"]
    for blocked in (
        "LOCALHOST.",
        "private.home.arpa",
        "metadata.google.internal.",
        "host.local",
        "127.1",
        "0177.0.0.1",
        "2130706433",
        "0x7f000001",
        "0x7f.0.0.1",
        "0.0.0.0",
        "10.0.0.1",
        "100.100.100.200",
        "168.63.129.16",
        "169.254.169.254",
        "172.19.0.1",
        "172.31.255.255",
        "192.0.0.9",
        "192.31.196.1",
        "192.52.193.1",
        "192.168.0.1",
        "192.175.48.1",
        "198.18.0.1",
        "224.0.0.1",
        "240.0.0.1",
        "::1",
        "fd00::1",
        "fe80::1%en0",
        "::ffff:ac13:1",
        "64:ff9b::7f00:1",
        "2001:db8::1",
        "2002:7f00:1::",
        "2620:4f:8000::1",
        "3fff::1",
    ):
        with pytest.raises(ValueError):
            validate(blocked)
    assert validate("notlocalhost.example.") is None
    assert str(validate(f"::ffff:{PUBLIC_IPV4}")) == PUBLIC_IPV4
    assert str(validate(PUBLIC_IPV6)) == PUBLIC_IPV6


def test_python_mcp_example_dependency_group(tmp_path: Path) -> None:
    """The tools must import HTTPX without relying on API or test groups."""
    context = {
        "project_slug": "mcp-contract",
        "package_name": "mcp_contract",
        "cli_module": "disabled",
        "cli_languages": [],
        "codegen_module": "disabled",
        "graphql_api_module": "disabled",
        "api_features": [],
        "quality_profile": "standard",
        "mcp_module": "enabled",
        "mcp_languages": ["python"],
    }
    with Worker(src_path=str(TEMPLATE), dst_path=tmp_path, defaults=True) as worker:
        template = worker.jinja_env.get_template("files/python/pyproject.toml.jinja")
        enabled = tomllib.loads(template.render(**context, mcp_example_tools=True))
        disabled = tomllib.loads(template.render(**context, mcp_example_tools=False))
    assert "httpx>=0.28.1" in enabled["dependency-groups"]["mcp"]
    assert not any(
        req.startswith("httpx") for req in disabled["dependency-groups"]["mcp"]
    )


class _MemoryStream:
    """A byte stream underneath real HTTPX/httpcore HTTP parsing."""

    def __init__(self, response: bytes, *, stall: bool, end_of_stream: type[Exception]):
        self.pending = response
        self.stall = stall
        self.end_of_stream = end_of_stream
        self.sent = bytearray()
        self.waiting_for_body = False
        self.closed = False

    async def receive(self, max_bytes: int) -> bytes:
        """Read fake wire bytes or wait for the request deadline."""
        if self.pending:
            chunk, self.pending = self.pending[:max_bytes], self.pending[max_bytes:]
            return chunk
        if self.stall:
            self.waiting_for_body = True
            await asyncio.Future()
        raise self.end_of_stream

    async def send(self, item: bytes) -> None:
        """Capture the actual request HTTPX sends on the wire."""
        self.sent.extend(item)

    async def aclose(self) -> None:
        """Record that the transport released the fake stream."""
        self.closed = True

    @staticmethod
    def extra(_attribute, default=None):
        """Expose no socket or ALPN attributes for this in-memory stream."""
        return default


@pytest.fixture(name="wire")
def _wire(monkeypatch):
    """Replace AnyIO's TCP and TLS boundary, keeping the real HTTPX transport."""
    pytest.importorskip("httpx")
    anyio = pytest.importorskip("anyio")
    tls = pytest.importorskip("anyio.streams.tls")
    wire = SimpleNamespace(replies=[], refused=set(), dials=[], tls=[], streams=[])

    async def connect_tcp(*, remote_host, remote_port, **_options):
        wire.dials.append((remote_host, remote_port))
        if remote_host in wire.refused:
            raise OSError("fixture refused the connection")
        assert wire.replies, f"Unexpected dial: {remote_host}:{remote_port}"
        response, stall = wire.replies.pop(0)
        stream = _MemoryStream(response, stall=stall, end_of_stream=anyio.EndOfStream)
        wire.streams.append(stream)
        return stream

    async def start_tls(transport_stream, *, hostname, ssl_context, **_options):
        wire.tls.append((hostname, ssl_context.check_hostname, ssl_context.verify_mode))
        return transport_stream

    async def no_unexpected_dns(_loop, host, _port, **_options):
        pytest.fail(f"Unexpected DNS: {host}")

    monkeypatch.setattr(anyio, "connect_tcp", connect_tcp)
    monkeypatch.setattr(tls.TLSStream, "wrap", staticmethod(start_tls))
    monkeypatch.setattr(asyncio.BaseEventLoop, "getaddrinfo", no_unexpected_dns)
    monkeypatch.delenv("MCP_HTTP_ALLOW_INSECURE", raising=False)
    return wire


def _answer(address: str, port: int = 443, *, scope: int = 0) -> tuple:
    """Build a getaddrinfo row without consulting a resolver."""
    family = socket.AF_INET6 if ":" in address else socket.AF_INET
    sockaddr = (
        (address, port, 0, scope) if family == socket.AF_INET6 else (address, port)
    )
    return family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", sockaddr


def _dns(monkeypatch, answers):
    """Return a resolver snapshot and simulate a private answer on second lookup."""
    calls = []

    async def lookup(_loop, host, port, **_options):
        calls.append((host, port))
        if isinstance(answers, OSError):
            raise answers
        return answers if len(calls) == 1 else [_answer("172.19.0.1", port)]

    monkeypatch.setattr(asyncio.BaseEventLoop, "getaddrinfo", lookup)
    return calls


def _reply(body: bytes, *, status: bytes = b"200 OK", headers: bytes = b"") -> bytes:
    """Build an HTTP/1.1 response for the fake wire."""
    length = str(len(body)).encode("ascii")
    return (
        b"HTTP/1.1 "
        + status
        + b"\r\nContent-Length: "
        + length
        + b"\r\nConnection: close\r\n"
        + headers
        + b"\r\n"
        + body
    )


def test_python_mcp_get_pins_dns_and_preserves_tls(wire, monkeypatch, tool_functions):
    """The real transport dials the checked IP but uses the original host for TLS."""
    calls = _dns(monkeypatch, [_answer(PUBLIC_IPV6, 8443)])
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.invalid:3128")
    monkeypatch.setenv("NO_PROXY", "")
    body = ("🙂" * 10003).encode()
    wire.replies.append(
        (
            _reply(
                body,
                status=b"302 Found",
                headers=(
                    b"Location: https://localhost/\r\n"
                    b"Content-Type: text/plain; charset=utf-8\r\n"
                ),
            ),
            False,
        )
    )
    result = asyncio.run(
        tool_functions["http_get"](
            "https://Bücher.example:8443/localhost?q=172.19.0.1",
            headers={"X-Fixture": "kept"},
        )
    )
    assert result["success"] and result["status_code"] == 302
    assert result["content"] == "🙂" * 10000
    assert result["content_length"] == len(body)
    assert result["content_type"] == "text/plain; charset=utf-8"
    assert calls == [("xn--bcher-kva.example", 8443)]
    assert wire.dials == [(PUBLIC_IPV6, 8443)]
    assert wire.tls == [("xn--bcher-kva.example", True, ssl.CERT_REQUIRED)]
    sent = bytes(wire.streams[0].sent).lower()
    assert b"get /localhost?q=172.19.0.1 http/1.1" in sent
    assert b"host: xn--bcher-kva.example:8443\r\n" in sent
    assert b"x-fixture: kept\r\n" in sent


@pytest.mark.parametrize(
    "answers",
    [
        [_answer(PUBLIC_IPV4), _answer("172.19.0.1")],
        [_answer("::ffff:a9fe:a9fe")],
        [_answer(PUBLIC_IPV6, scope=1)],
        [
            (
                socket.AF_INET6,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (PUBLIC_IPV4, 443),
            )
        ],
        [],
        socket.gaierror("fixture DNS failure"),
    ],
)
def test_python_mcp_rejects_entire_unsafe_dns_answer(
    wire, monkeypatch, tool_functions, answers
):
    """No method can connect when DNS includes a blocked result or fails."""
    calls = _dns(monkeypatch, answers)
    result = asyncio.run(tool_functions["http_head"](PUBLIC_URL))
    assert not result["success"] and result["error"]
    assert calls == [("public.example", 443)]
    assert not wire.dials


def test_python_mcp_rejects_credentials_host_override_and_timeouts(
    wire, tool_functions
):
    """Reject malformed authority, credentials, Host overrides, and invalid budgets."""
    get = tool_functions["http_get"]
    for url, params in (
        ("https://user:fixture@public.example/", {}),
        ("https://@public.example/", {}),
        ("https:public.example", {}),
        ("https://[::ffff:ac13:1]/", {}),
        ("http://public.example/", {}),
        (PUBLIC_URL, {"headers": {"hOsT": "localhost"}}),
        (PUBLIC_URL, {"timeout": 0}),
        (PUBLIC_URL, {"timeout": -1}),
        (PUBLIC_URL, {"timeout": 121}),
        (PUBLIC_URL, {"timeout": True}),
    ):
        result = asyncio.run(get(url, **params))
        assert not result["success"] and result["error"]
    assert not wire.dials


def test_python_mcp_post_fallback_does_not_replay_a_sent_request(
    wire, monkeypatch, tool_functions
):
    """A refused connection can try another vetted IP; a partial response cannot."""
    calls = _dns(monkeypatch, [_answer(PUBLIC_IPV6), _answer(PUBLIC_IPV4)])
    wire.refused.add(PUBLIC_IPV6)
    wire.replies.append((b"HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\n", False))
    post = tool_functions["http_post"]
    result = asyncio.run(
        post(PUBLIC_URL, data={"fallback": "form"}, json_body={"send": "json"})
    )
    assert not result["success"] and result["error"]
    assert calls == [("public.example", 443)]
    assert wire.dials == [(PUBLIC_IPV6, 443), (PUBLIC_IPV4, 443)]
    assert len(wire.streams) == 1
    sent = bytes(wire.streams[0].sent)
    assert b'\r\n\r\n{"send":"json"}' in sent and b"fallback" not in sent


def test_python_mcp_head_and_form_contracts(wire, monkeypatch, tool_functions):
    """An opt-in public HTTP HEAD and empty JSON POST retain their result shapes."""
    monkeypatch.setenv("MCP_HTTP_ALLOW_INSECURE", "yes")
    wire.replies.extend(
        [
            (
                b"HTTP/1.1 200 OK\r\nContent-Length: 42\r\nContent-Type: text/plain\r\n\r\n",
                False,
            ),
            (_reply(b"posted"), False),
        ]
    )
    head = asyncio.run(tool_functions["http_head"](f"http://{PUBLIC_IPV4}/"))
    assert head == {
        "success": True,
        "status_code": 200,
        "headers": {"content-length": "42", "content-type": "text/plain"},
        "content_type": "text/plain",
        "content_length": "42",
    }
    post = asyncio.run(
        tool_functions["http_post"](
            f"https://{PUBLIC_IPV4}/", data={"fallback": "form"}, json_body={}
        )
    )
    assert set(post) == {"success", "status_code", "headers", "content"}
    assert post["success"] and post["content"] == "posted"
    assert b"fallback=form" in bytes(wire.streams[1].sent)
    assert wire.dials == [(PUBLIC_IPV4, 80), (PUBLIC_IPV4, 443)]
    assert wire.tls == [(PUBLIC_IPV4, True, ssl.CERT_REQUIRED)]


def test_python_mcp_total_timeout_cancels_dns(wire, monkeypatch, tool_functions):
    """A stalled lookup must expire under the same user deadline without a dial."""
    stopped = []

    async def stall(_loop, host, port, **_options):
        try:
            await asyncio.Future()
        finally:
            stopped.append((host, port))

    monkeypatch.setattr(asyncio.BaseEventLoop, "getaddrinfo", stall)
    result = asyncio.run(
        asyncio.wait_for(tool_functions["http_get"](PUBLIC_URL, timeout=1), timeout=4)
    )
    assert result == {"success": False, "error": "Request timed out", "timeout": 1}
    assert stopped == [("public.example", 443)]
    assert not wire.dials


def test_python_mcp_total_timeout_cancels_body(wire, tool_functions):
    """The deadline still applies after HTTPX receives a response's headers."""
    wire.replies.append((b"HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\n", True))
    result = asyncio.run(
        asyncio.wait_for(
            tool_functions["http_post"](f"https://{PUBLIC_IPV4}/", timeout=1), timeout=4
        )
    )
    assert result == {"success": False, "error": "Request timed out"}
    assert wire.streams[0].waiting_for_body and wire.streams[0].closed


def _render_server_package(destination: Path) -> Path:
    """Render the actual project package and MCP subtree for an in-memory session."""
    source = TEMPLATE / PACKAGE_TEMPLATE
    paths = [
        source / "__init__.py.jinja",
        *sorted((source / "mcp").rglob("*.py.jinja")),
    ]
    variables = {
        "project_name": "Python MCP fixture",
        "project_slug": "python-mcp-fixture",
        "package_name": "python_mcp_fixture",
        "mcp_module": "enabled",
        "mcp_languages": ["python"],
        "mcp_example_tools": True,
        "mcp_transport": "stdio",
    }
    src = destination / "src"
    with Worker(src_path=str(TEMPLATE), dst_path=destination, defaults=True) as worker:
        for path in paths:
            relative = path.relative_to(source)
            template = worker.jinja_env.get_template(
                (PACKAGE_TEMPLATE / relative).as_posix()
            )
            output = src / "python_mcp_fixture" / relative.with_suffix("")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(template.render(**variables), encoding="utf-8")
    return src


def test_python_mcp_real_fastmcp_session(wire, monkeypatch, tmp_path):
    """The generated project server and external MCP SDK import and run together."""
    fastmcp = pytest.importorskip("fastmcp")
    source = _render_server_package(tmp_path)
    monkeypatch.syspath_prepend(str(source))
    generated = importlib.import_module("python_mcp_fixture.mcp")
    external = importlib.import_module("mcp.server.lowlevel")
    assert Path(generated.__file__).is_relative_to(source)
    assert not Path(external.__file__).is_relative_to(source)
    wire.replies.append((_reply(b"fixture"), False))

    async def invoke():
        async with fastmcp.Client(generated.mcp) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools} >= {
                "http_get",
                "http_post",
                "http_head",
            }
            return await client.call_tool(
                "http_get", {"url": f"https://{PUBLIC_IPV4}/"}
            )

    result = asyncio.run(asyncio.wait_for(invoke(), timeout=5))
    assert result.data["success"] and result.data["content"] == "fixture"
    assert wire.dials == [(PUBLIC_IPV4, 443)]
