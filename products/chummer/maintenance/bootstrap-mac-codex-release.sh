#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[chummer-mac-release] %s\n' "$*"
}

die() {
  printf '[chummer-mac-release] ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command missing: $1"
}

clone_or_update() {
  local repo_url="$1"
  local target_dir="$2"
  local ref="$3"
  local low_speed_limit="${CHUMMER_GIT_HTTP_LOW_SPEED_LIMIT:-100}"
  local low_speed_time="${CHUMMER_GIT_HTTP_LOW_SPEED_TIME:-120}"
  local max_attempts="${CHUMMER_GIT_MAX_ATTEMPTS:-4}"
  local retry_sleep="${CHUMMER_GIT_RETRY_SLEEP_SECONDS:-5}"

  run_git_cmd() {
    "$@"
  }

  run_git_cmd_with_retries() {
    local op="$1"
    local attempt=1
    shift

    while true; do
      local status=0
      set +e
      run_git_cmd "$@"
      status=$?
      set -e
      if (( status == 0 )); then
        return 0
      fi

      if (( attempt >= max_attempts )); then
        return "$status"
      fi

      attempt=$((attempt + 1))
      log "$op failed (status=$status), retrying in ${retry_sleep}s (attempt ${attempt}/${max_attempts})"
      sleep "$retry_sleep"
    done
  }

  with_git_transport_tuning() {
    GIT_HTTP_LOW_SPEED_LIMIT="$low_speed_limit" \
    GIT_HTTP_LOW_SPEED_TIME="$low_speed_time" \
    "$@"
  }

  clone_branch_checkout() {
    rm -rf "$target_dir"
    with_git_transport_tuning \
      git \
      clone --single-branch --depth 1 --branch "$ref" "$repo_url" "$target_dir"
  }

  github_archive_url_for_ref() {
    local normalized_repo_url="${repo_url%.git}"
    local encoded_ref
    case "$normalized_repo_url" in
      https://github.com/*/*)
        encoded_ref="$(python3 - "$ref" <<'PY'
from urllib.parse import quote
import sys

print(quote(sys.argv[1], safe=""))
PY
)"
        printf 'https://codeload.github.com/%s/tar.gz/%s' "${normalized_repo_url#https://github.com/}" "$encoded_ref"
        return 0
        ;;
    esac
    return 1
  }

  download_github_archive_checkout() {
    local archive_url
    local archive_root
    local archive_path
    local unpack_root
    local extracted_dir
    local archive_retries=$(( max_attempts - 1 ))

    archive_url="$(github_archive_url_for_ref)" || return 1
    archive_root="$(mktemp -d "${TMPDIR:-/tmp}/chummer-bootstrap-archive.XXXXXX")" || return 1
    archive_path="$archive_root/repo.tar.gz"
    unpack_root="$archive_root/unpack"
    mkdir -p "$unpack_root"

    log "git clone exhausted retries; downloading source archive for $(basename "$target_dir") -> $ref"
    if ! curl \
      --fail \
      --location \
      --retry "$archive_retries" \
      --retry-delay "$retry_sleep" \
      --connect-timeout 15 \
      --speed-limit "$low_speed_limit" \
      --speed-time "$low_speed_time" \
      "$archive_url" \
      -o "$archive_path"; then
      rm -rf "$archive_root"
      return 1
    fi

    rm -rf "$target_dir"
    if ! tar -xzf "$archive_path" -C "$unpack_root"; then
      rm -rf "$archive_root"
      return 1
    fi

    extracted_dir="$(find "$unpack_root" -mindepth 1 -maxdepth 1 -type d | sort | head -n 1)"
    if [[ -z "$extracted_dir" || ! -d "$extracted_dir" ]]; then
      rm -rf "$archive_root"
      return 1
    fi

    mv "$extracted_dir" "$target_dir"
    rm -rf "$archive_root"
    return 0
  }

  if [[ -d "$target_dir/.git" ]]; then
    log "updating $(basename "$target_dir") -> $ref"
    run_git_cmd git -C "$target_dir" remote set-url origin "$repo_url"
    run_git_cmd_with_retries \
      "fetching $(basename "$target_dir")" \
      with_git_transport_tuning \
      git \
      -C "$target_dir" \
      fetch --depth 1 origin "$ref"
    run_git_cmd_with_retries \
      "checking out $(basename "$target_dir")" \
      with_git_transport_tuning \
      git \
      -C "$target_dir" \
      checkout -q FETCH_HEAD
  else
    log "cloning $(basename "$target_dir") -> $ref"
    local clone_status=0
    set +e
    run_git_cmd_with_retries \
      "cloning $(basename "$target_dir")" \
      clone_branch_checkout
    clone_status=$?
    set -e
    if (( clone_status != 0 )); then
      if ! download_github_archive_checkout; then
        die "checkout failed for $(basename "$target_dir") -> $ref after ${max_attempts} git clone attempts and GitHub archive fallback"
      fi
    fi
  fi
}

infer_publish_mode() {
  if [[ -n "${CHUMMER_RELEASE_PUBLISH_MODE:-}" ]]; then
    printf '%s' "$CHUMMER_RELEASE_PUBLISH_MODE"
    return
  fi

  if [[ -n "${CHUMMER_PORTAL_DOWNLOADS_S3_URI:-}" ]]; then
    printf 's3'
    return
  fi

  if [[ -n "${CHUMMER_RELEASE_SSH_TARGET:-}" && -n "${CHUMMER_PORTAL_DOWNLOADS_DEPLOY_DIR:-}" ]]; then
    printf 'filesystem'
    return
  fi

  printf 'none'
}

capture_post_publish_manifest_projection() {
  local verify_url="$1"
  local dist_dir="$2"
  local projection_dir="$dist_dir/post-publish-manifest"
  local live_manifest="$projection_dir/releases.json"
  local live_canonical_manifest="$projection_dir/RELEASE_CHANNEL.generated.json"

  mkdir -p "$projection_dir"
  log "capturing post-publish live manifest projection"
  curl --fail --silent --show-error --location "$verify_url" -o "$live_manifest"
  curl --fail --silent --show-error --location "${verify_url%/releases.json}/RELEASE_CHANNEL.generated.json" -o "$live_canonical_manifest"

  python3 - "$dist_dir/RELEASE_CHANNEL.generated.json" "$live_canonical_manifest" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

local_payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
live_payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

local_ids = sorted(
    str(item.get("artifactId") or "").strip()
    for item in local_payload.get("artifacts") or []
    if isinstance(item, dict) and str(item.get("artifactId") or "").strip()
)
live_ids = sorted(
    str(item.get("artifactId") or "").strip()
    for item in live_payload.get("artifacts") or []
    if isinstance(item, dict) and str(item.get("artifactId") or "").strip()
)
if local_ids != live_ids:
    raise SystemExit(
        "Local canonical manifest reflects the just-built bundle fragment only if the live canonical artifact ids match. "
        f"local={local_ids} live={live_ids}"
    )
print("Local canonical manifest reflects the just-built bundle fragment.")
PY
}

main() {
  require_cmd git
  require_cmd dotnet
  require_cmd python3
  require_cmd jq
  require_cmd hdiutil
  require_cmd xcrun

  local work_root="${CHUMMER_MAC_RELEASE_WORK_ROOT:-$HOME/work/chummer-release}"
  local ui_ref="${CHUMMER_UI_REF:-main}"
  local core_ref="${CHUMMER_CORE_REF:-main}"
  local hub_ref="${CHUMMER_HUB_REF:-main}"
  local ui_kit_ref="${CHUMMER_UI_KIT_REF:-main}"
  local app="${CHUMMER_RELEASE_APP:-avalonia}"
  local rid="${CHUMMER_RELEASE_RID:-osx-arm64}"
  local release_channel="${CHUMMER_RELEASE_CHANNEL:-preview}"
  local release_version="${CHUMMER_RELEASE_VERSION:-run-$(date -u +%Y%m%d-%H%M%S)}"
  local publish_mode
  publish_mode="$(infer_publish_mode)"
  local verify_url="${CHUMMER_PORTAL_DOWNLOADS_VERIFY_URL:-https://chummer.run/downloads/releases.json}"

  local sign_identity="${CHUMMER_APP_SIGN_IDENTITY:-}"
  local notary_profile="${CHUMMER_NOTARY_PROFILE:-}"
  [[ -n "$sign_identity" ]] || die "set CHUMMER_APP_SIGN_IDENTITY"
  [[ -n "$notary_profile" ]] || die "set CHUMMER_NOTARY_PROFILE"

  local ui_repo="$work_root/r"
  local core_repo="$work_root/.c/core"
  local hub_repo="$work_root/.c/hub"
  local ui_kit_repo="$work_root/.c/ui"

  mkdir -p "$work_root" "$work_root/.c"

  clone_or_update "https://github.com/ArchonMegalon/chummer6-ui.git" "$ui_repo" "$ui_ref"
  clone_or_update "https://github.com/ArchonMegalon/chummer6-core.git" "$core_repo" "$core_ref"
  clone_or_update "https://github.com/ArchonMegalon/chummer6-hub.git" "$hub_repo" "$hub_ref"
  clone_or_update "https://github.com/ArchonMegalon/chummer6-ui-kit.git" "$ui_kit_repo" "$ui_kit_ref"

  cd "$ui_repo"

  local project launch_target
  case "$app" in
    avalonia)
      project="Chummer.Avalonia/Chummer.Avalonia.csproj"
      launch_target="Chummer.Avalonia"
      ;;
    *)
      die "unsupported app head: $app"
      ;;
  esac

  export CHUMMER_LOCAL_CONTRACTS_PROJECT="$core_repo/Chummer.Contracts/Chummer.Contracts.csproj"
  export CHUMMER_LOCAL_RUN_CONTRACTS_PROJECT="$hub_repo/Chummer.Run.Contracts/Chummer.Run.Contracts.csproj"
  export CHUMMER_LOCAL_UI_KIT_PROJECT="$ui_kit_repo/src/Chummer.Ui.Kit/Chummer.Ui.Kit.csproj"

  local out_dir="out/$app/$rid"
  local dist_dir="dist"
  local dmg_path="$dist_dir/chummer-$app-$rid-installer.dmg"
  local smoke_dir="$dist_dir/startup-smoke"

  log "restoring $project for $rid"
  dotnet restore "$project" \
    -r "$rid" \
    -p:ChummerUseLocalCompatibilityTree=true \
    -p:UseChummerEngineContractsLocalFeed=false \
    -p:ChummerLocalContractsProject="$CHUMMER_LOCAL_CONTRACTS_PROJECT" \
    -p:ChummerLocalRunContractsProject="$CHUMMER_LOCAL_RUN_CONTRACTS_PROJECT" \
    -p:ChummerLocalUiKitProject="$CHUMMER_LOCAL_UI_KIT_PROJECT"

  log "publishing $project"
  dotnet publish "$project" \
    -c Release \
    -r "$rid" \
    --self-contained true \
    -p:PublishSingleFile=true \
    -p:PublishTrimmed=false \
    -p:IncludeNativeLibrariesForSelfExtract=true \
    -p:ChummerUseLocalCompatibilityTree=true \
    -p:ChummerLocalContractsProject="$CHUMMER_LOCAL_CONTRACTS_PROJECT" \
    -p:ChummerLocalRunContractsProject="$CHUMMER_LOCAL_RUN_CONTRACTS_PROJECT" \
    -p:ChummerLocalUiKitProject="$CHUMMER_LOCAL_UI_KIT_PROJECT" \
    -p:ChummerDesktopReleaseVersion="$release_version" \
    -p:ChummerDesktopReleaseChannel="$release_channel" \
    -p:UseChummerEngineContractsLocalFeed=false \
    -o "$out_dir"

  log "packaging dmg"
  bash scripts/build-desktop-installer.sh \
    "$out_dir" \
    "$app" \
    "$rid" \
    "$launch_target" \
    "$dist_dir" \
    "$release_version"

  [[ -f "$dmg_path" ]] || die "dmg not produced: $dmg_path"

  log "repacking dmg with signed app bundle"
  local mount_dir repack_root app_bundle repacked_dmg
  mount_dir="$(mktemp -d "${TMPDIR:-/tmp}/chummer-mac-release-mount.XXXXXX")"
  repack_root="$(mktemp -d "${TMPDIR:-/tmp}/chummer-mac-release-repack.XXXXXX")"
  trap 'hdiutil detach "$mount_dir" >/dev/null 2>&1 || true; rm -rf "$mount_dir" "$repack_root"' EXIT

  hdiutil attach -nobrowse -readonly -mountpoint "$mount_dir" "$dmg_path" >/dev/null
  app_bundle="$(find "$mount_dir" -maxdepth 1 -type d -name '*.app' | sort | head -n 1)"
  [[ -n "$app_bundle" ]] || die "mounted dmg did not expose an .app bundle"
  cp -a "$app_bundle" "$repack_root/"
  hdiutil detach "$mount_dir" >/dev/null

  codesign --force --deep --options runtime --timestamp --sign "$sign_identity" "$repack_root/$(basename "$app_bundle")"

  repacked_dmg="${dmg_path%.dmg}-signed.dmg"
  rm -f "$repacked_dmg"
  hdiutil create \
    -volname "$(basename "$app_bundle" .app)" \
    -srcfolder "$repack_root" \
    -ov \
    -format UDZO \
    "$repacked_dmg" >/dev/null

  mv "$repacked_dmg" "$dmg_path"
  codesign --force --timestamp --sign "$sign_identity" "$dmg_path"

  log "notarizing dmg"
  xcrun notarytool submit "$dmg_path" --keychain-profile "$notary_profile" --wait
  xcrun stapler staple "$dmg_path"

  mkdir -p "$smoke_dir"
  log "running mac startup smoke"
  CHUMMER_DESKTOP_RELEASE_CHANNEL="$release_channel" \
  CHUMMER_DESKTOP_RELEASE_VERSION="$release_version" \
  CHUMMER_DESKTOP_STARTUP_SMOKE_HOST_CLASS="${CHUMMER_DESKTOP_STARTUP_SMOKE_HOST_CLASS:-mac-codex-runner}" \
  bash scripts/run-desktop-startup-smoke.sh \
    "$dmg_path" \
    "$app" \
    "$rid" \
    "$launch_target" \
    "$smoke_dir" \
    "$release_version"

  log "staging bundle"
  mkdir -p "$dist_dir/files"
  mv "$dmg_path" "$dist_dir/files/"

  local published_at
  published_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  DOWNLOADS_DIR="$dist_dir/files" \
  MANIFEST_PATH="$dist_dir/releases.json" \
  PORTAL_MANIFEST_PATH="$dist_dir/releases.json" \
  RELEASE_VERSION="$release_version" \
  RELEASE_CHANNEL="$release_channel" \
  RELEASE_PUBLISHED_AT="$published_at" \
  bash scripts/generate-releases-manifest.sh

  case "$publish_mode" in
    filesystem)
      require_cmd ssh
      require_cmd rsync
      [[ -n "${CHUMMER_RELEASE_SSH_TARGET:-}" ]] || die "set CHUMMER_RELEASE_SSH_TARGET for filesystem publish"
      [[ -n "${CHUMMER_PORTAL_DOWNLOADS_DEPLOY_DIR:-}" ]] || die "set CHUMMER_PORTAL_DOWNLOADS_DEPLOY_DIR for filesystem publish"
      local remote_stage="${CHUMMER_REMOTE_STAGING_DIR:-/tmp/chummer-mac-release-bundle}"
      local remote_ui_repo="${CHUMMER_REMOTE_UI_REPO_DIR:-/docker/chummercomplete/chummer6-ui}"
      log "syncing bundle to ${CHUMMER_RELEASE_SSH_TARGET}:${remote_stage}"
      rsync -az --delete "$dist_dir/" "${CHUMMER_RELEASE_SSH_TARGET}:${remote_stage}/"
      log "publishing bundle on remote host"
      ssh "$CHUMMER_RELEASE_SSH_TARGET" \
        "cd '$remote_ui_repo' && bash scripts/publish-download-bundle.sh '$remote_stage' '${CHUMMER_PORTAL_DOWNLOADS_DEPLOY_DIR}'"
      ;;
    s3)
      require_cmd aws
      [[ -n "${CHUMMER_PORTAL_DOWNLOADS_S3_URI:-}" ]] || die "set CHUMMER_PORTAL_DOWNLOADS_S3_URI for s3 publish"
      log "publishing bundle to object storage"
      CHUMMER_PORTAL_DOWNLOADS_VERIFY_URL="$verify_url" bash scripts/publish-download-bundle-s3.sh "$dist_dir"
      ;;
    none)
      log "publish mode is none; leaving built bundle in $ui_repo/$dist_dir"
      ;;
    *)
      die "unsupported publish mode: $publish_mode"
      ;;
  esac

  log "verifying local bundle manifest"
  bash scripts/verify-releases-manifest.sh "$dist_dir/releases.json"
  log "verifying local canonical release manifest"
  bash scripts/verify-releases-manifest.sh "$dist_dir/RELEASE_CHANNEL.generated.json"

  if [[ "$publish_mode" != "none" ]]; then
    capture_post_publish_manifest_projection "$verify_url" "$dist_dir"
    log "verifying live manifest at $verify_url"
    bash scripts/verify-releases-manifest.sh "$verify_url"
  fi

  log "done"
}

main "$@"
