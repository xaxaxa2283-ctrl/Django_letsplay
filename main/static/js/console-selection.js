/* Local console selection: no external requests or persistent storage. */
(() => {
  'use strict';
  const form = document.getElementById('console-selection');
  if (!form) return;
  const games = document.getElementById('selection-games');
  const budget = document.getElementById('selection-budget');
  const condition = document.getElementById('selection-condition');
  const platform = document.getElementById('selection-platform');
  const result = document.getElementById('selection-result');
  const summary = document.getElementById('selection-summary');
  const message = document.getElementById('selection-message');
  const copyStatus = document.getElementById('selection-copy-status');
  const budgetLabel = () => budget.value ? `до ${Number(budget.value).toLocaleString('ru-RU')} ₽` : 'пока не определён';
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const values = [
      ['Игры и пожелания', games.value.trim() || 'Обсудим с консультантом'],
      ['Бюджет на консоль', budgetLabel()],
      ['Состояние', condition.options[condition.selectedIndex].text],
      ['Платформа', platform.options[platform.selectedIndex].text]
    ];
    summary.replaceChildren();
    values.forEach(([label, value]) => {
      const row = document.createElement('div');
      const term = document.createElement('dt');term.textContent = label;
      const detail = document.createElement('dd');detail.textContent = value;
      row.append(term, detail);summary.append(row);
    });
    const url = new URL(form.action, window.location.origin);
    url.searchParams.set('category', 'consoles');
    if (budget.value) url.searchParams.set('max_price', budget.value);
    if (condition.value) url.searchParams.set('condition', condition.value);
    if (platform.value) url.searchParams.set('filter', platform.value);
    document.getElementById('selection-catalog').href = url.pathname + url.search;
    message.value = 'Здравствуйте! Помогите подобрать приставку.\n' + values.map(([label,value]) => `${label}: ${value}.`).join('\n') + '\nПодскажите подходящие варианты, доступность нужных игр и что войдёт в подготовку.';
    copyStatus.textContent = '';
    result.hidden = false;
    result.focus({preventScroll:true});
    result.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  });
  form.addEventListener('input', () => { result.hidden = true; });
  form.addEventListener('change', () => { result.hidden = true; });
  document.getElementById('selection-copy').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(message.value);
      copyStatus.textContent = 'Сообщение скопировано. Теперь его можно отправить консультанту.';
    } catch (error) {
      message.focus();message.select();
      copyStatus.textContent = 'Текст выделен. Скопируйте его через меню устройства или сочетание Ctrl+C.';
    }
  });
})();
