import os

filepath = r"C:\A2757\QuizProject\frontend\src\pages\AudienceDisplay.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace CHOICE_CONFIG
target_choice_cfg = '''const CHOICE_CONFIG = [
  {
    bg: "#ffffff",
    border: "rgba(15, 23, 42, 0.12)",
    hoverBg: "#f8fafc",
    accent: "#0f172a",
    label: "A",
    gradient: "#0f172a",
    badgeBg: "#f1f5f9",
    badgeBorder: "#cbd5e1",
    badgeColor: "#0f172a",
    glyph: "A",
  },
  {
    bg: "#ffffff",
    border: "rgba(15, 23, 42, 0.12)",
    hoverBg: "#f8fafc",
    accent: "#0f172a",
    label: "B",
    gradient: "#0f172a",
    badgeBg: "#f1f5f9",
    badgeBorder: "#cbd5e1",
    badgeColor: "#0f172a",
    glyph: "B",
  },
  {
    bg: "#ffffff",
    border: "rgba(15, 23, 42, 0.12)",
    hoverBg: "#f8fafc",
    accent: "#0f172a",
    label: "C",
    gradient: "#0f172a",
    badgeBg: "#f1f5f9",
    badgeBorder: "#cbd5e1",
    badgeColor: "#0f172a",
    glyph: "C",
  },
  {
    bg: "#ffffff",
    border: "rgba(15, 23, 42, 0.12)",
    hoverBg: "#f8fafc",
    accent: "#0f172a",
    label: "D",
    gradient: "#0f172a",
    badgeBg: "#f1f5f9",
    badgeBorder: "#cbd5e1",
    badgeColor: "#0f172a",
    glyph: "D",
  },
];'''

new_choice_cfg = '''const CHOICE_CONFIG = [
  {
    bg: "#ffffff",
    border: "#ef4444",
    hoverBg: "#fef2f2",
    accent: "#ef4444",
    label: "A",
    glyph: "▲",
    badgeBg: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
    badgeBorder: "#b91c1c",
    badgeColor: "#ffffff",
    glow: "rgba(239, 68, 68, 0.25)",
    barBg: "#ef4444",
    lightBg: "#fef2f2",
  },
  {
    bg: "#ffffff",
    border: "#3b82f6",
    hoverBg: "#eff6ff",
    accent: "#2563eb",
    label: "B",
    glyph: "◆",
    badgeBg: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    badgeBorder: "#1d4ed8",
    badgeColor: "#ffffff",
    glow: "rgba(59, 130, 246, 0.25)",
    barBg: "#3b82f6",
    lightBg: "#eff6ff",
  },
  {
    bg: "#ffffff",
    border: "#eab308",
    hoverBg: "#fefce8",
    accent: "#ca8a04",
    label: "C",
    glyph: "●",
    badgeBg: "linear-gradient(135deg, #facc15 0%, #eab308 100%)",
    badgeBorder: "#a16207",
    badgeColor: "#713f12",
    glow: "rgba(250, 204, 21, 0.3)",
    barBg: "#eab308",
    lightBg: "#fefce8",
  },
  {
    bg: "#ffffff",
    border: "#10b981",
    hoverBg: "#ecfdf5",
    accent: "#059669",
    label: "D",
    glyph: "■",
    badgeBg: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
    badgeBorder: "#047857",
    badgeColor: "#ffffff",
    glow: "rgba(16, 185, 129, 0.25)",
    barBg: "#10b981",
    lightBg: "#ecfdf5",
  },
];'''

if target_choice_cfg in content:
    content = content.replace(target_choice_cfg, new_choice_cfg)
    print("Replaced CHOICE_CONFIG successfully.")
else:
    print("Could not find exact target_choice_cfg.")

# Save back
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
