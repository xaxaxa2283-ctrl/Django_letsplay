(() => {
  const button = document.getElementById('loadMoreReviewsBtn');
  const grid = document.getElementById('reviewsGrid');
  const status = document.getElementById('reviews-status');
  if (!button || !grid) return;
  let offset = grid.querySelectorAll('.review-card').length;
  button.addEventListener('click', async () => {
    if (button.disabled) return;
    button.disabled = true;
    status.textContent = 'Загружаем отзывы…';
    try {
      const response = await fetch(`${button.dataset.url}?offset=${offset}&limit=8`);
      if (!response.ok) throw new Error('Reviews unavailable');
      const data = await response.json();
      for (const review of data.reviews) {
        const card = document.createElement('article');
        card.className = 'review-card';
        const name = document.createElement('h3');
        name.textContent = review.name;
        const rating = document.createElement('span');
        rating.className = 'lp-review-rating';
        rating.setAttribute('aria-label', `Оценка ${review.rating} из 5`);
        rating.textContent = `★ ${review.rating} / 5`;
        const text = document.createElement('p');
        text.className = 'lp-review-text';
        text.textContent = review.text;
        const top = document.createElement('div');
        top.className = 'lp-review-top';
        top.append(name, rating);
        card.append(top, text);
        grid.append(card);
      }
      offset = data.next_offset;
      button.hidden = !data.has_more;
      status.textContent = data.has_more ? '' : 'Все отзывы загружены.';
    } catch (error) {
      status.textContent = 'Не удалось загрузить отзывы. Попробуйте ещё раз.';
    } finally { button.disabled = false; }
  });
})();
