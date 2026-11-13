(() => {
  const config = window.DNBC_DOCS;
  const script = document.currentScript;
  const versionBase = new URL('../', script.src);
  const siteBase = new URL(config.root, versionBase);
  const currentPath = window.location.pathname.slice(versionBase.pathname.length) || 'index.html';
  const english = currentPath.startsWith('en/');
  const pagePath = english ? currentPath.slice(3) : currentPath;
  const text = (zh, en) => english ? en : zh;
  const current = config.versions.find(entry => entry.version === config.current);
  const destination = (entry, requestedPath) => {
    const exists = entry.pages.includes(requestedPath);
    const target = exists ? requestedPath : (requestedPath.startsWith('en/') ? 'en/index.html' : 'index.html');
    const url = new URL(entry.path + target, siteBase);
    url.search = window.location.search;
    if (!exists || !window.location.hash) return url;
    let anchor;
    try {
      anchor = decodeURIComponent(window.location.hash.slice(1));
    } catch (_) {
      return url;
    }
    const source = current.fragments[currentPath];
    const fragments = entry.fragments[target];
    if (!fragments) return url;
    const canonical = source?.aliases[anchor] || anchor;
    // Prefer the semantic heading ID, then known aliases for older links.
    const candidates = [canonical, anchor, ...Object.keys(source?.aliases || {})
      .filter(alias => source.aliases[alias] === canonical)];
    // Auto-numbered headings can refer to unrelated sections in another manual.
    const match = candidates.find(candidate => !/^_\d+$/.test(candidate) && fragments.anchors.includes(candidate));
    if (match) url.hash = fragments.aliases[match] || match;
    return url;
  };
  const ready = () => {
    const header = document.querySelector('.md-header__inner');
    if (!header || header.querySelector('.doc-version')) return;
    const label = document.createElement('label');
    label.className = 'doc-version';
    const caption = document.createElement('span');
    caption.textContent = text('版本', 'Version');
    const select = document.createElement('select');
    select.setAttribute('aria-label', text('切换文档版本', 'Documentation version'));
    for (const entry of config.versions) {
      const option = document.createElement('option');
      option.value = entry.version;
      option.textContent = entry.version + (entry.version === config.default ? text('（默认）', ' (default)') : '');
      option.selected = entry.version === config.current;
      select.append(option);
    }
    select.addEventListener('change', () => {
      const entry = config.versions.find(item => item.version === select.value);
      window.location.assign(destination(entry, currentPath).href);
    });
    label.append(caption, select);
    const language = header.querySelector('.md-header__option .md-select');
    if (language) {
      const link = document.createElement('a');
      link.className = 'doc-language';
      link.textContent = english ? '中文' : 'English';
      link.hreflang = english ? 'zh' : 'en';
      link.setAttribute('aria-label', english ? '切换到中文' : 'Switch to English');
      const updateLanguageLink = () => {
        link.href = destination(current, (english ? '' : 'en/') + pagePath).href;
      };
      updateLanguageLink();
      window.addEventListener('hashchange', updateLanguageLink);
      language.replaceWith(link);
      link.parentElement.before(label);
    } else {
      header.append(label);
    }
    if (config.current !== config.default) {
      const notice = document.createElement('aside');
      notice.className = 'doc-archive-notice';
      notice.setAttribute('aria-label', text('历史版本提示', 'Archived version'));
      notice.append(document.createTextNode(text('你正在阅读 3.1 历史文档。', 'You are reading the archived 3.1 manual. ')));
      const link = document.createElement('a');
      const latest = config.versions.find(item => item.version === config.default);
      const updateArchiveLink = () => { link.href = destination(latest, currentPath).href; };
      updateArchiveLink();
      window.addEventListener('hashchange', updateArchiveLink);
      link.textContent = text('查看 3.2 文档', 'Read the 3.2 manual');
      notice.append(link);
      document.querySelector('.md-content__inner')?.prepend(notice);
    }

    // Seamlessly follow browser/system dark mode preferences (no toggle icon)
    if (config.current === '3.2') {
      try {
        for (const key of Object.keys(localStorage)) {
          if (key.includes('__palette')) {
            localStorage.removeItem(key);
          }
        }
      } catch (e) {}

      const syncScheme = () => {
        const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.body.setAttribute('data-md-color-scheme', isDark ? 'slate' : 'default');
      };
      if (window.matchMedia) {
        const media = window.matchMedia('(prefers-color-scheme: dark)');
        if (media.addEventListener) {
          media.addEventListener('change', syncScheme);
        } else if (media.addListener) {
          media.addListener(syncScheme);
        }
        syncScheme();
      }
    }

    // Enhance parameter badges and semantic callouts in 3.2
    if (config.current === '3.2') {
      document.querySelectorAll('.md-typeset h4').forEach(h4 => {
        h4.childNodes.forEach(node => {
          if (node.nodeType === Node.TEXT_NODE && node.nodeValue) {
            const val = node.nodeValue;
            if (/\((?:必需|Required|可选|Optional|方式\d+|Option \d+|推荐|Recommended)\)/i.test(val)) {
              const span = document.createElement('span');
              span.innerHTML = val
                .replace(/\((必需|Required)\)/gi, '<span class="doc-badge doc-badge-req">$1</span>')
                .replace(/\((可选|Optional)\)/gi, '<span class="doc-badge doc-badge-opt">$1</span>')
                .replace(/\((方式\d+|Option \d+)\)/gi, '<span class="doc-badge doc-badge-mode">$1</span>')
                .replace(/\((推荐|Recommended)\)/gi, '<span class="doc-badge doc-badge-tip">$1</span>');
              node.replaceWith(span);
            }
          }
        });
      });

      document.querySelectorAll('.md-typeset blockquote').forEach(bq => {
        const strong = bq.querySelector('p:first-child > strong:first-child, strong:first-child');
        if (strong) {
          const t = strong.textContent.trim();
          if (/^(?:注意|警告|Warning|Caution)/i.test(t)) {
            bq.classList.add('doc-callout-warn');
          } else if (/^(?:提示|技巧|Tip|Note)/i.test(t)) {
            bq.classList.add('doc-callout-tip');
          } else if (/^(?:开始前|前置|要求|Prerequisite)/i.test(t)) {
            bq.classList.add('doc-callout-info');
          }
        }
      });
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();
})();
