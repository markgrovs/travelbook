# Travelbook

A standalone Hugo theme for a personal travel journal. The Field Notebook design uses warm paper, navy ink, rust accents, expressive serif headings, visible navigation, and optional overlapping photographs. A stable welcome sits beside a compact latest-entry excerpt; all journeys and up to three recent cairns are derived from content. Empty sections disappear. Entry pages and RSS retain the full text.

Requires Hugo 0.166.0 or later. All theme templates, CSS, JavaScript, and example configuration live in this folder; no prototype files are required. Fonts use locally available Lora/Inter with Iowan/Palatino/Georgia and Helvetica fallbacks. No font service is contacted.

## Use as a submodule

Install the theme in a consuming Hugo site:

```sh
git submodule add https://github.com/markgrovs/travelbook.git themes/travelbook
git submodule update --init --recursive
```

The repository is [markgrovs/travelbook](https://github.com/markgrovs/travelbook). Consuming sites pin a specific commit; upgrading the theme requires updating and committing the submodule pointer.

Select `theme = "travelbook"` in the consuming site's configuration. Existing site-level `layouts/` override theme templates: move or explicitly isolate those overrides when activating. The example site uses its own empty `layouts/` directory for this reason.

Copy the route, taxonomy, pagination, output, and markup settings from `exampleSite/minimal.hugo.toml` into your site configuration. Hugo 0.166.0 does not automatically merge those theme configuration categories. Optional site parameters: `author`, `tagline`, `introduction`, `instagram`. Homepage `_index.md` body takes precedence over `introduction`. Supplied content is used verbatim; no welcome or biography is generated. The minimal installation configuration is in `exampleSite/minimal.hugo.toml`; `exampleSite/hugo.toml` runs the labeled demo.

## Authoring

Journal entries are leaf bundles under `content/posts/<stable-name>/index.md`:

```yaml
---
title: "High Desert Pass"
date: 2026-09-30
location: "Colorado"
mileage: 142
---
```

Title is optional; ISO date plus supplied location is its fallback. `location` falls back to legacy `place`; mileage is optional. Bundle names determine URLs, independently of title. Optional `journeys: [stable-trip-id]` groups entries oldest first. Cairns use `content/cairns/`; About uses `content/about/index.md`. Root RSS contains published Journal and Cairns entries, excluding `fixture: true` and drafts.

```markdown
![Author-written alt text](images/photo.jpg "Optional visible caption")
```

Images resolve from page bundles; the optional `data/media.json` interface can point to pre-generated responsive assets. The theme never recompresses media. Missing required local images fail the build.

For a local MP4 in the same bundle:

```text
{{< ambient-video src="road.mp4" poster="images/poster.jpg" label="Road through the canyon" caption="Author-written note." >}}
```

The native player uses autoplay, loop, muted, playsinline, and controls. Browsers may block autoplay. A direct file link and controls remain available without JavaScript. The small enhancement supplies an explicit pause/play button and pauses for reduced-motion preferences. Native autoplay can begin briefly before the enhancement runs; omit ambient clips when strict motion-free delivery is required. Use a poster matching the video's aspect ratio. The theme renders explicitly delivered local MP4s; asset copying and any transcoding are the consuming publisher’s responsibility.

## Local checks

From the theme repository root:

```sh
python3 tests/check_theme.py --hugo hugo
node tests/appearance.cjs
hugo server --source exampleSite --renderToMemory --disableFastRender
```

The theme demo expects this checkout folder to be named `travelbook`. From a consuming site, use `hugo server --source themes/travelbook/exampleSite`. The Next Mountain Overland site's `scripts/check_travelbook.py` also checks its authored content and deployment configuration.

## Appearance

The masthead uses a large, mixed-case serif title. The Light/Dark buttons initially follow the device preference and store an explicit choice locally in the browser. The choice is applied before the stylesheet loads and persists between pages and visits. Storage failures leave the controls functional for the current page. Without JavaScript, controls are hidden and appearance follows the device through CSS.

## IndieWeb

Journal and Cairn pages expose `h-entry` with author `h-card`, `e-content`, canonical `u-url`/`u-uid`, publication/update dates, supplied location, and optional summary/categories. The homepage and entry lists expose `h-feed`; structural pages remain ordinary pages. Footer identity uses `h-card`, and the Instagram link uses `rel="me"`.

Optional post fields:

```yaml
summary: "An author-written summary"
lastmod: 2026-09-30
syndication: ["https://social.example.org/post/123"]
in_reply_to: "https://example.org/original"
like_of: "https://example.org/liked"
repost_of: "https://example.org/reposted"
```

Omit fields that do not apply. These describe an entry; they do not send Webmentions or publish social posts. `authors` accepts a name or list of names, falling back to site `params.author`. `params.indieweb.author_url` optionally supplies an author profile URL; otherwise the site homepage is used.

Optional site configuration (replace examples with your actual services; leave unconfigured services absent):

```toml
[params.indieweb]
  relme = ["https://social.example.org/your-profile"]
  # author_url = "https://example.org/"
  # webmention = "https://your-service.example/receive"
  # authorization_endpoint = "https://your-service.example/authorize"
  # token_endpoint = "https://your-service.example/token"
  # indieauth-metadata = "https://your-service.example/metadata"
  # micropub = "https://your-service.example/micropub"
```

Profile verification also requires the remote profile to link back to your site. Endpoint discovery is supported; hosting an IndieAuth, Webmention, or Micropub service is separate work. No third-party service is enabled automatically.

The markup follows [h-entry](https://microformats.org/wiki/h-entry) and [rel-me](https://indieweb.org/rel-me); Webmention discovery follows the [W3C recommendation](https://www.w3.org/TR/webmention/).

## Field Notebook homepage

Optional site parameters: `home_heading` (defaults to “A journal of our travels”) and `home_photos` (up to two asset records with `src`, `alt`, and optional `caption`). Existing homepage body / `introduction` supplies the welcome. Photographs must be approved delivery assets in the optional homepage bundle or the consuming site's `assets/` directory, never private originals. They are not taken automatically from the latest entry, so the opening can remain stable between updates. No photographs are required; the text-only layout keeps the latest note beneath the welcome, preserving the reading order.

```toml
[[params.home_photos]]
  src = "home/road.jpg"
  alt = "Author-written description"
  caption = "Optional author-written caption"
```

Missing configured photographs fail the build. Images retain their aspect ratios and dimensions; this interface does not generate publisher derivatives. The demo uses labeled synthetic fixtures. Obsidian routing and delivery-file generation belong to the consuming site’s publisher, not this theme. Do not edit publisher-owned text to configure the theme.


### Complete homepage composition

`params.home_page` may name a headless homepage bundle. Its Markdown body supplies the introduction and `home_photos` lists up to two bundle resources with alt text and optional captions. If that page is absent (for example, a draft bundle in a production build), the normal homepage body/settings apply. Fixture homepage bundles produce a visible design-review notice and noindex metadata. Ordinary homepages do not.

The latest Journal excerpt always follows the welcome. On desktop the opening photos occupy the right column; on phones they follow the latest note. The lower row presents all Journey terms sorted newest date first, with the first as the featured trip, and three Cairns sorted newest first. Optional `thumbnail: photo.jpg` resolves a resource in the corresponding Journey or Cairn bundle. Missing configured thumbnails fail builds; omitted thumbnails leave text-only rows. Decorative thumbnails have empty alt text because the adjacent link identifies the destination. The Journal archive remains reachable through navigation. Appearance controls live in the landscape footer.

## Journal location metadata

Use these YAML properties for Journal entries and Cairns; Journey introductions can carry the same location context. Coordinates and labels are supplied by the authoring workflow. The theme performs no geocoding or device capture.

```yaml
---
date: 2026-10-31
lat: 34.20
long: -90.57
location: "Clarksdale, MS"
journeys: [fall-motorcycle-trip-florida]
draft: true
---
```

Coordinates in this example and the design fixtures are approximate illustrative values, not captured travel positions. `lat` and `long` are decimal degrees, with negative longitude west of Greenwich. Latitude must be within -90..90 and longitude within -180..180. Supply both together; zero is valid. Empty properties are accepted while composing a draft. Existing content without coordinates remains compatible. `location` is the supplied display label; the theme does not infer it from coordinates. Legacy `place` remains a fallback.

Omit `title` for daily notes: the heading becomes `YYYY-MM-DD location`, consistently on the entry, Journal/Journey lists, browser title, and RSS. With no place label, the fallback is the ISO date. A deliberately supplied title still wins for longer narratives and Cairns, whose date/location metadata remains visible. Stable filenames continue to determine URLs. Entry metadata uses an ISO date followed by the location. Coordinates power a normal OpenStreetMap link and h-geo markup, without embedding a live map or making a lookup request.

`journeys` is a list of stable Journey identifiers; Journal entries and Cairns can belong to the same trip. Lists are generated automatically. The local archetypes provide the properties but do not install an Obsidian template. Capture tools and publishers are maintained separately; these fields define the theme’s content interface.

Set `params.date_timezone` to an IANA timezone such as `America/Denver` to display update timestamps in that zone, including timestamps supplied by Git. Set Hugo’s top-level `timeZone` for parsing dates without an explicit offset. Publication dates retain their authored calendar date.

### Journey discovery and metadata

The homepage and Journeys archive list all Journeys by date, newest first, ignoring weight. Introductions are visible before any daily entries are linked; entries within a Journey remain oldest first. Journey introductions display `authors` (with the site author fallback), their authored date, and the existing last-updated metadata. Undated introductions omit date metadata. To derive updates from Git, enable `enableGitInfo` in the consuming site and configure `[frontmatter] lastmod = ["lastmod", ":git", "date", "publishDate"]`. Git timestamps reflect repository changes, not first public deployment.

Journal, Cairn, and Journey headers share a compact byline beneath the title, readable calendar dates, and a quieter update date. Location, map links, mileage, and verification details occupy an optional secondary line. On small screens the update date wraps below the byline; machine-readable dates and author microformats are preserved.

### Full-post RSS

The main feed includes published Journal and Cairn entries; section feeds restrict that selection to their section. Drafts, fixtures, and future publications stay out even in preview builds. Each item contains the complete rendered article (including content after `<!--more-->`) in both `description` and `content:encoded`, with XML-safe titles and author names. Rendered image, download, and fragment links resolve against the article URL so readers can open them outside the site. Feeds include a self-link, language, publication dates, and Dublin Core author names.

An RSS-only footer thanks subscribers and links to the original post. Set `params.rss_footer` to customize its plain text. When a `/follow/` page exists, the feed footer and site footer link to it automatically. Every HTML page advertises the main feed for reader discovery. The theme does not generate the authored Follow page.
