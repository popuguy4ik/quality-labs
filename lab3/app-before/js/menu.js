/* Мобильное меню: панель справа, Esc, фокус не уходит за пределы меню */
(function () {
  'use strict';

  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');
  if (!burger || !menu) return;

  var panel = menu.querySelector('.menu__panel');
  var closeBtn = menu.querySelector('.menu__close');
  var backdrop = menu.querySelector('.menu__backdrop');

  function focusables() {
    return Array.prototype.slice.call(panel.querySelectorAll('a[href], button:not([disabled])'));
  }

  function open() {
    menu.classList.add('is-open');
    menu.removeAttribute('inert');
    burger.setAttribute('aria-expanded', 'true');
    document.body.classList.add('menu-open');
    window.setTimeout(function () { closeBtn.focus(); }, 60);
  }

  function close(restoreFocus) {
    if (!menu.classList.contains('is-open')) return;
    menu.classList.remove('is-open');
    menu.setAttribute('inert', '');
    burger.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('menu-open');
    if (restoreFocus) burger.focus();
  }

  burger.addEventListener('click', open);
  closeBtn.addEventListener('click', function () { close(true); });
  backdrop.addEventListener('click', function () { close(true); });

  document.addEventListener('keydown', function (e) {
    if (!menu.classList.contains('is-open')) return;
    if (e.key === 'Escape') { close(true); return; }
    if (e.key !== 'Tab') return;
    var items = focusables();
    var first = items[0];
    var last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  window.matchMedia('(min-width: 1024px)').addEventListener('change', function (e) {
    if (e.matches) close(false);
  });
})();
