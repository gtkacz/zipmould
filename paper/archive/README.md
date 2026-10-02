# Archival deposit handoff

`make paper-package` creates these local deliverables under `paper/dist/`:

- `natural-computing-source.zip`: flat publisher-source package;
- `zipmould-evidence.zip`: allowlisted source, synthetic public/test data,
  protocol, frozen results, current manuscripts, and a frozen pre-test code
  snapshot, with per-file SHA-256 checksums;
- `SHA256SUMS`: hashes of both ZIP files;
- `package-status.json`: unresolved author inputs and package status.

The snapshot intentionally excludes `benchmark/data/`, other legacy outputs,
Git internals, caches, credentials, and unreleased local runtime material.
The already released test seed is included in its documented evidence path.
Publisher files and the unmodified CTAN `threeparttable.sty` keep their own
notices; they are not relicensed as project code.

## Before depositing

Complete `author-inputs.json` from author-supplied facts. No roles, grant number,
license selection, or approval should be inferred. Software remains MIT under
the root `LICENSE`. An explicit synthetic-data license is awaiting the author's
choice; `metadata-draft.json` deliberately has no selected data license or DOI.

In Zenodo (or the chosen durable archive), create a dataset record owned by the
authors, use `metadata-draft.json` as the field-entry reference, choose the
confirmed data license, and upload `zipmould-evidence.zip` plus its checksum.
The JSON is a human-review draft, not a version-specific API request.
Reserve the record's DOI, add the actual DOI/URL to both `author-inputs.json`
and the Data Availability paragraph in `paper/main.typ`, regenerate the
packages, and replace the upload with the rebuilt ZIP before publication.
Do not claim that the deposit is public until the archive confirms publication.
The journal upload should follow publication or use the archive's supported
reviewer-access mechanism.

## Reproduction from the evidence ZIP

Extract the ZIP, install the locked environment with `uv sync`, and run
`make paper-reproduce`. This restores the already released test data, validates
all returned paths, and compares the regenerated report and bootstrap artifacts
with the archived originals. This analysis does not require Git history.

The nested `frozen-confirmatory-source.tar` preserves the selected code and
configuration bytes at the original pre-test commit, rather than describing
the revised manuscript tree as the experimental release. It omits third-party
legacy data. For the original solver execution workflow, clone the public
repository and check out `challenge-v1-confirmatory-v1`; the runner's original
Git/tag safeguards are intentionally retained. Do not move the pre-test tag.
