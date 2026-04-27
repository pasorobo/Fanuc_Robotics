#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

mkdir -p src

manifest="${1:-third_party.humble.repos}"

if ! command -v vcs >/dev/null 2>&1; then
  echo "vcs is not installed. Install python3-vcstool first." >&2
  exit 1
fi

vcs import src < "${manifest}"

if [ -d src/fanuc_driver/.git ]; then
  git -C src/fanuc_driver submodule update --init --recursive
fi

if [ -d src/fanuc_description/.git ]; then
  if git -C src/fanuc_description lfs version >/dev/null 2>&1; then
    git -C src/fanuc_description lfs install --local
    git -C src/fanuc_description lfs pull
  else
    echo "git-lfs is not installed; skipping FANUC mesh LFS download." >&2
  fi
fi
