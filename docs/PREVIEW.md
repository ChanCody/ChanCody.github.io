# Local preview and production builds

Run `./bin/preview` (or `./bin/preview 8087`) to start a preview on all IPv4
interfaces. The default port is 8086. The site path follows `_config.yml`,
currently `/`. Open `http://localhost:8086/` locally, or use the host's LAN IP
from another device.

Content changes automatically rebuild through polling; refresh the browser to
see the result. Restart the preview after configuration or dependency changes.
Ctrl+C stops the preview container started by that terminal. Running the same
command again reuses the running instance, prints an access hint, and exits;
it does not attach to its logs or wait for the initial build to finish. Check
the original terminal for build progress.

Run `./bin/preview --help` (or `-h`) for all commands and examples. Help works
without Docker. Commands that accept a port default to 8086:

```bash
./bin/preview                  # Start or reuse the default preview
./bin/preview 8087             # Start or reuse an independent preview
./bin/preview --restart        # Recreate the default preview in the foreground
./bin/preview --restart 8087    # Recreate only the preview on port 8087
./bin/preview --stop           # Stop the default preview; safe to repeat
./bin/preview --stop 8087      # Stop only the preview on port 8087
```

Use `--restart` after changing `_config.yml` or dependencies. It stops and
removes the selected preview, then creates a new container; if none exists,
it starts one. Previews are identified by the repository's physical absolute
path and port, so different repositories and ports are managed independently.
A restart from another terminal ends the old foreground session; its cleanup
cannot stop the replacement container.

A running instance is reused even if the initial site build is still underway.
If an instance is stuck during startup or in an abnormal state, inspect the
original terminal and use `--restart` to recover. Containers belonging to other
owners are never automatically stopped, and occupied ports are not automatically
changed. Use another port explicitly when you need concurrent previews.

Older versions of this script created randomly named containers. These are not
automatically adopted or stopped. If an old preview still occupies your port,
list running containers and inspect the host-port mapping:

```bash
docker ps --format 'table {{.ID}}\t{{.Names}}\t{{.Ports}}'
```

After confirming the container is your old preview (for example, its mapping
includes `0.0.0.0:8086->8080/tcp`), run `docker stop <container-ID>` and retry.
Use `sudo docker` if your Docker setup requires it. The container named in a
failed startup error is not necessarily the container occupying the port.

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
