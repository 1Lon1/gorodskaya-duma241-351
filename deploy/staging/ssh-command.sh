#!/usr/bin/env bash
set -euo pipefail

release="$HOME/duma-staging/release.sh"
command=${SSH_ORIGINAL_COMMAND-}
if [[ $command =~ ^deploy[[:space:]]([0-9a-f]{40})$ ]]; then
    exec "$release" deploy "${BASH_REMATCH[1]}"
fi
if [[ $command == rollback ]]; then
    exec "$release" rollback
fi
echo "Only deploy COMMIT_SHA and rollback are available" >&2
exit 1
