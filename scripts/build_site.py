"""Build the static teaching site with Python's standard library only.

The Markdown documents and content/catalog.json are the source of truth.
Run from any directory: python scripts/build_site.py
"""
from __future__ import annotations

import html
import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "content/catalog.json").read_text(encoding="utf-8"))
SITE = CATALOG["site"]
ENTRIES = CATALOG["entries"]
CATEGORIES = {
    "preparation": ("备课资料", "Preparation notes", "试卷解答、逐题考点与讲解思路，为每一次上课做好准备。"),
    "chapters": ("课堂章节", "Classroom chapters", "沿着实际课堂的学习进度，逐章整理知识、例题与解题方法。"),
}
ICONS = {
    "arrow": '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    "external": '<path d="M14 4h6v6m0-6-9 9"/><path d="M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/>',
    "book": '<path d="M12 5c-3-2-6-2-9-1v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1zm0 0v15"/>',
    "folder": '<path d="M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7z"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "download": '<path d="M12 3v12m-5-5 5 5 5-5M4 16v4h16v-4"/>',
    "print": '<path d="M7 8V3h10v5M7 17H4V9h16v8h-3M7 14h10v7H7zM17 11h.01"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8" cy="8" r="1.5"/><path d="m3 17 6-6 4 4 3-3 5 5"/>',
    "chevron": '<path d="m9 5 7 7-7 7"/>',
    "up": '<path d="m6 12 6-6 6 6m-6-6v15"/>',
    "github": '<path d="M9 20c-5 1-5-2-7-2m14 4v-4a3.5 3.5 0 0 0-1-2.7c3.3-.4 6.7-1.6 6.7-7A5.4 5.4 0 0 0 20.2 4a5 5 0 0 0-.1-3s-1.2-.4-4 1.5a14 14 0 0 0-7.2 0C6.1.6 4.9 1 4.9 1a5 5 0 0 0-.1 3A5.4 5.4 0 0 0 3.3 8.3c0 5.4 3.4 6.6 6.7 7A3.5 3.5 0 0 0 9 18v4" transform="translate(0 1) scale(.92)"/>',
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def icon(name: str) -> str:
    return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">' + ICONS[name] + "</svg>"


def href(target: str | Path, page: Path) -> str:
    relative = os.path.relpath(ROOT / target, page.parent).replace(os.sep, "/")
    return quote(relative, safe="/.-_~")


def entry_path(entry: dict) -> Path:
    return Path(entry["category"]) / entry["id"] / "index.html"


def validate() -> None:
    ids = set()
    for entry in ENTRIES:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]):
            raise ValueError(f"Invalid entry id: {entry['id']}")
        if entry["id"] in ids or entry["category"] not in CATEGORIES:
            raise ValueError(f"Duplicate id or unknown category: {entry['id']}")
        ids.add(entry["id"])
        date.fromisoformat(entry["updated"])
        if not entry["sections"]:
            raise ValueError(f"Entry has no sections: {entry['id']}")
        section_ids = set()
        for section in entry["sections"]:
            if not re.fullmatch(r"[a-z][a-z0-9-]*", section["id"]) or section["id"] in section_ids:
                raise ValueError(f"Invalid or duplicate section id: {section['id']}")
            section_ids.add(section["id"])
        for relative in [s["source"] for s in entry["sections"]] + [a["path"] for a in entry.get("attachments", [])]:
            source = (ROOT / relative).resolve()
            if not source.is_relative_to(ROOT) or not source.is_file():
                raise ValueError(f"Missing or unsafe source file: {relative}")


def layout(title: str, description: str, body: str, page: Path, active: str = "home", reader: bool = False) -> str:
    nav = []
    for key, label, target in [("home", "首页", "index.html"), ("preparation", "备课资料", "preparation/index.html"), ("chapters", "课堂章节", "chapters/index.html")]:
        current = ' aria-current="page"' if active == key else ""
        nav.append(f'<a href="{href(target,page)}"{current}>{label}</a>')
    nav.append(f'<a href="{href("index.html",page)}#guide">阅读与使用</a>')
    progress = '<div class="reading-progress" data-reading-progress aria-hidden="true"></div>' if reader else ""
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · {esc(SITE['title'])}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#20594e">
  <link rel="icon" type="image/svg+xml" href="{href('assets/favicon.svg',page)}">
  <link rel="stylesheet" href="{href('assets/site.css',page)}">
  <script src="{href('assets/site.js',page)}" defer></script>
</head>
<body id="top">
  <a class="skip" href="#main">跳到正文</a>
  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="{href('index.html',page)}" aria-label="数学小站首页">
        <img src="{href('assets/favicon.svg',page)}" alt="" width="40" height="40">
        <span class="brand-name">数学小站<span class="brand-en">PRIMARY MATH</span></span>
      </a>
      <nav class="main-nav" id="main-navigation" data-navigation aria-label="主导航">{''.join(nav)}</nav>
      <div class="header-actions">
        <span class="grade-pill">小学数学 · 五年级</span>
        <a class="github-link" href="{esc(SITE['repository'])}" target="_blank" rel="noopener noreferrer" aria-label="打开 GitHub 仓库">{icon('github')}<span>GitHub</span></a>
        <button class="menu-toggle" type="button" aria-label="展开或收起导航" aria-controls="main-navigation" aria-expanded="false" data-menu-toggle>{icon('menu')}</button>
      </div>
    </div>{progress}
  </header>
  {body}
  <footer class="site-footer"><div class="shell footer-inner"><span class="footer-brand">数学小站</span><p>让方法有来处，让知识连起来。</p><a href="{esc(SITE['repository'])}" target="_blank" rel="noopener noreferrer">在 GitHub 查看{icon('external')}</a></div></footer>
</body>
</html>
'''


def cover(entry: dict) -> str:
    formula = '1.25 × 3.2<span>× 0.25 = 1</span>' if entry['id'] == 'trial-decimals' else esc(entry['grade'])+'<span>数学笔记</span>'
    caption = '观察数的特点，发现运算的联系' if entry['id'] == 'trial-decimals' else ' · '.join(entry['topics'])
    return '<div class="note-cover" aria-hidden="true"><span class="cover-index">MATH NOTES</span><div class="cover-formula">'+formula+'</div><div class="cover-boxes"><i></i><i></i><i></i></div><span class="cover-label">'+esc(caption)+'</span></div>'


def card(entry: dict, page: Path) -> str:
    target = href(entry_path(entry), page)
    tags = "".join(f'<span class="topic-tag">{esc(topic)}</span>' for topic in entry["topics"])
    search_text = " ".join([entry["title"], entry["summary"], entry["grade"], *entry["topics"], *entry.get("keywords", [])])
    return f'''<article class="featured-note" data-entry data-topics="{esc(json.dumps(entry['topics'],ensure_ascii=False))}" data-search="{esc(search_text)}">
      {cover(entry)}
      <div class="note-body">
        <div class="note-meta"><span>{esc(entry['grade'])}</span><span class="meta-divider">/</span><span>{esc(CATEGORIES[entry['category']][0])}</span></div>
        <h3><a href="{target}">{esc(entry['title'])}</a></h3>
        <p>{esc(entry['summary'])}</p><div class="topic-tags">{tags}</div>
        <div class="note-bottom"><span>{esc(entry['updated'].replace('-','.'))} 更新 · {entry.get('figures',0)} 张图解</span><a href="{target}">开始阅读{icon('arrow')}</a></div>
      </div>
    </article>'''


def homepage() -> None:
    page = ROOT / "index.html"
    prep = sum(e["category"] == "preparation" for e in ENTRIES)
    chapters = sum(e["category"] == "chapters" for e in ENTRIES)
    latest = sorted(ENTRIES, key=lambda e: e["updated"], reverse=True)
    featured = "".join(card(entry, page) for entry in latest[:1])
    method_entry = next((entry for entry in ENTRIES if entry['id'] == 'trial-decimals'),None)
    primary = href(entry_path(method_entry),page) if method_entry else href("preparation/index.html",page)
    body = f'''<main id="main" class="shell">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <div class="eyebrow"><span class="dot"></span>一本持续生长的数学手册</div>
        <h1 id="hero-title">从一张试卷，<br>到<span>一整个学期。</span></h1>
        <p class="hero-description">把每一次备课、每一节课堂里的知识与方法，<br>整理成随时可以翻阅的学习路径。<br>从理解一道题，开始连接更多的数学。</p>
        <div class="hero-actions"><a class="button" href="{href('preparation/index.html',page)}">浏览备课资料{icon('arrow')}</a><a class="text-link" href="{href('chapters/index.html',page)}">查看课堂章节{icon('chevron')}</a></div>
        <div class="hero-foot"><span class="dash"></span><span>备课有思路</span><span>·</span><span>课堂有方法</span><span>·</span><span>复习有线索</span></div>
      </div>
      <div class="hero-art"><img src="{href('assets/math-notebook.svg',page)}" alt="小数简算笔记：把3.2拆成4乘0.8，再运用乘法运算律配对，得到1" width="640" height="510"><span class="art-caption">观察 → 理解 → 应用</span></div>
    </section>
    <section class="entrances" aria-label="内容导航">
      <a class="entrance" href="{href('preparation/index.html',page)}"><div class="entrance-top"><span class="entrance-icon">{icon('folder')}</span><span class="entrance-number">01 / PREPARE</span></div><h2>备课资料</h2><p>试卷解答、逐题考点与讲解思路</p><div class="entrance-bottom"><span class="status-tag">{prep} 份已收录</span>{icon('arrow')}</div></a>
      <a class="entrance" href="{href('chapters/index.html',page)}"><div class="entrance-top"><span class="entrance-icon">{icon('book')}</span><span class="entrance-number">02 / LEARN</span></div><h2>课堂章节</h2><p>按上课内容，逐章积累知识与方法</p><div class="entrance-bottom"><span class="status-tag {'muted' if chapters == 0 else ''}">{str(chapters)+' 章已收录' if chapters else '随课堂陆续更新'}</span>{icon('arrow')}</div></a>
      <a class="entrance" href="#guide"><div class="entrance-top"><span class="entrance-icon">{icon('grid')}</span><span class="entrance-number">03 / EXPLORE</span></div><h2>阅读与使用</h2><p>在线阅读、图解核对与打印备课</p><div class="entrance-bottom"><span class="status-tag muted">随时翻阅</span>{icon('arrow')}</div></a>
    </section>
    <section aria-labelledby="recent-title"><div class="section-heading"><div><div class="eyebrow">LATEST NOTES</div><h2 id="recent-title">最近整理</h2></div><a class="text-link" href="{href('preparation/index.html',page)}">全部备课资料{icon('arrow')}</a></div>
      <div class="recent-grid">{featured}<aside class="method-card"><div class="eyebrow">A TEACHING NOTE</div><h3>先发现配对关系，<br>再拆分因数。</h3><p>怎样让孩子想到把3.2拆成4×0.8？<br>从已有的小数知识出发，<br>把“算得快”讲成“想得明白”。</p><a class="text-link" href="{primary}#detail">在逐题讲解中查看{icon('arrow')}</a></aside></div>
    </section>
    <section class="guide" id="guide" aria-labelledby="guide-title"><div class="guide-panel"><div class="guide-heading"><div class="eyebrow">HOW TO USE</div><h2 id="guide-title">一份资料，三种打开方式</h2><p>顺着自己的节奏，找到需要的内容。</p></div><div class="guide-steps"><div class="guide-step"><span>01</span><h3>课前，梳理方法</h3><p>阅读逐题解析，明确考点、解题依据与容易出错的地方。</p></div><div class="guide-step"><span>02</span><h3>做完，核对答案</h3><p>跳转到答案速查，再结合图形示意检查过程与方向。</p></div><div class="guide-step"><span>03</span><h3>课堂，随时翻阅</h3><p>手机或电脑都能阅读，也可以下载讲义、打印后使用。</p></div></div></div></section>
  </main>'''
    page.write_text(layout("首页",SITE["description"],body,page),encoding="utf-8")


def breadcrumb(page: Path, category: str, title: str | None = None) -> str:
    label = CATEGORIES[category][0]
    pieces = [f'<a href="{href("index.html",page)}">首页</a>', icon("chevron")]
    if title:
        pieces += [f'<a href="{href(category+"/index.html",page)}">{label}</a>', icon("chevron"), f'<span>{esc(title)}</span>']
    else:
        pieces += [f'<span>{label}</span>']
    return '<div class="breadcrumb" aria-label="当前位置">' + "".join(pieces) + "</div>"


def library(category: str) -> None:
    page = ROOT / category / "index.html"
    page.parent.mkdir(parents=True,exist_ok=True)
    title, english, description = CATEGORIES[category]
    entries = sorted([e for e in ENTRIES if e["category"] == category],key=lambda e:e["updated"],reverse=True)
    if entries:
        topics = list(dict.fromkeys(t for e in entries for t in e["topics"]))
        filters = '<button type="button" class="filter" data-filter="全部" aria-pressed="true">全部</button>' + "".join(f'<button type="button" class="filter" data-filter="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in topics)
        contents = f'''<div class="library-toolbar"><div class="filter-list" role="group" aria-label="按考点筛选">{filters}</div><label class="search">{icon('search')}<span class="visually-hidden">搜索题目、考点或方法</span><input type="search" placeholder="搜索题目、考点或方法" data-search autocomplete="off"></label></div>
        <section class="library-results" aria-label="资料列表"><p class="results-count" data-results-count role="status" aria-live="polite">共 {len(entries)} 份资料</p><div class="library-grid">{''.join(card(e,page) for e in entries)}</div><div class="no-results" data-no-results hidden><p>暂时没有找到匹配的资料，试试其他关键词。</p><button type="button" data-reset-search>清除搜索与筛选</button></div></section>'''
    else:
        contents = f'''<section class="empty-state"><div class="empty-symbol">{icon('book')}</div><h2>下一节课，从这里接着写。</h2><p>课堂章节会随着实际教学进度陆续补充。<br>现在可以先从试课备课资料开始，查看答案与讲解思路。</p><a class="button" href="{href('preparation/index.html',page)}">先看备课资料{icon('arrow')}</a></section>'''
    body = f'''<main id="main" class="shell">{breadcrumb(page,category)}<section class="library-intro"><div><div class="eyebrow">{english}</div><h1>{title}</h1><p>{description}</p></div><div class="library-count"><strong>{len(entries):02d}</strong><span>{'份资料' if category=='preparation' else '个章节'}</span></div></section>{contents}</main>'''
    page.write_text(layout(title,description,body,page,category),encoding="utf-8")


def resolve_content_url(url: str, source: Path, page: Path) -> str:
    if url.startswith("#") or urlsplit(url).scheme in ("https","http","mailto"):
        return url
    if re.match(r"^[A-Za-z]:[\\/]",url):
        # Backwards compatibility for source documents authored before publication.
        marker = "备课资料/"
        normalized = url.replace("\\","/")
        if marker not in normalized:
            raise ValueError(f"Nonportable URL in {source}: {url}")
        target = ROOT / "备课资料" / normalized.split(marker,1)[1]
    else:
        target = source.parent / url
    target = target.resolve()
    if not target.is_relative_to(ROOT) or not target.is_file():
        raise ValueError(f"Broken content link in {source}: {url}")
    for entry in ENTRIES:
        for section in entry["sections"]:
            if target == (ROOT / section["source"]).resolve():
                return href(entry_path(entry),page) + "#" + section["id"]
    return href(target.relative_to(ROOT),page)


def inline(text: str, source: Path, page: Path) -> str:
    protected = []
    def protect(value: str) -> str:
        protected.append(value)
        return f"\x00{len(protected)-1}\x00"
    def image_match(match: re.Match) -> str:
        url = resolve_content_url(match.group(2),source,page)
        return protect(f'<img src="{esc(url)}" alt="{esc(match.group(1))}" loading="lazy" decoding="async">')
    def link_match(match: re.Match) -> str:
        url = resolve_content_url(match.group(2),source,page)
        attrs = ' target="_blank" rel="noopener noreferrer"' if urlsplit(url).scheme in ("http","https") else ""
        return protect(f'<a href="{esc(url)}"{attrs}>{esc(match.group(1))}</a>')
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",image_match,text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",link_match,text)
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",text)
    text = re.sub(r"`([^`]+)`",r"<code>\1</code>",text)
    return re.sub(r"\x00(\d+)\x00",lambda m:protected[int(m.group(1))],text)


def markdown(source: Path, page: Path, prefix: str) -> tuple[str,list[tuple[str,str]]]:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    out, toc = [], []
    index = heading_index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            code = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index]); index += 1
            out.append("<pre><code>"+esc("\n".join(code))+"</code></pre>")
            index += 1
            continue
        if line.startswith("|") and index+1 < len(lines) and re.fullmatch(r"\|[\s:|\-]+\|",lines[index+1]):
            cells = lambda row: [part.strip() for part in row.strip().strip("|").split("|")]
            out.append('<div class="table-wrap"><table><thead><tr>'+"".join("<th>"+inline(c,source,page)+"</th>" for c in cells(line))+"</tr></thead><tbody>")
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                out.append("<tr>"+"".join("<td>"+inline(c,source,page)+"</td>" for c in cells(lines[index]))+"</tr>")
                index += 1
            out.append("</tbody></table></div>")
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)",line)
        if heading:
            original_level = len(heading[1])
            if original_level > 1:
                level = min(6,original_level+1)
                heading_index += 1
                anchor = f"{prefix}-{heading_index}"
                out.append(f'<h{level} id="{anchor}">'+inline(heading[2],source,page)+f'</h{level}>')
                if original_level == 2:
                    toc.append((anchor,heading[2]))
            index += 1
            continue
        if line == "---":
            out.append("<hr>");index += 1;continue
        ordered = re.match(r"^\d+\. ",line)
        if line.startswith("- ") or ordered:
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>")
            while index < len(lines) and (re.match(r"^\d+\. ",lines[index]) if ordered else lines[index].startswith("- ")):
                item = re.sub(r"^\d+\. ","",lines[index]) if ordered else lines[index][2:]
                out.append("<li>"+inline(item,source,page)+"</li>")
                index += 1
            out.append(f"</{tag}>")
            continue
        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not re.match(r"^(#|\||```|- |\d+\. |---$)",lines[index]):
            paragraph.append(lines[index]);index += 1
        content = "".join(inline(part.rstrip(),source,page)+("<br>" if part.endswith("  ") else " ") for part in paragraph).rstrip()
        out.append("<p>"+content+"</p>")
    return "\n".join(out),toc


def lesson(entry: dict) -> None:
    page = ROOT / entry_path(entry)
    page.parent.mkdir(parents=True,exist_ok=True)
    section_html, toc = [], []
    for number, section in enumerate(entry["sections"],1):
        content, headings = markdown(ROOT / section["source"],page,section["id"])
        section_html.append(f'<section class="reading-section" id="{section["id"]}" aria-labelledby="{section["id"]}-title"><div class="section-label"><span></span>PART {number:02d}</div><h2 id="{section["id"]}-title">{esc(section["title"])}</h2><div class="prose">{content}</div></section>')
        toc.append(f'<a class="toc-main" href="#{section["id"]}">{esc(section["title"])}</a>')
        if section["id"] != "quick":
            toc.extend(f'<a class="toc-sub" href="#{anchor}">{esc(title)}</a>' for anchor,title in headings)
    resources = []
    actions = []
    for attachment in entry.get("attachments",[]):
        kind = attachment["kind"]
        symbol = "image" if kind == "image" else "download" if kind == "pdf" else "book"
        link = href(attachment["path"],page)
        attrs = ' download' if kind == "pdf" else ' target="_blank" rel="noopener noreferrer"'
        resources.append(f'<a href="{link}"{attrs}>{icon(symbol)}{esc(attachment["title"])}</a>')
        if kind in ("image","paper","pdf"):
            label = "查看原卷" if kind in ("image","paper") else "下载 PDF"
            actions.append(f'<a class="button secondary" href="{link}"{attrs}>{icon(symbol)}{label}</a>')
    toc_html = '<nav class="toc" aria-label="本节目录">'+"".join(toc)+"</nav>"
    switches = "".join(f'<a href="#{s["id"]}">{esc(s["title"])}</a>' for s in entry["sections"])
    body = f'''<main id="main" class="shell">{breadcrumb(page,entry['category'],entry['title'])}
    <div class="reader-layout"><aside class="reader-sidebar"><p class="sidebar-label">IN THIS NOTE / 本节目录</p>{toc_html}<div class="sidebar-resources"><p class="sidebar-label">原卷与讲义</p>{''.join(resources)}</div></aside>
      <div class="reader-main"><header class="reader-header"><div class="eyebrow">{CATEGORIES[entry['category']][1]}</div><h1>{esc(entry['title'])}</h1><p>{esc(entry['summary'])}</p><div class="note-meta"><span>{esc(entry['grade'])}</span><span class="meta-divider">/</span><span>{esc(' · '.join(entry['topics']))}</span><span class="meta-divider">/</span><span>{esc(entry['updated'].replace('-','.'))} 更新</span></div><div class="reader-actions"><button class="button" type="button" data-print>{icon('print')}打印本节资料</button>{''.join(actions)}</div></header>
        <div class="reader-switch">{switches}<span>先独立完成，再核对方法。</span></div>
        <details class="reader-mobile-toc"><summary>展开本节目录</summary>{toc_html}</details>
        {''.join(section_html)}<a class="back-top" href="#top">{icon('up')}回到本节顶部</a>
      </div>
    </div></main>'''
    page.write_text(layout(entry["title"],entry["summary"],body,page,entry["category"],True),encoding="utf-8")


def main() -> None:
    validate()
    homepage()
    for category in CATEGORIES:
        library(category)
    for entry in ENTRIES:
        lesson(entry)
    print(f"Built {3+len(ENTRIES)} HTML pages from {len(ENTRIES)} catalog entries.")


if __name__ == "__main__":
    main()
