import os
import glob

replacements = {
    "💰": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Money%20bag/3D/money_bag_3d.png" alt="Money" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "📊": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bar%20chart/3D/bar_chart_3d.png" alt="Chart" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "🤖": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Robot/3D/robot_3d.png" alt="Robot" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "🔒": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Locked%20with%20key/3D/locked_with_key_3d.png" alt="Lock" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "💡": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Light%20bulb/3D/light_bulb_3d.png" alt="Idea" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "⚠️": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Warning/3D/warning_3d.png" alt="Warning" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "✨": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Sparkles/3D/sparkles_3d.png" alt="Sparkles" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">',
    "✅": '<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Check%20mark%20button/3D/check_mark_button_3d.png" alt="Check" style="width: 1.2em; height: 1.2em; vertical-align: middle; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));">'
}

html_files = glob.glob("public/*.html")
for file in html_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)
print("Emojis replaced successfully.")
