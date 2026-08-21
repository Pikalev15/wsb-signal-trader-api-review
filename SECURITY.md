# Security and API-Safety Controls

## Secrets

The review package contains no credentials. Runtime credentials must be supplied through local
configuration/environment variables and must not be committed, printed, or included in normal
application telemetry.

Expected secret values include:

- Reddit OAuth client ID
- Reddit OAuth client secret

Access tokens are transient authentication material and should not be persisted unnecessarily.

## User-Agent

The client requires a descriptive User-Agent identifying the application version and the real
Reddit operator account, for example:

```text
linux:wsb-signal-trader:0.1.0 (by /u/Pikalev15)
```

The exact final value should accurately describe the deployed application.

## Authentication failures

An HTTP 401 response invalidates the cached access token and allows one controlled refresh/retry.
The client does not fall back to anonymous scraping.

## Rate limiting

The application treats Reddit's rate-limit state as authoritative operational input.

It parses:

- `X-Ratelimit-Used`
- `X-Ratelimit-Remaining`
- `X-Ratelimit-Reset`

The collector preserves configurable unused capacity and spreads requests over the remaining
window. A 429 response stops normal request flow and honors `Retry-After` when supplied.

The project does not intentionally rotate OAuth applications, Reddit accounts, IP addresses,
proxies, or identities to evade API limits.

## Network resilience

Transient failures use bounded exponential backoff with jitter. Timeouts are finite. Retry logic
is bounded so an unavailable provider cannot create an uncontrolled retry loop.

## Read-only scope

This client exposes only read methods for recent public listings. It does not contain methods for:

- submitting posts or comments
- voting
- private messages/chat
- moderation actions
- account creation
- engagement automation

## Separation from trading execution

The Reddit API component returns observed data. It does not contain brokerage credentials or order
submission methods. The larger project maintains a separate paper/observe-only safety boundary.

## Reporting vulnerabilities

This is a private developer project rather than a public service. Security issues found in this
review package should be reported directly to the repository owner rather than by publishing
credentials or exploitable secret material.
