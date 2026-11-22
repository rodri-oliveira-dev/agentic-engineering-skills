# Artifacts and pipeline

Read this reference when readiness depends on build reproducibility, artifact integrity or provenance, dependencies, packaging, registries, CI/CD changes, publishing, or pipeline secrets.

## Trace source to deployable artifact

Identify the source revision, build definition, inputs, toolchain, dependency resolution, target platform, produced artifact, immutable version, integrity metadata, storage location, promotion path, and deployment reference. Confirm that tested and proposed artifacts are the same bytes or have an evidenced reproducible relationship; a matching human-readable version is insufficient when artifacts can be overwritten.

Reproducibility may mean byte-for-byte determinism, repeatable functional output from pinned inputs, or a documented controlled build depending on project needs. State which property is required and what evidence exists. Do not claim reproducibility from one successful build.

## Inspect dependencies and packaging

Check resolved rather than merely declared versions, lockfiles, trusted sources, integrity or signature verification, licensing or policy gates where required, transitive changes, target runtime support, and packaging completeness. Treat vulnerability scanner output as evidence to triage, not automatic proof of reachability or safety.

Verify startup files, migrations, static assets, configuration schemas, native libraries, manifests, permissions, and metadata required by the actual deployment unit. A passing compile does not prove a package is installable or runnable in the target.

## Assess pipeline trust

Inspect trigger and approval boundaries, token and job permissions, secret exposure, external contributions, untrusted code execution, artifact upload and download, environment protection, action or plugin pinning, cache poisoning risk, publishing identity, provenance, retention, and audit trail only as relevant to the pipeline.

Do not expose secret values to verify availability. Prefer reference existence, access policy, expiry or rotation metadata, and an authorized bounded integration check. Do not rerun or approve jobs, publish artifacts, clear caches, or change pipeline permissions as part of assessment.

## Evidence

Record pipeline run identifier, revision, definition version, timestamp, environment, result, skipped or allowed-to-fail stages, artifact digest, and retention. Stale results, results for another revision, or manually uploaded artifacts are gaps until their relationship to the release is established.
