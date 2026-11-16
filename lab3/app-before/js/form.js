/* Проверка форм на клиенте. Данные никуда не отправляются, это учебный проект */
(function () {
  'use strict';

  var MESSAGES = {
    valueMissing: 'Заполните это поле',
    typeMismatch: 'Проверьте адрес, например: name@mail.ru',
    tooShort: 'Слишком коротко'
  };

  function messageFor(field) {
    var v = field.validity;
    if (v.valueMissing) return field.type === 'checkbox' ? 'Нужно согласие на обработку данных' : MESSAGES.valueMissing;
    if (v.typeMismatch) return MESSAGES.typeMismatch;
    if (v.tooShort) return MESSAGES.tooShort + ': минимум ' + field.minLength + ' символов';
    return '';
  }

  function check(field) {
    var error = document.getElementById(field.id + '-error');
    var text = field.checkValidity() ? '' : messageFor(field);
    if (text) field.setAttribute('aria-invalid', 'true');
    else field.removeAttribute('aria-invalid');
    if (error) error.textContent = text;
    return !text;
  }

  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    var fields = form.querySelectorAll('input, textarea, select');
    var status = form.querySelector('[role="status"]');
    var initial = status ? status.textContent : '';

    fields.forEach(function (field) {
      field.addEventListener('blur', function () { if (field.value) check(field); });
      field.addEventListener('input', function () { if (field.getAttribute('aria-invalid')) check(field); });
      field.addEventListener('change', function () { if (field.getAttribute('aria-invalid')) check(field); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      fields.forEach(function (field) {
        if (!check(field) && !firstBad) firstBad = field;
      });
      if (firstBad) {
        firstBad.focus();
        if (status) { status.classList.add('is-error'); status.textContent = form.dataset.error || initial; }
        return;
      }
      if (status) {
        status.classList.remove('is-error');
        status.textContent = form.dataset.success;
      }
      form.reset();
    });
  });
})();
