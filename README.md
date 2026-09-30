# Travelbook

A standalone Hugo theme for a personal chronicle. Warm alabaster paper, charcoal text, trail-dust rules, and clay links. A single-column homepage shows the latest journal entry in full, followed by older dispatches. Media stays inline at its natural proportions.

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

Title is optional; the date is its fallback. `location` falls back to legacy `place`; mileage is optional. Bundle names determine URLs, independently of title. Optional `journeys: [stable-trip-id]` groups entries oldest first. Cairns use `content/cairns/`; About uses `content/about/index.md`. Root RSS contains published Journal and Cairns entries, excluding `fixture: true` and drafts.

```markdown
![Author-written alt text](images/photo.jpg "Optional visible caption")
```

Images resolve from page bundles; the optional `data/media.json` interface can point to pre-generated responsive assets. The theme never recompresses media. Missing required local images fail the build.

For a local MP4 in the same bundle:

```text
{{< ambient-video src="road.mp4" poster="images/poster.jpg" label="Road through the canyon" caption="Author-written note." >}}
```

The native player uses autoplay, loop, muted, playsinline, and controls. Browsers may block autoplay. A direct file link and controls remain available without JavaScript. The small enhancement supplies an explicit pause/play button and pauses for reduced-motion preferences. Native autoplay can begin briefly before the enhancement runs; omit ambient clips when strict motion-free delivery is required. Use a poster matching the video's aspect ratio. The current publisher does not yet process videos: this shortcode is a rendering interface for explicitly delivered local MP4s.

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
