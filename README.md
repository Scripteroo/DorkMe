# DorkMe.com

Static mirror of the DorkMe.com public-web discovery console uploaded from the live site for repository backup and deployment.

## Included files

The repository contains the homepage HTML, compiled JavaScript and CSS bundles, logo media, and locally backed-up hero imagery observed on the live site. The HTML still references the same public asset paths used by the live deployment, while the external CloudFront images are also preserved under `external-assets/` for backup.

## Testing notes

The homepage at `https://dorkme.com/` loaded successfully during upload preparation. The live `/tools` route returned a `500 Internal Server Error` at capture time, so this repository includes `tools/index.html` as a static route fallback for hosts that serve directory index files.
