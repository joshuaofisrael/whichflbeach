# Launch notes

whichflbeach.com is a static site. Page paths stay root-relative (`/assets/...`, `/beaches/...`). The `CNAME` file stays `whichflbeach.com`. Canonicals, the sitemap, robots, and JSON-LD use `https://whichflbeach.com/`.

`GA4_ID` in `_build/build.py` is a public GA4 measurement ID. It is an empty string until you paste yours (`G-XXXXXXXXXX`). Do not put API secrets in the repo.

`python3 _build/check.py --launch` exits 1 while `GA4_ID` is empty. It also exits 1 if any page is missing the Cloudflare Web Analytics beacon or the GA4 loader (`gtag/js`, Consent Mode v2 defaults denied, `assets/consent.js`).

## Launch commands

From the repo root, after `GA4_ID` is set:

```bash
python3 _build/build.py --launch
python3 _build/check.py --launch
python3 _build/legal_gate.py check
```

`--launch` is the only flag that removes `noindex`. It keeps root-relative paths and `CNAME`, and it adds all of the following on every page:

- Cloudflare Web Analytics beacon
- Google Analytics 4 with Consent Mode v2 defaults denied (`ad_storage`, `ad_user_data`, `ad_personalization`, `analytics_storage`)
- `assets/consent.js`, which loads `gtag` only after the visitor accepts
- a footer link labeled Cookie settings

The same build rewrites these files and does not drop them:

- `CNAME` (`whichflbeach.com`)
- `sitemap.xml` (every URL has `lastmod`)
- `robots.txt` (Googlebot, Bingbot, and the listed AI crawlers are allowed)
- `llms.txt`
- IndexNow key file `af525312177496563755bb04b53948e9.txt`

After those three commands exit 0 and the domain resolves, ping IndexNow:

```bash
bash indexnow.sh
```

## Preview

The default build stays noindex and omits both analytics snippets. Use it until launch day:

```bash
python3 _build/build.py
python3 _build/check.py
python3 _build/legal_gate.py check
```
