// Native controls and direct file links work independently of this enhancement.
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
for (const video of document.querySelectorAll('.travel-video')) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'video-toggle';
  video.after(button);
  const update = () => { button.textContent = video.paused ? 'Play silent loop' : 'Pause silent loop'; };
  const applyPreference = () => {
    video.autoplay = !motion.matches;
    if (motion.matches) video.pause();
    update();
  };
  button.addEventListener('click', () => {
    if (video.paused) video.play().catch(update);
    else video.pause();
  });
  video.addEventListener('play', update);
  video.addEventListener('pause', update);
  motion.addEventListener('change', applyPreference);
  applyPreference();
}
