#!/bin/bash
# Ping IndexNow after whichflbeach.com is live. Do not run during the noindex preview.
KEY=af525312177496563755bb04b53948e9
cd "$(dirname "$0")"
if [ $# -gt 0 ]; then URLS=$(printf '"%s",' "$@"); else URLS=$(grep -o '<loc>[^<]*' sitemap.xml | sed 's/<loc>//' | sed 's/.*/"&"/' | paste -sd, -); fi
curl -s -o /dev/null -w "IndexNow HTTP %{http_code}\n" -H "Content-Type: application/json; charset=utf-8" https://api.indexnow.org/indexnow \
 -d "{\"host\":\"whichflbeach.com\",\"key\":\"$KEY\",\"keyLocation\":\"https://whichflbeach.com/$KEY.txt\",\"urlList\":[${URLS%,}]}"
