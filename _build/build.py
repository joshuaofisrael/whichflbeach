#!/usr/bin/env python3
"""Which FL Beach static site builder. Run from the repo root.

  python3 _build/build.py            # preview: root paths, CNAME, noindex on every page
  python3 _build/build.py --launch   # live domain: same paths and CNAME, indexable, CF beacon, GA4
  python3 _build/check.py --launch
  python3 _build/legal_gate.py check

The single launch flag is `--launch`. Until you pass it, every page stays noindex.
Canonicals, sitemap and JSON-LD always use https://whichflbeach.com/.
Set GA4_ID before launch. See LAUNCH-NOTES.md.
"""
import os, sys, json, html, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from beaches import BEACHES, REGIONS, COUNTIES
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SINGLE FLAG. Leave this False until whichflbeach.com resolves and you are ready to index.
LAUNCH = "--launch" in sys.argv
BASE = "https://whichflbeach.com/"
BRAND = "Which FL Beach"
PUBLISHED = "2026-11-16"          # first publication of this page set. Do not replace with a rebuild clock.
PUBLISHED_H = "16 Nov 2026"
INDEXNOW_KEY = "af525312177496563755bb04b53948e9"
CF_BEACON_TOKEN = "eac63f2b5dbc4539a2d95249baab6472"
# Public GA4 measurement ID. Owner pastes G-XXXXXXXXXX. Empty until then. Not a secret.
GA4_ID = "G-F8FHL1H2HM"
CONTACT = "joshuaofisrael@gmail.com"
E = html.escape
PAGES = []  # (path, lastmod) for the sitemap. 404 and other noindex utility pages stay out.

FWC_FAQ = ("FWC: Red Tide FAQ", "https://myfwc.com/research/redtide/faq/")
FWC_STATUS = ("FWC: Red Tide Current Status", "https://myfwc.com/research/redtide/statewide/")
FWC_MAP = ("FWC: Red Tide daily sample map", "https://gis.myfwc.com/redtidecurrentstatus/")
FWC_TOOLS = ("FWC: Tools for tracking red tides", "https://myfwc.com/research/redtide/tools/")
MOTE = ("Mote Marine Laboratory: Beach Conditions Reporting System (linked from FWC)", "https://visitbeaches.org/")
FDOH = ("Florida Department of Health: beach water quality", "https://www.floridahealth.gov/community-environmental-public-health/environmental-public-health/water-quality/beach-water-quality/")
FDOH_MAP = ("Florida Department of Health: Healthy Beaches map", "https://fdoh.maps.arcgis.com/apps/instant/nearby/index.html?appid=7106a20597de4bff98cc5ebc7f932047")
FWC_SHELLS = ("FWC: recreational sea shell collecting", "https://myfwc.com/fishing/saltwater/recreational/sea-shells/")
LIVE = [FWC_STATUS, FWC_MAP, FWC_TOOLS, MOTE, FDOH, FDOH_MAP]

def url(path):
    return BASE + path.lstrip("/")

def write(path, content):
    fp = os.path.join(ROOT, path.lstrip("/"))
    if path.endswith("/"):
        fp = os.path.join(fp, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)

def clip(d, n=155):
    d = re.sub(r"\s+", " ", d).strip()
    if len(d) <= n:
        return d
    c = d[:n]
    i = c.rfind(". ")
    if i > 80:
        return c[:i + 1]
    j = c.rfind(" ")
    return (c[:j] if j > 80 else c).rstrip(",;:") + "."

LOGO = '<svg width="34" height="34" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><rect width="64" height="64" rx="14" fill="#0b3954"/><circle cx="44" cy="18" r="8" fill="#f0b429"/><path d="M8 40c6-8 12-8 18 0s12 8 18 0 12-8 18 0v16H8z" fill="#0c7c86"/><path d="M8 48c6-6 12-6 18 0s12 6 18 0 12-6 18 0v8H8z" fill="#8fd0c8"/></svg>'
NAV = [("/", "Home"), ("/beaches/", "Beaches"), ("/regions/", "Regions"), ("/guides/best-shelling/", "Shelling"), ("/guides/how-to-pick-a-florida-beach/", "How to pick")]

def analytics_tags():
    # Preview stays free of the beacon and of Google. Launch adds both.
    # gtag.js is not requested until consent.js calls loadGA4 after Accept.
    if not LAUNCH:
        return "<!-- cf-beacon: added by the launch flag -->"
    ga = """<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'analytics_storage': 'denied',
  'functionality_storage': 'denied',
  'personalization_storage': 'denied',
  'security_storage': 'granted',
  'wait_for_update': 500
});
gtag('set', 'ads_data_redaction', true);
gtag('set', 'url_passthrough', true);
window.GA4_ID = %s;
window.loadGA4 = function(){
  if(!window.GA4_ID || window.__ga4Loaded) return;
  window.__ga4Loaded = true;
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + window.GA4_ID;
  document.head.appendChild(s);
  gtag('js', new Date());
  gtag('consent', 'update', {
    'analytics_storage': 'granted',
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied'
  });
  gtag('config', window.GA4_ID);
};
window.setGA4Consent = function(granted){
  if(granted){ window.loadGA4(); return; }
  if(window.__ga4Loaded){
    gtag('consent', 'update', {
      'analytics_storage': 'denied',
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied'
    });
  }
};
</script>
<script src="/assets/consent.js?v=1" defer></script>
""" % json.dumps(GA4_ID)
    beacon = ("<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"%s\"}'></script><!-- End Cloudflare Web Analytics -->" % CF_BEACON_TOKEN)
    return ga + beacon

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def human_date(iso):
    y, m, d = iso.split("-")
    return "%d %s %s" % (int(d), MONTHS[int(m)], y)

# Pages whose content changed on this run only. Everything else keeps its original
# PUBLISHED lastmod untouched -- no manufactured freshness across the rest of the site.
TODAY = "2026-11-19"
TODAY_H = "19 Nov 2026"
# Explicit lastmod (and first-publish when the second value is set) for hubs that changed
# after the site-wide PUBLISHED date. Unlisted hubs keep PUBLISHED.
HUB_DATES = {
    # First published 18 Nov
    "/counties/nassau/": ("2026-11-18", "2026-11-18"),
    # Material hub edits 18 Nov (new Atlantic beaches)
    "/counties/duval/": (None, "2026-11-18"),
    "/regions/atlantic/": (None, "2026-11-18"),
    "/guides/best-shelling/": (None, "2026-11-18"),
    # Material edits 19 Nov (dogs refresh, AdSense/privacy, Siesta and Fort De Soto fact updates)
    "/beaches/": (None, "2026-11-19"),
    "/regions/": (None, "2026-11-19"),
    "/regions/gulf/": (None, "2026-11-19"),
    "/counties/pinellas/": (None, "2026-11-19"),
    "/counties/sarasota/": (None, "2026-11-19"),
    "/about/": (None, "2026-11-19"),
    "/": (None, "2026-11-19"),
    "/guides/best-for-dogs/": (None, "2026-11-19"),
    "/guides/best-for-accessibility/": (None, "2026-11-19"),
    "/guides/best-for-kids/": (None, "2026-11-19"),
    "/guides/best-for-sunsets/": (None, "2026-11-19"),
    "/privacy/": (None, "2026-11-19"),
    "/ad-disclosure/": (None, "2026-11-19"),
    "/image-policy/": (None, "2026-11-19"),
}
ADSENSE_PUB = "ca-pub-5681559774142917"

def hub_dates(path):
    return HUB_DATES.get(path, (None, None))

# AdSense low-value-content fix (20 Nov 2026): paths listed in _build/thin-noindex.txt
# get noindex,follow and stay out of the sitemap until they have real unique substance.
_THIN_NOINDEX = set()
try:
    import os as _os
    with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "thin-noindex.txt"), encoding="utf-8") as _fh:
        _THIN_NOINDEX = {l.strip().strip("/") for l in _fh if l.strip() and not l.startswith("#")}
except FileNotFoundError:
    pass


def _is_thin(path):
    return str(path).strip("/") in _THIN_NOINDEX


def page(path, title, desc, body, jsonld=None, crumbs=None, noindex=False, legal=False, og_type="website", lastmod=None):
    if _is_thin(path):
        noindex = True
    if len(title) >= 60:
        raise SystemExit("title too long (%d): %s" % (len(title), title))
    desc = clip(desc)
    canon = url(path)
    # 404 and other hard noindex pages stay out of the sitemap even after launch.
    if not noindex:
        PAGES.append((path, lastmod or PUBLISHED))
    robots = "noindex, follow" if (noindex or not LAUNCH) else "index, follow, max-image-preview:large"
    ld = []
    if path == "/":
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": BASE,
                   "description": "A guide to picking a Florida beach from county and state park facts.",
                   "publisher": {"@type": "Organization", "name": BRAND, "url": BASE, "logo": url("/logo.png")}})
        ld.append({"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": BASE,
                   "logo": url("/logo.png")})
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)} for i, (p, n) in enumerate(crumbs)]})
    if jsonld:
        ld += jsonld if isinstance(jsonld, list) else [jsonld]
    ldh = "".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)
    nav = "".join('<a href="%s"%s>%s</a>' % (p, ' aria-current="page"' if p == path else "", n) for p, n in NAV)
    bc = ""
    if crumbs:
        items = []
        for i, (p, n) in enumerate(crumbs):
            items.append('<li><a href="%s">%s</a></li>' % (p, E(n)) if i < len(crumbs) - 1 else '<li aria-current="page">%s</li>' % E(n))
        bc = '<nav class="crumbs" aria-label="Breadcrumb"><ol>%s</ol></nav>' % "".join(items)
    tags = analytics_tags()
    legal_line = '<p class="legal-line">© 2026 Joshua Israel Ventures LLC. All rights reserved. Which FL Beach is a trade name of Joshua Israel Ventures LLC, a Florida limited liability company.</p>' if legal else ""
    cookie = ' | <a href="#cookie-settings" id="cookie-settings">Cookie settings</a>' if LAUNCH else ""
    adsense = ""
    if LAUNCH:
        adsense = (
            '<meta name="google-adsense-account" content="%s">'
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=%s" crossorigin="anonymous"></script>'
        ) % (ADSENSE_PUB, ADSENSE_PUB)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
{adsense}
<meta property="og:type" content="{E(og_type)}"><meta property="og:site_name" content="{BRAND}"><meta property="og:locale" content="en_US"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{url('/og.png')}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{url('/og.png')}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/style.css?v=3">{ldh}
</head><body><a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap"><a class="brand" href="/">{LOGO}<span>{BRAND}</span></a><nav class="main" aria-label="Main">{nav}</nav></div></header>
<main id="main" class="wrap">{bc}{body}</main>
<footer class="site"><div class="wrap"><p class="fbrand"><strong>{BRAND}</strong> helps you pick a Florida beach from facts published by county and city parks, Florida State Parks, the Florida Fish and Wildlife Conservation Commission, and the Florida Department of Health. We do not post live water conditions. Read the managing agency page before you go.</p>
<p class="flinks"><a href="/about/">About</a> | <a href="/contact/">Contact</a> | <a href="/privacy/">Privacy</a> | <a href="/terms/">Terms of use</a> | <a href="/disclaimer/">Disclaimer</a> | <a href="/copyright/">Copyright and DMCA</a> | <a href="/ad-disclosure/">Advertising disclosure</a> | <a href="/image-policy/">Image policy</a> | <a href="/methodology/">Sources and methods</a>{cookie}</p>
{legal_line}</div></footer>
<script src="/assets/site.js?v=1" defer></script>{tags}
</body></html>'''

def link(pair):
    return '<a href="%s" rel="nofollow noopener">%s</a>' % (pair[1], E(pair[0]))

def src_list(pairs):
    return "<ul>" + "".join("<li>%s</li>" % link(p) for p in pairs) + "</ul>"

def byline(date_h=None):
    return '<p class="byline">By %s · Last verified %s</p>' % (BRAND, date_h or PUBLISHED_H)

def article_ld(headline, path, about=None, published=None, modified=None):
    data = {"@context": "https://schema.org", "@type": "Article", "headline": headline,
            "datePublished": published or PUBLISHED, "dateModified": modified or published or PUBLISHED,
            "author": {"@type": "Organization", "name": BRAND, "url": BASE},
            "publisher": {"@type": "Organization", "name": BRAND, "url": BASE, "logo": {"@type": "ImageObject", "url": url("/logo.png")}},
            "image": url("/og.png"), "mainEntityOfPage": url(path)}
    if about:
        data["about"] = about
    return data

def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def faq_html(faqs):
    return '<section class="faq" aria-labelledby="faq-h"><h2 id="faq-h">Questions people ask</h2>' + "".join(
        "<details><summary>%s</summary><p>%s</p></details>" % (E(q), E(a)) for q, a in faqs) + "</section>"

def next_reads(items, heading="Related reads"):
    """items: list of (href, title, blurb). Thumbnails use the site graphic until a news photo exists for that page."""
    lis = []
    for href, title, blurb in items:
        lis.append(
            '<li class="nextread">'
            '<a class="nextread-thumb" href="/image-policy/">'
            '<img src="/og.png" alt="" width="320" height="168" loading="lazy">'
            '</a>'
            '<div class="nextread-body">'
            '<a href="%s">%s</a>'
            '<p>%s</p>'
            '</div></li>' % (href, E(title), E(blurb))
        )
    return (
        '<section class="nextreads" aria-labelledby="next-h">'
        '<h2 id="next-h">%s</h2>'
        '<ul class="nextread-list">%s</ul>'
        '<p class="note">Thumbnails use the site social graphic until each guide has its own news photo. '
        '<a href="/image-policy/">Image policy</a>.</p></section>'
    ) % (E(heading), "".join(lis))

def compare_box(heading, lines_html):
    return (
        '<aside class="compare" aria-labelledby="compare-h">'
        '<h2 id="compare-h">%s</h2>%s</aside>'
    ) % (E(heading), lines_html)

def bpath(b):
    return "/beaches/%s/" % b["slug"]

def by_slug(slug):
    return next(b for b in BEACHES if b["slug"] == slug)

def yn(v, yes="Yes, on the managing agency page", no="No, on the managing agency page", other="Not stated on the page we checked"):
    return {"yes": yes, "no": no, "seasonal": "Seasonal, on the managing agency page", "service": "Service animals only, where the page says so",
            "designated": "Only in a designated area the page describes", "unstated": other}.get(v, other)

def fact_table(b):
    rows = [
        ("Managed by", b["manager"]),
        ("Place", b["place"] + ", " + b["county_name"]),
        ("Open water", {"gulf": "Gulf", "atlantic": "Atlantic", "bay": "Bay or Intracoastal", "both": "Gulf and Atlantic"}[b["water"]]),
        ("Parking", b["parking"]),
        ("When the lot fills", b["fills"]),
        ("Shelling", b["shell_note"]),
        ("Dogs", b["dogs_note"]),
        ("Lifeguards", b["guard_note"]),
        ("Restrooms", b["rest_note"]),
        ("Beach wheelchair", b["chair_note"]),
        ("Access mat", b["mat_note"]),
    ]
    return '<div class="tablewrap"><table class="stats"><tbody>' + "".join(
        '<tr><th scope="row">%s</th><td>%s</td></tr>' % (E(k), E(v)) for k, v in rows) + "</tbody></table></div>"

def tags(b):
    t = []
    if b["dogs"] in ("yes", "designated"):
        t.append("Dogs")
    if b["guard"] in ("yes", "seasonal"):
        t.append("Lifeguards")
    if b["chair"] == "yes" or b["mat"] == "yes":
        t.append("Access")
    if b["shell"] == "yes":
        t.append("Shells")
    if b["kids"]:
        t.append("Kids")
    if b["water"] == "gulf":
        t.append("Gulf sunset direction")
    return '<p class="tags">' + "".join('<span class="tag">%s</span>' % E(x) for x in t) + "</p>" if t else ""

def red_blurb(b):
    coast = {"gulf": "This beach is on the Gulf, the coast where FWC says Florida red tides were documented in the 1840s and where blooms most often form in late summer and early fall.",
             "atlantic": "This beach is on the Atlantic. FWC says some Gulf blooms have been carried by the Gulf Stream into the Atlantic, as far as Delaware, so an east coast beach is not automatically clear.",
             "both": "This shore sits between the Gulf and the Atlantic. FWC reports the two coasts separately, so match the sample to this county rather than to a statewide headline.",
             "bay": "This is a bay or Intracoastal shore. FWC says Florida red tide can enter bays and estuaries, and that Karenia brevis does not persist in freshwater."}[b["water"]]
    return ("<h2>Red tide and water quality</h2><p>%s We do not post this week's conditions. FWC updates a daily sample map and a status report, and it points readers to the Mote beach conditions reports. The Florida Department of Health posts bacteria results and advisories on its Healthy Beaches map. Read those before you swim, and read the longer background on our <a href=\"/guides/red-tide/\">red tide guide</a>.</p>" % E(coast))

def related(b):
    bits = ['<a href="/beaches/">All beaches</a>',
            '<a href="/counties/%s/">%s beaches</a>' % (b["county"], E(b["county_name"])),
            '<a href="/regions/%s/">%s</a>' % (b["region"], E(REGIONS[b["region"]]["name"]))]
    for s in b["nearby"]:
        n = by_slug(s)
        bits.append('<a href="%s">%s</a>' % (bpath(n), E(n["name"])))
    if b["shell"] == "yes":
        bits.append('<a href="/guides/best-shelling/">Beaches where shelling is described</a>')
    if b["dogs"] in ("yes", "designated"):
        bits.append('<a href="/guides/best-for-dogs/">Beaches that allow dogs</a>')
    if b["kids"]:
        bits.append('<a href="/guides/best-for-kids/">Beaches that suit kids</a>')
    if b["chair"] == "yes" or b["mat"] == "yes":
        bits.append('<a href="/guides/best-for-accessibility/">Beaches with a wheelchair or mat</a>')
    if b["water"] == "gulf" or b.get("sunset"):
        bits.append('<a href="/guides/best-for-sunsets/">Sunset direction</a>')
    bits.append('<a href="/guides/how-to-pick-a-florida-beach/">How to pick a Florida beach</a>')
    return "<p>" + " · ".join(bits) + "</p>"

def beach_faqs(b):
    if b.get("faqs"):
        return b["faqs"]
    return [
        ("Can I bring a dog to %s?" % b["name"], b["dogs_note"]),
        ("Are there lifeguards at %s?" % b["name"], b["guard_note"] + " A lifeguard schedule can change. Read the agency page the week you go."),
        ("Is there a beach wheelchair or an access mat at %s?" % b["name"], b["chair_note"] + " " + b["mat_note"]),
        ("What does the agency say about parking at %s?" % b["name"], b["parking"] + " " + b["fills"]),
    ]

def beach_page(b):
    path = bpath(b)
    title = "%s | %s" % (b["short"], BRAND)
    desc = b["angle"]
    faqs = beach_faqs(b)
    paras = "".join("<p>%s</p>" % E(p) for p in [b["angle"]] + b.get("extra", []))
    # Most beach records share the site-wide PUBLISHED/PUBLISHED_H fact-check date.
    # A record only sets "published" when it was fact-checked on a later date; "modified"
    # covers a later edit (e.g. a new cross-link) without claiming the facts were rechecked.
    pub = b.get("published", PUBLISHED)
    mod = b.get("modified", pub)
    verified_h = human_date(pub) if b.get("published") else PUBLISHED_H
    body = f'''<article class="prose wide"><h1>{E(b["name"])}</h1>{byline(verified_h)}
<p class="sub">{E(b["place"])} · {E(b["county_name"])} · {E(b["manager"])}</p>
{tags(b)}
<div class="answer"><p><strong>Quick read.</strong> {E(b["who"])}</p></div>
{paras}
<h2>What the managing agency publishes</h2>
{fact_table(b)}
<p class="note">Fees and hours change. If a dollar amount or a clock time is not in the table, the page we checked did not state it. Confirm on the linked agency page before you go.</p>
{red_blurb(b)}
<h2>Who it suits</h2>
<p>{E(b["who"])}</p>
<p>Our read follows the facts above. It is a planning note, not a rule of the park.</p>
{faq_html(faqs)}
<section class="sources" aria-labelledby="src-h"><h2 id="src-h">Sources</h2>
{src_list(b["sources"] + [FWC_FAQ, FWC_STATUS, FWC_SHELLS, FDOH])}
<p class="note">Retrieved {verified_h}. Which FL Beach is not the park manager and is not affiliated with the agencies linked above. See <a href="/methodology/">how we check a page</a>.</p></section>
{related(b)}</article>'''
    about = {"@type": ["Beach", "TouristAttraction"], "name": b["name"], "url": url(path),
             "description": clip(b["angle"]), "publicAccess": True,
             "address": {"@type": "PostalAddress", "addressLocality": b["place"], "addressRegion": "FL", "addressCountry": "US"},
             "containedInPlace": {"@type": "AdministrativeArea", "name": b["county_name"]}}
    if b.get("free_access"):
        about["isAccessibleForFree"] = True
    ld = [article_ld(b["name"], path, about, published=pub, modified=mod), faq_ld(faqs),
          {"@context": "https://schema.org", "@type": ["Beach", "TouristAttraction"], "name": b["name"],
           "url": url(path), "description": clip(b["angle"]), "publicAccess": True,
           "address": about["address"], "containedInPlace": about["containedInPlace"]}]
    if b.get("free_access"):
        ld[2]["isAccessibleForFree"] = True
    crumbs = [("/", "Home"), ("/beaches/", "Beaches"), ("/regions/%s/" % b["region"], REGIONS[b["region"]]["name"]),
              ("/counties/%s/" % b["county"], b["county_name"]), (path, b["name"])]
    write(path, page(path, title, desc, body, ld, crumbs, og_type="article", lastmod=mod))

def card(b):
    return '<li class="card"><h2><a href="%s">%s</a></h2><p>%s</p></li>' % (bpath(b), E(b["name"]), E(b["angle"]))

def beaches_index():
    faqs = [
        ("How do I choose a beach from this list?", "Use the homepage picker to filter by region, dogs, lifeguards, a wheelchair or mat, shelling, or kids. Or open a region, then a county, then the beach page."),
        ("Where do the facts on each beach come from?", "Each beach page cites a county, city, or Florida State Parks page. Live red tide and bacteria results stay on FWC and the Florida Department of Health."),
    ]
    body = '<h1>Florida beach guides</h1><p class="answer">%d beaches, each tied to a county, city, or Florida State Parks page. Filter them on the <a href="/">homepage picker</a>, or start with a <a href="/regions/">region</a>.</p><ul class="cards">%s</ul>%s' % (
        len(BEACHES), "".join(card(b) for b in BEACHES), faq_html(faqs))
    pub, mod = hub_dates("/beaches/")
    write("/beaches/", page("/beaches/", "Florida Beach Guides | %s" % BRAND,
                            "Guides to Florida beaches with parking, shelling, dogs, lifeguards, restrooms and access, cited to the managing agency.",
                            body, [article_ld("Florida beach guides", "/beaches/", published=pub, modified=mod), faq_ld(faqs)],
                            [("/", "Home"), ("/beaches/", "Beaches")], og_type="article", lastmod=mod))

def region_pages():
    cards = []
    for key, R in REGIONS.items():
        bs = [b for b in BEACHES if b["region"] == key]
        counties = sorted({b["county"]: b["county_name"] for b in bs}.items(), key=lambda kv: kv[1])
        county_html = "<h2>Counties</h2><ul class=\"cols\">" + "".join(
            '<li><a href="/counties/%s/">%s</a></li>' % (k, E(n)) for k, n in counties) + "</ul>"
        path = "/regions/%s/" % key
        faqs = [("How should I choose a beach in this region?", R["intro"] + " Open a county, then a beach page, for the parking, dog, lifeguard and access facts, then confirm them on the agency link.")]
        body = '<article class="prose wide"><h1>%s beaches</h1>%s<p class="answer">%s</p>%s<h2>Beaches</h2><ul class="cards">%s</ul><p><a href="/regions/">All regions</a> · <a href="/beaches/">All beaches</a> · <a href="/guides/how-to-pick-a-florida-beach/">How to pick</a></p>%s</article>' % (
            E(R["name"]), byline(), E(R["intro"]), county_html, "".join(card(b) for b in bs), faq_html(faqs))
        pub, mod = hub_dates(path)
        ld = [article_ld(R["name"] + " beaches", path, published=pub, modified=mod), faq_ld(faqs)]
        write(path, page(path, "%s Beaches | %s" % (R["name"], BRAND), R["intro"], body, ld,
                         [("/", "Home"), ("/regions/", "Regions"), (path, R["name"])], og_type="article", lastmod=mod))
        cards.append('<li class="card"><h2><a href="%s">%s</a></h2><p>%d beaches. %s</p></li>' % (path, E(R["name"]), len(bs), E(R["blurb"])))
    hub_faqs = [
        ("Which Florida coast should I open?", "Open the Gulf Coast, the Atlantic Coast, the Panhandle, or the Florida Keys. Each region page lists its counties and beaches."),
        ("Is there one best beach in Florida?", "No. Choose the constraint that would ruin the day, then open that beach page and the managing agency link."),
    ]
    body = '<h1>Florida beaches by region</h1><p class="answer">Four coasts, one question: which beach fits the day you actually have.</p><ul class="cards">%s</ul><p>Or use the <a href="/">homepage picker</a> and the <a href="/beaches/">full beach list</a>.</p>%s' % (
        "".join(cards), faq_html(hub_faqs))
    pub, mod = hub_dates("/regions/")
    write("/regions/", page("/regions/", "Florida Beaches by Region | %s" % BRAND,
                            "Gulf Coast, Atlantic Coast, Panhandle and Florida Keys beach guides, with county hubs inside each region.",
                            body, [article_ld("Florida beaches by region", "/regions/", published=pub, modified=mod), faq_ld(hub_faqs)],
                            [("/", "Home"), ("/regions/", "Regions")], og_type="article", lastmod=mod))

def county_pages():
    for key, name in sorted(COUNTIES.items(), key=lambda kv: kv[1]):
        bs = [b for b in BEACHES if b["county"] == key]
        if not bs:
            continue
        region = bs[0]["region"]
        intro = "%s has %d beaches in this guide. Each page uses that county's park page or the Florida State Parks page for the park, plus FWC and the Florida Department of Health for shells, red tide and bacteria." % (name, len(bs))
        path = "/counties/%s/" % key
        faqs = [("Where do the %s facts come from?" % name, "From the county or city park page, or the Florida State Parks experiences page, linked on each beach. Live red tide and bacteria results stay on FWC and the Florida Department of Health.")]
        body = '<article class="prose wide"><h1>%s beaches</h1>%s<p class="answer">%s</p><ul class="cards">%s</ul>%s%s</article>' % (
            E(name), byline(), E(intro), "".join(card(b) for b in bs), pick_links(bs, region), faq_html(faqs))
        pub, mod = hub_dates(path)
        write(path, page(path, "%s Beaches | %s" % (name, BRAND), clip(intro), body,
                         [article_ld(name + " beaches", path, published=pub, modified=mod), faq_ld(faqs)],
                         [("/", "Home"), ("/regions/", "Regions"), ("/regions/%s/" % region, REGIONS[region]["name"]), (path, name)],
                         og_type="article", lastmod=mod))

def pick_links(bs, region):
    bits = [
        '<a href="/regions/%s/">%s</a>' % (region, E(REGIONS[region]["name"])),
        '<a href="/beaches/">All beaches</a>',
        '<a href="/guides/how-to-pick-a-florida-beach/">How to pick</a>',
        '<a href="/guides/red-tide/">Red tide</a>',
    ]
    if any(b["shell"] == "yes" for b in bs):
        bits.append('<a href="/guides/best-shelling/">Beaches where shelling is described</a>')
    if any(b["dogs"] in ("yes", "designated") for b in bs):
        bits.append('<a href="/guides/best-for-dogs/">Beaches that allow dogs</a>')
    if any(b["kids"] for b in bs):
        bits.append('<a href="/guides/best-for-kids/">Beaches that suit kids</a>')
    if any(b["chair"] == "yes" or b["mat"] == "yes" for b in bs):
        bits.append('<a href="/guides/best-for-accessibility/">Beaches with a wheelchair or mat</a>')
    if any(b["water"] == "gulf" or b.get("sunset") for b in bs):
        bits.append('<a href="/guides/best-for-sunsets/">Sunset direction</a>')
    return "<p>%s</p>" % " · ".join(bits)

def guide(path, title, h1, desc, inner, faqs, sources, verified_h=None, published=None, modified=None):
    more = ['<a href="/">Homepage picker</a>', '<a href="/beaches/">All beaches</a>', '<a href="/regions/">Regions</a>']
    if path != "/guides/how-to-pick-a-florida-beach/":
        more.append('<a href="/guides/how-to-pick-a-florida-beach/">How to pick</a>')
    inner += "<p>%s</p>" % " · ".join(more)
    v_h = verified_h or PUBLISHED_H
    hub_pub, hub_mod = hub_dates(path)
    pub = published if published is not None else hub_pub
    mod = modified if modified is not None else hub_mod
    body = '<article class="prose"><h1>%s</h1>%s%s%s<section class="sources"><h2>Sources</h2>%s<p class="note">Retrieved %s.</p></section></article>' % (
        E(h1), byline(v_h), inner, faq_html(faqs), src_list(sources), v_h)
    write(path, page(path, title, desc, body, [article_ld(h1, path, published=pub, modified=mod), faq_ld(faqs)],
                      [("/", "Home"), (path, h1)], og_type="article", lastmod=mod))

def guides():
    shell = [b for b in BEACHES if b["shell"] == "yes"]
    dogs = [b for b in BEACHES if b["dogs"] in ("yes", "designated")]
    kids = [b for b in BEACHES if b["kids"]]
    access = [b for b in BEACHES if b["chair"] == "yes" or b["mat"] == "yes"]
    sunset_named = [b for b in BEACHES if b.get("sunset")]
    gulf = [b for b in BEACHES if b["water"] == "gulf"]

    def lst(bs):
        return "<ul>" + "".join('<li><a href="%s">%s</a>. %s</li>' % (bpath(b), E(b["name"]), E(b["angle"])) for b in bs) + "</ul>"

    guide("/guides/how-to-pick-a-florida-beach/", "How to Pick a Florida Beach | %s" % BRAND, "How to pick a Florida beach",
          "Pick a Florida beach by parking, dogs, lifeguards, access and shelling, then check FWC and the health department the day you go.",
          '''<div class="answer"><p><strong>Short version.</strong> Choose the constraint that would ruin the day, then open that beach's page and the agency link. We do not rank a single winner.</p></div>
<h2>1. Parking and arrival</h2><p>Read whether the lot is free, metered, or covered by a park entrance fee, and whether the agency says the lot fills. If the page does not give a clock time, we do not invent one. Have a second beach in the same county.</p>
<h2>2. Dogs, kids, and step free access</h2><p>Dog rules change at the county line. A beach wheelchair or an access mat is listed only when the park page says so. Lifeguard coverage is listed only when the page says who is on duty, and for which hours.</p>
<h2>3. Shells</h2><p>Empty shells and live animals are different things. Read the <a href="/guides/best-shelling/">shelling guide</a> and the FWC page before you pocket anything.</p>
<h2>4. The day you go</h2><p>Red tide and bacteria are not facts we freeze on a page. Use the <a href="/guides/red-tide/">red tide guide</a> and the health department map that morning.</p>
<h2>Start here</h2><ul class="cols"><li><a href="/">Homepage picker</a></li><li><a href="/regions/gulf/">Gulf Coast</a></li><li><a href="/regions/atlantic/">Atlantic Coast</a></li><li><a href="/regions/panhandle/">Panhandle</a></li><li><a href="/regions/keys/">Florida Keys</a></li><li><a href="/counties/sarasota/">Sarasota County</a></li></ul>''',
          [("What is the best Florida beach?", "There is no single best beach. The useful question is which published constraint matters: a guarded swim, a dog, a beach wheelchair, shells, or a lot that the agency says fills."),
           ("Do you post today's red tide?", "No. FWC posts the current status and a daily sample map. We link those pages and explain how to read them.")],
          [FWC_FAQ, FDOH, FWC_SHELLS])

    guide("/guides/red-tide/", "Red Tide: History and Where to Check | %s" % BRAND, "Red tide history and where to check today",
          "Florida red tide background from FWC, plus the live status map, beach conditions reports, and the health department bacteria map.",
          '''<div class="answer"><p><strong>Check today, do not trust a saved page.</strong> Open the FWC current status page and the daily sample map. Then open the Florida Department of Health Healthy Beaches map for bacteria. This guide explains the background. It does not state this week's cell counts.</p></div>
<h2>What FWC says it is</h2><p>FWC describes red tide as a higher than normal concentration of a microscopic alga. In Florida, the species behind most red tides is Karenia brevis. At high concentrations the water can turn red or brown, and it can also stay its normal color.</p>
<h2>It is not new, and it is not only one coast</h2><p>FWC says red tides were documented along Florida's Gulf coast in the 1840s, and that fish kills near Tampa Bay appear in the records of Spanish explorers. Blooms most often form in late summer and early fall and can persist through winter into spring. A bloom can last a few weeks or longer than a year, and it can fade and return. FWC says Karenia brevis is found almost exclusively in the Gulf, from Mexico to Florida, and that some blooms have been carried by the Gulf Stream into the Atlantic as far as Delaware. The organism can show up in bays and estuaries. It does not persist in freshwater.</p>
<h2>What it can do</h2><p>FWC says Karenia brevis produces brevetoxins that can kill fish, and that wave action can put toxins in the air and irritate breathing. People with asthma or other chronic respiratory disease can become seriously ill. FWC says not to swim in or around red tide because it can irritate skin and eyes. That is the agency's warning, not a diagnosis. For a suspected exposure, FWC points people to a doctor or Florida Poison Information. Shellfish from a restaurant or market are monitored. Recreational clams, oysters and mussels from a closed area are not a safe harvest. Cooking does not remove the toxin. Pets can be affected. FWC says not to let them eat dead fish or foam, and to rinse them if they swim in a bloom.</p>
<h2>Where to look the day you go</h2><ul>
<li>FWC current status, updated on a schedule the status page explains, plus a phone recording the same page describes.</li>
<li>The daily sample map of the last eight days, which FWC says is updated daily.</li>
<li>Beach conditions reports from Mote Marine Laboratory, which FWC lists as a complement to its own reports.</li>
<li>The Florida Department of Health beach water map for enterococci, which is a different problem from red tide. The department describes an advisory when a sample over 70 colony forming units per 100 milliliters is confirmed by a resample.</li>
</ul>
<p>Gulf beaches in this guide sit on the coast with the long written record. Atlantic and Keys pages explain why a clear headline for the other coast is not enough. County pages sometimes add their own red tide link. Use that too.</p>''',
          [("Is the red tide bad at my beach today?", "We do not answer that on this site. Open the FWC status page and the daily sample map, then the health department map."),
           ("When does red tide usually happen?", "FWC says blooms most often form in late summer and early fall and can last into spring. They also occur outside that window."),
           ("Does red tide reach the Atlantic side?", "FWC says some blooms have been carried by the Gulf Stream into the Atlantic, as far as Delaware.")],
          [FWC_FAQ, FWC_STATUS, FWC_MAP, FWC_TOOLS, MOTE, FDOH, FDOH_MAP])

    guide("/guides/best-shelling/", "Best Florida Beaches for Shelling | %s" % BRAND, "Beaches where the park page talks about shelling",
          "Florida beaches whose county or state park page mentions shells or beachcombing, plus the FWC rules on empty and live shells.",
          '''<div class="answer"><p><strong>How this list is made.</strong> A beach is here only when the managing agency page mentions shells, shelling, or beachcombing. Famous reputations that the park page does not state are left off.</p></div>
<p>FWC says you may collect a sea shell depending on whether anything is living in it, what that animal is, and where you are. A recreational saltwater fishing license is required to take a shell that contains a living organism, even from shore. Live oysters and live hard clams follow their own rules and may be taken only from approved harvest areas that are open. In Lee County, FWC says you may not harvest or possess a shell containing a live organism, with stated exceptions for oysters, hard clams, sunray venus clams and coquinas. In Manatee County the limit is two live shells of any single species per day, with the same exceptions, and the count includes sand dollars and starfish. Bahama starfish harvest is prohibited. Live queen conch may not be possessed. An empty queen conch shell has conditions on the FWC page, including no hole of the kind the rule describes. Many state park pages add their own ban on taking live shells. Ask the park if the page is unclear.</p>
<h2>Beaches</h2>%s''' % lst(shell),
          [("Can I take a live shell home?", "FWC requires a recreational saltwater fishing license to take a shell with a living animal, even from shore, and some counties and parks ban or limit live shells."),
           ("Why is a famous shelling beach missing?", "If the county or state park page we checked does not mention shells, it is not on this list. Tell us if a newer page does.")],
          [FWC_SHELLS] + shell[0]["sources"][:2])

    dogs_mid = next_reads([
        ("/beaches/fort-de-soto/", "Fort De Soto Park", "Pinellas County's only beach where dogs may use a designated dog beach."),
        ("/beaches/honeymoon-island/", "Honeymoon Island State Park", "The state park pet beach on the southern tip, separate from the main swim shore."),
        ("/guides/best-for-kids/", "Beaches that suit kids", "Playgrounds, guarded swims, and coves the park page describes for children."),
    ], "Keep reading")
    dogs_end = next_reads([
        ("/guides/best-shelling/", "Beaches where shelling is described", "Empty shells and live animals follow different FWC and park rules."),
        ("/guides/how-to-pick-a-florida-beach/", "How to pick a Florida beach", "Start with the constraint that would ruin the day, then open the agency page."),
        ("/regions/gulf/", "Gulf Coast beaches", "Gulf pages from Pasco and Pinellas through Sarasota to Collier."),
        ("/counties/sarasota/", "Sarasota County beaches", "County directory beaches, including the two dog friendly sand listings we cover."),
    ], "More to check")
    dogs_compare = compare_box(
        "Check another beach",
        '<p>Open a beach page for the parking and lifeguard lines before you load the crate. Or jump to '
        '<a href="/beaches/fort-de-soto/">Fort De Soto</a>, '
        '<a href="/beaches/honeymoon-island/">Honeymoon Island</a>, '
        '<a href="/beaches/maxine-barritt/">Maxine Barritt Park</a>, or '
        '<a href="/beaches/siesta-access-1/">Siesta Key Beach Access 1</a>.</p>'
        '<p>Prefer a filter? Use the <a href="/">homepage picker</a> with Dogs set to Allowed on the sand.</p>'
    )
    guide("/guides/best-for-dogs/", "Florida Beaches That Allow Dogs on Sand | %s" % BRAND, "Which Florida beaches allow dogs on the sand?",
          "Florida beaches where the park page allows dogs on the sand or in a designated dog beach. Service animals are a separate rule.",
          '''<div class="answer"><p><strong>How this list is made.</strong> The sand allows a dog only when the managing agency says so. A dog park next to a beach is not the beach. Service animals are not pets, and the park pages describe them separately.</p></div>
<p>We rechecked the linked county and Florida State Parks pages on %s. The five beaches below still match a published dog rule for sand or a named pet beach. Most Florida State Parks pages we checked still keep pets off the beach. <a href="/beaches/honeymoon-island/">Honeymoon Island</a> remains the clear state park exception, with a pet beach at the southern tip. County rules stay local. Read the note on each beach page before you unload the dog.</p>
%s
<h2>Beaches with a published dog rule</h2>%s
<p>Sarasota County's beach directory still marks <a href="/beaches/maxine-barritt/">Maxine Barritt Park</a> and <a href="/beaches/siesta-access-1/">Siesta Key Beach Access 1</a> as dog friendly with a leash required. The same directory lists other Siesta accesses without that mark, and the Siesta Beach destination page still allows only service animals on that main beach.</p>
<p>Pinellas County still says dogs are not allowed on county beaches except the dog beach at <a href="/beaches/fort-de-soto/">Fort De Soto</a>, reached from the dog park. The county page also notes that Fort De Soto ranked among top dog friendly beaches in a 2024 list; that ranking is not our score, and the sand rule is still the designated dog beach only.</p>
<p><a href="/beaches/anclote-key/">Anclote Key Preserve</a> still bars pets on Anclote Key itself. Pets are permitted only on North Anclote Bar, on a six foot handheld leash, per the state park page.</p>
%s
%s''' % (TODAY_H, dogs_mid, lst(dogs), dogs_compare, dogs_end),
          [("Can I bring my dog to any Florida beach?", "No. Many county and state park pages prohibit pets on the sand. Use this list, then read the beach page."),
           ("Are service animals allowed?", "Park pages we cite say service animals are welcome more broadly than pets. Confirm the definition on that agency's page."),
           ("Is a dog park the same as a dog beach?", "No. A fenced dog park next to the sand is not permission to walk the open beach. Fort De Soto is the Pinellas exception with a designated dog beach reached from its dog park.")],
          [
              ("Sarasota County: beach directory", "https://www.sarasotacountyparks.com/parks-and-facilities/discover-a-park/type-of-park/beaches"),
              ("Pinellas County: Fort De Soto Park", "https://pinellas.gov/parks/fort-de-soto-park/"),
              ("Pinellas County: dog parks", "https://pinellas.gov/dog-parks/"),
              ("Florida State Parks: Honeymoon Island", "https://www.floridastateparks.org/parks-and-trails/honeymoon-island-state-park/experiences-amenities"),
              ("Florida State Parks: Anclote Key", "https://www.floridastateparks.org/parks-and-trails/anclote-key-preserve-state-park/experiences-amenities"),
              FWC_FAQ,
          ],
          verified_h=TODAY_H, published=PUBLISHED, modified=TODAY)

    guide("/guides/best-for-kids/", "Best Florida Beaches for Kids | %s" % BRAND, "Beaches that suit kids",
          "Florida beaches with a playground, a guarded swim, or a protected cove the park page describes for children.",
          '''<div class="answer"><p><strong>How this list is made.</strong> A beach is here when the agency page lists a playground, staffed lifeguards, or a protected spot it describes for children. Calm looking water is not a promise.</p></div>
<p>Lifeguard hours end. Flags change. Read the beach page for what is actually staffed, and the red tide guide the morning you go.</p>
<h2>Beaches</h2>%s''' % lst(kids),
          [("Are these beaches lifeguarded all day?", "Only if that beach page says so. Some parks staff a seasonal window. Others say lifeguards are not provided."),
           ("Is a playground the same as a safe swim?", "No. A playground is on land. Read the lifeguard line before anyone goes in.")],
          [FDOH, FWC_FAQ])

    guide("/guides/best-for-accessibility/", "Most Accessible Florida Beaches | %s" % BRAND, "Beaches with a wheelchair or an access mat",
          "Florida beaches where the park page offers a beach wheelchair, a swimming chair, or an access mat. Ask the park about availability.",
          '''<div class="answer"><p><strong>How this list is made.</strong> A beach is here when the managing agency page says it has a beach wheelchair, a swimming chair, or a mat onto the sand. We do not infer access from a paved lot alone.</p></div>
<p>Chairs are often first come, first served, and some parks ask you to reserve. The page says where to ask. We do not publish a phone number here. Use the link on the beach page.</p>
<h2>Beaches</h2>%s''' % lst(access),
          [("Is the chair free?", "When the park page says there is no charge, the beach page repeats that. If the page is silent, we do not guess."),
           ("Does a mat reach the water?", "Only if the park page describes the length or the route. Siesta Beach is one page that states a length.")],
          access[0]["sources"][:2])

    guide("/guides/best-for-sunsets/", "Best Florida Beaches for Sunsets | %s" % BRAND, "Where the sun sets over the water",
          "Gulf beaches face west, so the open water is the sunset side. A few park pages also mention sunset. We do not rank the view.",
          '''<div class="answer"><p><strong>How to use this page.</strong> On the Gulf, the open water is to the west, so a clear evening puts the sun over the water. Atlantic beaches look toward sunrise instead. This is geography, not a score. Weather and buildings still block the view.</p></div>
<h2>Park pages that mention sunset</h2>%s
<h2>Other Gulf beaches in this guide</h2><p>These also face the Gulf. Their park pages may not discuss sunset. The direction is the same.</p>%s''' % (lst(sunset_named), lst([b for b in gulf if not b.get("sunset")])),
          [("Which beach has the best sunset?", "We do not rank sunsets. Gulf beaches have the sun setting over the open water when the sky is clear. Read the park page for access and parking."),
           ("Do Atlantic beaches get a sunset over the water?", "No. They face east. The morning light is the ocean light.")],
          [FWC_FAQ])

def home():
    regions = "".join('<li class="card"><h3><a href="/regions/%s/">%s</a></h3><p>%s</p></li>' % (k, E(R["name"]), E(R["blurb"])) for k, R in REGIONS.items())
    counties = "".join('<li><a href="/counties/%s/">%s</a></li>' % (k, E(n)) for k, n in sorted(COUNTIES.items(), key=lambda kv: kv[1]) if any(b["county"] == k for b in BEACHES))
    sarasota = "".join('<li><a href="%s">%s</a></li>' % (bpath(b), E(b["name"])) for b in BEACHES if b["county"] == "sarasota")
    faqs = [
        ("Which Florida beach should I pick?", "There is no single best beach. Use the picker for the constraint that would ruin the day: region, dogs, lifeguards, a wheelchair or mat, shelling, or a kids playground or guarded swim. Then open the beach page and the agency link."),
        ("Do you post today's red tide or bacteria results?", "No. FWC posts the current status and a daily sample map. The Florida Department of Health posts bacteria results. This site links those pages and does not freeze a cell count."),
        ("Where do the parking, dog, and access facts come from?", "From the county or city park page, or the Florida State Parks page, linked on each beach. If a fee, an hour, or a fill time is not on that page, it is not on ours."),
    ]
    body = f'''<section class="hero"><h1>Which Florida beach should you go to?</h1>
<p class="answer">A per beach guide for people who need the practical answer: parking, shelling, red tide, wheelchairs and mats, dogs, lifeguards, restrooms, and who the beach suits. Facts come from the county or state park page. Live conditions stay on FWC and the Florida Department of Health.</p>
<p class="btnrow"><a class="btn" href="#picker">Pick a beach</a> <a class="btn alt" href="/guides/how-to-pick-a-florida-beach/">How to pick</a></p></section>
<form class="picker" id="picker" action="/beaches/">
<h2>Beach picker</h2>
<p>Choose what would ruin the day. The list uses the same facts as the beach pages.</p>
<div class="filters">
<label>Region<select name="region"><option value="">Any</option><option value="gulf">Gulf Coast</option><option value="atlantic">Atlantic Coast</option><option value="panhandle">Panhandle</option><option value="keys">Florida Keys</option></select></label>
<label>Dogs<select name="dogs"><option value="">Any</option><option value="yes">Allowed on the sand</option><option value="no">Not allowed</option></select></label>
<label>Lifeguards<select name="guard"><option value="">Any</option><option value="yes">Page describes lifeguards</option><option value="no">Page says none</option></select></label>
<label>Access<select name="chair"><option value="">Any</option><option value="yes">Wheelchair or mat</option></select></label>
<label>Shelling<select name="shell"><option value="">Any</option><option value="yes">Page mentions shells</option></select></label>
<label>Kids<select name="kids"><option value="">Any</option><option value="yes">Playground, guards, or a kids cove</option></select></label>
</div>
<p class="btnrow"><button class="btn" type="submit">Show beaches</button></p>
<p id="picker-status" role="status">Loading beaches.</p>
<ul id="picker-results"></ul>
</form>
<h2>Regions</h2><ul class="cards">{regions}</ul>
<h2>Guides</h2><ul class="cols">
<li><a href="/guides/how-to-pick-a-florida-beach/">How to pick a Florida beach</a></li>
<li><a href="/guides/red-tide/">Red tide history and where to check</a></li>
<li><a href="/guides/best-shelling/">Shelling</a></li>
<li><a href="/guides/best-for-dogs/">Dogs</a></li>
<li><a href="/guides/best-for-kids/">Kids</a></li>
<li><a href="/guides/best-for-accessibility/">Wheelchairs and mats</a></li>
<li><a href="/guides/best-for-sunsets/">Sunset direction</a></li>
</ul>
<h2>Counties</h2><ul class="cols">{counties}</ul>
<h2>Siesta Key and Sarasota</h2><p>Sarasota County is covered beach by beach, including Siesta Key accesses that differ on dogs, parking, and lifeguards.</p><ul class="cols">{sarasota}</ul>
<h2>How the facts are chosen</h2><p>We cite the managing agency and leave out fees, hours, and fill times the page does not state. <a href="/methodology/">Sources and methods</a>.</p>
{faq_html(faqs)}'''
    pub, mod = hub_dates("/")
    write("/", page("/", "Which Florida Beach? Parking, Shells, Dogs and Access",
                    "Pick a Florida beach by parking, shelling, red tide, wheelchairs, dogs, lifeguards and restrooms. Facts from parks, FWC and the health department.",
                    body, [article_ld("Which Florida beach should you go to?", "/", published=pub, modified=mod), faq_ld(faqs)], lastmod=mod))

def simple(path, title, desc, h1, inner, crumb=None, noindex=False, legal=False):
    pub, mod = hub_dates(path)
    write(path, page(path, title, desc, '<article class="prose"><h1>%s</h1>%s</article>' % (E(h1), inner),
                     article_ld(h1, path, published=pub, modified=mod), [("/", "Home"), (path, crumb or h1)],
                     noindex=noindex, legal=legal, og_type="article", lastmod=mod))

def about_legal():
    simple("/about/", "About %s" % BRAND, "What Which FL Beach is and how the beach guides are checked.", "About Which FL Beach", f'''
{byline()}
<p>Which FL Beach is an independent guide to choosing a Florida beach. The question on every page is practical: parking, shells, red tide, step free access, dogs, lifeguards, restrooms, and who the beach suits.</p>
<h2>What we cover</h2><p>{len(BEACHES)} beaches on the Gulf Coast, the Atlantic coast, the Panhandle and the Keys, with extra depth on Siesta Key and Sarasota County. We add a beach when we can cite a county, city, or Florida State Parks page.</p>
<h2>How we work</h2><p>We read the managing agency page, write the summary ourselves, and link it. If a fee, an hour, or a fill time is not on that page, it is not on ours. Live red tide and bacteria results stay on FWC and the Florida Department of Health. See <a href="/methodology/">sources and methods</a>.</p>
<h2>Independence</h2><p>Which FL Beach is not a park agency and is not paid by one. Place names are used only to identify the beaches.</p>
<p>See a stale fact after a park changes its page? <a href="/contact/">Write to us</a>.</p>''')
    simple("/methodology/", "Sources and Methods | %s" % BRAND, "Where Which FL Beach facts come from, and what we leave out when a park page is silent.", "Sources and methods", f'''
{byline()}
<h2>Managing agencies</h2><p>Beach facts come from the county or city parks page, or from the Florida State Parks experiences and amenities page for that park. The link is on the beach page. We checked those pages on {PUBLISHED_H}.</p>
<h2>What we copy into the table</h2><p>Parking, including a price only when the page states one. Whether the agency says the lot fills. Shelling only when the page mentions shells or beachcombing. Dog rules in the words the page supports. Lifeguards only when the page says they are on duty or that they are not provided. Restrooms, beach wheelchairs and access mats the same way. If the page is silent, the table says so.</p>
<h2>What we never freeze</h2><p>Current red tide cell counts, current bacteria advisories, and temporary closures. FWC and the Florida Department of Health publish those. Our <a href="/guides/red-tide/">red tide guide</a> explains the history and the links.</p>
<h2>Shells and health</h2><p>Shell rules follow the FWC recreational sea shell page. Health warnings about red tide are attributed to FWC or the health department. They are not medical advice from this site.</p>
<h2>Our read of who a beach suits</h2><p>The "who it suits" line is our planning note from the published facts. It is labeled that way. It is not a rule of the park.</p>
<h2>Corrections</h2><p><a href="/contact/">Email us</a> with the page address and the agency link that shows the change. We update the verified date when we recheck.</p>''', "Sources and methods")
    simple("/image-policy/", "Image Policy | %s" % BRAND, "How Which FL Beach handles graphics, social images, and AI generated news photos.", "Image policy", f'''
<p>Last updated {TODAY_H}.</p>
<h2>Graphics</h2><p>The logo and the social image are original graphics we drew for this site. They are not photographs of a beach, and they are not copies of a park map or logo.</p>
<h2>Photos</h2><p>We do not copy park photography. When a guide uses a news style thumbnail, the image links here and carries a credit.</p>
<h2>AI generated images</h2><p>Guide thumbnails that are AI generated carry a visible credit that says AI generated image, link to this page, do not depict a real identifiable person, and are not presented as documentary photos of a named park. Until a guide has its own news photo, related read cards may use the site social graphic instead.</p>
<h2>Names</h2><p>We do not display agency logos. Names identify places.</p>
<p>If you believe a graphic uses your work, see the <a href="/copyright/">copyright policy</a> or <a href="/contact/">contact us</a>.</p>''', "Image policy")
    simple("/contact/", "Contact %s" % BRAND, "Email Which FL Beach about a correction or a beach to add.", "Contact us", f'''
<p>Questions and corrections go to <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
<h2>Corrections</h2><p>Send the page address, what looks wrong, and a link to the county, city, state park, FWC, or health department page that shows the current fact. We recheck before we change a page.</p>
<h2>What to expect</h2><p>We read every message. We do not take bookings and we do not speak for a park.</p>
<p class="note">This address is the contact for the site. See the <a href="/privacy/">privacy policy</a> for how a message is handled.</p>''', "Contact")
    D = PUBLISHED_H
    legal = {
    "/terms/": ("Terms of Use", f'''<p>Last updated {D}. These terms govern your use of whichflbeach.com ("Which FL Beach", "we", "us"). Which FL Beach is a trade name of Joshua Israel Ventures LLC, a Florida limited liability company. By using the site you agree to these terms.</p>
<h2>Information only</h2><p>Which FL Beach provides general information to help you choose a beach. It is not travel, medical, or legal advice, and it is not a substitute for the managing agency. Park rules, fees, hours and water conditions change. Read the agency page and the posted signs before you go.</p>
<h2>Accuracy</h2><p>We cite our sources and leave out what those sources do not state. We do not warrant that a page is complete or current.</p>
<h2>Acceptable use</h2><p>You may view and share links for personal, non commercial use. You may not scrape the site in bulk, republish our original text or compilations without permission, or try to disrupt the site.</p>
<h2>Intellectual property</h2><p>Original text, design and compilations belong to Joshua Israel Ventures LLC. Park and agency names belong to their owners and are used only to identify places.</p>
<h2>Third party links</h2><p>We link to park agencies, FWC, the Florida Department of Health and other public sources. We are not responsible for their content. The site is hosted on GitHub Pages.</p>
<h2>Disclaimer of warranties and limitation of liability</h2><p>The site is provided as is and as available. To the fullest extent permitted by law, Joshua Israel Ventures LLC disclaims all warranties and will not be liable for indirect, incidental, special, consequential or punitive damages, or any loss from your use of the site or a trip you take. Our total liability for any claim relating to the site is limited to 100 US dollars.</p>
<h2>Indemnity</h2><p>You agree to indemnify Joshua Israel Ventures LLC against claims arising from your misuse of the site or your breach of these terms.</p>
<h2>Governing law</h2><p>These terms are governed by the laws of the State of Florida, without regard to conflict of law rules. Disputes will be resolved in the state or federal courts located in Florida, and you consent to their jurisdiction.</p>
<h2>Changes</h2><p>We may update these terms. The date above is the latest version. Questions: <a href="/contact/">contact us</a>.</p>'''),
    "/privacy/": ("Privacy Policy", f'''<p>Last updated {TODAY_H}. This policy explains how Which FL Beach (whichflbeach.com), a trade name of Joshua Israel Ventures LLC, a Florida limited liability company, handles information.</p>
<h2>Analytics</h2><p>The public site uses Cloudflare Web Analytics and Google Analytics 4.</p>
<p>Cloudflare Web Analytics counts visits. It does not use cookies and does not track you across sites. The launch build includes that beacon on every page. The preview build does not include it.</p>
<p>Google Analytics 4 measures page visits for this site. The launch build loads the Google tag (gtag) only after you accept the cookie banner. Until then, Google Consent Mode v2 defaults are denied for ad storage, ad user data, ad personalization, and analytics storage. If you accept, analytics storage is set to granted and the tag loads for our GA4 property. Ad storage stays denied until advertising consent is collected. If you reject, the tag is not loaded. Use the Cookie settings link in the footer to change your choice. That choice is stored in local storage in your browser. The preview build does not include Google Analytics 4.</p>
<h2>Contact</h2><p>If you email {CONTACT}, we use your message and your address to reply. We keep them only as long as we need for that reply and for a record of a correction.</p>
<h2>Advertising</h2><p>Which FL Beach uses Google AdSense account {ADSENSE_PUB}. The site includes the AdSense script and a google-adsense-account meta tag so Google can verify the property. We have not placed ad units on pages yet, so you should not see display ads today.</p>
<h2>Google advertising cookies and your choices</h2><p>Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites. Google's use of advertising cookies enables it and its partners to serve ads based on your visit to this site and/or other sites on the Internet. You may opt out of personalized advertising by visiting <a href="https://adssettings.google.com/" rel="nofollow noopener">Google Ads Settings</a>. Alternatively, you can opt out of a third-party vendor's use of cookies for personalized advertising at <a href="https://www.aboutads.info/choices/" rel="nofollow noopener">aboutads.info/choices</a>. For more information, see <a href="https://policies.google.com/technologies/partner-sites" rel="nofollow noopener">how Google uses information from sites or apps that use its services</a>.</p>
<p>When ad units go live, Google and its partners may use cookies or similar technology to serve and measure ads, including ads based on prior visits to this or other sites. You can opt out of personalized advertising at Google Ads Settings and at aboutads.info. Where the law requires it, we will ask for consent before advertising cookies are set. Our Consent Mode defaults keep ad storage denied until that consent step is added. Publisher details also appear in the site root ads.txt file.</p>
<p>An advertiser does not choose beach facts. See the <a href="/ad-disclosure/">advertising disclosure</a>.</p>
<h2>Cookies</h2><p>Which FL Beach itself sets no cookies. Google Analytics 4 may set cookies only after you accept. Cloudflare Web Analytics does not use cookies. When AdSense ad units are active and consent is granted, Google may set advertising cookies. The site works if your browser blocks cookies.</p>
<h2>Hosting</h2><p>The site is hosted on GitHub Pages, which may log IP addresses for security and operations.</p>
<h2>Your rights</h2><p>You can ask us to access, correct or delete personal information we hold. Email <a href="mailto:{CONTACT}">{CONTACT}</a>. Residents of some states and countries may have additional rights, which we will honor.</p>
<h2>Children</h2><p>The site is for a general audience and is not directed at children under 13. We do not knowingly collect personal information from children.</p>
<h2>Changes</h2><p>We will post changes here with a new date.</p>'''),
    "/disclaimer/": ("Disclaimer", f'''<p>Last updated {D}.</p>
<h2>Not a park agency</h2><p>Which FL Beach is independent. It is not affiliated with, endorsed by, or speaking for any county, city, Florida State Parks, the Florida Fish and Wildlife Conservation Commission, or the Florida Department of Health. Names identify places.</p>
<h2>Rules and conditions change</h2><p>Fees, hours, lifeguard schedules, dog rules and access equipment change. Our pages reflect the sources on the date shown. The agency page and the signs at the beach control.</p>
<h2>No live conditions, and no medical advice</h2><p>We do not state current red tide or bacteria conditions. Health notes are summaries of agency pages, not medical advice. Talk to a clinician about your own health. Suitability notes are our planning opinions.</p>
<h2>Accuracy</h2><p>We cite sources and omit what we cannot verify. Errors still happen. <a href="/contact/">Report one</a> and we will correct a verified mistake.</p>
<h2>Limitation of liability</h2><p>To the extent permitted by law, Joshua Israel Ventures LLC is not liable for loss from reliance on this site. See the <a href="/terms/">terms of use</a>.</p>'''),
    "/copyright/": ("Copyright and DMCA Policy", f'''<p>Last updated {D}. Original text, design and compilations on Which FL Beach are owned by Joshua Israel Ventures LLC. Facts are cited to their sources. The site does not reproduce park photos. See the <a href="/image-policy/">image policy</a>.</p>
<h2>Reporting infringement</h2><p>If you believe material on this site infringes your copyright, email <a href="mailto:{CONTACT}">{CONTACT}</a> with: your name and contact details; a description of the copyrighted work; the URL of the material; a statement that you have a good faith belief the use is not authorized; a statement, under penalty of perjury, that the notice is accurate and that you are the owner or authorized to act for the owner; and your physical or electronic signature. We will review notices and remove or disable material where that is the right step.</p>
<h2>Counter notice</h2><p>If your material was removed and you believe that was a mistake, you may send a counter notice to the same address with the details required by 17 U.S.C. section 512(g).</p>
<h2>Repeat infringement</h2><p>We will act against repeat infringement where that is appropriate.</p>'''),
    "/ad-disclosure/": ("Advertising and Affiliate Disclosure", f'''<p>Last updated {TODAY_H}. Which FL Beach is free to use. The site is prepared for Google AdSense (publisher {ADSENSE_PUB}) and publishes an ads.txt line for that account. Display ad units are not placed on pages yet, so you should not see ads in the guides today. The site has no affiliate links.</p>
<p>When ads appear they will be separate from the guides and labeled. An advertiser will not change a beach fact. If we add a paid link we will label it.</p>
<h2>Editorial independence</h2><p>No park agency pays for a mention. Questions: <a href="/contact/">contact us</a>.</p>'''),
    }
    for p, (t, inner) in legal.items():
        body = '<article class="prose"><h1>%s</h1>%s<p class="legal-line">© 2026 Joshua Israel Ventures LLC. All rights reserved. Which FL Beach is a trade name of Joshua Israel Ventures LLC, a Florida limited liability company.</p></article>' % (E(t), inner)
        pub, mod = hub_dates(p)
        write(p, page(p, "%s | %s" % (t, BRAND), "%s for Which FL Beach (whichflbeach.com)." % t, body,
                      article_ld(t, p, published=pub, modified=mod), [("/", "Home"), (p, t)], og_type="article", lastmod=mod))

def not_found():
    body = '<h1>Page not found</h1><p>That address is not a beach guide. Try the <a href="/beaches/">beach list</a> or the <a href="/">picker</a>.</p>'
    write("/404.html", page("/404.html", "Page not found | %s" % BRAND, "That page is not on Which FL Beach.", body, noindex=True))

def png(path, w, h, fn):
    import zlib, struct
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw += bytes(fn(x, y))
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(blob)

def extras():
    with open(os.path.join(ROOT, "CNAME"), "w") as f:
        f.write("whichflbeach.com\n")
    with open(os.path.join(ROOT, INDEXNOW_KEY + ".txt"), "w") as f:
        f.write(INDEXNOW_KEY)
    with open(os.path.join(ROOT, "ads.txt"), "w") as f:
        f.write("google.com, pub-5681559774142917, DIRECT, f08c47fec0942fa0\n")
    bots = ["*", "Googlebot", "Bingbot", "Mediapartners-Google", "OAI-SearchBot", "ChatGPT-User", "GPTBot",
            "PerplexityBot", "Perplexity-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "Google-Extended",
            "Applebot", "Applebot-Extended", "Bytespider", "DuckAssistBot", "Amazonbot", "CCBot"]
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write("".join("User-agent: %s\nAllow: /\n\n" % b for b in bots) + "Sitemap: %ssitemap.xml\n" % BASE)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (url(p), m) for p, m in PAGES) + "</urlset>\n")
    lines = ["# %s" % BRAND, "",
             "> Which FL Beach (whichflbeach.com) helps a reader pick a Florida beach. Each beach page covers parking, shelling, red tide links, beach wheelchairs and mats, dogs, lifeguards, restrooms, and who the beach suits. Facts are cited to county or city parks, Florida State Parks, FWC, and the Florida Department of Health. Verified %s. The site does not state current red tide or bacteria conditions." % PUBLISHED_H,
             "", "## Guides",
             "- [How to pick a Florida beach](%s)" % url("/guides/how-to-pick-a-florida-beach/"),
             "- [Red tide history and where to check](%s)" % url("/guides/red-tide/"),
             "- [Shelling](%s)" % url("/guides/best-shelling/"),
             "- [Dogs](%s)" % url("/guides/best-for-dogs/"),
             "- [Kids](%s)" % url("/guides/best-for-kids/"),
             "- [Wheelchairs and mats](%s)" % url("/guides/best-for-accessibility/"),
             "- [Sunset direction](%s)" % url("/guides/best-for-sunsets/"),
             "- [Sources and methods](%s)" % url("/methodology/"),
             "", "## Regions"]
    for k, R in REGIONS.items():
        lines.append("- [%s](%s)" % (R["name"], url("/regions/%s/" % k)))
    lines += ["", "## Counties"]
    for k, n in sorted(COUNTIES.items(), key=lambda kv: kv[1]):
        if any(b["county"] == k for b in BEACHES):
            lines.append("- [%s](%s)" % (n, url("/counties/%s/" % k)))
    lines += ["", "## Beaches"]
    for b in BEACHES:
        lines.append("- [%s](%s) (%s, %s)" % (b["name"], url(bpath(b)), b["county_name"], REGIONS[b["region"]]["name"]))
    with open(os.path.join(ROOT, "llms.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(ROOT, "favicon.svg"), "w") as f:
        f.write(LOGO.replace('width="34" height="34" ', 'xmlns="http://www.w3.org/2000/svg" ').replace(' aria-hidden="true" focusable="false"', ""))
    def sky(x, y):
        if y < 220:
            return (11, 57, 84)
        if y < 250:
            return (240, 180, 41)
        band = int((x / 40 + y / 18) % 2)
        return (12, 124, 134) if band == 0 else (143, 208, 200)
    png(os.path.join(ROOT, "og.png"), 1200, 630, sky)
    png(os.path.join(ROOT, "logo.png"), 128, 128, lambda x, y: (11, 57, 84) if y < 70 else ((240, 180, 41) if y < 84 else (12, 124, 134)))
    slim = [{"slug": b["slug"], "name": b["name"], "region": b["region"], "county": b["county"], "countyName": b["county_name"],
             "place": b["place"], "dogs": b["dogs"], "shell": b["shell"], "chair": b["chair"], "mat": b["mat"],
             "guard": b["guard"], "kids": bool(b["kids"]), "water": b["water"]} for b in BEACHES]
    with open(os.path.join(ROOT, "assets", "beaches.json"), "w") as f:
        json.dump(slim, f, ensure_ascii=False)

def main():
    slugs = [b["slug"] for b in BEACHES]
    if len(slugs) != len(set(slugs)):
        raise SystemExit("duplicate beach slug")
    for b in BEACHES:
        for s in b["nearby"]:
            if s not in slugs:
                raise SystemExit("missing nearby %s on %s" % (s, b["slug"]))
        if b["county"] not in COUNTIES or b["region"] not in REGIONS:
            raise SystemExit("bad region or county on %s" % b["slug"])
    for b in BEACHES:
        beach_page(b)
    beaches_index(); region_pages(); county_pages(); guides(); home(); about_legal(); not_found(); extras()
    if LAUNCH and not GA4_ID:
        print("WARNING: GA4_ID is empty. check.py --launch fails until you set a G- measurement ID.")
    print(len(BEACHES), "beaches", len(PAGES), "sitemap urls", "LAUNCH" if LAUNCH else "PREVIEW")

if __name__ == "__main__":
    main()
