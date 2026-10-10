# SemverGate: Did This Release Label Its Changes Honestly?

**Category:** Intelligent Contracts (standalone primitive)
**Files:** `semvergate.py` (contract), `test_flow.py` (call-sequence walkthrough)

## The problem

Software versions are a promise. A "patch" release (1.4.2 to 1.4.3) says
"nothing will break." A "minor" release says "new things added, nothing
broke." Only a "major" release may break things.

Automated tools trust that promise and update software without a human
looking. When a maintainer labels a breaking change as a patch, by mistake
or on purpose, every project downstream can break overnight, and there is
no neutral way to say "this release was mislabelled." It turns into an
argument in an issue thread.

## The primitive

A release is registered with its declared bump (patch, minor or major) and
a public evidence URL, such as a compare page or changelog. Anyone can
request an audit. Every validator fetches the evidence page itself, inside
the contract, and decides on its own what the minimum correct bump should
have been. The result is a receipt: declared bump, required bump, whether
the label was too low, and the breaking changes found.

Other contracts and CI gates can read `get_verdict(release_id)` and get one
of `unaudited`, `compliant` or `violation`.

## Consensus design: ordinal agreement

The three bumps are ordered: patch < minor < major. That makes this a
different shape from a numeric reading. There is no "close enough" between
"minor" and "major": if validators split on that, it is exactly the dispute
the contract exists to settle, so tolerance would hide real disagreement.

- **Contract-side retrieval.** `gl.get_webpage()` runs inside the function
  every validator re-runs, so every validator does its own real fetch.
- **Exact agreement on the category.** The validator accepts the leader's
  answer only if its own independent reading gives the same required bump.
- **Explicit outcome agreement.** It also checks both readings give the
  same violation result against the declared bump. This is implied by the
  first check but kept visible so the verdict binding is not accidental.
- If validators cannot agree, the audit does not resolve and no receipt is
  written.

## Replay and challenge rules

- One audit per `release_id`. A second `file_audit` is rejected.
- The ruling can be challenged **once**, by anyone, with `challenge_audit`.
  This reruns the full fetch-and-consensus round, since the evidence page
  may have changed or been corrected.
- If the challenge flips the violation outcome, the ruling is marked
  overturned and the challenge result is final. If not, the original ruling
  stands. After one challenge the ruling is final, so nobody can keep
  re-rolling for a favourable answer.

## State design

| Map | Key | Value |
|---|---|---|
| `releases` | `release_id` | registrant, package, from/to version, declared bump, diff_url |
| `audits` | `release_id` | declared bump, required bump, violation, breaking changes, evidence URL, challenge result, final verdict |

No page content is stored, only the receipt. `total_releases` and
`total_audits` are `u256` counters.

## Access control

Registering a release is open. `file_audit` and `challenge_audit` have no
caller restriction: the point is that anyone can check, not just the
maintainer.

## Known limitations (stated up front)

- **Evidence neutrality.** The registrant chooses `diff_url`. Use a neutral,
  canonical page (the hosting platform's compare page for the two exact
  versions), not a page the maintainer can quietly edit. The contract
  checks what the page says, not whether the page is honest.
- **LLM judgement, not a compiler.** The required bump is a model's reading
  of a diff, not a formal proof of API compatibility. Treat the receipt as
  a neutral, reproducible second opinion.
- **Untrusted page text.** The prompt marks page content as data and the
  answer is limited to three allowed values, but a determined page author
  could still try to steer the reading.
- **No challenge bond.** The single-challenge cap is the only anti-spam
  rule.

## Extending this primitive

- Require a small bond to challenge, forfeited if the ruling is upheld.
- Accept two evidence URLs (diff plus changelog) and require agreement.
- Let a package registry contract refuse to mark a release "stable" while
  `get_verdict` returns `violation`.
- Add pre-release and build-metadata handling for fuller semver coverage.
