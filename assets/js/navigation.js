(function () {
  var searchBtn = document.getElementById('search-toggle');
  var searchPanel = document.getElementById('search-panel');
  var themeBtn = document.getElementById('theme-toggle');

  if (!searchBtn || !searchPanel || !themeBtn) return;

  var searchInitialized = false;

  function closePanel(btn, panel) {
    panel.classList.add('collapsed');
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = btn.dataset.open;
  }

  function openPanel(btn, panel) {
    panel.classList.remove('collapsed');
    btn.setAttribute('aria-expanded', 'true');
    btn.textContent = btn.dataset.close;
  }

  function togglePanel(btn, panel) {
    if (panel.classList.contains('collapsed')) openPanel(btn, panel);
    else closePanel(btn, panel);
  }

  // Search
  searchBtn.addEventListener('click', function () {
    togglePanel(searchBtn, searchPanel);

    if (!searchPanel.classList.contains('collapsed') && !searchInitialized) {
      searchInitialized = true;
      var lang = document.documentElement.getAttribute('lang') || 'en';
      var isJa = lang === 'ja';
      var script = document.createElement('script');
      script.src = '/pagefind/pagefind-ui.js';
      script.onload = function () {
        new PagefindUI({
          element: '#pagefind-search',
          showImages: false,
          pageSize: 8,
          resetStyles: true,
          translations: isJa ? {
            placeholder: '検索...',
            clear_search: 'クリア',
            load_more: 'さらに読み込む',
            search_label: 'このサイトを検索',
            filters_label: 'フィルター',
            zero_results: '「[SEARCH_TERM]」の結果が見つかりません',
            many_results: '[COUNT] 件の結果',
            one_result: '[COUNT] 件の結果',
            alt_search: '「[SEARCH_TERM]」の結果なし。「[DIFFERENT_TERM]」を表示中',
            searching: '「[SEARCH_TERM]」を検索中…'
          } : {
            placeholder: 'Search...',
            clear_search: 'Clear',
            load_more: 'Load more results',
            search_label: 'Search this site',
            filters_label: 'Filters',
            zero_results: 'No results for "[SEARCH_TERM]"',
            many_results: '[COUNT] results for "[SEARCH_TERM]"',
            one_result: '[COUNT] result for "[SEARCH_TERM]"',
            alt_search: 'No results for "[SEARCH_TERM]". Showing results for "[DIFFERENT_TERM]" instead',
            searching: 'Searching for "[SEARCH_TERM]"…'
          }
        });
        var input = document.querySelector('.pagefind-ui__search-input');
        if (input) input.focus();
      };
      document.head.appendChild(script);
    } else if (!searchPanel.classList.contains('collapsed')) {
      var input = document.querySelector('.pagefind-ui__search-input');
      if (input) input.focus();
    }
  });

  // Click outside to close the search panel
  document.addEventListener('click', function (e) {
    if (!searchPanel.classList.contains('collapsed') &&
        !searchPanel.contains(e.target) &&
        !searchBtn.contains(e.target)) {
      closePanel(searchBtn, searchPanel);
    }
  });

  // Escape key closes the search panel
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (!searchPanel.classList.contains('collapsed')) closePanel(searchBtn, searchPanel);
    }
  });

  // Theme toggle
  var themes = ['auto', 'light', 'dark'];
  var currentTheme = localStorage.getItem('theme') || 'auto';

  function updateThemeBtn() {
    themeBtn.textContent = (themeBtn.dataset.label || 'Theme: ') +
      (themeBtn.dataset[currentTheme] || currentTheme.charAt(0).toUpperCase() + currentTheme.slice(1));
  }

  updateThemeBtn();

  themeBtn.addEventListener('click', function () {
    currentTheme = themes[(themes.indexOf(currentTheme) + 1) % themes.length];
    localStorage.setItem('theme', currentTheme);
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeBtn();
  });
})();
