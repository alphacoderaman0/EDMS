import re
import requests

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
r = requests.get("https://www.netflix.com/in/", headers=headers, timeout=30)
print("status", r.status_code, "len", len(r.text))
html = r.text

css = re.findall(r'href="([^"]+\.css[^"]*)"', html)
print("css links", len(css))
for c in css[:20]:
    print(" ", c[:160])

fonts = list(set(re.findall(r"font-family:[^;\"']+", html, re.I)))
print("inline fonts sample:")
for f in fonts[:30]:
    print(" ", f[:120])

hexes = sorted(set(re.findall(r"#[0-9a-fA-F]{3,8}", html)))
print("hex count", len(hexes))
print(hexes)

# also pull a couple CSS files
collected = set()
for url in css[:8]:
    if url.startswith("/"):
        url = "https://www.netflix.com" + url
    try:
        cr = requests.get(url, headers=headers, timeout=20)
        print("css fetch", cr.status_code, url[:80], "len", len(cr.text))
        collected.update(re.findall(r"#[0-9a-fA-F]{3,8}", cr.text))
        ff = re.findall(r"font-family:\s*([^;}{]+)", cr.text, re.I)
        for f in list(set(ff))[:15]:
            print("  font:", f.strip()[:100])
        # border-radius samples
        br = re.findall(r"border-radius:\s*([^;}{]+)", cr.text, re.I)
        print("  radii sample:", list(set(br))[:20])
        # box-shadow
        sh = re.findall(r"box-shadow:\s*([^;}{]+)", cr.text, re.I)
        print("  shadows sample:", list(set(sh))[:15])
    except Exception as e:
        print("css err", e)

print("all hex from css:", sorted(collected)[:100])
