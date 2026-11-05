#!/usr/bin/env python3
"""Build isolated outputs and verify the reading/media contract without extra dependencies."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from email.utils import parsedate_to_datetime
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'exampleSite'

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.images, self.videos, self.sources, self.elements = [], [], [], [], []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == 'img': self.images.append(attrs)
        if tag == 'video': self.videos.append(attrs)
        if tag == 'source': self.sources.append(attrs)
        for key in ('href', 'src', 'poster'):
            if key in attrs: self.links.append(attrs[key])
        for candidate in attrs.get('srcset', '').split(','):
            if candidate.strip(): self.links.append(candidate.strip().split()[0])

def require(condition, message):
    if not condition: raise AssertionError(message)

def run(hugo, source, config, output, extra=(), expect_ok=True):
    env = dict(os.environ, HUGO_RESOURCEDIR=str(output.parent / (output.name+'-resources')))
    result = subprocess.run([hugo, '--source', str(source), '--config', str(config),
                             '--destination', str(output), '--cacheDir', str(output.parent/'cache'),
                             '--noBuildLock', *extra], capture_output=True, text=True, env=env)
    require((result.returncode == 0) == expect_ok, result.stdout+result.stderr)
    return result

def audit_links(output):
    for file in output.rglob('*.html'):
        page = Page(file.read_text())
        for url in page.links:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path: continue
            path = unquote(parsed.path)
            target = output / path.lstrip('/') if path.startswith('/') else file.parent / path
            require(target.is_file() or (target / 'index.html').is_file(), f'Broken link in {file}: {url}')
        for image in page.images:
            require(all(key in image for key in ('alt','width','height')), f'Image metadata missing: {file}')

def contrast(a, b):
    def luminance(color):
        channels = [int(color[i:i+2],16)/255 for i in (1,3,5)]
        return sum(v*w for v,w in zip([c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in channels], [.2126,.7152,.0722]))
    values = sorted([luminance(a),luminance(b)])
    return (values[1]+.05)/(values[0]+.05)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hugo', default='hugo')
    args = parser.parse_args()
    print(subprocess.check_output([args.hugo, 'version'],text=True).strip())
    scratch = EXAMPLE / '.checks'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='travelbook-check-', dir=scratch) as tmp:
        work = Path(tmp)
        prod, preview = work/'production', work/'preview'
        for out, flags in ((prod,()),(preview,('--buildDrafts','--buildFuture'))):
            run(args.hugo, EXAMPLE, EXAMPLE/'hugo.toml', out, flags)
            audit_links(out)
        home = (prod/'index.html').read_text()
        entry = (prod/'dispatches/latest/index.html').read_text()
        require('Sample location' in home and 'Mile 142' in home, 'Homepage location/mileage missing')
        require('Read entry' in home and 'Earlier days' not in home, 'Compact homepage navigation missing')
        require('Synthetic landscape fixture for the proposed media interface.' not in home, 'Homepage renders full long entry')
        require('srcset=' in entry, 'Entry responsive variants missing')
        require('aria-label="Main navigation"' in home, 'Header navigation missing')
        require(len(Page(home).images) == 2, 'Configured notebook photographs missing')
        require('Explore the journey' in home and 'Notes &amp; learnings' in home, 'Content discovery sections missing')
        require(not (prod/'dispatches/draft-only').exists(), 'Draft leaked into production')
        require((preview/'dispatches/draft-only/index.html').is_file(), 'Draft preview missing')
        media = json.loads((EXAMPLE/'data/media.json').read_text())
        require(not (prod/media['media:draft']['src']).exists(), 'Draft-only asset leaked')
        require((preview/media['media:draft']['src']).is_file(), 'Draft asset missing in preview')
        titleless = (prod/'dispatches/text-only/index.html').read_text()
        require('2026-01-01</a></h1>' in titleless, 'Titleless entry date fallback missing')
        journey = (prod/'journeys/test-sequence/index.html').read_text()
        require(journey.index('dispatches/text-only/') < journey.index('dispatches/latest/'), 'Journey start/latest order wrong')
        video = Page((prod/'dispatches/video/index.html').read_text()).videos[0]
        require(all(attr in video for attr in ('autoplay','loop','muted','playsinline','controls','poster')), 'Native ambient video contract incomplete')
        require(ET.parse(prod/'index.xml').findall('./channel/item') == [], 'Fixtures appeared in RSS')
        # Extracted theme builds without relying on parent layouts or prototype directories.
        site = work/'standalone';site.mkdir()
        shutil.copytree(ROOT, site/'themes/travelbook', ignore=shutil.ignore_patterns('.git', '.checks', 'public', 'resources', 'cache', '__pycache__'))
        (site/'hugo.toml').write_text((site/'themes/travelbook/exampleSite/minimal.hugo.toml').read_text()+'\n[params.indieweb]\nrelme = ["https://social.example.org/test"]\nwebmention = "https://webmention.example.org/receive"\nauthorization_endpoint = "https://auth.example.org/authorize"\ntoken_endpoint = "https://auth.example.org/token"\nmicropub = "https://publish.example.org/micropub"\nindieauth-metadata = "https://auth.example.org/metadata"\n')
        content = site/'content';content.mkdir()
        empty = work/'empty'
        run(args.hugo,site,site/'hugo.toml',empty)
        require('Older dispatches' not in (empty/'index.html').read_text(), 'Empty site shows an archive')
        bundle = content/'posts/stable-name';bundle.mkdir(parents=True)
        note = bundle/'index.md'
        note.write_text('---\ntitle: First title\ndate: 2026-01-01\nlastmod: 2026-01-02\nauthors: [Test Author]\nsummary: Author-written summary\ntags: [sample]\nsyndication: [https://social.example.org/post/1]\nin_reply_to: https://example.org/original\nlike_of: https://example.org/liked\nrepost_of: https://example.org/reposted\nlocation: Test place\nmileage: 0\n---\nOpening paragraph.\n\n<!--more-->\n\nComplete trailing paragraph.\n')
        (content/'contact.md').write_text('---\ntitle: Contact\n---\nStructural page.')
        cairn = content/'cairns/guide';cairn.mkdir(parents=True)
        (cairn/'index.md').write_text('---\ntitle: Guide\ndate: 2026-01-01\n---\nGuide body.')
        # Unlinked introductions must remain discoverable, beyond four, regardless of weight.
        for number in range(1, 7):
            intro = content/f'journeys/trip-{number}'
            intro.mkdir(parents=True)
            (intro/'_index.md').write_text(f'---\ntitle: Trip {number}\ndate: 2026-01-0{number}\nweight: {number}\nauthors: [Journey Author]\nlastmod: 2026-02-01\n---\nTrip introduction.')
        single = work/'single';run(args.hugo,site,site/'hugo.toml',single)
        audit_links(single)
        single_home = (single/'index.html').read_text()
        for listing in (single_home, (single/'journeys/index.html').read_text()):
            positions = [listing.index(f'href="/journeys/trip-{n}/"') for n in range(6, 0, -1)]
            require(positions == sorted(positions), 'Journey list omitted unlinked trips or ignored date ordering')
        intro_html = (single/'journeys/trip-6/index.html').read_text()
        require('Journey Author' in intro_html and 'Jan 6, 2026</time>' in intro_html
                and 'Feb 1, 2026</time>' in intro_html, 'Journey author/date/update metadata missing')

        parsed = Page((single/'dispatches/stable-name/index.html').read_text())
        classes = {name for _, attrs in parsed.elements for name in attrs.get('class', '').split()}
        require({'h-entry','p-name','u-url','u-uid','dt-published','dt-updated','e-content','p-author','h-card','p-location','p-summary','p-category','u-syndication','u-in-reply-to','u-like-of','u-repost-of'} <= classes, 'IndieWeb entry fields missing')
        rels = {attrs.get('rel') for _, attrs in parsed.elements}
        require({'me','webmention','authorization_endpoint','token_endpoint','micropub','indieauth-metadata'} <= rels, 'Configured IndieWeb discovery missing')
        require(any('u-url' in attrs.get('class','').split() and attrs.get('href') == 'https://example.org/dispatches/stable-name/' for _, attrs in parsed.elements), 'Entry microformat URL is not canonical')
        require('h-entry' not in {c for _, attrs in Page((single/'contact/index.html').read_text()).elements for c in attrs.get('class','').split()}, 'Structural page marked as a post')
        require('authorization_endpoint' not in home and 'webmention' not in home, 'Unconfigured endpoints advertised')
        require('Complete trailing paragraph.' not in single_home and 'Mile 0' in single_home, 'Homepage excerpt or zero mileage incorrect')
        require('Older dispatches' not in single_home, 'Single entry shows an archive')
        items = ET.parse(single/'index.xml').findall('./channel/item')
        require({item.findtext('title') for item in items} == {'First title','Guide'}, 'RSS membership wrong')
        for feed in ('dispatches/index.xml','cairns/index.xml'):
            require(len(ET.parse(single/feed).findall('./channel/item')) == 1, 'Section feed wrong')
        # Reader-facing RSS: full content, XML escaping, footer, and portable links/media.
        rss_site = work/'rss-site'
        shutil.copytree(site, rss_site)
        rss_config = rss_site/'hugo.toml'
        rss_config.write_text(rss_config.read_text().replace('title = "The Passage"', 'title = "Roads & Rivers"')
                              .replace('[params]', '[params]\nrss_footer = "Thanks for keeping RSS alive. — Mark & Valarie"'))
        rss_note = rss_site/'content/posts/stable-name/index.md'
        rss_note.write_text(note.read_text().replace('title: First title', 'title: "Roads & rivers <a story>"')
                            .replace('authors: [Test Author]', 'authors: ["Mark & Valarie"]')
                            + '\n## Route\n\n![Route & river](photo.png "Map & notes")\n\n'
                            '[Download](notes.txt?x=1&y=2) · [Jump](#route) · [Contact](/contact/)\n')
        shutil.copyfile(EXAMPLE/'content/cairns/checklist/images/diagram.png', rss_note.parent/'photo.png')
        (rss_note.parent/'notes.txt').write_text('Route notes')
        for slug, fields in [('draft-rss', 'draft: true'), ('fixture-rss', 'fixture: true'),
                             ('future-rss', 'date: 2999-01-01')]:
            (rss_site/f'content/posts/{slug}.md').write_text(f'---\ntitle: {slug}\n{fields}\n---\nExcluded.')
        for name, flags in [('rss-production', ()), ('rss-preview', ('--buildDrafts', '--buildFuture', '--minify'))]:
            rss_out = work/name
            run(args.hugo, rss_site, rss_config, rss_out, flags)
            for feed_path in ('index.xml', 'dispatches/index.xml', 'cairns/index.xml'):
                channel = ET.parse(rss_out/feed_path).find('channel')
                require('Roads & Rivers' in channel.findtext('title'), 'RSS channel escaping incorrect')
                self_link = channel.find('{http://www.w3.org/2005/Atom}link')
                require(self_link is not None and self_link.attrib == {
                    'href': 'https://example.org/'+feed_path, 'rel': 'self', 'type': 'application/rss+xml'},
                    'RSS self-link missing or incorrect')
                feed_items = channel.findall('item')
                require(all(i.findtext('title') not in {'draft-rss','fixture-rss','future-rss'} for i in feed_items),
                        'Unpublished content leaked into RSS')
                for item in feed_items:
                    require(parsedate_to_datetime(item.findtext('pubDate')).tzinfo is not None, 'RSS date lacks timezone')
                    body = item.findtext('description')
                    require(body == item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded'),
                            'Readers receive different full-post content')
                    require(body.count('Thanks for keeping RSS alive.') == 1, 'RSS footer absent or duplicated')
                    require('Follow via RSS' not in body, 'Missing Follow page linked in RSS')
                    if item.findtext('link').endswith('/stable-name/'):
                        require(item.findtext('title') == 'Roads & rivers <a story>', 'RSS title double escaped')
                        require(item.findtext('{http://purl.org/dc/elements/1.1/}creator') == 'Mark & Valarie',
                                'RSS author escaping incorrect')
                        require('Opening paragraph.' in body and 'Complete trailing paragraph.' in body,
                                'RSS truncated at excerpt break')
                        require('<p>Opening paragraph.</p>' in body, 'RSS HTML not decoded correctly')
                        require('Map &amp; notes' in body, 'Image caption missing from RSS')
                        parsed_feed = Page(body)
                        require(parsed_feed.images[0]['src'] == 'https://example.org/dispatches/stable-name/photo.png',
                                'RSS image URL not portable')
                        for link in ('https://example.org/dispatches/stable-name/notes.txt?x=1&y=2',
                                     'https://example.org/dispatches/stable-name/#route', 'https://example.org/contact/'):
                            require(link in parsed_feed.links, f'RSS link not portable: {link}')
            require('Thanks for keeping RSS alive.' not in (rss_out/'dispatches/stable-name/index.html').read_text(),
                    'RSS footer leaked into article HTML')
        (rss_site/'content/follow.md').write_text('---\ntitle: Follow via RSS\n---\nSubscribe here.')
        rss_follow = work/'rss-follow'
        run(args.hugo, rss_site, rss_config, rss_follow)
        follow_body = ET.parse(rss_follow/'index.xml').findtext('./channel/item/description')
        require('https://example.org/follow/' in follow_body, 'Authored Follow page missing from RSS footer')
        article_html = (rss_follow/'dispatches/stable-name/index.html').read_text()
        article_links = Page(article_html)
        require(any(tag == 'link' and attrs.get('rel') == 'alternate'
                    and attrs.get('type') == 'application/rss+xml'
                    and attrs.get('href') == 'https://example.org/index.xml'
                    for tag, attrs in article_links.elements), 'Article does not advertise the main RSS feed')
        require('/follow/' in article_links.links, 'Authored Follow page missing from site navigation')
        # Explicit UTC updates cross calendar days and DST offsets in Colorado.
        original_note = note.read_text()
        config_file = site/'hugo.toml'
        config_file.write_text(config_file.read_text().replace('[params]', '[params]\ndate_timezone = "America/Denver"'))
        for stamp, expected in (('2026-11-01T01:41:38Z', '2026-10-31T19:41:38-06:00'),
                                ('2026-12-01T01:41:38Z', '2026-11-30T18:41:38-07:00')):
            note.write_text(original_note.replace('lastmod: 2026-01-02', 'lastmod: '+stamp))
            zone_output = work/'timezone'
            run(args.hugo, site, config_file, zone_output)
            html = (zone_output/'dispatches/stable-name/index.html').read_text()
            require(f'class="dt-updated" datetime="{expected}"' in html,
                    'Update timestamp did not convert to configured timezone')
        note.write_text(original_note)
        note.write_text(note.read_text().replace('First title','Changed title'))
        renamed = work/'renamed';run(args.hugo,site,site/'hugo.toml',renamed)
        require((renamed/'dispatches/stable-name/index.html').is_file(), 'Title edit changed address')
        for number in range(7):
            (content/f'posts/older-{number}.md').write_text(f'---\ntitle: Older {number}\ndate: 2025-01-0{number+1}\n---\nSmall note.')
        archive = work/'archive';run(args.hugo,site,site/'hugo.toml',archive)
        archive_home = (archive/'index.html').read_text()
        require('Older 6' not in archive_home and 'Older 1' not in archive_home, 'Homepage unexpectedly includes the Journal archive')
        require('Journal</a>' in archive_home, 'Journal navigation missing')
        require(len(Page(single_home).images) == 0, 'Text-only site unexpectedly requires images')
        # Date/location headings are shared by page, archive, and RSS; coordinates accept zero.
        saved_note = note.read_text()
        note.write_text(saved_note.replace('title: Changed title\n', '').replace('location: Test place', 'location: Clarksdale, MS\nlat: 0\nlong: 0'))
        located = work/'located';run(args.hugo,site,site/'hugo.toml',located)
        located_entry = (located/'dispatches/stable-name/index.html').read_text()
        require('2026-01-01 Clarksdale, MS</a></h1>' in located_entry, 'Date/location heading missing')
        require('2026-01-01 Clarksdale, MS' in (located/'dispatches/index.html').read_text(), 'Archive date/location missing')
        require('2026-01-01 Clarksdale, MS' in [i.findtext('title') for i in ET.parse(located/'index.xml').findall('./channel/item')], 'RSS date/location missing')
        require('mlat=0' in located_entry and 'mlon=0' in located_entry, 'Zero coordinates lost')
        require('p-latitude' in located_entry and 'p-longitude' in located_entry, 'Geographic metadata missing')
        valid_note = note.read_text()
        for replacement, expected in [('lat: 91', 'Coordinates out of range'), ('lat: north', 'must be numeric')]:
            note.write_text(valid_note.replace('lat: 0', replacement))
            invalid = run(args.hugo,site,site/'hugo.toml',work/'invalid-geo',expect_ok=False)
            require(expected in invalid.stderr+invalid.stdout, 'Invalid coordinate error unclear')
        note.write_text(valid_note.replace('long: 0\n', ''))
        invalid = run(args.hugo,site,site/'hugo.toml',work/'missing-coordinate',expect_ok=False)
        require('Supply both lat and long' in invalid.stderr+invalid.stdout, 'Incomplete coordinate pair accepted')
        note.write_text(saved_note)
        note.write_text(note.read_text()+'\n![Missing photograph](missing.jpg)\n')
        failure = run(args.hugo,site,site/'hugo.toml',work/'broken',expect_ok=False)
        require('Missing local image' in failure.stderr+failure.stdout, 'Missing image did not fail clearly')
        print('PASS: isolated production/preview, local links, compact homepage, metadata, stable URLs, journeys, native video, responsive images, RSS, empty/single sites, draft asset exclusion, missing-media failure, standalone theme, and IndieWeb fields/discovery.')
        print(f'Prototype production output: {sum(p.stat().st_size for p in prod.rglob("*") if p.is_file()):,} bytes (includes synthetic video fixture).')
        for label, paper, ink, muted, accent in [('light','#fbf7ed','#14243a','#586171','#a63124'),('dark','#17212b','#f4eddf','#c4bcb0','#f2a18c')]:
            ratios = [contrast(paper,color) for color in (ink,muted,accent)]
            require(min(ratios)>=4.5, f'{label} text contrast below AA')
            print(f'{label} contrast: text {ratios[0]:.2f}:1, metadata {ratios[1]:.2f}:1, links {ratios[2]:.2f}:1')

if __name__ == '__main__': main()
