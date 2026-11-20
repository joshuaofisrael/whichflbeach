#!/usr/bin/env python3
"""Site QA. Usage: python3 _build/check.py [--launch]
Root paths in both modes. noindex on every page unless --launch.
404 stays noindex. CNAME is whichflbeach.com in both modes.
--launch also requires a non-empty GA4_ID, the Cloudflare beacon, and the GA4 loader.
"""
import glob, re, json, os, sys, html

# Paths in _build/thin-noindex.txt are intentionally noindex (AdSense low-value-content fix, 20 Nov 2026).
import os as _os
_THIN = set()
try:
    with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "thin-noindex.txt"), encoding="utf-8") as _fh:
        _THIN = {l.strip().strip("/") for l in _fh if l.strip() and not l.startswith("#")}
except FileNotFoundError:
    pass


def _thin_rel(rel):
    r = str(rel).replace("\\", "/")
    if r.endswith("index.html"):
        r = r[: -len("index.html")]
    return r.strip("/") in _THIN


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCH = "--launch" in sys.argv
LEGAL = {"terms", "privacy", "disclaimer", "copyright", "ad-disclosure"}
FOOTER = ["/about/", "/contact/", "/privacy/", "/terms/", "/disclaimer/", "/copyright/", "/ad-disclosure/", "/image-policy/"]
bad = 0
titles = {}
descs = {}

def read_ga4():
    src = open(os.path.join(ROOT, "_build", "build.py"), encoding="utf-8").read()
    m = re.search(r'(?m)^GA4_ID\s*=\s*(["\'])(.*)\1\s*$', src)
    return m.group(2) if m else None

def needs_faq(rel):
    if rel in ("index.html", "beaches/index.html", "regions/index.html"):
        return True
    if rel.startswith("guides/") or rel.startswith("counties/"):
        return True
    if rel.startswith("regions/") and rel != "regions/index.html":
        return True
    if rel.startswith("beaches/") and rel.count("/") >= 2:
        return True
    return False

GA4 = read_ga4()
files = [f for f in glob.glob(ROOT + "/**/*.html", recursive=True) if "/_build/" not in f]
for f in files:
    h = open(f, encoding="utf-8").read()
    rel = os.path.relpath(f, ROOT)
    top = rel.split("/")[0]
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h):
        try:
            json.loads(m)
        except Exception as e:
            print("JSONLD", rel, e); bad += 1
    vis = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    if top not in LEGAL and re.search(r"Joshua|Israel Ventures|©", vis):
        print("LLC", rel); bad += 1
    if top in LEGAL and "is a trade name of Joshua Israel Ventures LLC" not in h:
        print("nolegalline", rel); bad += 1
    if not re.search(r'<link rel="canonical" href="https://whichflbeach\.com/', h):
        print("canonical", rel); bad += 1
    if "github.io" in h:
        print("githubio", rel); bad += 1
    if h.count("<h1") != 1:
        print("h1", rel, h.count("<h1")); bad += 1
    desc = re.search(r'<meta name="description" content="(.*?)"', h)
    dtext = html.unescape(desc.group(1)).strip() if desc else ""
    if not dtext or len(dtext) > 155:
        print("desc", rel, len(dtext)); bad += 1
    else:
        descs.setdefault(dtext, []).append(rel)
    if LAUNCH:
        if "static.cloudflareinsights.com/beacon.min.js" not in h:
            print("nobeacon", rel); bad += 1
        if "https://www.googletagmanager.com/gtag/js?id=" not in h or "window.loadGA4" not in h:
            print("noga4", rel); bad += 1
        if "gtag('consent', 'default'" not in h or "'analytics_storage': 'denied'" not in h:
            print("noconsent", rel); bad += 1
        if 'src="/assets/consent.js' not in h:
            print("noconsentjs", rel); bad += 1
        if 'id="cookie-settings"' not in h or ">Cookie settings<" not in h:
            print("nocookie", rel); bad += 1
        if GA4 is None or ("window.GA4_ID = %s;" % json.dumps(GA4)) not in h:
            print("ga4-id-page", rel); bad += 1
        if "noindex" in h and rel != "404.html" and not _thin_rel(rel):
            print("noindex", rel); bad += 1
    elif "noindex" not in h:
        print("preview-missing-noindex", rel); bad += 1
    if rel == "404.html" and "noindex" not in h:
        print("404-index", rel); bad += 1
    if "—" in h or "–" in h:
        print("dash", rel); bad += 1
    t = html.unescape(re.search(r"<title>(.*?)</title>", h).group(1))
    titles.setdefault(t, []).append(rel)
    if len(t) >= 60:
        print("longtitle", len(t), t); bad += 1
    for prop in ("og:type", "og:site_name", "og:title", "og:description", "og:url", "og:image"):
        if 'property="%s"' % prop not in h:
            print("og", rel, prop); bad += 1
    if 'name="twitter:card"' not in h or 'name="twitter:title"' not in h or 'name="twitter:image"' not in h:
        print("twitter", rel); bad += 1
    if rel != "404.html" and '"@type": "Article"' not in h:
        print("noarticle", rel); bad += 1
    if rel not in ("404.html", "index.html") and '"@type": "BreadcrumbList"' not in h:
        print("nocrumb", rel); bad += 1
    if rel == "index.html" and '"@type": "WebSite"' not in h:
        print("nowebsite", rel); bad += 1
    if needs_faq(rel) and ('"@type": "FAQPage"' not in h or 'class="faq"' not in h):
        print("nofaq", rel); bad += 1
    for href in FOOTER:
        if 'href="%s"' % href not in h:
            print("footer", rel, href); bad += 1
    stripped = re.sub(r'<a\b[^>]*href="/image-policy/"[^>]*>.*?</a>', "", h, flags=re.S)
    if re.search(r"<img\b", stripped, re.I):
        print("photo-policy", rel); bad += 1
    if re.search(r'(?:href|src)="(?!/|https?:|#|mailto:)[^"]+"', h):
        print("relpath", rel); bad += 1
    if rel.startswith("beaches/") and rel.count("/") >= 2:
        if '"Beach"' not in h or "TouristAttraction" not in h:
            print("beachschema", rel); bad += 1
        if "FAQPage" not in h:
            print("faq", rel); bad += 1
        if 'class="byline"' not in h:
            print("byline", rel); bad += 1
        sec = re.search(r'<section class="sources".*?</section>', h, re.S)
        if not sec or not re.search(r'href="https?://', sec.group(0)):
            print("sources", rel); bad += 1
        if 'href="/counties/' not in h or 'href="/regions/' not in h:
            print("beachhub", rel); bad += 1
    if rel.startswith("counties/") and 'href="/beaches/' not in h:
        print("countyhub", rel); bad += 1
    if re.match(r"regions/[^/]+/index\.html$", rel) and 'href="/counties/' not in h:
        print("regionhub", rel); bad += 1
    if rel.startswith("guides/") and ('href="/beaches/"' not in h or 'href="/regions/"' not in h):
        print("guidelinks", rel); bad += 1
    for link in re.findall(r'(?:href|src)="(/[^"#?]*)', h):
        if link.startswith("//"):
            continue
        p = os.path.join(ROOT, link.lstrip("/"))
        if not (os.path.isfile(p) or os.path.isfile(os.path.join(p, "index.html"))):
            print("broken", rel, link); bad += 1
for t, fs in titles.items():
    if len(fs) > 1:
        print("duptitle", t, fs); bad += 1
for d, fs in descs.items():
    if len(fs) > 1:
        print("dupdesc", d[:80], fs); bad += 1
cname = open(os.path.join(ROOT, "CNAME"), encoding="utf-8").read().strip()
if cname != "whichflbeach.com":
    print("cname", cname); bad += 1
robots = open(os.path.join(ROOT, "robots.txt"), encoding="utf-8").read()
for bot in ["Googlebot", "Bingbot", "GPTBot", "ClaudeBot", "PerplexityBot", "OAI-SearchBot", "CCBot", "Google-Extended", "Applebot-Extended", "Bytespider"]:
    if bot not in robots:
        print("robot", bot); bad += 1
if "User-agent: Googlebot\nAllow: /" not in robots or "User-agent: Bingbot\nAllow: /" not in robots:
    print("robot-allow"); bad += 1
if "Sitemap: https://whichflbeach.com/sitemap.xml" not in robots:
    print("sitemap-line"); bad += 1
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
if "404" in sm:
    print("404-in-sitemap"); bad += 1
blocks = re.findall(r"<url>.*?</url>", sm, re.S)
if not blocks or any("<lastmod>" not in b or "<loc>" not in b for b in blocks):
    print("nolastmod"); bad += 1
if sm.count("<loc>") < 70:
    print("thin-sitemap", sm.count("<loc>")); bad += 1
nbeaches = len(glob.glob(ROOT + "/beaches/*/index.html"))
if nbeaches < 70:
    print("beachcount", nbeaches); bad += 1
key = "af525312177496563755bb04b53948e9"
key_path = os.path.join(ROOT, key + ".txt")
if not os.path.isfile(key_path) or open(key_path, encoding="utf-8").read().strip() != key:
    print("indexnow"); bad += 1
llms = open(os.path.join(ROOT, "llms.txt"), encoding="utf-8").read()
if "https://whichflbeach.com/" not in llms or "## Beaches" not in llms:
    print("llms"); bad += 1
priv = open(os.path.join(ROOT, "privacy", "index.html"), encoding="utf-8").read()
if "Google Analytics 4" not in priv or "Cloudflare Web Analytics" not in priv:
    print("privacy-analytics"); bad += 1
if LAUNCH:
    if GA4 is None or not str(GA4).strip():
        print("ga4-id-empty"); bad += 1
    elif not re.fullmatch(r"G-[A-Z0-9]+", GA4):
        print("ga4-id-format", GA4); bad += 1
print("files", len(files), "beaches", nbeaches, "issues", bad)
sys.exit(1 if bad else 0)
