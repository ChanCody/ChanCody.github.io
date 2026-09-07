#!/usr/bin/env bash
# Source from an integration test after creating tmp_dir and its cleanup trap.
prepare_fixture_site() {
  local repo_root
  repo_root="$(pwd)"
  # ruby/setup-ruby installs into the original checkout's configured bundle.
  export BUNDLE_GEMFILE="${repo_root}/Gemfile"
  fixture_source="${tmp_dir}/source"
  mkdir -p "${fixture_source}"
  tar --exclude=./.git --exclude=./_site --exclude=./node_modules \
    --exclude=./vendor --exclude=./.bundle --exclude=./.venv \
    --exclude=./.jekyll-cache --exclude=./.jekyll-metadata \
    --exclude=./test-results --exclude=./output \
    -cf - . | tar -xf - -C "${fixture_source}"
  mkdir -p "${fixture_source}/_posts"
  cp "${repo_root}"/test/fixtures/posts/*.md "${fixture_source}/_posts/"
  cat >"${tmp_override}" <<'YAML'
baseurl: ""
disqus_shortname: al-folio
giscus:
  repo: alshedivat/al-folio
  repo_id: R_kgDOExample
  category: Comments
  category_id: DIC_kwDOExample
imagemagick:
  enabled: false
YAML
  cd "${fixture_source}"
}
