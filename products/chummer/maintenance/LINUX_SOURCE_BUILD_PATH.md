# Linux Source Build Path

Purpose: keep the Linux build-from-source path canonical, minimal, and non-drifting.

This path has one executable build script, one executable install helper, and one user-facing explanation.

## Canonical files

Executable build script:

- `Chummer6/scripts/build-chummer6-linux.sh`

Executable install script:

- `Chummer6/scripts/install-chummer6-linux-local.sh`

User-facing guide:

- `Chummer6/SOURCE_BUILD_LINUX.md`

Public download pointer:

- `Chummer6/DOWNLOAD.md`

These files are the canonical Linux source-build lane. Do not mirror the shell scripts into `chummer-design`.

## Required posture

The Linux source-build lane must stay:

1. local and inspectable
2. split into a build step and a separate user-local install step
3. notify-only for auto-update by default
4. clean about temporary build artifacts
5. explicit that `chummer.run` remains the official binary shelf

## Required behavior

The checked-in scripts must:

1. audit the host without cloning or building when `--audit-only` is used
2. build from the owner-repo compatibility tree rather than a partial repo checkout
3. install the pinned .NET SDK into the local workspace instead of relying on a global SDK
4. emit a manifest with exact source revisions
5. keep the build step separate from the user-local install step
6. remove temporary package-plane and runtime build files unless `CHUMMER_KEEP_BUILD_TEMP=1`
7. default `CHUMMER_DESKTOP_UPDATE_MODE` to `notify`
8. default `CHUMMER_DESKTOP_ANALYTICS_DEFAULT` to `off`
9. avoid `sudo` and any system-wide install claim in the local-build lane

## Ownership

`Chummer6` owns:

- the shell script
- the install helper
- the user-facing source-build guide
- the build-from-source tests

`chummer-design` owns:

- the policy that source-built copies remain notify-only by default
- the policy that the Linux local-source-build lane stays split into build -> install
- the rule that this path must stay single-sourced
- the rule that docs point at `chummer.run` for official binaries

## Verification

Minimum validation for this lane:

```bash
cd Chummer6
bash -n scripts/build-chummer6-linux.sh
bash -n scripts/install-chummer6-linux-local.sh
pytest -q tests/test_linux_source_build_script.py
```

Real build verification remains a separate host-capacity concern. A successful real run should produce:

- `artifacts/chummer6-linux-*/Chummer.Avalonia`
- `artifacts/chummer6-linux-*/run-chummer6.sh`
- `artifacts/chummer6-linux-*/BUILD-MANIFEST.txt`
- `artifacts/chummer6-linux-*.tar.gz`

The local install step should then create:

- a user-local install directory under `~/.local/opt`
- a user-local command link under `~/.local/bin`

## Drift rules

Do not:

- create a second copy of the Linux source-build script in `chummer-design`
- collapse the separate build and install steps into one ambiguous instruction
- describe source-built copies as official releases
- default source-built copies to full auto-update
- make GitHub the user-facing binary shelf

When behavior changes, update the checked-in script and `Chummer6/SOURCE_BUILD_LINUX.md` first, then adjust this maintenance note only if the governing posture changed.
