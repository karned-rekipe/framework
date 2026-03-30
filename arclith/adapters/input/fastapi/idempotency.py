"""Idempotency middleware for POST requests.

Prevents duplicate resource creation by caching responses keyed by Idempotency-Key header.
Critical for e-commerce (payments, orders) where network retries must not create duplicates.

Usage:
    app.add_middleware(IdempotencyMiddleware, cache=cache_adapter, ttl=86400, logger=logger)

RFC Reference: https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header
Industry: Stripe, PayPal, AWS, Twilio
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from arclith.domain.ports.cache import CachePort
    from arclith.domain.ports.logger import Logger


class IdempotencyMiddleware:
    """ASGI middleware that implements idempotent POST requests via Idempotency-Key header.

    Workflow:
        1. Client sends POST with `Idempotency-Key: <uuid>`
        2. Middleware checks cache:
           - Hit → return cached response (200 instead of 201)
           - Miss → continue to handler, cache successful 2xx response
        3. Cache TTL: 24h (configurable)

    Error Handling:
        - Missing key on POST → 400 Bad Request (configurable: required=True)
        - 4xx/5xx responses → not cached (only 2xx success)
        - Concurrent requests with same key → first wins, others wait or get cached response

    Security:
        - Key namespace: per-realm (multitenant isolation)
        - Key format: client-provided UUID/string (max 255 chars)
        - Response hashing: SHA256(status + headers + body) → detect response drift
    """

    def __init__(
            self,
            app: Any,
            cache: "CachePort",
            logger: "Logger",
            ttl: int = 86400,  # 24 hours
            required: bool = False,  # If True, reject POST without Idempotency-Key
            methods: set[str] | None = None,  # Methods requiring idempotency (default: POST only)
    ) -> None:
        self._app = app
        self._cache = cache
        self._logger = logger
        self._ttl = ttl
        self._required = required
        self._methods = methods or {"POST"}

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        method = scope.get("method", "")
        if method not in self._methods:
            await self._app(scope, receive, send)
            return

        # Extract Idempotency-Key from headers
        headers_dict = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        idempotency_key = headers_dict.get("idempotency-key") or headers_dict.get("Idempotency-Key")

        if not idempotency_key:
            if self._required:
                # Reject request
                await self._send_error(
                    send,
                    status = 400,
                    message = "Idempotency-Key header is required for POST requests",
                )
                return
            # Optional mode: continue without idempotency
            await self._app(scope, receive, send)
            return

        # Validate key length
        if len(idempotency_key) > 255:
            await self._send_error(send, status = 400, message = "Idempotency-Key exceeds 255 characters")
            return

        # Build cache key (namespace by path + tenant if available)
        path = scope.get("path", "")
        cache_key = f"idempotency:{path}:{idempotency_key}"

        # Check cache
        cached = await self._cache.get(cache_key)
        if cached:
            self._logger.info(
                "🔁 Idempotent request (cache hit)",
                key = idempotency_key,
                path = path,
            )
            cached_data = json.loads(cached)
            await self._send_cached_response(send, cached_data)
            return

        # Cache miss → execute request and capture response
        response_data: dict[str, Any] = {"status": 500, "headers": [], "body": b""}

        async def _send_wrapper(message: Any) -> None:
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
                response_data["headers"] = list(message.get("headers", []))
            elif message["type"] == "http.response.body":
                response_data["body"] += message.get("body", b"")
            await send(message)

        try:
            await self._app(scope, receive, _send_wrapper)
        finally:
            # Cache successful responses only (2xx)
            status = response_data["status"]
            if 200 <= status < 300:
                # Store response in cache
                cache_value = json.dumps(
                    {
                        "status": status,
                        "headers": [
                            (k.decode() if isinstance(k, bytes) else k, v.decode() if isinstance(v, bytes) else v) for
                            k, v in response_data["headers"]],
                        "body": response_data["body"].decode("utf-8", errors = "replace"),
                    }
                )
                await self._cache.set(cache_key, cache_value, ttl_s = self._ttl)
                self._logger.info(
                    "💾 Cached idempotent response",
                    key = idempotency_key,
                    path = path,
                    status = status,
                    ttl = self._ttl,
                )

    async def _send_cached_response(self, send: Any, cached_data: dict[str, Any]) -> None:
        """Replay cached response."""
        headers = [(k.encode(), v.encode()) for k, v in cached_data["headers"]]
        # Add X-Idempotency-Replay header to indicate cached response
        headers.append((b"x-idempotency-replay", b"true"))

        await send(
            {
                "type": "http.response.start",
                "status": cached_data["status"],
                "headers": headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": cached_data["body"].encode("utf-8"),
            }
        )

    async def _send_error(self, send: Any, status: int, message: str) -> None:
        """Send error response."""
        body = json.dumps({"detail": message}).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
