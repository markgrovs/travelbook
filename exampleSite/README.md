# Local travelbook preview

From the theme repository root:

```sh
hugo server --source exampleSite --renderToMemory --disableFastRender
```

Open http://localhost:1313/. Stop with Ctrl+C. Add `--buildDrafts` to inspect the draft-only entry. Use `--port 1314` if 1313 is occupied.

This configuration replaces the default configuration; it does not merge with hugo.toml. Fixtures are outside normal content. All sample text is labeled. Synthetic bands exercise landscape, portrait, and responsive media; the single-photo fixture copies an existing development photograph. No media is recompressed by the theme. The media index models a proposed publisher interface, not a deployed daemon feature.

From a consuming site, run `hugo server --source themes/travelbook/exampleSite` to see this demo. Normal site builds use their own authored content.

Build output, resource/cache files, and automated check artifacts stay under `exampleSite/` and are ignored by Git. Run `python3 tests/check_theme.py --hugo hugo` to verify the theme on the installed Hugo version.

The revised design shows the latest entry in full and lists older dispatches beneath it. `location` (or legacy `place`) and `mileage` are optional. The video entry demonstrates a native silent loop with a poster, controls, and reduced-motion handling. Theme extraction/submodule instructions are in `../README.md`.

## Verification — 2026-09-30

Hugo 0.166.0 passed the production/preview and standalone-theme checks. Safari desktop and 402px phone previews were visually reviewed in dark appearance; native video playback and the pause button were checked. Computed light text/metadata/link contrast is 13.50/5.45/7.44 to 1; dark is 12.98/7.72/6.95 to 1. Prototype production output totals 752,888 bytes, including synthetic video. Real media transfer sizes and loading behavior still depend on supplied photographs and clips.

The masthead now uses a large mixed-case serif title. Light/Dark controls follow device appearance until the reader chooses a mode, then remember that choice. Preference lifecycle checks passed with `node tests/appearance.cjs`.

IndieWeb microformats and optional endpoint discovery are covered by the rendered-output checks. All fixtures remain excluded from production-site content and RSS.
