# test_flow.py
#
# Step-by-step walkthrough for GenLayer Studio. Consensus cannot be faked
# outside real validators, so this is a call sequence with what to expect,
# not an automated test suite.
#
# Use a real, public compare page as diff_url (for example a GitHub
# "compare" page between two tags of a small open-source project) so the
# validators have real changes to read.


def run(contract):
    """contract is a client bound to a deployed SemverGate instance."""

    # 1. Register a release that CLAIMS to be a patch.
    contract.register_release(
        release_id="demo-1",
        package="example-lib",
        from_version="1.4.2",
        to_version="1.4.3",
        declared_bump="patch",
        diff_url="https://github.com/OWNER/REPO/compare/v1.4.2...v1.4.3",
    ).transact()

    # 2. Anyone can request the audit. Expect "violation" if the diff
    #    removes or renames something users depend on, "compliant" if
    #    it is only bug fixes.
    verdict = contract.file_audit(release_id="demo-1").transact()
    assert verdict in ("violation", "compliant")

    # 3. Read the receipt: declared_bump, required_bump, violation,
    #    breaking_changes, evidence_url.
    print(contract.get_audit(release_id="demo-1").call())

    # 4. One-time challenge. Reruns the whole consensus round.
    #    Returns "overturned" if the outcome flipped, else "upheld".
    outcome = contract.challenge_audit(release_id="demo-1").transact()
    assert outcome in ("overturned", "upheld")

    # 5. These must all be rejected (revert):
    #    - file_audit again on demo-1            -> "already audited"
    #    - challenge_audit again on demo-1       -> "already challenged"
    #    - register_release with declared_bump="hotfix" -> invalid bump
    #    - register_release with diff_url="not-a-url"   -> invalid URL

    # 6. Easy gate for CI or other contracts:
    print(contract.get_verdict(release_id="demo-1").call())
    # "violation", "compliant", or "unaudited"


if __name__ == "__main__":
    print(__doc__)
