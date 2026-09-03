import os
from services.character_catalog import CHARACTER_CATALOG

AVATAR_DIR = os.path.join(os.path.dirname(__file__), "static", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

for char in CHARACTER_CATALOG:
    slug = char["slug"]
    name = char["name"]
    game = char["game"]
    color = char.get("accent_color", "#38bdf8")
    
    if game == "blue_archive":
        bg_from, bg_to = "#070f26", "#0f172a"
        badge_text = "BLUE ARCHIVE"
        badge_bg = "rgba(56, 189, 248, 0.2)"
        badge_border = "rgba(56, 189, 248, 0.4)"
        halo_svg = f"""
        <ellipse cx="100" cy="42" rx="36" ry="8" fill="none" stroke="{color}" stroke-width="3" opacity="0.9" filter="url(#glow)"/>
        <circle cx="100" cy="42" r="2" fill="#fff"/>
        """
    elif game == "wuthering_waves":
        bg_from, bg_to = "#18120c", "#0f172a"
        badge_text = "WUTHERING WAVES"
        badge_bg = "rgba(245, 158, 11, 0.2)"
        badge_border = "rgba(245, 158, 11, 0.4)"
        halo_svg = f"""
        <circle cx="100" cy="100" r="68" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.6"/>
        <circle cx="100" cy="100" r="78" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="3 5" opacity="0.4"/>
        """
    else:  # endfield
        bg_from, bg_to = "#1c1917", "#0a0a0c"
        badge_text = "ENDFIELD"
        badge_bg = "rgba(234, 179, 8, 0.25)"
        badge_border = "rgba(234, 179, 8, 0.5)"
        halo_svg = f"""
        <polygon points="100,28 116,44 100,60 84,44" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.8"/>
        <line x1="25" y1="175" x2="175" y2="175" stroke="{color}" stroke-width="2" stroke-dasharray="8 6" opacity="0.5"/>
        """
    
    char_display = name[:2]
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="bg_{slug}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_from}"/>
      <stop offset="100%" stop-color="{bg_to}"/>
    </linearGradient>
    <linearGradient id="accent_{slug}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}"/>
      <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  
  <!-- Card Background -->
  <rect width="200" height="200" rx="24" fill="url(#bg_{slug})" />
  <rect width="198" height="198" x="1" y="1" rx="23" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.35" />
  
  <!-- Subtle Grid Pattern -->
  <circle cx="100" cy="100" r="52" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.06" />
  
  <!-- Game Themed Graphic -->
  {halo_svg}
  
  <!-- Character Center Avatar Orb -->
  <circle cx="100" cy="100" r="42" fill="#0b0f19" stroke="{color}" stroke-width="2" />
  <text x="100" y="109" font-family="'Cinzel', 'Shippori Mincho', 'Noto Serif SC', 'PingFang SC', sans-serif" font-weight="bold" font-size="22" fill="url(#accent_{slug})" text-anchor="middle" letter-spacing="1">{char_display}</text>
  
  <!-- Top Game Badge -->
  <rect x="25" y="12" width="150" height="18" rx="9" fill="{badge_bg}" stroke="{badge_border}" stroke-width="0.8" />
  <text x="100" y="24.5" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="700" fill="{color}" text-anchor="middle" letter-spacing="1.5">{badge_text}</text>
  
  <!-- Bottom Character Full Name -->
  <text x="100" y="165" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="13" font-weight="700" fill="#ffffff" text-anchor="middle">{name}</text>
</svg>"""

    filepath = os.path.join(AVATAR_DIR, f"{slug}.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")

print(f"Generated {len(CHARACTER_CATALOG)} character avatars in {AVATAR_DIR}")
