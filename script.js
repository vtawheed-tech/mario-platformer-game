const spreads = [...document.querySelectorAll('.spread')];
const cover = document.querySelector('.front-cover');
const previous = document.querySelector('.previous');
const next = document.querySelector('.next');
const label = document.querySelector('#spread-label');
const fill = document.querySelector('#progress-fill');
const readButton = document.querySelector('.read-button');
const soundButton = document.querySelector('.sound-button');
const pauseButton = document.querySelector('.pause-button');
const bookStage = document.querySelector('.book-stage');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let current = 0;
let previewTimer;
let previewPaused = reduceMotion;

function updateBook(index) {
  current = Math.max(0, Math.min(index, spreads.length - 1));
  cover.classList.toggle('open', current > 0);
  spreads.forEach((spread, position) => spread.classList.toggle('is-flipped', position < current));
  label.textContent = `${String(current + 1).padStart(2, '0')} / ${String(spreads.length).padStart(2, '0')}`;
  fill.style.width = `${((current + 1) / spreads.length) * 100}%`;
  previous.disabled = current === 0;
  next.disabled = current === spreads.length - 1;
}

function stopPreview() {
  window.clearInterval(previewTimer);
}

function startPreview() {
  stopPreview();
  if (!previewPaused) {
    previewTimer = window.setInterval(() => updateBook(current === spreads.length - 1 ? 0 : current + 1), 3400);
  }
}

next.addEventListener('click', () => { updateBook(current + 1); startPreview(); });
previous.addEventListener('click', () => { updateBook(current - 1); startPreview(); });
readButton.addEventListener('click', () => { bookStage.scrollIntoView({ behavior: 'smooth', block: 'center' }); updateBook(1); startPreview(); });
bookStage.addEventListener('click', (event) => { updateBook(event.clientX > window.innerWidth / 2 ? current + 1 : current - 1); startPreview(); });
bookStage.addEventListener('mouseenter', stopPreview);
bookStage.addEventListener('mouseleave', startPreview);
pauseButton.addEventListener('click', () => { previewPaused = !previewPaused; pauseButton.setAttribute('aria-pressed', String(previewPaused)); pauseButton.textContent = previewPaused ? 'play preview' : 'pause preview'; startPreview(); });
soundButton.addEventListener('click', () => { const enabled = soundButton.getAttribute('aria-pressed') === 'true'; soundButton.setAttribute('aria-pressed', String(!enabled)); soundButton.innerHTML = `<span class="sound-icon">⌁</span> sound ${enabled ? 'off' : 'on'}`; });
updateBook(0);
startPreview();
