# Shared by local --rebuild and GitHub Pages deployment. No site sources or
# installed project dependencies are baked into this image.
FROM python:3.13.7-slim-bookworm AS python
FROM node:20.19.5-bookworm-slim AS node
FROM ruby:3.3.5-slim-bookworm

COPY --from=python /usr/local/ /usr/local/
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/ /usr/local/lib/node_modules/
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential git imagemagick libyaml-dev zlib1g-dev \
       libbz2-1.0 libexpat1 libffi8 liblzma5 libsqlite3-0 libuuid1 libncursesw6 libreadline8 libgdbm6 libgdbm-compat4 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir nbconvert==7.16.6 \
    && npm install --global purgecss@7.0.2

ENV JEKYLL_ENV=production BUNDLE_FROZEN=true LANG=C.UTF-8
WORKDIR /work
