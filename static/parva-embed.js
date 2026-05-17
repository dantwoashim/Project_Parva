(function () {
  window.ParvaEmbed = {
    render(target, card) {
      const el = typeof target === 'string' ? document.querySelector(target) : target;
      if (!el) return false;
      const article = document.createElement('article');
      article.setAttribute('data-parva-card', 'embed');

      const title = document.createElement('strong');
      title.textContent = String(card && card.title ? card.title : '');

      const body = document.createElement('p');
      body.textContent = String(card && card.boundary ? card.boundary : '');

      article.append(title, body);
      el.replaceChildren(article);
      return true;
    },
  };
})();
