# Live `/tools` Route Fix

The live server for DorkMe.com identifies as Apache and currently serves `/` and `/assets/...` successfully, but returns `500 Internal Server Error` for `/tools`, `/tools/`, `/404.html`, and `/tools/index.html`. This indicates that the live document root has not yet received the static `/tools/index.html` fallback and/or has a broken host-level error document or rewrite configuration.

## Recommended production fix

Upload the full contents of this repository to the DorkMe.com document root, including hidden files such as `.htaccess`. The important files for the route fix are:

| File | Purpose |
|---|---|
| `.htaccess` | Apache SPA fallback: existing files are served normally, while client-side routes fall back to `index.html`. |
| `tools/index.html` | Directory-index fallback for `/tools/` on static hosts. |
| `404.html` | Static fallback for hosts that use a custom 404 page. |
| `_redirects` | Netlify-style SPA fallback if the site is ever deployed there. |

## Expected result after deployment

After the repository is deployed to the live host, these checks should succeed:

```bash
curl -I https://dorkme.com/tools
curl -I https://dorkme.com/tools/
curl -I https://dorkme.com/tools/index.html
```

`/tools` may redirect to `/tools/` depending on Apache directory handling, but `/tools/` should return `200 OK` and serve the DorkMe SPA rather than returning `500`.
