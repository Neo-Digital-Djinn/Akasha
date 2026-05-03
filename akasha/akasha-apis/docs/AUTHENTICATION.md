# Authentication

V2 keeps authentication minimal.

Current adapters are no-auth or stub-first.

If a provider later requires auth:
- add env variable entry to `API_KEYS.env.example`
- keep secrets out of canon
- surface `auth_required` in adapter metadata
