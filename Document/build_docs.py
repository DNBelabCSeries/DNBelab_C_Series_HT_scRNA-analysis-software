#!/usr/bin/env python3
"""Build current bilingual documentation and the frozen 3.1 manual together."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
VERSIONS = [('3.2', ''), ('3.1', '3.1/')]


class PageAnchors(HTMLParser):
    """Record valid fragments and aliases belonging to the same heading."""
    def __init__(self):
        super().__init__()
        self.anchors = set()
        self.aliases = {}
        self.heading = None

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        anchor = attributes.get('id') or (attributes.get('name') if tag == 'a' else None)
        if anchor:
            self.anchors.add(anchor)
        if re.fullmatch(r'h[1-6]', tag):
            self.heading = anchor
        elif anchor and self.heading and anchor != self.heading:
            self.aliases[anchor] = self.heading

    def handle_endtag(self, tag):
        if re.fullmatch(r'h[1-6]', tag):
            self.heading = None


def version_manifest(version, prefix, output):
    fragments = {}
    for path in sorted(output.rglob('*.html')):
        page = PageAnchors()
        page.feed(path.read_text())
        fragments[path.relative_to(output).as_posix()] = {
            'anchors': sorted(page.anchors), 'aliases': page.aliases,
        }
    return {'version': version, 'path': prefix,
            'pages': sorted(fragments), 'fragments': fragments}


def prepare(source, target, version):
    target.mkdir(parents=True)
    shutil.copytree(source / 'doc', target / 'doc')
    for page in (source / 'home').glob('*.md'):
        shutil.copy2(page, target / page.name)
    shutil.copytree(ROOT / 'assets' / 'images', target / 'assets' / 'images')
    (target / 'stylesheets').mkdir()
    stylesheet = 'legacy.css' if version == '3.1' else 'extra.css'
    shutil.copy2(ROOT / 'assets' / 'stylesheets' / stylesheet, target / 'stylesheets' / 'extra.css')
    (target / 'javascripts').mkdir()
    (target / 'javascripts' / 'doc-controls.js').write_text('')
    for path in target.rglob('*.md'):
        content = path.read_text()
        if path.parent != target:
            content = re.sub(r'<(div|section|article)(?![^>]*\bmarkdown=)([^>]*)>',
                             r'<\1\2 markdown="block">', content)
        content = content.replace('markdown="1"', 'markdown="block"')
        # English suffixes are source names; both locales publish the same .html basename.
        def local_link(match):
            url = match.group(2)
            if urlsplit(url).scheme or url.startswith('//'):
                return match.group(0)
            url = url.replace('README.md', 'index.md')
            url = re.sub(r'\.en\.md(?=$|#)', '.md', url)
            if match.group(1) == 'href="':
                url = re.sub(r'\.md(?=$|#)', '.html', url)
            return match.group(1) + url + match.group(3)
        content = re.sub(r'(href=")([^"\n]+)(")|(\]\()([^\s)]+)(\))',
                         lambda m: local_link(m) if m.group(1) else
                         local_markdown_link(m), content)
        if path.name in ('json.md', 'json.en.md'):
            content = re.sub(r'^\s+(<(?:h4|img)\b.*)$', r'\1', content, flags=re.M)
        content = content.replace('](LICENSE)', '](https://github.com/MGI-tech-bioinformatics/'
                                  'DNBelab_C_Series_HT_scRNA-analysis-software/blob/version3.0/LICENSE)')
        path.write_text(content)


def local_markdown_link(match):
    url = match.group(5)
    if not urlsplit(url).scheme and not url.startswith('//'):
        url = url.replace('README.md', 'index.md')
        url = re.sub(r'\.en\.md(?=$|#)', '.md', url)
    return match.group(4) + url + match.group(6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    site = args.site_dir.resolve()
    # Reject all source directories and their descendants/ancestors.
    protected = [REPO / 'doc', ROOT / 'home', ROOT / 'assets', ROOT / 'versions',
                 ROOT / 'docs', ROOT / '.build']
    if site == REPO or site in REPO.parents or any(
        site == path or path in site.parents or site in path.parents for path in protected
    ):
        parser.error('Choose a dedicated site output directory outside source trees.')
    if site.exists() and any(site.iterdir()):
        known_site = site == ROOT / 'site' and (site / 'index.html').is_file()
        if not known_site and not (site / '.dnbc-docs-site').is_file():
            parser.error('Refusing to replace an unrelated nonempty directory.')
    ROOT.joinpath('.build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / '.build') as work:
        work = Path(work)
        outputs = {}
        for version, prefix in VERSIONS:
            source = ROOT if version == '3.2' else ROOT / 'versions' / version
            docs = work / version / 'docs'
            if version == '3.2':
                current = work / 'current'
                current.mkdir()
                shutil.copytree(REPO / 'doc', current / 'doc')
                shutil.copytree(ROOT / 'home', current / 'home')
                source = current
            prepare(source, docs, version)
            config = yaml.safe_load((ROOT / 'mkdocs.yml').read_text())
            config['docs_dir'] = str(docs)
            config['site_dir'] = str(work / version / 'site')
            config['copyright'] = ('Copyright &copy; 2026 MGI Tech Bioinformatics.<br>'
                                   'Documentation ' + version + (' · Archived / 历史版本' if version == '3.1'
                                   else ' · Updated 2026-10-23'))
            if version == '3.1':
                legacy_config = yaml.safe_load((source / 'mkdocs.yml').read_text())
                config['nav'] = legacy_config['nav']
                config['theme'] = legacy_config['theme']
                config['repo_name'] = legacy_config['repo_name']
                config['site_name'] = legacy_config['site_name']
                config['plugins'] = legacy_config['plugins']
                config['markdown_extensions'] = legacy_config['markdown_extensions']
            config_path = work / version / 'mkdocs.yml'
            config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
            subprocess.run([sys.executable, '-m', 'mkdocs', 'build', '--strict',
                            '-f', str(config_path)], check=True)
            output = work / version / 'site'
            # Raw HTML image URLs are not translated by the i18n plugin.
            shutil.copytree(output / 'doc' / 'images', output / 'en' / 'doc' / 'images', dirs_exist_ok=True)
            outputs[version] = output
            if version == '3.2':
                if (ROOT / 'docs').exists():
                    shutil.rmtree(ROOT / 'docs')
                shutil.copytree(docs, ROOT / 'docs')
        manifest = {'default': '3.2', 'versions': [
            version_manifest(v, prefix, outputs[v]) for v, prefix in VERSIONS]}
        controls = (ROOT / 'assets' / 'javascripts' / 'doc-controls.js').read_text()
        for version, prefix in VERSIONS:
            settings = {'current': version, 'root': '../' if prefix else './', **manifest}
            js = 'window.DNBC_DOCS = ' + json.dumps(settings, ensure_ascii=False) + ';\n' + controls
            (outputs[version] / 'javascripts' / 'doc-controls.js').write_text(js)
            if version == '3.2':
                (ROOT / 'docs' / 'javascripts' / 'doc-controls.js').write_text(js)
        # Build both versions before replacing the published tree.
        if site.exists():
            shutil.rmtree(site)
        shutil.copytree(outputs['3.2'], site)
        shutil.copytree(outputs['3.1'], site / '3.1')
        (site / 'versions.json').write_text(json.dumps(manifest, indent=2) + '\n')
        (site / '.dnbc-docs-site').write_text('Generated by Document/build_docs.py\n')
    print('Built default 3.2 and archived 3.1: ' + str(site / 'index.html'))


if __name__ == '__main__':
    main()
