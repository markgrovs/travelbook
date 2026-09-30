// Behavior checks for the browser preference lifecycle; no test dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../assets/js/appearance.js'), 'utf8');
function browser({ saved = null, dark = false, blocked = false } = {}) {
  let ready = false;
  const root = { dataset: {} };
  const callbacks = {};
  const device = { matches: dark, addEventListener: (_, fn) => { device.change = fn; } };
  const buttons = ['light', 'dark'].map(mode => ({
    dataset: { appearance: mode },
    attrs: {},
    setAttribute(key, value) { this.attrs[key] = value; },
    addEventListener(_, fn) { this.click = fn; },
  }));
  const controls = { hidden: true, querySelectorAll: () => buttons };
  const storage = {
    value: saved,
    getItem() { if (blocked) throw new Error('Storage blocked'); return this.value; },
    setItem(_, value) { if (blocked) throw new Error('Storage blocked'); this.value = value; },
  };
  vm.runInNewContext(script, {
    document: {
      documentElement: root,
      querySelectorAll: () => ready ? buttons : [],
      querySelector: () => controls,
      addEventListener: (type, fn) => { callbacks[type] = fn; },
    },
    window: {
      matchMedia: () => device,
      addEventListener: (type, fn) => { callbacks[type] = fn; },
    },
    localStorage: storage,
  });
  return {
    root, controls, buttons, storage,
    ready() { ready = true; callbacks.DOMContentLoaded(); },
    device(dark) { device.matches = dark; device.change(); },
    storageEvent(value) { callbacks.storage({ key: 'travelbook-appearance', newValue: value }); },
  };
}
let page = browser({ dark: true });
assert.equal(page.root.dataset.theme, 'dark', 'Device appearance is applied before DOM readiness');
page.ready();
assert.equal(page.controls.hidden, false);
assert.equal(page.buttons[1].attrs['aria-pressed'], 'true');
page.device(false);
assert.equal(page.root.dataset.theme, 'light', 'Device changes are followed before an explicit choice');
page.buttons[1].click();
assert.equal(page.storage.value, 'dark');
page.device(false);
assert.equal(page.root.dataset.theme, 'dark', 'Explicit choice overrides device preference');
page = browser({ saved: page.storage.value, dark: false });
assert.equal(page.root.dataset.theme, 'dark', 'Saved choice survives a new page load');
page.ready();
page.storageEvent('light');
assert.equal(page.root.dataset.theme, 'light', 'Other-tab preference changes are applied');
page.storageEvent(null);
page.device(true);
assert.equal(page.root.dataset.theme, 'dark', 'Clearing the preference restores device behavior');
page = browser({ saved: 'invalid', dark: false });
assert.equal(page.root.dataset.theme, 'light', 'Invalid saved values are ignored');
page = browser({ blocked: true, dark: true });
page.ready();
page.buttons[0].click();
assert.equal(page.root.dataset.theme, 'light', 'Controls work with blocked storage');
assert.equal(page.buttons[0].attrs['aria-pressed'], 'true');
assert.equal(page.buttons[1].attrs['aria-pressed'], 'false');
console.log('PASS: initial device choice, early saved preference, persistence, device changes, explicit override, cross-tab updates, and blocked storage.');
