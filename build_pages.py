#!/usr/bin/env python3
"""Build standalone SEO pages (e.g. /storage/) from index.html.

The site is a single-page app with hash views (#storage). Google ignores
the part after '#', so each important view also gets a real URL: a copy of
index.html that opens on that view, with its own title, description,
canonical and structured data.

Run after every change to index.html:   python3 build_pages.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).parent
SITE = "https://adir-movings.co.il"

PAGES = {
    "storage": {
        "title": "מחסן להשכרה ליד ראש העין | אחסנת תכולה מ-13 ₪ ליום | אדיר",
        "description": "מחסן להשכרה ואחסנת תכולה ליד ראש העין: מבנה בטון סגור, מצלמות ואזעקה 24/7, תכולה מבוטחת. החל מ-13 ₪ ליום בתשלום חודשי, איסוף מהבית בכל המרכז. הצעת מחיר בוואטסאפ.",
        "og_title": "מחסן להשכרה ליד ראש העין — אחסנת תכולה מאובטחת",
        "schema": {
            "@context": "https://schema.org",
            "@type": "SelfStorage",
            "name": "אדיר שירותי הובלות ואחסנה — מחסן להשכרה",
            "url": f"{SITE}/storage/",
            "telephone": "+972-54-383-8376",
            "image": f"{SITE}/img/hero_warehouse.webp",
            "priceRange": "החל מ-13 ₪ ליום",
            "address": {"@type": "PostalAddress", "addressLocality": "ראש העין", "addressCountry": "IL"},
            "areaServed": ["ראש העין", "פתח תקווה", "שוהם", "אלעד", "יהוד", "מודיעין", "כפר סבא", "הוד השרון", "רעננה", "הרצליה", "תל אביב", "רמת גן", "גבעתיים", "בני ברק", "קריית אונו", "ראשון לציון"],
        },
    },
}


def sub_once(pattern, repl, s):
    new, n = re.subn(pattern, lambda m: repl, s, count=1)
    if n != 1:
        raise SystemExit(f"pattern not found: {pattern}")
    return new


def build(view, cfg, src):
    url = f"{SITE}/{view}/"
    s = src
    # Relative assets (img/, favicon, pdf) must resolve from the site root.
    s = sub_once(r'<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', s) if '<meta charset="utf-8">' in s else s.replace("<head>", '<head>\n<base href="/">', 1)
    s = sub_once(r'<title>.*?</title>', f"<title>{cfg['title']}</title>", s)
    s = sub_once(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{cfg["description"]}">', s)
    s = sub_once(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s)
    s = sub_once(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', s)
    s = sub_once(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{cfg["og_title"]}">', s)
    s = sub_once(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{cfg["description"]}">', s)
    schema = json.dumps(cfg["schema"], ensure_ascii=False)
    s = s.replace("</title>", f'</title>\n<script type="application/ld+json">{schema}</script>', 1)
    # Open on this view instead of home (visible without JS too).
    s = sub_once(r'<section data-view="home">', '<section data-view="home" hidden>', s)
    s = sub_once(rf'<section data-view="{view}" hidden>', f'<section data-view="{view}">', s)
    s = sub_once(r"show\(\(location\.hash\|\|'#home'\)\.slice\(1\)\);\n</script>", f"show((location.hash||'#{view}').slice(1));\n</script>", s)
    s = s.replace("const v=(location.hash||'#home').slice(1); show(v);", f"const v=(location.hash||'#{view}').slice(1); show(v);")
    out = ROOT / view / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding="utf-8")
    return url


def main():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    urls = [f"{SITE}/"] + [build(v, c, src) for v, c in PAGES.items()]
    import datetime
    today = datetime.date.today().isoformat()
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n",
        encoding="utf-8")
    print("built:", *urls, sep="\n  ")


if __name__ == "__main__":
    main()
