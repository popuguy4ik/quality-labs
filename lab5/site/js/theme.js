/* Тёмная тема: JS только меняет data-theme, цвета задают CSS-переменные */
(function () {
  'use strict';

  var STORAGE_KEY = 'sova-theme';
  var root = document.documentElement;
  var media = window.matchMedia('(prefers-color-scheme: dark)');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function getSaved() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  // Определение начальной темы: сохранённый выбор, иначе настройка системы
  function getPreferredTheme() {
    var saved = getSaved();
    if (saved === 'light' || saved === 'dark') return saved;
    return media.matches ? 'dark' : 'light';
  }

  function syncButtons(theme) {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', String(theme === 'dark'));
      btn.setAttribute('aria-label', theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему');
    });
  }

  function applyTheme(theme, save) {
    if (save && !reduceMotion.matches) {
      root.classList.add('theme-switching');
      window.setTimeout(function () { root.classList.remove('theme-switching'); }, 450);
    }
    root.setAttribute('data-theme', theme);
    if (save) {
      try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
    }
    syncButtons(theme);
  }

  // Инициализация (data-theme уже выставлен скриптом в <head>, здесь синхронизируем кнопки)
  applyTheme(getPreferredTheme(), false);

  // Клик по переключателю. Это <button>, поэтому Enter и Space работают сами
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
  });

  // Реакция на смену системной темы, если пользователь сам ничего не выбирал
  media.addEventListener('change', function (e) {
    if (!getSaved()) applyTheme(e.matches ? 'dark' : 'light', false);
  });
})();
