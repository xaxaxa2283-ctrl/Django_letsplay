/* Filtering a small, fully rendered catalog; without JS server category links remain usable. */
(() => {
  'use strict';
  const root = document.querySelector('.sf-catalog');
  if (!root) return;
  // Keep the selected category visible in its horizontal rail without moving the page.
  const rail = root.querySelector('.sf-tabs');
  const revealCategory = () => {
    const selected = rail?.querySelector('[aria-current]');
    if (!selected) return;
    const r = rail.getBoundingClientRect(), a = selected.getBoundingClientRect();
    if (a.left < r.left || a.right > r.right) rail.scrollLeft += a.left - r.left - 12;
  };
  revealCategory();
  window.addEventListener('resize', revealCategory);
  // These remain functional even when the server returns no products.
  root.querySelectorAll('.sf-subfilters a, .sf-refinements a, .sf-budget-note a').forEach(link => {
    const current = new URL(location.href), target = new URL(link.href);
    if (target.searchParams.get('category') !== current.searchParams.get('category')) return;
    ['q', 'sort', 'stock'].forEach(key => {
      if (current.searchParams.has(key)) target.searchParams.set(key, current.searchParams.get(key));
    });
    link.href = target.href;
  });
  const tools = root.querySelector('[data-catalog-tools]');
  if (!tools) return;
  const search = root.querySelector('#catalog-search');
  const sort = root.querySelector('#catalog-sort');
  const stock = root.querySelector('#catalog-stock');
  const clear = root.querySelector('[data-catalog-clear]');
  const empty = root.querySelector('[data-catalog-empty]');
  const count = root.querySelector('#catalog-count');
  const grid = root.querySelector('#catalog-products');
  const restore = () => {
    const params = new URL(location.href).searchParams;
    search.value = (params.get('q') || '').slice(0, 100);
    sort.value = ['price-asc', 'price-desc', 'name'].includes(params.get('sort')) ? params.get('sort') : 'default';
    stock.checked = params.get('stock') === '1';
  };
  const preserve = () => {
    const url = new URL(location.href);
    const set = (params, key, value) => value ? params.set(key, value) : params.delete(key);
    const apply = params => {
      set(params, 'q', search.value.trim());
      set(params, 'sort', sort.value === 'default' ? '' : sort.value);
      set(params, 'stock', stock.checked ? '1' : '');
    };
    apply(url.searchParams);
    history.replaceState(null, '', url);
    root.querySelectorAll('.sf-subfilters a, .sf-refinements a, .sf-budget-note a').forEach(link => {
      const target = new URL(link.href);
      if (target.searchParams.get('category') === url.searchParams.get('category')) {
        apply(target.searchParams);
        link.href = target.href;
      }
    });
  };
  const normalize = value => value.toLocaleLowerCase('ru').replace(/\bps\s*([45])\b/g, 'playstation $1');
  const products = Array.from(grid.querySelectorAll('[data-catalog-product]')).map((node, index) => ({
    node, index, name: normalize(node.dataset.name),
    price: Number(node.dataset.price.replace(',', '.')), inStock: node.dataset.stock === '1'
  }));
  const update = () => {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    const ordered = [...products].sort((a, b) => {
      if (sort.value === 'price-asc') return a.price - b.price || a.index - b.index;
      if (sort.value === 'price-desc') return b.price - a.price || a.index - b.index;
      if (sort.value === 'name') return a.name.localeCompare(b.name, 'ru') || a.index - b.index;
      return a.index - b.index;
    });
    ordered.forEach(product => {
      const show = terms.every(term => product.name.includes(term)) && (!stock.checked || product.inStock);
      product.node.hidden = !show;
      if (show) visible += 1;
      grid.appendChild(product.node);
    });
    clear.hidden = search.value.length === 0;
    empty.hidden = visible > 0;
    count.textContent = `Найдено: ${visible}`;
    preserve();
  };
  search.addEventListener('input', update);
  sort.addEventListener('change', update);
  stock.addEventListener('change', update);
  clear.addEventListener('click', () => { search.value = ''; update(); search.focus(); });
  root.querySelector('[data-catalog-reset]').addEventListener('click', () => {
    search.value = ''; stock.checked = false; update(); search.focus();
  });
  tools.hidden = false;
  restore();
  update();
  window.addEventListener('pageshow', () => { restore(); update(); });
})();
