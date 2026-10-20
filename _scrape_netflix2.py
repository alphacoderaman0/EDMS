import re
import requests

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
css_url = (
    "https://assets.nflxext.com/web/ffe/wp/@nf-web-ui/ui-shared/"
    "dist/less/signup/nmhp/nmhp.1afe2e52bff213979e1d.css"
)
r = requests.get(css_url, headers=headers, timeout=30)
print("css status", r.status_code, "len", len(r.text))
text = r.text
# save for inspection
open("_netflix_nmhp.css", "w", encoding="utf-8").write(text)

# Extract CSS custom properties from HTML (design tokens often inline)
html = requests.get("https://www.netflix.com/in/", headers=headers, timeout=30).text
open("_netflix_in.html", "w", encoding="utf-8", errors="ignore").write(html)

# Find --variables
vars_found = sorted(set(re.findall(r"--[a-zA-Z0-9_-]+\s*:\s*[^;]+", html)))
print("css vars in html", len(vars_found))
for v in vars_found[:80]:
    print(" ", v[:140])

# look for design token blocks
for key in [
    "E50914",
    "e50914",
    "Netflix Sans",
    "border-radius",
    "rgba(0,0,0",
    "background",
    "font-size",
    "--layout",
    "gradient",
]:
    print(key, html.lower().count(key.lower()), "css", text.lower().count(key.lower()))

# Extract style attributes with colors
print("--- sample style attrs ---")
styles = re.findall(r'style="([^"]{20,200})"', html)
for s in styles[:30]:
    print(s[:180])
