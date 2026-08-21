# Architecture

## Scope boundary

This review package covers only Reddit ingestion and the immediately adjacent deterministic
processing boundary. It deliberately excludes brokerage execution, strategy implementation,
private deployment details, and credentials.

## Components

### 1. OAuth client

The application uses Reddit OAuth rather than anonymous requests. The initial read-only client
uses the `client_credentials` flow, caches the returned access token only for its usable lifetime,
and refreshes it when necessary.

A rejected token results in one controlled refresh attempt. The client does not fall back to an
unauthenticated endpoint.

### 2. Read-only listing collector

The initial collector is limited to recent public content from `r/wallstreetbets`:

- new submissions
- recent comments

Listing sizes are bounded. The collector does not fetch private messages, chats, moderation data,
or private subreddit content.

### 3. Rate-limit controller

Each listing response is inspected for Reddit's standard rate-limit headers:

- `X-Ratelimit-Used`
- `X-Ratelimit-Remaining`
- `X-Ratelimit-Reset`

The application computes a conservative delay from remaining capacity and reset time while
preserving an unused reserve. HTTP 429 responses are treated as an explicit stop signal and the
client respects `Retry-After` when provided.

There is no client/account/IP rotation mechanism intended to increase available quota.

### 4. Observation and deduplication

The system keeps Reddit's content creation time separate from the local observation time. This is
important for measuring source/collector latency without rewriting Reddit timestamps.

Because listing endpoints can return the same objects repeatedly, objects are deduplicated before
they are treated as newly observed events.

### 5. Deterministic text processing

Public submission/comment text can be passed through deterministic parsing to identify candidate
mentions of publicly traded securities. Candidate tokens are checked against an independently
obtained security universe and contextual filtering is used to reduce false positives.

The Reddit layer does not require user-level profiling to produce these aggregate features.

### 6. Aggregate feature generation

Accepted mentions may be aggregated into metrics such as security-level mention counts over
explicit time windows. These features can then be compared with independently sourced market data.

### 7. Paper-trading / observe-only boundary

Reddit ingestion itself does not place orders. The broader project is designed with paper-trading
and observe-only defaults. Reddit observations are treated as input data, not executable trading
commands.

## Simplified sequence

```text
Operator configuration
      |
      v
OAuth token request ----------------------+
      |                                    |
      v                                    |
GET recent Reddit listing                  |
      |                                    |
      +--> parse rate headers              |
      +--> 401? refresh token once --------+
      +--> 429? honor Retry-After
      +--> timeout/5xx? bounded backoff
      |
      v
record received_at
      |
      v
deduplicate Reddit IDs
      |
      v
parse public text
      |
      v
candidate ticker/security mentions
      |
      v
aggregate security-level features
      |
      v
external market-data comparison
      |
      v
paper/observe-only evaluation
```

## Non-goals

The Reddit integration is not designed for:

- posting or commenting
- voting
- user messaging/chat
- moderation
- engagement manipulation
- bulk historical archiving
- anonymous scraping
- private-data access
- user deanonymization
- advertising profiles
- resale of Reddit data
- AI/LLM/model training on Reddit content

## Why Devvit is not the application runtime

The project's core runtime is an external Python analytics process that must combine Reddit input
with non-Reddit financial systems and local state. Devvit is therefore not simply missing a UI
feature; the architectural center of gravity is outside Reddit. Reddit is one authenticated data
source among several external providers.
