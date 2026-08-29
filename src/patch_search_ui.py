# -*- coding: utf-8 -*-
import sys

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
FILES = [REPO + '/src/page_template.html', REPO + '/index.html']

EDITS = []

# 1) CSS: dropdown results panel + flash highlight + anchor scroll-margins
EDITS.append((
    '  .search-count{ font-size:12px; color:var(--ink-faint); margin-top:6px; min-height:14px; }',
    '  .search-count{ font-size:12px; color:var(--ink-faint); margin-top:6px; min-height:14px; }\n'
    '  .search-results{\n'
    '    display:none; position:absolute; top:100%; inset-inline:0; margin-top:6px;\n'
    '    background:var(--surface); border:1px solid var(--line-strong); border-radius:10px;\n'
    '    box-shadow:var(--shadow); max-height:60vh; overflow-y:auto; z-index:25;\n'
    '  }\n'
    '  .search-results.show{ display:block; }\n'
    '  .search-result{\n'
    '    display:flex; flex-direction:column; gap:2px; width:100%; text-align:start;\n'
    '    padding:10px 12px; border:none; background:none; cursor:pointer;\n'
    '    border-bottom:1px solid var(--line); font-family:inherit;\n'
    '  }\n'
    '  .search-result:last-child{ border-bottom:none; }\n'
    '  .search-result:hover{ background:var(--surface-2); }\n'
    '  .sr-type{ font-size:10.5px; color:var(--gold); font-weight:700; }\n'
    '  .sr-label{ font-size:13.5px; font-weight:700; color:var(--ink); }\n'
    '  .sr-snippet{ font-size:12px; color:var(--ink-faint); line-height:1.5; }\n'
    '  .sr-snippet mark{ background:var(--accent-soft); color:var(--accent); border-radius:3px; padding:0 2px; }\n'
    '  .search-empty{ padding:14px; font-size:13px; color:var(--ink-faint); text-align:center; }\n'
    '  .case-title[id], .topic-title[id]{ scroll-margin-top:24px; }\n'
    '  tr[id]{ scroll-margin-top:90px; }\n'
    '  @keyframes searchFlashBg{ 0%,100%{ background-color:transparent; } 30%{ background-color:var(--accent-soft); } }\n'
    '  .search-flash{ animation:searchFlashBg 2s ease; border-radius:8px; }'
))

# 2) HTML: add results container right after the search-count div
EDITS.append((
    '<div class="search-count" id="search-count"></div>',
    '<div class="search-count" id="search-count"></div>\n'
    '      <div class="search-results" id="search-results"></div>'
))

# 3) JS: replace the whole "search" block with the richer implementation
OLD_JS = (
    "  // search\n"
    "  var index = JSON.parse(document.getElementById('search-index').textContent);\n"
    "  var textById = {};\n"
    "  index.forEach(function(row){ textById[row.id] = (row.label + ' ' + row.text).toLowerCase(); });\n"
    "\n"
    "  var input = document.getElementById('search');\n"
    "  var countEl = document.getElementById('search-count');\n"
    "\n"
    "  function normalize(s){ return (s||'').toLowerCase(); }\n"
    "\n"
    "  input.addEventListener('input', function(){\n"
    "    var q = normalize(input.value.trim());\n"
    "    var lis = document.querySelectorAll('#nav .nav-list > li');\n"
    "    var matches = 0;\n"
    "    if(!q){\n"
    "      lis.forEach(function(li){\n"
    "        li.classList.remove('is-hidden');\n"
    "        li.querySelectorAll('.nav-sublist > li').forEach(function(sub){ sub.classList.remove('is-hidden'); });\n"
    "      });\n"
    "      countEl.textContent = '';\n"
    "      return;\n"
    "    }\n"
    "    lis.forEach(function(li){\n"
    "      var mainLink = li.querySelector(':scope > .nav-link');\n"
    "      var mainId = mainLink.dataset.target;\n"
    "      var mainHit = (textById[mainId] || '').indexOf(q) !== -1;\n"
    "      var anySubHit = false;\n"
    "      var subItems = li.querySelectorAll('.nav-sublist > li');\n"
    "      subItems.forEach(function(subLi){\n"
    "        var subLink = subLi.querySelector('.nav-sub-link');\n"
    "        var subId = subLink.dataset.target;\n"
    "        var hit = (textById[subId] || '').indexOf(q) !== -1;\n"
    "        subLi.classList.toggle('is-hidden', !hit && !mainHit);\n"
    "        if(hit){ anySubHit = true; matches++; }\n"
    "      });\n"
    "      var show = mainHit || anySubHit;\n"
    "      li.classList.toggle('is-hidden', !show);\n"
    "      if(mainHit) matches++;\n"
    "    });\n"
    "    countEl.textContent = matches ? (matches + ' תוצאות') : 'אין תוצאות';\n"
    "  });"
)

NEW_JS = r"""  // search
  var index = JSON.parse(document.getElementById('search-index').textContent);
  var itemIndex = index.filter(function(r){ return r.type !== 'chapter'; });
  var textById = {};
  index.forEach(function(row){ textById[row.id] = (row.label + ' ' + row.text).toLowerCase(); });

  var input = document.getElementById('search');
  var countEl = document.getElementById('search-count');
  var resultsEl = document.getElementById('search-results');
  var TYPE_LABEL = { case: '⚖ פסיקה', topic: '● נושא', row: '▤ טבלה' };

  function normalize(s){ return (s||'').toLowerCase(); }

  function escapeHtml(s){
    return s.replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function snippet(text, q){
    var idx = text.toLowerCase().indexOf(q);
    if(idx === -1) return escapeHtml(text.slice(0, 110));
    var start = Math.max(0, idx - 40);
    var end = Math.min(text.length, idx + q.length + 70);
    var pre = (start > 0 ? '…' : '') + text.slice(start, idx);
    var hit = text.slice(idx, idx + q.length);
    var post = text.slice(idx + q.length, end) + (end < text.length ? '…' : '');
    return escapeHtml(pre) + '<mark>' + escapeHtml(hit) + '</mark>' + escapeHtml(post);
  }

  function renderResults(qn){
    if(!qn){ resultsEl.classList.remove('show'); resultsEl.innerHTML = ''; return 0; }
    var scored = [];
    itemIndex.forEach(function(row){
      var labelN = normalize(row.label);
      var textN = normalize(row.text);
      var li = labelN.indexOf(qn);
      var ti = textN.indexOf(qn);
      if(li === -1 && ti === -1) return;
      scored.push({ row: row, score: li === 0 ? 0 : (li !== -1 ? 1 : 2), useText: li === -1 });
    });
    scored.sort(function(a, b){ return a.score - b.score; });
    var top = scored.slice(0, 30);
    if(!top.length){
      resultsEl.innerHTML = '<div class="search-empty">אין תוצאות</div>';
      resultsEl.classList.add('show');
      return 0;
    }
    resultsEl.innerHTML = top.map(function(item){
      var row = item.row;
      var basis = item.useText ? row.text : row.label;
      return '<button type="button" class="search-result" data-target="' + row.id + '">' +
        '<span class="sr-type">' + (TYPE_LABEL[row.type] || '') + '</span>' +
        '<span class="sr-label">' + escapeHtml(row.label) + '</span>' +
        '<span class="sr-snippet">' + snippet(basis, qn) + '</span>' +
        '</button>';
    }).join('');
    resultsEl.classList.add('show');
    return scored.length;
  }

  input.addEventListener('input', function(){
    var qn = normalize(input.value.trim());
    var resultCount = renderResults(qn);

    var lis = document.querySelectorAll('#nav .nav-list > li');
    if(!qn){
      lis.forEach(function(li){
        li.classList.remove('is-hidden');
        li.querySelectorAll('.nav-sublist > li').forEach(function(sub){ sub.classList.remove('is-hidden'); });
      });
      countEl.textContent = '';
      return;
    }
    var navMatches = 0;
    lis.forEach(function(li){
      var mainLink = li.querySelector(':scope > .nav-link');
      var mainId = mainLink.dataset.target;
      var mainHit = (textById[mainId] || '').indexOf(qn) !== -1;
      var anySubHit = false;
      var subItems = li.querySelectorAll('.nav-sublist > li');
      subItems.forEach(function(subLi){
        var subLink = subLi.querySelector('.nav-sub-link');
        var subId = subLink.dataset.target;
        var hit = (textById[subId] || '').indexOf(qn) !== -1;
        subLi.classList.toggle('is-hidden', !hit && !mainHit);
        if(hit){ anySubHit = true; navMatches++; }
      });
      li.classList.toggle('is-hidden', !(mainHit || anySubHit));
      if(mainHit) navMatches++;
    });
    countEl.textContent = resultCount ? (resultCount + ' תוצאות') : 'אין תוצאות';
  });

  resultsEl.addEventListener('click', function(e){
    var btn = e.target.closest('.search-result');
    if(!btn) return;
    var target = document.getElementById(btn.dataset.target);
    if(!target) return;
    resultsEl.classList.remove('show');
    closeMenu();
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    var flashEls = target.tagName === 'TR' ? Array.prototype.slice.call(target.children) : [target];
    flashEls.forEach(function(el){ el.classList.add('search-flash'); });
    setTimeout(function(){ flashEls.forEach(function(el){ el.classList.remove('search-flash'); }); }, 2200);
  });

  document.addEventListener('click', function(e){
    if(!e.target.closest('.search-wrap')) resultsEl.classList.remove('show');
  });
  input.addEventListener('focus', function(){ if(input.value.trim()) resultsEl.classList.add('show'); });"""

EDITS.append((OLD_JS, NEW_JS))

for path in FILES:
    src = open(path, encoding='utf-8').read()
    for old, new in EDITS:
        cnt = src.count(old)
        if cnt != 1:
            print('WARN: %r... occurs %d times in %s' % (old[:50], cnt, path), file=sys.stderr)
            continue
        src = src.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(src)
    print('patched', path)
