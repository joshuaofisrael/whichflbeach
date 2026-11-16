# Which FL Beach (whichflbeach.com)

A static guide that helps people pick a Florida beach. Each beach page covers parking, shelling, where to check red tide, beach wheelchairs and mats, dogs, lifeguards, restrooms, and who the beach suits.

GitHub Pages, branch `main`, folder `/`. The `CNAME` file is `whichflbeach.com`.

## Build

```
python3 _build/build.py            # preview: root paths, CNAME, noindex on every page
python3 _build/build.py --launch   # live site: same paths and CNAME, indexable, Cloudflare beacon, GA4
python3 _build/check.py [--launch]
python3 _build/legal_gate.py check
```

`--launch` is the single flag that removes `noindex`. Leave it off until the domain resolves. Set `GA4_ID` in `_build/build.py` before the launch check. Exact commands: [LAUNCH-NOTES.md](LAUNCH-NOTES.md).

Facts come from county and city park pages, Florida State Parks, FWC, and the Florida Department of Health. The build does not invent a fee, an hour, or a fill time the source page did not state, and it does not post current water conditions.

Contact: joshuaofisrael@gmail.com
