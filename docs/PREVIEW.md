# Local preview and production builds

Run `./bin/preview` (or `./bin/preview 8087`) to start a preview on all IPv4
interfaces. The default port is 8086. The site path follows `_config.yml`,
currently `/`. Open `http://localhost:8086/` locally, or use the host's LAN IP
from another device.

Content changes automatically rebuild through polling; refresh the browser to
see the result. Restart the preview after configuration or dependency changes.
Ctrl+C stops the preview container.

Run `./bin/preview --rebuild` to build production output into `_site` and exit.
It neither starts a server nor stops an existing preview. This delegates to
`bash bin/build-site`, the same entry point used by the deployment workflow.
It rebuilds the shared production image without cached layers, installs locked
project dependencies, applies the deployment repository setting, runs Jekyll in
production mode, and purges unused CSS. It requires network access and takes
longer than normal preview. Runtime and production tool versions live in
`bin/production.Dockerfile`; change them there for both local and CI builds.

The build uses an isolated snapshot of tracked files and non-ignored new files,
including uncommitted edits. Generated output, dependencies, and Jekyll caches
are excluded. Source files and lockfiles are not changed. Only a successful
build replaces `_site`; after a failed build any previous `_site` remains the
previous result, not a successful new build.

The GitHub repository is read from `GITHUB_REPOSITORY` in CI or Git origin
locally. Set `GITHUB_REPOSITORY=owner/repo` explicitly when origin cannot identify
the intended deployment repository.

Local and remote builds share their recipe and environment definition. Compare
the same source revision and repository setting; uncommitted local changes,
external data, build timestamps, and upstream OS/transitive tool updates can
still change output. Ordinary watch preview is an editing aid; `--rebuild`
checks the production build, including CSS cleanup.
