# Security Notes

This is an educational Lab04 data engineering project. The repository parses a
public upstream Python project and demonstrates streaming ingestion. It is not a
security analysis product.

## Sensitive Data

Do not commit:

- `.env` files
- database passwords that are not throwaway lab defaults
- private keys, tokens, or GitHub credentials
- MongoDB, Neo4j, Kafka Connect, or Docker host credentials
- local screenshots that reveal private machine paths, tokens, or accounts

Use `.env.example` for placeholders and keep real values local.

## Docker And Connectors

- Treat Docker volumes as stateful lab data. Do not prune or remove them without
  explicit approval.
- Register Kafka Connect connectors only against the intended local lab
  Connect URL.
- Before connector changes, record the connector name, topics, target Neo4j URI,
  and rollback command.

## Upstream Repository

The selected upstream repository is `huggingface/datasets`. Clone it as public
source code for parsing only. Do not modify or publish changes upstream as part
of this lab.

## Public Submission

The final GitHub Pages Jupyter Book is public. Before publishing, verify that
notebooks, logs, and screenshots do not contain credentials, local secrets, or
irrelevant personal data.

## Hook And Agent Config

Project hooks in `.codex/hooks/` execute local code. Review hook diffs like
source code. The doctor script validates syntax and checks for Lab04-specific
context drift.
