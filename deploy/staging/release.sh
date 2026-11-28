#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "$0")"
unset SECRET_KEY
umask 077

fail() {
    echo "$*" >&2
    exit 1
}

valid_revision() {
    [[ $1 =~ ^[0-9a-f]{40}$ ]]
}

compose() {
    RELEASE_IMAGE="$1" docker compose --project-name duma-lab6-staging \
        --env-file .env -f compose.yaml "${:2}"
}

apply_release() {
    local revision=$1 image=$2 expected_id container_id running
    expected_id=$(docker image inspect --format '{{.Id}}' "$image") || return 1
    compose "$image" up -d --no-build --pull never --wait --wait-timeout 45 || return 1
    container_id=$(compose "$image" ps -q app) || return 1
    running=$(docker inspect --format '{{.Image}} {{.State.Health.Status}}' "$container_id") ||
        return 1
    if [[ $running != "$expected_id healthy" ]]; then
        echo "Expected healthy container using $expected_id, got $running" >&2
        return 1
    fi
    python3 smoke.py "$revision"
}

ensure_cached() {
    docker image inspect "$1" >/dev/null 2>&1 || timeout 120 docker pull "$1"
}

[[ $# -ge 1 ]] || fail "Usage: release.sh deploy COMMIT_SHA | rollback"
case "$1" in
    deploy)
        [[ $# == 2 ]] && valid_revision "$2" || fail "Expected a 40-character commit SHA"
        ;;
    rollback)
        [[ $# == 1 ]] || fail "Usage: release.sh rollback"
        ;;
    *) fail "Unknown release command" ;;
esac

exec 9>.release.lock
flock -n 9 || fail "Another staging deployment holds the lock"

[[ -s .env && -s smoke.json && -s registry ]] || fail "Missing .env, smoke.json or registry"
read -r registry < registry
[[ $registry =~ ^[a-z0-9.-]+(:[0-9]+)?(/[a-z0-9._-]+)+$ ]] ||
    fail "Invalid registry repository"
compose "$registry:preflight" config --quiet || fail "Invalid staging settings"

current_revision= current_image= previous_revision= previous_image=
if [[ -f .releases ]]; then
    {
        read -r current_revision current_image
        read -r previous_revision previous_image || true
    } < .releases
fi

if [[ $1 == rollback ]]; then
    [[ -n $previous_revision && -n $previous_image ]] || fail "No previous accepted release"
    revision=$previous_revision
    image=$previous_image
    ensure_cached "$image" || fail "Could not obtain the previous image"
else
    revision=$2
    tag="$registry:$revision"
    timeout 120 docker pull "$tag" || fail "Could not pull $tag"
    digests=$(docker image inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' "$tag") ||
        fail "Could not inspect $tag"
    image=$(awk -v prefix="$registry@" 'index($0, prefix) == 1 {print; exit}' <<< "$digests")
    [[ ${image#"$registry@"} =~ ^sha256:[0-9a-f]{64}$ ]] ||
        fail "Registry returned no digest for $tag"
fi

image_revision=$(docker image inspect \
    --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$image")
[[ $image_revision == "$revision" ]] || fail "Image revision does not match $revision"

if [[ -n $current_image ]]; then
    ensure_cached "$current_image" || fail "Could not obtain the current image for recovery"
fi

state=
if [[ $image != "$current_image" ]]; then
    state=$(mktemp .releases.XXXXXX)
    trap 'rm -f -- "$state"' EXIT
    printf '%s %s\n%s %s\n' "$revision" "$image" \
        "$current_revision" "$current_image" > "$state"
fi

if ! apply_release "$revision" "$image" ||
    { [[ -n $state ]] && ! mv -f -- "$state" .releases; }; then
    echo "Release verification failed for $revision" >&2
    if [[ -n $current_image ]]; then
        apply_release "$current_revision" "$current_image" ||
            fail "Recovery failed. Inspect staging before retrying."
        echo "Restored accepted release $current_revision"
    else
        compose "$image" stop app || fail "Could not stop the failed first release"
    fi
    exit 1
fi

echo "Accepted release $revision ($image)"
