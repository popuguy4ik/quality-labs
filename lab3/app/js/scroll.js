/* Анимации при скролле, прогресс-бар, активный пункт оглавления */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  // Задержка для карточек в сетке, чтобы они появлялись по очереди
  document.querySelectorAll('[data-animate-stagger]').forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (item, i) {
      if (!item.hasAttribute('data-animate')) item.setAttribute('data-animate', '');
      item.style.setProperty('--animate-delay', (i % 3) * 100 + 'ms');
    });
  });

  var items = document.querySelectorAll('[data-animate]');

  function showAll() {
    items.forEach(function (el) { el.classList.add('is-visible'); });
  }

  if (reduceMotion.matches || !('IntersectionObserver' in window)) {
    showAll();
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
    items.forEach(function (el) { observer.observe(el); });
  }
  reduceMotion.addEventListener('change', function () { if (reduceMotion.matches) showAll(); });

  // Прогресс прокрутки страницы
  var bar = document.querySelector('.progress__bar');
  var ticking = false;

  function update() {
    ticking = false;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var value = max > 0 ? Math.min(1, window.scrollY / max) : 0;
    if (bar) bar.style.transform = 'scaleX(' + value + ')';
  }

  function request() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }

  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', request);
  request();

  // Оглавление статьи: подсвечиваем раздел, который сейчас читают
  var tocLinks = document.querySelectorAll('.toc a[href^="#"]');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.remove('is-active'); a.removeAttribute('aria-current'); });
        var link = byId[entry.target.id];
        if (link) { link.classList.add('is-active'); link.setAttribute('aria-current', 'true'); }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(byId).forEach(function (id) {
      var section = document.getElementById(id);
      if (section) spy.observe(section);
    });
  }
})();
