# macOS Source Build Path

Purpose: keep the personal macOS build-from-source path canonical, minimal, and non-drifting.

This path has one executable implementation, one executable install helper, and one user-facing explanation.

## Canonical files

Executable build script:

- `Chummer6/scripts/build-chummer6-macos-local.sh`

Executable install script:

- `Chummer6/scripts/install-chummer6-macos-local.sh`

User-facing guide:

- `Chummer6/SOURCE_BUILD_MACOS.md`

Public download pointer:

- `Chummer6/DOWNLOAD.md`

These files are the canonical macOS local-source-build lane. Do not mirror the shell scripts into `chummer-design`.

## Required posture

The macOS local-source-build lane must stay:

1. personal and inspectable
2. split into a build step and a separate install step
3. notify-only for auto-update by default
4. analytics-off by default
5. explicit that it is not the public macOS release path on `chummer.run`

## Required behavior

The checked-in scripts must:

1. audit the host without cloning or building when `--audit-only` is used
2. build from the owner-repo compatibility tree rather than a partial repo checkout
3. install the pinned .NET SDK into the local workspace instead of relying on a global SDK
4. emit a manifest with exact source revisions
5. keep the build step separate from the local `.app` install step
6. default `CHUMMER_DESKTOP_UPDATE_MODE` to `notify`
7. default `CHUMMER_DESKTOP_ANALYTICS_DEFAULT` to `off`
8. avoid `sudo`, codesign, notarization, and public-support claims in the personal local-build lane

## Ownership

`Chummer6` owns:

- the shell scripts
- the user-facing source-build guide
- the build-from-source tests

`chummer-design` owns:

- the rule that the mac local-source-build lane stays single-sourced
- the rule that it remains personal and non-public
- the public-guide pointer language in `DOWNLOAD.md`

## Verification

Minimum validation for this lane:

```bash
cd Chummer6
bash -n scripts/build-chummer6-macos-local.sh
bash -n scripts/install-chummer6-macos-local.sh
python3 -m unittest tests/test_macos_source_build_script.py -q
```

A real binary build still has to happen on a Mac host.

## Drift rules

Do not:

- create a second copy of either macOS local-build script in `chummer-design`
- describe this path as the normal public macOS install flow
- describe the output as signed, notarized, or officially supported
- collapse the separate build and install steps into one ambiguous public-facing instruction

When behavior changes, update the checked-in scripts and `Chummer6/SOURCE_BUILD_MACOS.md` first, then adjust this maintenance note only if the governing posture changed.
