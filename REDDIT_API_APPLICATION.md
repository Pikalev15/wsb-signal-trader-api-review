# Reddit Data API Application — Copy/Paste Answers

This document matches the currently visible Reddit developer request form fields.

## What is your inquiry?

Select:

> I'm a developer and want to build a Reddit App that does not work in the Devvit ecosystem.

## Reddit account name

`u/Pikalev15`

## What benefit/purpose will the bot/app have for Redditors?

The application is a read-only, non-commercial analytics project intended to study aggregate
discussion trends in r/wallstreetbets and evaluate whether changes in discussion activity have
measurable relationships with public market activity.

The application will not post, comment, vote, message users, perform moderation actions, or
otherwise interact with Redditors. It will only read publicly available submissions and comments
through Reddit's official authenticated API.

The system is intentionally designed to have minimal impact on Reddit and its users. It uses
bounded polling, respects Reddit's rate-limit headers and HTTP 429 responses, deduplicates
previously observed content, and does not attempt to bypass Reddit API limits.

Analysis is performed primarily at the aggregate security/ticker level rather than by profiling
individual Reddit users. The application does not sell Reddit data, provide raw Reddit data to
third parties, or use Reddit content to train an AI or machine-learning model.

Its purpose is private software development and paper-trading signal evaluation rather than
providing an automated Reddit bot or commercial Reddit-data product.

## Provide a detailed description of what the Bot/App will be doing on the Reddit platform.

WSB Signal Trader is an external, read-only application that collects a limited stream of recent
public submissions and comments from r/wallstreetbets using Reddit's official OAuth-authenticated
Data API.

The initial application scope is limited to r/wallstreetbets.

The Reddit portion of the application performs the following process:

1. Authenticate using an approved Reddit OAuth application and a descriptive User-Agent identifying
   the application and operator.
2. Periodically request recent public submissions from r/wallstreetbets.
3. Periodically request recent public comments from r/wallstreetbets.
4. Read Reddit API rate-limit response headers including X-Ratelimit-Used,
   X-Ratelimit-Remaining and X-Ratelimit-Reset.
5. Automatically reduce request frequency as available API capacity decreases.
6. Respect HTTP 429 responses and Retry-After instructions.
7. Record the time each Reddit object was observed separately from the object's original creation
   timestamp.
8. Deduplicate objects returned by multiple polling requests so the same submission/comment is not
   repeatedly treated as new activity.
9. Pass public submission/comment text through a deterministic local processing pipeline.
10. Identify possible mentions of publicly traded securities. For example, a token such as AAPL may
    be checked against an independently obtained list of eligible securities.
11. Apply deterministic contextual filtering to reduce false ticker matches caused by ordinary
    words, abbreviations, URLs, code fragments and other irrelevant text.
12. Convert accepted mentions into aggregate measurements such as the number of qualifying mentions
    of a security during a defined time period.
13. Compare those aggregate measurements with independently sourced financial-market data inside a
    local paper-trading/observe-only environment.

Reddit is used only as a source of public discussion data. The Reddit API component does not place
trades or issue brokerage commands.

The application will not create posts/comments, vote, send private messages/chat messages, perform
moderation actions, automate engagement, scrape Reddit HTML, use unofficial mirrors to avoid the
API, rotate clients/accounts/IP addresses to evade limits, access private user data, attempt to
deanonymize users, sell/redistribute Reddit data, expose a third-party Reddit-data API, or use
Reddit content to train an LLM/generative-AI/machine-learning model.

The client includes explicit handling for expired OAuth tokens, HTTP 401 responses, HTTP 429 rate
limits, request timeouts, transient server errors and bounded backoff.

## What is missing from Devvit that prevents building on that platform?

Devvit is well suited to applications that operate primarily within Reddit, but this project's
core application is an external financial-data processing system rather than a Reddit user
experience. Reddit ingestion is only one input to a larger local pipeline.

The application needs to combine Reddit observations with external systems including an
independently sourced universe of publicly traded U.S. securities, external financial-market data,
local deterministic ticker extraction/filtering, local persistence and replay, historical signal
evaluation, paper-trading infrastructure, and application health/latency monitoring.

For example, a Reddit comment mentioning NVDA is observed through the Reddit API. The external
Python application then compares that candidate with a separately sourced securities universe,
applies deterministic filtering, aggregates qualifying mentions over time, and compares the
resulting signal with market data from a separate provider.

The system also requires local persistence so processing behavior can be reproduced and tested,
including separate content-created and content-observed timestamps, deduplication state,
signal-processing results, and system-health information.

Finally, the project has its own paper-trading safety architecture. Reddit ingestion is deliberately
isolated from market-data and brokerage components so disabling Reddit access does not alter the
safety state of the rest of the application.

The project's fundamental functionality therefore occurs outside Reddit. I am requesting the
Reddit Data API as an authenticated external data source rather than attempting to use Devvit as
the runtime for an application whose primary processing and integrations are external.

## Provide a link to source code or platform that will access the API.

`https://github.com/Pikalev15/wsb-signal-trader-api-review`

This public review repository is a sanitized representation of the Reddit-facing integration. It
contains the OAuth/read-only client, rate-limit behavior, data-flow documentation, privacy/data
minimization documentation, and security controls, but intentionally excludes credentials,
brokerage execution code and unrelated proprietary strategy logic.

## What subreddits do you intend to use the bot/app in?

`r/wallstreetbets`

## If applicable, what username will you be operating this Bot/App under? (optional)

`u/Pikalev15`

The application is read-only and does not post publicly under this account; the username identifies
the developer/operator and is used in descriptive User-Agent information.

## Attachments (optional)

No attachment is required if the public review repository is available. If an attachment is useful,
a PDF or screenshot of the architecture/data-flow page can be supplied, but it should contain no
credentials, tokens or private repository content.
