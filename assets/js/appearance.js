// Apply the saved choice before styles load, avoiding a flash of the wrong palette.
(() => {
  const key = 'travelbook-appearance';
  const root = document.documentElement;
  const device = window.matchMedia('(prefers-color-scheme: dark)');
  const valid = value => value === 'light' || value === 'dark';
  let choice = null;
  try {
    const saved = localStorage.getItem(key);
    if (valid(saved)) choice = saved;
  } catch (_) { /* Appearance still works when storage is unavailable. */ }
  function apply() {
    const current = choice || (device.matches ? 'dark' : 'light');
    root.dataset.theme = current;
    for (const button of document.querySelectorAll('[data-appearance]')) {
      button.setAttribute('aria-pressed', String(button.dataset.appearance === current));
    }
  }
  apply();
  device.addEventListener('change', () => { if (!choice) apply(); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      choice = valid(event.newValue) ? event.newValue : null;
      apply();
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    const controls = document.querySelector('.appearance');
    if (!controls) return;
    for (const button of controls.querySelectorAll('[data-appearance]')) {
      button.addEventListener('click', () => {
        choice = button.dataset.appearance;
        try { localStorage.setItem(key, choice); } catch (_) {}
        apply();
      });
    }
    apply();
    controls.hidden = false;
  });
})();
