# Mac Codex Release To chummer.run

Purpose: let a Codex session running on a Mac build a public-ready desktop artifact, prove it, and promote it onto the live `chummer.run` downloads shelf through the authenticated HTTP upload endpoint instead of manual server file copies.

Use the signed-in path by opening `https://chummer.run/downloads/release-upload` in the browser first, copying the generated `Command` block, and pasting that exact command into the Mac shell. The signed-in handoff mints a short-lived upload code, embeds it in the generated bootstrap command, pins the hosted bootstrap digest, and keeps the published command synchronized with the current hosted bootstrap.

## One command

Open `https://chummer.run/downloads/release-upload`, copy the generated `Command` block, and paste that exact command into the Mac release shell.

Do not run `https://chummer.run/downloads/release-upload/bootstrap.sh` directly for live promotion; it can pass SHA-256 verification and still stop at upload time because a raw public script has no upload credential.
Do not paste `curl -fsSL https://chummer.run/downloads/release-upload/bootstrap.command | bash` unless you explicitly attach `?ticket=...` or `?apiToken=...`; terminal curl does not inherit the browser sign-in session.

Repo-local checkout fallback:

```bash
repo_root="$(git rev-parse --show-toplevel)"
bash "$repo_root/chummer6-hub/scripts/run-mac-release-bootstrap.sh"
```

Do not hardcode `/docker/chummercomplete/.../bootstrap.sh` on the Mac host. That path is for provisioned Linux control environments, not a normal Mac release workstation.

The bootstrap is the public deep link. It now:

1. clones or updates the required repos
2. builds the mac desktop head
3. packages a `.dmg`
4. codesigns, notarizes, staples, and validates it
5. runs startup smoke
6. generates both public release manifests
7. writes `release-evidence/public-promotion.json`
8. uploads the full bundle to `https://chummer.run/api/internal/releases/bundles`
9. verifies the promoted live shelf and prints the resulting `/downloads/install/{artifactId}` handoff URL
10. prints signed-in claim codes when it was launched from the signed-in release-upload handoff

## Minimum environment variables

```bash
export CHUMMER_APP_SIGN_IDENTITY="Developer ID Application: YOUR ORG (TEAMID)"
export CHUMMER_NOTARY_PROFILE="chummer-notary"
```

Optional overrides:

```bash
export CHUMMER_RELEASE_UPLOAD_URL="https://chummer.run/api/internal/releases/bundles"
export CHUMMER_PORTAL_DOWNLOADS_VERIFY_URL="https://chummer.run/downloads/RELEASE_CHANNEL.generated.json"
export CHUMMER_RELEASE_VERIFY_REQUIRE_COMPATIBILITY_PROJECTION="0"
export CHUMMER_RELEASE_CHANNEL="preview"
export CHUMMER_RELEASE_APP="avalonia"
export CHUMMER_RELEASE_RID="osx-arm64"
export CHUMMER_UI_REF="fleet/ui"
export CHUMMER_CORE_REF="fleet/core"
export CHUMMER_HUB_REF="main"
export CHUMMER_UI_KIT_REF="fleet/ui-kit"
export CHUMMER_HUB_REGISTRY_REF="fleet/hub-registry"
export CHUMMER_LEGACY_REF="Docker"
```

## Promotion gate

The upload endpoint may merge platform slices independently, but it only makes an installer public when the bundle includes:

1. the artifact file under `files/`
2. `releases.json`
3. `RELEASE_CHANNEL.generated.json`
4. startup-smoke receipts matching the uploaded digest
5. `release-evidence/public-promotion.json`

For macOS that evidence must prove:

1. `promotionStatus=pass`
2. `startupSmokeStatus=pass`
3. `signingStatus=pass`
4. `notarizationStatus=pass`

For Windows promotion the same endpoint is valid, but the evidence must prove startup smoke and signing before the public shelf can expose the installer.

## Public result

Once the upload succeeds:

1. `https://chummer.run/downloads/RELEASE_CHANNEL.generated.json` contains the authoritative promoted artifact set
2. `https://chummer.run/downloads/releases.json` stays coherent as the installer-oriented compatibility view
3. the direct file URL resolves under `/downloads/files/...`
4. the signed-in claim-code handoff is live at `/downloads/install/{artifactId}`
5. the desktop app also ships `Samples/Legacy/Soma-Career.chum5`, bundled from the legacy Chummer5 test fixtures for a real completed-runner import check

The bootstrap now treats the canonical `RELEASE_CHANNEL.generated.json` projection as the success gate.
If the compatibility `releases.json` shelf lags briefly after publish, the run logs a warning instead of failing.
Set `CHUMMER_RELEASE_VERIFY_REQUIRE_COMPATIBILITY_PROJECTION=1` only when you explicitly want compatibility drift to fail the run.
