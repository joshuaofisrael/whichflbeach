#!/usr/bin/env python3
"""Site QA. Usage: python3 _build/check.py [--launch]
Root paths in both modes. noindex on every page unless --launch.
404 stays noindex. CNAME is whichflbeach.com in both modes.
"""
import glob, re, json, os, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCH = "--launch" in sys.argv
LEGAL = {"terms", "privacy", "disclaimer", "copyright", "ad-disclosure"}
bad = 0
titles = {}
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
    if not desc or len(html.unescape(desc.group(1))) > 155:
        print("desc", rel, 0 if not desc else len(html.unescape(desc.group(1)))); bad += 1
    if LAUNCH:
        if "static.cloudflareinsights.com/beacon.min.js" not in h:
            print("nobeacon", rel); bad += 1
        if "noindex" in h and rel != "404.html":
            print("noindex", rel); bad += 1
    elif "noindex" not in h:
        print("preview-missing-noindex", rel); bad += 1
    if rel == "404.html" and "noindex" not in h:
        print("404-index", rel); bad += 1
    if "—" in h or "–" in h:
        print("dash", rel); bad += 1
    t = html.unescape(re.search(r"<title>(.*?)</title>", h).group(1))
    titles.setdefault(t, []).append(rel)
    if len(t) > 70:
        print("longtitle", len(t), t)
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
    for link in re.findall(r'(?:href|src)="(/[^"#?]*)', h):
        if link.startswith("//"):
            continue
        p = os.path.join(ROOT, link.lstrip("/"))
        if not (os.path.isfile(p) or os.path.isfile(os.path.join(p, "index.html"))):
            print("broken", rel, link); bad += 1
for t, fs in titles.items():
    if len(fs) > 1:
        print("duptitle", t, fs); bad += 1
cname = open(os.path.join(ROOT, "CNAME"), encoding="utf-8").read().strip()
if cname != "whichflbeach.com":
    print("cname", cname); bad += 1
robots = open(os.path.join(ROOT, "robots.txt"), encoding="utf-8").read()
for bot in ["Googlebot", "Bingbot", "GPTBot", "ClaudeBot", "PerplexityBot", "OAI-SearchBot", "CCBot", "Google-Extended", "Applebot-Extended", "Bytespider"]:
    if bot not in robots:
        print("robot", bot); bad += 1
if "Sitemap: https://whichflbeach.com/sitemap.xml" not in robots:
    print("sitemap-line"); bad += 1
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
if "404" in sm:
    print("404-in-sitemap"); bad += 1
if sm.count("<loc>") < 70:
    print("thin-sitemap", sm.count("<loc>")); bad += 1
nbeaches = len(glob.glob(ROOT + "/beaches/*/index.html"))
if nbeaches < 70:
    print("beachcount", nbeaches); bad += 1
print("files", len(files), "beaches", nbeaches, "issues", bad)
sys.exit(1 if bad else 0)
