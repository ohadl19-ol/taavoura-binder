# -*- coding: utf-8 -*-
# Applies the same set of shell (CSS/HTML/JS) edits to both the template
# (src/page_template.html, source of truth for regeneration) and the
# already-rendered index.html (whose shell is currently byte-identical).
import sys

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
FILES = [REPO + '/src/page_template.html', REPO + '/index.html']

EDITS = []

# 1) anti-flash theme bootstrap, as early as possible in <head>
EDITS.append((
    '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<script>(function(){try{var t=localStorage.getItem(\'theme\');'
    'if(t===\'light\'||t===\'dark\'){document.documentElement.setAttribute(\'data-theme\',t);}}catch(e){}})();</script>'
))

# 2) strong{} -> accent-colored emphasis instead of plain ink bold
EDITS.append((
    'strong{ color:var(--ink); font-weight:700; }',
    'strong{ color:var(--accent); font-weight:800; }'
))

# 3) reading progress bar CSS (insert right before .shell rule)
EDITS.append((
    '  /* ---------- shell layout ---------- */\n  .shell{ display:flex; min-height:100vh; align-items:stretch; }',
    '  /* ---------- reading progress ---------- */\n'
    '  .progress-bar{ position:fixed; inset-inline-start:0; top:0; height:3px; width:0%; background:var(--accent); z-index:30; transition:width .08s linear; }\n\n'
    '  /* ---------- shell layout ---------- */\n  .shell{ display:flex; min-height:100vh; align-items:stretch; }'
))

# 4) brand row + theme toggle button CSS (insert after .brand-sub rule)
EDITS.append((
    '  .brand-sub{ margin:4px 0 0; font-size:12.5px; color:var(--ink-faint); letter-spacing:.02em; }',
    '  .brand-sub{ margin:4px 0 0; font-size:12.5px; color:var(--ink-faint); letter-spacing:.02em; }\n'
    '  .brand-row{ display:flex; align-items:center; justify-content:space-between; gap:10px; }\n'
    '  .theme-toggle{\n'
    '    display:inline-flex; align-items:center; justify-content:center; flex:none;\n'
    '    width:34px; height:34px; border-radius:9px; border:1px solid var(--line-strong);\n'
    '    background:var(--paper); color:var(--ink); cursor:pointer; font-size:15px;\n'
    '  }\n'
    '  .theme-toggle:hover{ background:var(--surface-2); }'
))

# 5) brand HTML markup: wrap in brand-row + add toggle button
EDITS.append((
    '<div class="brand"><span class="brand-mark">⚖️</span><h1>קלסר תעבורה</h1></div>',
    '<div class="brand-row">\n'
    '        <div class="brand"><span class="brand-mark">⚖️</span><h1>קלסר תעבורה</h1></div>\n'
    '        <button class="theme-toggle" id="theme-toggle" type="button" aria-label="החלפת מצב תצוגה, בהיר או כהה" title="בהיר / כהה">🌓</button>\n'
    '      </div>'
))

# 6) replace the lone .to-top button + its CSS with a floating action row (TOC + to-top)
EDITS.append((
    '  .to-top{\n'
    '    position:fixed; inset-inline-end:26px; bottom:26px; z-index:6;\n'
    '    background:var(--accent); color:var(--accent-ink); border:none; border-radius:999px;\n'
    '    width:44px; height:44px; font-size:18px; cursor:pointer; box-shadow:var(--shadow);\n'
    '    opacity:0; pointer-events:none; transition:opacity .18s;\n'
    '  }\n'
    '  .to-top.show{ opacity:1; pointer-events:auto; }',
    '  .fab-row{ position:fixed; inset-inline-end:26px; bottom:26px; z-index:6; display:flex; flex-direction:column; gap:10px; }\n'
    '  .fab{\n'
    '    background:var(--accent); color:var(--accent-ink); border:none; border-radius:999px;\n'
    '    width:44px; height:44px; font-size:18px; cursor:pointer; box-shadow:var(--shadow);\n'
    '    opacity:0; pointer-events:none; transition:opacity .18s;\n'
    '    display:flex; align-items:center; justify-content:center;\n'
    '  }\n'
    '  .fab.show{ opacity:1; pointer-events:auto; }'
))

EDITS.append((
    '<button class="to-top" id="to-top" aria-label="חזרה למעלה">↑</button>',
    '<div class="progress-bar" id="progress-bar"></div>\n'
    '<div class="fab-row">\n'
    '  <button class="fab" id="fab-toc" type="button" aria-label="פתיחת תוכן העניינים" title="תוכן העניינים">📑</button>\n'
    '  <button class="fab" id="to-top" type="button" aria-label="חזרה למעלה" title="חזרה למעלה">↑</button>\n'
    '</div>'
))

# 7) JS: progress bar + theme toggle wiring + fab-toc wiring
EDITS.append((
    '  // to-top button\n'
    '  var toTop = document.getElementById(\'to-top\');\n'
    '  window.addEventListener(\'scroll\', function(){\n'
    '    toTop.classList.toggle(\'show\', window.scrollY > 600);\n'
    '  }, { passive: true });\n'
    '  toTop.addEventListener(\'click\', function(){ window.scrollTo({top:0, behavior:\'smooth\'}); });',
    '  // floating action buttons (to-top + open-TOC)\n'
    '  var toTop = document.getElementById(\'to-top\');\n'
    '  var fabToc = document.getElementById(\'fab-toc\');\n'
    '  window.addEventListener(\'scroll\', function(){\n'
    '    var show = window.scrollY > 600;\n'
    '    toTop.classList.toggle(\'show\', show);\n'
    '    fabToc.classList.toggle(\'show\', show);\n'
    '  }, { passive: true });\n'
    '  toTop.addEventListener(\'click\', function(){ window.scrollTo({top:0, behavior:\'smooth\'}); });\n'
    '  fabToc.addEventListener(\'click\', openMenu);\n\n'
    '  // reading progress bar\n'
    '  var progressBar = document.getElementById(\'progress-bar\');\n'
    '  function updateProgress(){\n'
    '    var h = document.documentElement;\n'
    '    var max = h.scrollHeight - h.clientHeight;\n'
    '    var pct = max > 0 ? (window.scrollY / max) * 100 : 0;\n'
    '    progressBar.style.width = pct + \'%\';\n'
    '  }\n'
    '  window.addEventListener(\'scroll\', updateProgress, { passive: true });\n'
    '  window.addEventListener(\'resize\', updateProgress);\n'
    '  updateProgress();\n\n'
    '  // theme toggle\n'
    '  var themeBtn = document.getElementById(\'theme-toggle\');\n'
    '  function systemDark(){ return window.matchMedia(\'(prefers-color-scheme: dark)\').matches; }\n'
    '  function effectiveTheme(){\n'
    '    var t = document.documentElement.getAttribute(\'data-theme\');\n'
    '    return (t === \'light\' || t === \'dark\') ? t : (systemDark() ? \'dark\' : \'light\');\n'
    '  }\n'
    '  function paintThemeBtn(){ themeBtn.textContent = effectiveTheme() === \'dark\' ? \'☀️\' : \'🌙\'; }\n'
    '  paintThemeBtn();\n'
    '  themeBtn.addEventListener(\'click\', function(){\n'
    '    var next = effectiveTheme() === \'dark\' ? \'light\' : \'dark\';\n'
    '    document.documentElement.setAttribute(\'data-theme\', next);\n'
    '    try{ localStorage.setItem(\'theme\', next); }catch(e){}\n'
    '    paintThemeBtn();\n'
    '  });'
))

for path in FILES:
    src = open(path, encoding='utf-8').read()
    for old, new in EDITS:
        cnt = src.count(old)
        if cnt != 1:
            print('WARN: %r occurs %d times in %s' % (old[:60], cnt, path), file=sys.stderr)
            continue
        src = src.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(src)
    print('patched', path)
