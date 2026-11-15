document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.lp-spec-editor').forEach(editor => {
    const rows = editor.querySelector('.lp-spec-rows');
    editor.querySelector('.lp-spec-add').hidden = false;
    rows.querySelectorAll('button').forEach(button => button.hidden = false);
    editor.querySelector('.lp-spec-add').addEventListener('click', () => {
      const row = rows.firstElementChild.cloneNode(true);
      row.querySelectorAll('input').forEach(input => input.value = '');
      rows.appendChild(row);
      row.querySelector('input').focus();
    });
    rows.addEventListener('click', event => {
      if (!event.target.closest('.lp-spec-remove')) return;
      const row = event.target.closest('.lp-spec-row');
      if (rows.children.length === 1) row.querySelectorAll('input').forEach(input => input.value = '');
      else row.remove();
      rows.lastElementChild.querySelector('input').focus();
    });
  });
});
