import sys
import os
import logging
import asyncio
import json
from base64 import b64decode
from aiohttp import web

#logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] (L:%(lineno)s) %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(format='[%(levelname)-8s] (L:%(lineno)s) %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

filepath = None
instances = {}
store = None
usernames = {}
uids = {}

def fetch_user_info(identifier, query):
    id_type = query.get('idType', None)
    if not id_type:
        raise web.HTTPBadRequest(text='Missing or wrong idType')
    LOG.info(f'Requesting User {identifier} [type {id_type}]')
    if id_type == 'username':
        pos = usernames.get(identifier, None)
        return store[pos] if pos is not None else None
    if id_type == 'uid':
        try:
            pos = uids.get(int(identifier), None)
            return store[pos] if pos is not None else None
        except Exception:
            return None
    raise web.HTTPBadRequest(text='Missing or wrong idType')

async def user(request):
    # Authenticate
    auth_header = request.headers.get('AUTHORIZATION')
    if not auth_header:
        raise web.HTTPUnauthorized(text=f'Protected access\n')
    _, token = auth_header.split(None, 1)  # Skipping the Basic keyword
    LOG.debug(f'Token is {token}')
    instance, passwd = b64decode(token).decode().split(':', 1)
    LOG.debug(f'I am instance {instance} and the password is {passwd}')
    info = instances.get(instance)
    if info is None or info != passwd:
        raise web.HTTPUnauthorized(text=f'Protected access\n')

    # Reload users list
    load_users()

    # Find user
    user_info = fetch_user_info(request.match_info['identifier'], request.rel_url.query)
    if user_info is None:
        raise web.HTTPBadRequest(text=f'No info for that user\n')
    return web.json_response({ 'header': { "apiVersion": "v1",
                                           "code": "200",
                                           "service": "users",
                                           "developerMessage": "",
                                           "userMessage": "OK",
                                           "errorCode": "1",
                                           "docLink": "https://ega-archive.org",
                                           "errorStack": "" },
                               'response': { "numTotalResults": 1,
                                             "resultType": "eu.crg.ega.microservice.dto.lega.v1.users.LocalEgaUser",
                                             "result": [ user_info ]}
    })

def main():
    print("Main is being run")
    if len(sys.argv) < 3:
        print('Usage: {sys.argv[0] <hostaddr> <port> <filepath>}', file=sys.stderr)
        sys.exit(2)

    host = sys.argv[1]
    port = sys.argv[2]

    global filepath
    filepath = sys.argv[3]

    server = web.Application()
    load_users()

    # Registering the routes
    server.router.add_get('/lega/v1/legas/users/{identifier}', user, name='user')

    # aaaand... cue music
    web.run_app(server, host=host, port=port, shutdown_timeout=0)


def load_users():
    # Initialization
    global filepath, instances, store, usernames, uids
    instances[os.environ[f'CEGA_USERS_USER']] = os.environ[f'CEGA_USERS_PASSWORD']
    with open(filepath, 'rt') as f:
        store = json.load(f)
    for i, d in enumerate(store):
        usernames[d['username']] = i
        uids[d['uid']] = i


if __name__ == '__main__':
    main()
