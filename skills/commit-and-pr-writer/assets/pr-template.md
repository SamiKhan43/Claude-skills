## What

<!-- One or two sentences: what this pull request changes. -->

## Why

<!-- The problem or goal. Link the issue so it closes on merge: Closes #123 -->

## How

<!-- Notable approach or design decisions. Skip anything the diff already makes obvious. -->

## How to test

1. <!-- exact commands or steps, e.g. `pytest tests/test_auth.py` -->
2. <!-- what to call or click -->

**Expected result:** <!-- what the reviewer should see -->

## Backend impact

<!-- Keep only the lines that apply and delete the rest. -->

- **Database / migrations:** <!-- what changes, is it backward compatible, how to roll back -->
- **API changes:** <!-- new or changed endpoints, status codes, error format; breaking? versioned? -->
- **Security / authorization:** <!-- who can do what now; ownership checks; new inputs validated -->
- **Performance:** <!-- new queries, indexes, caching, N+1 risk, expected load -->
- **Config / env / feature flags:** <!-- new variables, defaults, flags, secrets to provision -->
- **Rollout and rollback:** <!-- deploy order, flag to turn off, how to revert safely -->

## Screenshots or examples

<!-- Example request and response for API changes, or screenshots for UI changes. -->

## Checklist

- [ ] Tests added or updated
- [ ] Docs or API spec updated
- [ ] Migration is backward compatible
- [ ] No secrets, debug code, or unrelated changes
