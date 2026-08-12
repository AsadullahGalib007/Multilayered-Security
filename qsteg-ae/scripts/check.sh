#!/usr/bin/env bash
# Everything CI runs, runnable locally with one command.
#
# The CI workflow calls this script rather than duplicating the steps, so "green
# locally" and "green in CI" cannot drift apart.
#
#   ./scripts/check.sh
#
# Assumes `uv sync --all-groups` has run and, for the liboqs tests,
# `./scripts/bootstrap_liboqs.sh` (see docs/decisions/001-pqc-library.md).
set -euo pipefail

cd "$(dirname "$0")/.."

# liboqs lives outside uv.lock (decision 001); without this the oqs tests skip.
export LD_LIBRARY_PATH="${HOME}/_oqs/lib:${LD_LIBRARY_PATH:-}"

step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

step "ruff"
uv run ruff check .

step "black"
uv run black --check .

step "pytest"
uv run pytest

# Protocol step 6: every experiment is re-runnable with one command. Running them in
# --smoke mode here means CI executes the real code path, so an experiment that has
# rotted is caught by the build rather than three phases later when its number is needed.
step "smoke experiments"
smoke_out="$(mktemp -d)"
trap 'rm -rf "${smoke_out}"' EXIT
for module in experiments/*.py; do
    name="$(basename "${module}" .py)"
    [ "${name}" = "__init__" ] && continue
    [ "${name}" = "_harness" ] && continue
    printf '  -> experiments.%s\n' "${name}"
    uv run python -m "experiments.${name}" --smoke --out "${smoke_out}/${name}"
    test -f "${smoke_out}/${name}/manifest.json" \
        || { echo "experiments.${name} wrote no manifest"; exit 1; }
done

printf '\n\033[1mAll checks passed.\033[0m\n'
