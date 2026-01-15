/**
 * Tool Catalog - Interactive filtering, sorting, and search
 * Powered by Iconify for beautiful icons
 * Enhanced with quick filters, keyboard shortcuts, and animations
 */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('tool-search');
  const categoryFilter = document.getElementById('category-filter');
  const typeFilter = document.getElementById('type-filter');
  const sortSelect = document.getElementById('sort-select');
  const grid = document.getElementById('tool-catalog');
  const emptyState = document.getElementById('tool-empty');
  const resultsCount = document.getElementById('results-count');
  const gridViewBtn = document.getElementById('grid-view-btn');
  const listViewBtn = document.getElementById('list-view-btn');
  const filterPills = document.querySelectorAll('.filter-pill');

  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll('.tool-card'));
  const originalOrder = [...cards];
  let debounceTimer;

  // ========================================
  // Sorting Functions
  // ========================================
  const sortFunctions = {
    'name-asc': (a, b) => a.dataset.name.localeCompare(b.dataset.name),
    'name-desc': (a, b) => b.dataset.name.localeCompare(a.dataset.name),
    'category': (a, b) => {
      const catCompare = a.dataset.category.localeCompare(b.dataset.category);
      return catCompare !== 0 ? catCompare : a.dataset.name.localeCompare(b.dataset.name);
    },
    'type': (a, b) => {
      const typeCompare = a.dataset.type.localeCompare(b.dataset.type);
      return typeCompare !== 0 ? typeCompare : a.dataset.name.localeCompare(b.dataset.name);
    },
    'popularity': (a, b) => {
      const popA = parseInt(a.dataset.popularity || '0', 10);
      const popB = parseInt(b.dataset.popularity || '0', 10);
      return popB - popA; // Descending
    },
    'default': () => 0 // Preserve original order
  };

  function sortCards() {
    const sortKey = sortSelect?.value || 'default';
    const sortFn = sortFunctions[sortKey] || sortFunctions['default'];

    if (sortKey === 'default') {
      // Restore original order
      originalOrder.forEach(card => grid.appendChild(card));
    } else {
      const sorted = [...cards].sort(sortFn);
      sorted.forEach(card => grid.appendChild(card));
    }
  }

  // ========================================
  // Filtering Function
  // ========================================
  function filterCards() {
    const searchTerm = searchInput?.value.toLowerCase().trim() || '';
    const category = categoryFilter?.value || '';
    const type = typeFilter?.value || '';
    let visibleCount = 0;

    cards.forEach(card => {
      const name = card.dataset.name || '';
      const tags = card.dataset.tags || '';
      const desc = card.querySelector('.tool-description')?.textContent.toLowerCase() || '';
      const cardCategory = card.dataset.category || '';
      const cardType = card.dataset.type || '';

      // Search matches name, tags, or description
      const matchesSearch = !searchTerm ||
        name.includes(searchTerm) ||
        tags.includes(searchTerm) ||
        desc.includes(searchTerm);

      const matchesCategory = !category || cardCategory === category;
      const matchesType = !type || cardType === type;

      const visible = matchesSearch && matchesCategory && matchesType;
      card.setAttribute('aria-hidden', !visible);
      if (visible) visibleCount++;
    });

    // Update empty state
    if (emptyState) {
      emptyState.setAttribute('aria-hidden', visibleCount > 0);
    }

    // Update results count (accessible)
    if (resultsCount) {
      const countText = visibleCount === cards.length
        ? `Showing all ${visibleCount} tools`
        : `${visibleCount} of ${cards.length} tools`;
      resultsCount.textContent = countText;
    }
  }

  function debounceFilter() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(filterCards, 150);
  }

  // ========================================
  // View Toggle (Grid/List)
  // ========================================
  function setView(view) {
    if (view === 'list') {
      grid.classList.add('list-view');
      gridViewBtn?.classList.remove('active');
      listViewBtn?.classList.add('active');
      localStorage.setItem('tool-catalog-view', 'list');
    } else {
      grid.classList.remove('list-view');
      gridViewBtn?.classList.add('active');
      listViewBtn?.classList.remove('active');
      localStorage.setItem('tool-catalog-view', 'grid');
    }
  }

  // ========================================
  // Clear All Filters
  // ========================================
  window.clearAllFilters = function() {
    if (searchInput) searchInput.value = '';
    if (categoryFilter) categoryFilter.value = '';
    if (typeFilter) typeFilter.value = '';
    if (sortSelect) sortSelect.value = 'default';
    updatePillActiveState('');
    sortCards();
    filterCards();
    searchInput?.focus();
  };

  // ========================================
  // Quick Filter Pills
  // ========================================
  function updatePillActiveState(category) {
    filterPills.forEach(pill => {
      const pillCategory = pill.dataset.category;
      if (pillCategory === category) {
        pill.classList.add('active');
        pill.setAttribute('aria-pressed', 'true');
      } else {
        pill.classList.remove('active');
        pill.setAttribute('aria-pressed', 'false');
      }
    });
  }

  window.setQuickFilter = function(category) {
    // Update category dropdown to match
    if (categoryFilter) {
      categoryFilter.value = category;
    }
    // Clear type filter when using quick filters
    if (typeFilter) {
      typeFilter.value = '';
    }
    // Update pill active states
    updatePillActiveState(category);
    // Apply the filter
    filterCards();
    // Scroll to results smoothly
    const resultsBar = document.querySelector('.tool-results-bar');
    if (resultsBar) {
      resultsBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // ========================================
  // Keyboard Shortcuts
  // ========================================
  document.addEventListener('keydown', (e) => {
    // "/" key focuses search (unless already in an input)
    if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
      e.preventDefault();
      searchInput?.focus();
      searchInput?.select();
    }
    // Escape clears search when focused
    if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.value = '';
      searchInput.blur();
      filterCards();
    }
  });

  // ========================================
  // Event Listeners
  // ========================================
  searchInput?.addEventListener('input', debounceFilter);
  categoryFilter?.addEventListener('change', () => {
    updatePillActiveState(categoryFilter.value);
    filterCards();
  });
  typeFilter?.addEventListener('change', filterCards);
  sortSelect?.addEventListener('change', () => {
    sortCards();
    filterCards(); // Re-apply filters after sort
  });

  gridViewBtn?.addEventListener('click', () => setView('grid'));
  listViewBtn?.addEventListener('click', () => setView('list'));

  // Keyboard navigation for cards
  cards.forEach(card => {
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const link = card.querySelector('a');
        if (link) link.click();
      }
    });
  });

  // ========================================
  // Initialize
  // ========================================
  // Restore saved view preference
  const savedView = localStorage.getItem('tool-catalog-view');
  if (savedView) setView(savedView);

  // Set "All" pill as active initially
  updatePillActiveState('');

  // Initial filter (show all)
  filterCards();

  // Add entrance animation delay to cards
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.03}s`;
  });
});
