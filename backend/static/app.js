// Basic UX improvements: disable submit while processing
window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', (e) => {
      const btn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (!btn) return;
      btn.disabled = true;
      const original = btn.innerHTML;
      btn.dataset.originalText = original;
      if (btn.innerHTML.trim().length) {
        btn.innerHTML = 'Processing...';
      }
    });
  });
});

