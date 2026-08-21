# Privacy and Data Minimisation

## Principles

The Reddit integration is designed around data minimisation and aggregate analysis rather than
user-level profiling.

## Intended data

The initial scope is limited to publicly available submissions and comments from
`r/wallstreetbets` that are returned by Reddit's approved OAuth Data API.

Processing may require fields such as:

- Reddit object ID
- object type
- subreddit
- creation timestamp
- local observation timestamp
- public title/body text needed for deterministic signal processing
- limited public metadata required for deduplication/processing

## Author identifiers

Direct Reddit usernames are not necessary for the core security/ticker aggregation use case.
Where an author identifier is technically useful for deduplication or abuse-resistance, the full
application can pseudonymize that value rather than treating the username as an analytical feature.

The project is not intended to create advertising profiles, infer real-world identities, or
attempt to deanonymize Reddit users.

## Derived data

The primary outputs are aggregate, security-level measurements such as qualifying mention counts,
changes in mention frequency, processing confidence/rejection reasons, and ingestion-health
metrics.

The application is not intended to reproduce Reddit conversations as a standalone content product.

## Redistribution

The intended use does not sell, license, or redistribute Reddit data and does not expose a
third-party Reddit-data API.

## AI / model training

Reddit content collected for this approved use is not intended to train a machine-learning model,
large language model, generative model, or foundation model. Core ticker extraction/filtering is
designed as deterministic software logic.

## Retention and deletion

The application should retain Reddit-derived information only for as long as it remains necessary
and permitted for the approved purpose. If Reddit content must be removed or becomes unavailable
under applicable policy/API requirements, the corresponding stored Reddit-derived data should be
removed or otherwise handled as required by those rules.

## Credentials

OAuth client secrets and access tokens are not part of the dataset. They are supplied locally at
runtime, excluded from source control, and should be redacted from normal logs/diagnostics.
