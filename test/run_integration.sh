#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
log_dir="${CI_LOG_DIR:-test-results/integration}"
mkdir -p "${log_dir}"
log_dir="$(cd "${log_dir}" && pwd)"
printf 'test\texit_code\n' >"${log_dir}/summary.tsv"
failed=0
for name in comments plugin_toggles distill bootstrap_compat upgrade_cli css_minify; do
  echo "Running ${name} integration test"
  status=0
  bash "test/integration_${name}.sh" >"${log_dir}/${name}.log" 2>&1 || status=$?
  cat "${log_dir}/${name}.log"
  printf '%s\t%s\n' "${name}" "${status}" >>"${log_dir}/summary.tsv"
  if [[ "${status}" -ne 0 ]]; then
    failed=1
  fi
done
cat "${log_dir}/summary.tsv"
exit "${failed}"
