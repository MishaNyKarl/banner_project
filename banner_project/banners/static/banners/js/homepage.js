document.addEventListener('DOMContentLoaded', () => {
  const items = window.bannerItems || [];
  let idx = 0;
  const container = document.getElementById('banner-container');
  const anchor = document.getElementById('scroll-anchor');

  function renderNext() {
      if (!items.length) return;
      const { image_url, title, ad_link } = items[idx];
      const el = document.createElement('div');
      el.className = 'banner-item';
      el.innerHTML = `
        <a href="${ad_link}" style="text-decoration: none">
          <div class="thumb">
            <img src="${image_url}" alt="${title}">
          </div>
          <div class="title">${title}</div>
        </a>
      `;
      container.appendChild(el);

      idx = (idx + 1) % items.length;
    }


  // Предзагрузка первых 20 баннеров
  for (let i = 0; i < 20; i++) {
    renderNext();
  }

  // Когда «якорь» прокручивается в область видимости, подгружаем ещё
  const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      // подгружаем по 10 штук
      for (let i = 0; i < 10; i++) {
        renderNext();
      }
    }
  }, {
    rootMargin: '200px'
  });

  observer.observe(anchor);
});