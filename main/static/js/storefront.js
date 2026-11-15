/* Progressive enhancement: ordinary form POST remains functional without JavaScript. */
(() => {
  'use strict';
  document.querySelectorAll('[data-storefront-cart]').forEach(form => {
    const cartLink = form.closest('.sf-product-page .sf-buy')?.querySelector(':scope > .sf-text-link');
    if (cartLink) cartLink.hidden = true;
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const status = form.querySelector('[role="status"]');
      if (button.disabled) return;
      const label = button.innerHTML;
      button.disabled = true;
      button.textContent = 'Добавляем…';
      status.textContent = '';
      try {
        const response = await fetch(form.action, {
          method: 'POST', body: new FormData(form), credentials: 'same-origin',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) throw new Error('Request failed');
        const data = await response.json();
        if (!data.ok) throw new Error('Cart rejected');
        status.textContent = 'Товар добавлен. Можно перейти в корзину.';
        if (cartLink) cartLink.hidden = false;
        const counter = document.getElementById('cart-counter');
        if (counter && Number.isInteger(data.cart_count)) {
          counter.textContent = String(data.cart_count);
          counter.hidden = false;
        }
      } catch (error) {
        status.textContent = 'Не удалось подтвердить добавление. Проверьте корзину перед повторной попыткой.';
        if (cartLink) cartLink.hidden = false;
      } finally {
        button.disabled = false;
        button.innerHTML = label;
      }
    });
  });
  document.querySelectorAll('[data-sf-image]').forEach(button => {
    button.addEventListener('click', () => {
      const main = document.getElementById('sf-main-image');
      if (main) {
        main.src = button.dataset.sfImage;
        main.hidden = false;
        main.parentElement.querySelector('.sf-image-empty')?.remove();
        document.querySelectorAll('[data-sf-image]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      }
    });
  });
  document.querySelectorAll('.sf-product-image img,.sf-detail-image img,.sf-hero-console').forEach(img => {
    img.addEventListener('error', () => {
      img.hidden = true;
      const message = document.createElement('span');
      message.className = 'sf-image-empty';
      message.textContent = 'Фотографию уточним перед покупкой';
      img.after(message);
    }, { once: true });
  });
})();
(() => {
  const button = document.getElementById('menu-toggle');
  const menu = document.getElementById('mobile-menu');
  if (!button || !menu) return;
  const setOpen = open => {
    menu.classList.toggle('open', open);
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  };
  button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      button.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!menu.contains(event.target) && !button.contains(event.target)) setOpen(false);
  });
  window.matchMedia('(min-width: 768px)').addEventListener('change', event => {
    if (event.matches) setOpen(false);
  });
})();

/* Product-only controls and clearance for consent/chat layers. */
(() => {
  const product = document.querySelector('.sf-product-page');
  if (!product) return;
  const gallery = product.querySelector('.sf-thumbnails');
  if (gallery) {
    const buttons = [...gallery.querySelectorAll('[data-sf-image]')];
    if (buttons.length < 2) gallery.hidden = true;
    buttons.forEach((button, index) => {
      button.setAttribute('aria-pressed', String(index === 0));
      button.addEventListener('keydown', event => {
        let target;
        if (event.key === 'ArrowRight') target = (index + 1) % buttons.length;
        if (event.key === 'ArrowLeft') target = (index - 1 + buttons.length) % buttons.length;
        if (event.key === 'Home') target = 0;
        if (event.key === 'End') target = buttons.length - 1;
        if (target === undefined) return;
        event.preventDefault();buttons[target].focus();buttons[target].click();
      });
    });
  }
  const action = product.querySelector('[data-storefront-cart] button[type="submit"]');
  const widget = document.getElementById('lp-contact-widget');
  let pending = false;
  const update = () => {
    pending = false;
    const banner = document.getElementById('legal-cookie-banner');
    const bannerRect = banner?.getBoundingClientRect();
    const reserve = bannerRect && bannerRect.height && getComputedStyle(banner).display !== 'none' ? bannerRect.height + 24 : 0;
    product.style.setProperty('--product-overlay-space', `${reserve}px`);
    if (!action || !widget) return;
    const a = action.getBoundingClientRect();
    const w = widget.getBoundingClientRect();
    const overlap = a.top < w.bottom + 12 && a.bottom > w.top - 12 && a.left < w.right + 12 && a.right > w.left - 12;
    document.body.classList.toggle('lp-product-action-clear', overlap);
  };
  const schedule = () => { if (!pending) { pending = true; requestAnimationFrame(update); } };
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule);
  const observer = new MutationObserver(schedule);
  observer.observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['hidden','aria-hidden']});
  if (window.ResizeObserver) {
    const resize = new ResizeObserver(schedule);
    resize.observe(product);
    const banner = document.getElementById('legal-cookie-banner');
    if (banner) resize.observe(banner);
  }
  schedule();
})();
