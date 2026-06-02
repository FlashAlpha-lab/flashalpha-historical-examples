# Compatibility matrix

The supported versions of every runtime, CLI, and language environment
required to run this examples repo. CI enforces these — if your local
environment falls outside the matrix, expect backtests to drift from the
committed goldens.

| Examples version | Bridge version                | LEAN CLI | .NET | Python    |
| ---------------- | ----------------------------- | -------- | ---- | --------- |
| v0.1.0           | flashalpha-quantconnect 0.1.4 | lean 1.x | 9.0  | 3.10–3.12 |

---

## Bridge upgrade policy

A single PR bumps every essay's pin in lockstep when the
[`flashalpha-quantconnect`](https://github.com/FlashAlpha-lab/flashalpha-quantconnect)
bridge updates. CI's drift guard (validation Tier 0 + main plan
Layer 0) asserts no essay falls behind the repo-wide minimum.

Concretely, every essay's `python/requirements.txt` and `csharp/*.csproj`
must pin the bridge to the same version. `tools/verify-essay.py` walks
the tree and fails the PR if any essay diverges. Bridge bumps therefore
land as wide, repository-spanning PRs — not per-essay drips.

The same PR is expected to:

1. Bump the version in this matrix.
2. Re-capture goldens for every stable essay touched by behaviour changes
   in the new bridge release.
3. Note the upgrade in `CHANGELOG.md`.

## LEAN CLI

`lean` CLI is the **only supported runner**. QC Cloud parallel runs are
out of scope for v1.0 — CI runs everything locally inside the
`quantconnect/lean:latest` Docker container, and contributor reproduction
is expected to do the same. See
[lean-cli-cheatsheet.md](lean-cli-cheatsheet.md) for the commands you'll
use.

## Python

Python 3.10, 3.11, and 3.12 are all CI-tested. Older 3.9 and earlier are
unsupported; newer 3.13 has not been validated against the LEAN container
runtime as of v0.1.0.

## .NET

.NET 9 SDK is required even for Python-only contributors — the LEAN CLI
shells out to `dotnet` regardless of algorithm language. Older .NET 6/7/8
SDKs are not supported because LEAN's C# project templates target net9.0.
