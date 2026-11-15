document.addEventListener('DOMContentLoaded', () => {
  const category = document.getElementById('id_category');
  const platform = document.getElementById('id_platform');
  if (!category || !platform) return;
  const toggle = (name, visible) => {
    const field = document.getElementById('id_' + name);
    if (!field) return;
    const row = field.closest('.form-row');
    if (row) row.hidden = !visible;
    field.disabled = !visible;
  };
  const update = () => {
    const type = category.selectedOptions[0]?.dataset.categoryType;
    // New categories added through the admin popup may not yet carry metadata.
    if (!type) {
      ['condition', 'firmware_status', 'subscription_type'].forEach(name => toggle(name, true));
      return;
    }
    toggle('condition', type === 'consoles' || type === 'disks');
    toggle('firmware_status', type === 'consoles' && platform.value === 'ps4');
    toggle('subscription_type', type === 'subscriptions');
  };
  category.addEventListener('change', update);
  platform.addEventListener('change', update);
  // Django's related-object popup dispatches a jQuery change event.
  if (window.django?.jQuery) window.django.jQuery(category).on('change', update);
  update();
});
