/* TrialGuard — main JavaScript */

// Auto-set today's date on check-in form if field is empty
document.addEventListener('DOMContentLoaded', function () {
  const dateInput = document.getElementById('occurred_at');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0, 10);
  }

  // Mode selector visual feedback
  document.querySelectorAll('.mode-option input[type=radio]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      document.querySelectorAll('.mode-option').forEach(function (opt) {
        opt.classList.remove('mode-selected');
      });
      radio.closest('.mode-option').classList.add('mode-selected');
    });
    // Highlight on load
    if (radio.checked) {
      radio.closest('.mode-option').classList.add('mode-selected');
    }
  });

  // Disable submit button after click to prevent double-submit
  const form = document.querySelector('.checkin-form');
  if (form) {
    form.addEventListener('submit', function () {
      const btn = form.querySelector('button[type=submit]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Analyzing…';
      }
    });
  }
});
