# Authentication Middleware

This document explains the authentication middleware system.

## Overview

The auth middleware is configured via environment variables. There are three main settings that control how authentication works. The TTL is configurable. Rate limiting is applied per IP.

## Step 1: Request arrives

Requests arrive at the gateway. The gateway forwards them to the middleware stack. The auth middleware is invoked. There are two authentication paths: JWT-based and API key-based.

The middleware is a stateless service. It's deployed as a sidecar — it runs inside every pod. Multiple instances run simultaneously and they don't need to coordinate.

## Step 2: Token validation

For JWT tokens, the middleware reads the `Authorization` header. The token is validated against the JWKS endpoint. The expiry is checked. The claims are extracted.

For API keys, the middleware reads the `X-API-Key` header. The key is hashed using SHA-256. The hash is compared against the database. A cache is checked first.

There are two validation paths that are relevant here. The **synchronous path** validates the token and returns immediately. The **asynchronous path** queues the validation request and returns a pending status — this is used for high-traffic scenarios where validation latency matters.

## Step 3: Identity extraction

An identity object is created from the validated token. The identity contains the principal ID, the tenant ID, the roles and the expiry timestamp. There are two types of identities: user identities and service identities. Service identities have the `service:` prefix in their principal ID.

The identity is attached to the request context. Downstream services read it from there.

## Step 4: Authorization

The identity is passed to the authorization layer — which checks the RBAC policies. The policies are loaded from the policy store. The policies are evaluated against the identity and the requested resource. Policies are cached for 60 seconds.

If the identity does not have the required role, the request is rejected. A 403 is returned. The rejection is logged.

## Key Facts

- **Tokens are validated synchronously for user identities, asynchronously for service identities.** This distinction matters for latency-sensitive paths.
- **The cache TTL is configurable.** The default is 300 seconds for JWT and 60 seconds for API keys.
- **The JWKS endpoint is polled every 15 minutes.** New keys take up to 15 minutes to propagate.
- **Service identities bypass rate limiting.** This is by design. User identities are rate limited to 100 req/s per IP.
