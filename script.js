const spreads = [...document.querySelectorAll('.spread')];
const cover = document.querySelector('.front-cover');
const previous = document.querySelector('.previous');
const next = document.querySelector('.next');
const label = document.querySelector('#spread-label');
const fill = document.querySelector('#progress-fill');
const readButton = document.querySelector('.read-button');
const soundButton = document.querySelector('.sound-button');
let current = 0;

function updateBook(index) {
  current = Math.max(0, Math.min(index, spreads.length - 1));
  cover.classList.toggle('open', current > 0);
  spreads.forEach((spread, position) => spread.classList.toggle('is-flipped', position < current));
  label.textContent = `${String(current + 1).padStart(2, '0')} / ${String(spreads.length).padStart(2, '0')}`;
  fill.style.width = `${((current + 1) / spreads.length) * 100}%`;
  previous.disabled = current === 0;
  next.disabled = current === spreads.length - 1;
}

next.addEventListener('click', () => updateBook(current + 1));
previous.addEventListener('click', () => updateBook(current - 1));
readButton.addEventListener('click', () => { document.querySelector('.book-stage').scrollIntoView({ behavior: 'smooth', block: 'center' }); updateBook(1); });
document.querySelector('.book-stage').addEventListener('click', (event) => updateBook(event.clientX > window.innerWidth / 2 ? current + 1 : current - 1));
soundButton.addEventListener('click', () => { const enabled = soundButton.getAttribute('aria-pressed') === 'true'; soundButton.setAttribute('aria-pressed', String(!enabled)); soundButton.innerHTML = `<span class="sound-icon">⌁</span> sound ${enabled ? 'off' : 'on'}`; });
updateBook(0);
