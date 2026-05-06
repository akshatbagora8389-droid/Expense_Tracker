import glob
import os

target_html = '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Money%20bag/3D/money_bag_3d.png" alt="Money" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">'
replacement_html = '<img src="/img/logo.svg" alt="ExpenseIQ Logo">'

# In case there's another variation in index.html due to spacing or something, I'll also just replace the generic img tag if it's inside logo-icon.
# But string replace is safest first.

html_files = glob.glob("public/*.html")
for file in html_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if target_html in content:
        content = content.replace(target_html, replacement_html)
    else:
        # fallback regex if exact string mismatch
        import re
        content = re.sub(
            r'<div class="logo-icon">\s*<img[^>]+Money bag[^>]+>\s*</div>',
            '<div class="logo-icon">\n                    <img src="/img/logo.svg" alt="ExpenseIQ Logo">\n                </div>',
            content
        )

    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Replaced logo in HTML files.")
