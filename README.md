# LocalEGA-deploy-swarm
[![Build Status](https://travis-ci.org/neicnordic/LocalEGA-deploy-swarm.svg?branch=master)](https://travis-ci.org/neicnordic/LocalEGA-deploy-swarm)

Docker Swarm deployment of LocalEGA

## Pre-requisites

- `mkcert` (https://github.com/FiloSottile/mkcert)
- `crypt4gh` (https://github.com/uio-bmi/crypt4gh)

## How-to

- `source variables.sh` (CEGA-related env-vars should be set manually, e.g. `CEGA_CONNECTION`)
- `source bootstrap.sh`
- `source deploy.sh`

Cleaning up: `source sleanup.sh`
