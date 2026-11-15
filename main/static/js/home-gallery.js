(() => {
  document.querySelectorAll('[data-copy-address]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const status = button.parentElement.querySelector('[data-copy-status]');
      try {
        await navigator.clipboard.writeText(button.dataset.copyAddress);
        status.textContent = 'Адрес скопирован.';
      } catch (_) {
        status.textContent = `Скопируйте адрес: ${button.dataset.copyAddress}`;
      }
    });
  });
  const links = [...document.querySelectorAll('[data-store-photo]')];
  const dialog = document.querySelector('.home-photo-dialog');
  if (!dialog || !dialog.showModal) return;
  let current = 0;
  let trigger;
  let previousOverflow;
  const show = index => {
    current = (index + links.length) % links.length;
    const link = links[current];
    const img = dialog.querySelector('img');
    img.src = link.href;
    img.alt = link.querySelector('img').alt;
    dialog.querySelector('figcaption').textContent = link.dataset.caption;
    dialog.querySelector('[data-photo-count]').textContent = `${current + 1} / ${links.length}`;
  };
  links.forEach((link, index) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    trigger = link;
    show(index);
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialog.showModal();
  }));
  dialog.querySelector('.home-photo-close').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-photo-prev]').addEventListener('click', () => show(current - 1));
  dialog.querySelector('[data-photo-next]').addEventListener('click', () => show(current + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      show(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    trigger?.focus({preventScroll: true});
  });
})();
