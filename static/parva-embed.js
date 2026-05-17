(function () {
  window.ParvaEmbed = {
    render(target, card) {
      const el = typeof target === 'string' ? document.querySelector(target) : target;
      if (!el) return false;
      el.innerHTML = `<article data-parva-card="embed"><strong>${card.title}</strong><p>${card.boundary}</p></article>`;
      return true;
    },
  };
})();
