// ==========================================
// Flexible Quantity & Custom Limits System
// ==========================================
function onSearchLimitChange(val) {
  const customWrap = document.getElementById('search-custom-limit-wrap');
  if (val === 'custom') {
    if (customWrap) {
      customWrap.classList.remove('hidden');
      customWrap.classList.add('flex');
    }
    const customInput = document.getElementById('search-custom-limit');
    if (customInput) customInput.focus();
  } else {
    if (customWrap) {
      customWrap.classList.add('hidden');
      customWrap.classList.remove('flex');
    }
    const num = parseInt(val, 10) || 50;
    localStorage.setItem('aurora_crawl_limit', num);
  }
}

function getActiveSearchLimit() {
  const limitSelect = document.getElementById('search-limit');
  if (!limitSelect) return 50;
  if (limitSelect.value === 'custom') {
    const customInput = document.getElementById('search-custom-limit');
    const num = customInput ? parseInt(customInput.value, 10) : 20;
    return Math.max(1, Math.min(300, num || 20));
  }
  return Math.max(1, Math.min(300, parseInt(limitSelect.value, 10) || 50));
}

function onBatchLimitChange(val, source) {
  const topSelect = document.getElementById('top-batch-limit');
  const bottomSelect = document.getElementById('next-batch-limit');
  const topWrap = document.getElementById('top-custom-limit-wrap');
  const bottomWrap = document.getElementById('bottom-custom-limit-wrap');
  const topInput = document.getElementById('top-custom-limit');
  const bottomInput = document.getElementById('bottom-custom-limit');

  if (topSelect) topSelect.value = val;
  if (bottomSelect) bottomSelect.value = val;

  if (val === 'custom') {
    if (topWrap) { topWrap.classList.remove('hidden'); topWrap.classList.add('flex'); }
    if (bottomWrap) { bottomWrap.classList.remove('hidden'); bottomWrap.classList.add('flex'); }
    const activeInput = source === 'top' ? topInput : bottomInput;
    if (activeInput) activeInput.focus();
  } else {
    if (topWrap) { topWrap.classList.add('hidden'); topWrap.classList.remove('flex'); }
    if (bottomWrap) { bottomWrap.classList.add('hidden'); bottomWrap.classList.remove('flex'); }
    const num = parseInt(val, 10) || 50;
    localStorage.setItem('aurora_crawl_limit', num);
    updateBatchButtonsText(num);
  }
  updateFabDisplay();
}

function syncCustomBatchLimit(val, source) {
  const topInput = document.getElementById('top-custom-limit');
  const bottomInput = document.getElementById('bottom-custom-limit');
  if (source === 'top' && bottomInput) bottomInput.value = val;
  if (source === 'bottom' && topInput) topInput.value = val;
  const num = Math.max(1, Math.min(300, parseInt(val, 10) || 20));
  localStorage.setItem('aurora_crawl_limit', num);
  updateBatchButtonsText(num);
  updateFabDisplay();
}

function updateBatchButtonsText(limit) {
  const topBtnText = document.getElementById('top-btn-fetch-text');
  if (topBtnText) {
    topBtnText.innerText = `抓取下 ${limit} 张`;
  }
  const floatingBtnText = document.getElementById('floating-btn-text');
  if (floatingBtnText) {
    floatingBtnText.innerText = `⚡ 抓取下 ${limit} 张`;
  }
  updateFabDisplay();
}

function getActiveBatchLimit() {
  const topSelect = document.getElementById('top-batch-limit');
  const bottomSelect = document.getElementById('next-batch-limit');
  const selectVal = topSelect ? topSelect.value : (bottomSelect ? bottomSelect.value : '50');

  if (selectVal === 'custom') {
    const topInput = document.getElementById('top-custom-limit');
    const bottomInput = document.getElementById('bottom-custom-limit');
    const customVal = (topInput && topInput.value) || (bottomInput && bottomInput.value) || '20';
    return Math.max(1, Math.min(300, parseInt(customVal, 10) || 20));
  }
  return Math.max(1, Math.min(300, parseInt(selectVal, 10) || 50));
}

// ==========================================
// FLOATING FAB CLUSTER & BATCH CONFIG MODAL
// ==========================================
function updateFabDisplay() {
  const fabCluster = document.getElementById('gallery-floating-cluster');
  if (!fabCluster) return;

  if (AppState.currentView === 'character') {
    fabCluster.classList.remove('hidden');
  } else {
    fabCluster.classList.add('hidden');
    return;
  }

  const rating = AppState.workbenchRating || 'sfw';
  const limit = getActiveBatchLimit();

  const ratingBadge = document.getElementById('fab-rating-badge');
  if (ratingBadge) {
    if (rating === 'r18') {
      ratingBadge.className = 'px-2.5 py-0.5 rounded-full bg-pink-500/20 text-pink-300 border border-pink-500/40 text-[11px] font-mono font-bold flex items-center gap-1';
      ratingBadge.innerHTML = '🔞 R-18专区';
    } else {
      ratingBadge.className = 'px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[11px] font-mono font-bold flex items-center gap-1';
      ratingBadge.innerHTML = '🍀 全年龄';
    }
  }

  const countBadge = document.getElementById('fab-count-badge');
  if (countBadge) {
    countBadge.innerText = limit;
  }
}

function openBatchConfigModal() {
  const modal = document.getElementById('modal-batch-config');
  const card = document.getElementById('modal-batch-config-card');
  if (!modal) return;

  const rating = AppState.workbenchRating || 'sfw';
  const limit = getActiveBatchLimit();

  setModalConfigRating(rating, false);
  setModalConfigLimit(limit, false);

  modal.classList.remove('hidden');
  setTimeout(() => {
    modal.classList.remove('opacity-0');
    if (card) {
      card.classList.remove('scale-95');
      card.classList.add('scale-100');
    }
  }, 10);
}

function closeBatchConfigModal() {
  const modal = document.getElementById('modal-batch-config');
  const card = document.getElementById('modal-batch-config-card');
  if (!modal) return;

  modal.classList.add('opacity-0');
  if (card) {
    card.classList.remove('scale-100');
    card.classList.add('scale-95');
  }
  setTimeout(() => {
    modal.classList.add('hidden');
  }, 200);
}

function setModalConfigRating(rating, triggerSync = true) {
  AppState.workbenchRating = rating;
  if (triggerSync) {
    setCharWorkbenchRating(rating);
  }
  const sfwBtn = document.getElementById('cfg-rating-sfw');
  const r18Btn = document.getElementById('cfg-rating-r18');
  if (sfwBtn && r18Btn) {
    if (rating === 'r18') {
      r18Btn.className = 'batch-rating-pill-btn active-r18';
      sfwBtn.className = 'batch-rating-pill-btn';
    } else {
      sfwBtn.className = 'batch-rating-pill-btn active-sfw';
      r18Btn.className = 'batch-rating-pill-btn';
    }
  }
  updateModalSubmitButton();
  updateFabDisplay();
}

function setModalConfigLimit(limit, triggerSync = true) {
  const num = Math.max(1, Math.min(300, parseInt(limit, 10) || 20));
  if (triggerSync) {
    onBatchLimitChange(String(num), 'top');
    const topSelect = document.getElementById('top-batch-limit');
    if (topSelect) {
      if ([10, 20, 30, 50, 100].includes(num)) {
        topSelect.value = String(num);
      } else {
        topSelect.value = 'custom';
        const topWrap = document.getElementById('top-custom-limit-wrap');
        if (topWrap) { topWrap.classList.remove('hidden'); topWrap.classList.add('flex'); }
        const topInput = document.getElementById('top-custom-limit');
        if (topInput) topInput.value = num;
      }
    }
  }
  document.querySelectorAll('.cfg-limit-btn').forEach(btn => {
    const btnLimit = parseInt(btn.getAttribute('data-limit'), 10);
    const isActive = (btnLimit === num);
    btn.className = `cfg-limit-btn ${isActive ? 'active' : ''}`;
  });

  const customInput = document.getElementById('cfg-modal-custom-input');
  if (customInput) {
    customInput.value = ![20, 50, 100, 150, 200].includes(num) ? num : '';
  }

  const hint = document.getElementById('cfg-current-limit-val');
  if (hint) hint.innerText = num;

  updateModalSubmitButton();
  updateFabDisplay();
}

function onModalCustomLimitInput(val) {
  const num = parseInt(val, 10);
  if (!isNaN(num) && num >= 1 && num <= 300) {
    setModalConfigLimit(num, true);
  }
}

function updateModalSubmitButton() {
  const limit = getActiveBatchLimit();
  const rating = AppState.workbenchRating || 'sfw';
  const countEl = document.getElementById('cfg-submit-count');
  const ratingEl = document.getElementById('cfg-submit-rating');
  if (countEl) countEl.innerText = limit;
  if (ratingEl) ratingEl.innerText = (rating === 'r18' ? '🔞 R-18专区' : '🍀 全年龄');
}

function confirmModalBatchFetch() {
  closeBatchConfigModal();
  triggerFetchNextBatch();
}

function scrollToLatestBatch() {
  let maxBatch = 1;
  (AppState.images || []).forEach(img => {
    if (img.batch_number && img.batch_number > maxBatch) maxBatch = img.batch_number;
  });
  smoothScrollToBatch(maxBatch);
}

function scrollToPageTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}


// ==========================================
// Enhanced Batch Navigation & Smooth Positioning
// ==========================================
function smoothScrollToBatch(batchNum) {
  const targetElement = document.getElementById(`batch-divider-${batchNum}`) || document.getElementById(`batch-section-${batchNum}`);
  if (!targetElement) return;

  const rect = targetElement.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const targetY = rect.top + scrollTop - 105;

  window.scrollTo({
    top: Math.max(0, targetY),
    behavior: 'smooth'
  });

  // Trigger high-taste focus glow pulse
  targetElement.classList.remove('highlight-new-batch');
  void targetElement.offsetWidth;
  targetElement.classList.add('highlight-new-batch');

  // Highlight active pill in batch switcher
  document.querySelectorAll('.batch-nav-pill').forEach(pill => {
    const isActive = pill.id === `batch-nav-pill-${batchNum}`;
    pill.classList.toggle('active', isActive);
  });
}

function selectBatchImages(batchNum, event) {
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }
  const batchImages = (AppState.filteredImages || AppState.images).filter(i => (i.batch_number || 1) === batchNum);
  if (batchImages.length === 0) return;

  const allSelected = batchImages.every(i => AppState.selectedImageIds.has(i.id));

  batchImages.forEach(img => {
    if (allSelected) {
      AppState.selectedImageIds.delete(img.id);
    } else {
      AppState.selectedImageIds.add(img.id);
    }
  });

  updateBatchActionBar();
  renderGalleryFeed();

  showToast(allSelected ? `已取消第 ${batchNum} 批次的选择` : `已选中第 ${batchNum} 批次共 ${batchImages.length} 张图片`, 'info');
}

function renderBatchSwitcher() {
  const bar = document.getElementById('batch-switcher-bar');
  const container = document.getElementById('batch-nav-pills-container');
  if (!bar || !container) return;

  const images = AppState.filteredImages || AppState.images || [];
  const batches = Array.from(new Set(images.map(i => i.batch_number || 1))).sort((a, b) => a - b);
  
  if (batches.length <= 1) {
    bar.classList.add('hidden');
    bar.classList.remove('flex');
    return;
  }

  bar.classList.remove('hidden');
  bar.classList.add('flex');

  container.innerHTML = batches.map(b => {
    const count = images.filter(i => (i.batch_number || 1) === b).length;
    return `
      <button 
        onclick="smoothScrollToBatch(${b})" 
        id="batch-nav-pill-${b}"
        class="batch-nav-pill"
        title="点击平滑跳转至第 ${b} 批次"
      >
        <i data-lucide="layers" class="w-3 h-3 text-[#c5a880]"></i>
        <span>第 ${b} 批 (${count}张)</span>
      </button>
    `;
  }).join('') + `
    <button 
      onclick="triggerFetchNextBatch()" 
      class="batch-nav-pill text-[#c5a880] border-[#c5a880]/30 hover:border-[#c5a880] hover:bg-[#c5a880]/20"
      title="抓取下一批"
    >
      <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i>
      <span>抓取下一批</span>
    </button>
  `;

  lucide.createIcons({ root: container });
}


// ==========================================
// Gallery Filter & Card Action Helpers
// ==========================================
function filterGalleryStatus(status, btn) {
  AppState.galleryStatusFilter = status;
  document.querySelectorAll('.gallery-tab-btn').forEach(b => {
    const isTarget = (b === btn) || (b.getAttribute('data-status') === status);
    b.classList.toggle('active', isTarget);
    b.classList.toggle('bg-white/10', isTarget);
    b.classList.toggle('text-white', isTarget);
    b.classList.toggle('text-slate-400', !isTarget);
  });
  renderGalleryFeed();
}

function filterGalleryRating(rating, btn) {
  AppState.galleryRatingFilter = rating;
  document.querySelectorAll('.gallery-rating-filter-btn').forEach(b => {
    const isTarget = (b === btn) || (b.getAttribute('data-rating') === rating);
    b.classList.toggle('active', isTarget);
    b.classList.toggle('bg-white/10', isTarget);
    b.classList.toggle('text-white', isTarget);
    b.classList.toggle('text-slate-400', !isTarget);
  });
  renderGalleryFeed();
}

async function toggleFavoriteSingle(imageId, event) {
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }
  return toggleFavoriteImage(imageId);
}

/**
 * AURORA & CURATOR WORKBENCH CONTROLLER
 * Anime Gallery Manager
 */

// Immediate Auth Key Capture & Persistence
(function() {
  try {
    const params = new URLSearchParams(window.location.search);
    const magicKey = (params.get('key') || params.get('auth_key') || '').trim();
    if (magicKey && /^[a-zA-Z0-9_-]+$/.test(magicKey)) {
      localStorage.setItem('aurora_auth_token', magicKey);
      document.cookie = `auth_token=${encodeURIComponent(magicKey)}; max-age=315360000; path=/; samesite=lax`;
    }
  } catch (e) {}
})();

const API_BASE = window.location.pathname.startsWith('/gallery') ? '/gallery' : '';

// Authenticated API Fetch Helper
async function apiFetch(url, options = {}) {
  options.headers = options.headers || {};
  let rawToken = localStorage.getItem('aurora_auth_token');
  
  if (!rawToken) {
    const match = document.cookie.match(/auth_token=([^;]+)/);
    if (match) {
      rawToken = decodeURIComponent(match[1]);
      localStorage.setItem('aurora_auth_token', rawToken);
    }
  }

  const token = (rawToken || '').trim();
  const isCleanToken = /^[a-zA-Z0-9_-]+$/.test(token);

  if (isCleanToken) {
    if (options.headers instanceof Headers) {
      options.headers.set('Authorization', `Bearer ${token}`);
    } else {
      options.headers['Authorization'] = `Bearer ${token}`;
    }
    // Append token to query as guaranteed fallback
    const sep = url.includes('?') ? '&' : '?';
    if (!url.includes('token=') && !url.includes('key=')) {
      url = `${url}${sep}token=${encodeURIComponent(token)}`;
    }
  }
  options.credentials = 'include';

  try {
    const res = await fetch(url, options);
    return res;
  } catch (err) {
    console.warn('API Fetch Error, attempting clean retry:', url, err);
    try {
      const fallbackOpts = { ...options };
      if (fallbackOpts.headers && !(fallbackOpts.headers instanceof Headers)) {
        const cleanHeaders = { ...fallbackOpts.headers };
        delete cleanHeaders['Authorization'];
        fallbackOpts.headers = cleanHeaders;
      }
      const fallbackRes = await fetch(url, fallbackOpts);
      return fallbackRes;
    } catch (fallbackErr) {
      console.error('Fallback Fetch also failed:', fallbackErr);
      throw err;
    }
  }
}

const AppState = {
  currentView: 'home',
  currentCharacter: null,
  images: [],
  selectedImageIds: new Set(),
  galleryStatusFilter: 'all',
  galleryRatingFilter: 'all',
  crawlRating: localStorage.getItem('aurora_crawl_rating') || 'sfw', // 'sfw' or 'r18'
  workbenchRating: localStorage.getItem('aurora_wb_rating') || 'sfw', // 'sfw' or 'r18'
  layoutMode: localStorage.getItem('aurora_layout_mode') || 'single', // 'single', '2col', 'masonry'
  favLayoutMode: localStorage.getItem('aurora_fav_layout_mode') || 'single',
  lightboxIndex: 0,
  taskPollInterval: null,
  cachedCharacters: [],
  activeGameFilter: 'all',
  characterKeyword: '',
  quickCrawlTarget: null,
  quickCrawlRating: localStorage.getItem('aurora_qc_rating') || 'sfw',
  quickCrawlLimit: parseInt(localStorage.getItem('aurora_qc_limit'), 10) || 50,
  rosterGame: 'wuthering_waves',
  rosterCatalog: [],
  rosterKeyword: ''
};

// Rating Mode Switchers
function setCrawlRating(rating) {
  AppState.crawlRating = rating;
  localStorage.setItem('aurora_crawl_rating', rating);

  const sfwBtn = document.getElementById('btn-rating-sfw');
  const r18Btn = document.getElementById('btn-rating-r18');
  if (sfwBtn && r18Btn) {
    if (rating === 'r18') {
      r18Btn.className = 'px-3 py-2 rounded-lg font-bold flex items-center gap-1.5 transition-all text-pink-400 bg-pink-500/20 border border-pink-500/30';
      sfwBtn.className = 'px-3 py-2 rounded-lg font-bold flex items-center gap-1.5 transition-all text-slate-400 hover:text-white';
    } else {
      sfwBtn.className = 'px-3 py-2 rounded-lg font-bold flex items-center gap-1.5 transition-all text-[#c5a880] bg-[#c5a880]/15 border border-[#c5a880]/30';
      r18Btn.className = 'px-3 py-2 rounded-lg font-bold flex items-center gap-1.5 transition-all text-slate-400 hover:text-white';
    }
  }

  updateTopRatingBadge();
}

function setCharWorkbenchRating(rating) {
  AppState.workbenchRating = rating;
  localStorage.setItem('aurora_wb_rating', rating);

  const sfwBtn = document.getElementById('btn-char-rating-sfw');
  const r18Btn = document.getElementById('btn-char-rating-r18');
  if (sfwBtn && r18Btn) {
    if (rating === 'r18') {
      r18Btn.className = 'px-2.5 py-1.5 rounded-lg font-bold flex items-center gap-1 transition-all text-pink-400 bg-pink-500/20 border border-pink-500/30';
      sfwBtn.className = 'px-2.5 py-1.5 rounded-lg font-bold flex items-center gap-1 transition-all text-slate-400 hover:text-white';
    } else {
      sfwBtn.className = 'px-2.5 py-1.5 rounded-lg font-bold flex items-center gap-1 transition-all text-[#c5a880] bg-[#c5a880]/15 border border-[#c5a880]/30';
      r18Btn.className = 'px-2.5 py-1.5 rounded-lg font-bold flex items-center gap-1 transition-all text-slate-400 hover:text-white';
    }
  }
  updateFabDisplay();
}

function updateTopRatingBadge() {
  const dot = document.getElementById('top-rating-dot');
  const text = document.getElementById('top-rating-text');
  if (dot && text) {
    if (AppState.crawlRating === 'r18') {
      dot.className = 'w-2 h-2 rounded-full bg-pink-500 animate-pulse';
      text.innerText = 'R-18 限制级模式 (无全年龄)';
      text.className = 'text-pink-300 font-bold';
    } else {
      dot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
      text.innerText = 'SFW 全年龄模式 (无R-18)';
      text.className = 'text-slate-300';
    }
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const bgClass = type === 'success' ? 'bg-emerald-600 text-white' : (type === 'error' ? 'bg-red-600 text-white' : 'bg-[#1a1c28] border border-white/20 text-white');
  const icon = type === 'success' ? 'check-circle' : (type === 'error' ? 'alert-circle' : 'info');

  toast.className = `${bgClass} backdrop-blur-xl px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 text-xs font-mono font-semibold animate-in fade-in slide-in-from-bottom-5 duration-200 pointer-events-auto`;
  toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4"></i> <span>${message}</span>`;
  container.appendChild(toast);
  lucide.createIcons({ root: toast });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'transition-opacity', 'duration-300');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// SPA Router & Navigation
function navigate(viewName, event) {
  if (event) event.preventDefault();
  AppState.currentView = viewName;

  // Desktop Nav Buttons
  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.id === `nav-${viewName}`);
  });

  // Mobile Bottom Nav Buttons
  document.querySelectorAll('.mob-nav-btn').forEach(btn => {
    const isActive = btn.id === `mob-nav-${viewName}`;
    btn.classList.toggle('active', isActive);
    btn.classList.toggle('text-[#c5a880]', isActive);
    btn.classList.toggle('text-slate-400', !isActive);
  });

  // View Panels
  document.querySelectorAll('.spa-view').forEach(panel => {
    panel.classList.add('hidden');
    panel.classList.remove('active');
  });

  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.remove('hidden');
    target.classList.add('active');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });

  updateFabDisplay();

  if (viewName === 'home') {
    loadRecentTasks();
  } else if (viewName === 'characters') {
    loadCharactersList();
  } else if (viewName === 'favorites') {
    loadFavoritesList();
  } else if (viewName === 'settings') {
    loadSettings();
    loadAuthorizedDevices();
    loadMagicLinkInfo();
  }
}

// Layout Switcher (Single Column Feed / 2-Col / Masonry)
function setLayoutMode(mode) {
  AppState.layoutMode = mode;
  localStorage.setItem('aurora_layout_mode', mode);

  ['single', '2col', 'masonry'].forEach(m => {
    const btn = document.getElementById(`btn-layout-${m}`);
    if (btn) {
      const active = m === mode;
      btn.className = active 
        ? 'px-3 py-1 rounded-md font-semibold text-[#c5a880] bg-[#c5a880]/15 flex items-center gap-1.5 transition-all'
        : 'px-2.5 py-1 rounded-md text-slate-400 hover:text-white flex items-center gap-1 transition-all';
    }
  });

  renderGalleryFeed();
}

function setFavLayoutMode(mode) {
  AppState.favLayoutMode = mode;
  localStorage.setItem('aurora_fav_layout_mode', mode);

  ['single', 'masonry'].forEach(m => {
    const btn = document.getElementById(`btn-fav-layout-${m}`);
    if (btn) {
      const active = m === mode;
      btn.className = active 
        ? 'px-3 py-1 rounded-md font-semibold text-[#c5a880] bg-[#c5a880]/15 flex items-center gap-1.5'
        : 'px-3 py-1 rounded-md text-slate-400 hover:text-white flex items-center gap-1.5';
    }
  });

  renderFavoritesFeed();
}

// Search Actions
function fillSearch(name) {
  const input = document.getElementById('search-input');
  if (input) {
    input.value = name;
    startSearch();
  }
}

async function startSearch() {
  const input = document.getElementById('search-input');
  const charName = input.value.trim();
  const limit = getActiveSearchLimit();
  const ratingMode = AppState.crawlRating || 'sfw';
  const ratingDesc = ratingMode === 'r18' ? 'R-18 限制级' : '全年龄';

  if (!charName) {
    showToast('请输入动漫角色名称', 'error');
    input.focus();
    return;
  }

  const btn = document.getElementById('btn-start-search');
  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>正在启动...</span>`;
  lucide.createIcons({ root: btn });

  try {
    const res = await apiFetch(`${API_BASE}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character_name: charName, limit, rating: ratingMode })
    });

    if (!res.ok) {
      let errMsg = '创建任务失败';
      try {
        const err = await res.json();
        errMsg = err.detail || errMsg;
      } catch (_) {
        errMsg = `服务器响应异常 (${res.status})`;
      }
      throw new Error(errMsg);
    }

    const data = await res.json();
    showToast(`⚡ 任务已启动！正在按【${ratingDesc}】点赞量并发收集【${charName}】的 ${limit} 张无损原画`, 'success');
    input.value = '';

    await loadRecentTasks();
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i> <span>开始收集</span>`;
    lucide.createIcons({ root: btn });
  }
}

// Tasks Polling
async function loadRecentTasks() {
  const container = document.getElementById('tasks-container');
  if (!container) return;

  try {
    const res = await apiFetch(`${API_BASE}/api/tasks?limit=6`);
    if (!res.ok) return;
    const tasks = await res.json();

    if (tasks.length === 0) {
      container.innerHTML = `
        <div class="col-span-full p-8 rounded-2xl bg-white/[0.02] border border-white/5 text-center text-slate-500 font-mono text-xs">
          暂无历史任务，输入角色名称即可秒级并发收集
        </div>
      `;
      return;
    }

    container.innerHTML = tasks.map(t => {
      const isRunning = ['queued', 'searching', 'downloading', 'processing'].includes(t.status);
      const isDone = t.status === 'completed' && t.progress_current > 0;
      const isEmpty = t.status === 'empty' || (t.status === 'completed' && t.progress_current === 0);
      const isFailed = t.status === 'failed';
      const isR18 = t.rating === 'r18';
      
      const pct = isDone ? 100 : (t.progress_total > 0 ? Math.round((t.progress_current / t.progress_total) * 100) : 0);

      const ratingBadge = isR18 
        ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-pink-500/20 text-pink-300 border border-pink-500/40 font-bold flex items-center gap-1"><i data-lucide="flame" class="w-3 h-3 text-pink-400"></i> R-18</span>`
        : `<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold flex items-center gap-1"><i data-lucide="shield-check" class="w-3 h-3 text-emerald-400"></i> 全年龄</span>`;

      let statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">✓ 已收录 ${t.progress_current} 张</span>`;
      if (isRunning) {
        statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-[#c5a880]/20 text-[#c5a880] border border-[#c5a880]/40 flex items-center gap-1 font-bold"><i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i> 进行中 (${pct}%)</span>`;
      } else if (isEmpty) {
        statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-white/5 text-slate-400 border border-white/10">无新作品</span>`;
      } else if (isFailed) {
        statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-red-500/20 text-red-300 border border-red-500/30">异常</span>`;
      }

      return `
        <div 
          onclick="openCharacterGallery('${t.character_name}')"
          class="p-5 rounded-2xl bg-[#13141c] border border-white/10 hover:border-[#c5a880]/50 flex flex-col justify-between gap-4 shadow-lg transition-all relative group cursor-pointer"
        >
          <div>
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="text-base font-serif font-bold text-white group-hover:text-[#c5a880] transition-colors">${t.character_name}</span>
                ${ratingBadge}
              </div>
              <div class="flex items-center gap-2">
                ${statusBadge}
                <button onclick="deleteTaskRecord('${t.id}', event)" class="p-1 rounded-lg text-slate-500 hover:text-red-400 hover:bg-white/5 transition-all opacity-70 group-hover:opacity-100" title="删除本条记录">
                  <i data-lucide="x" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
            <p class="text-xs text-slate-400 font-mono line-clamp-1 mb-3">${t.progress_message || '处理中...'}</p>
            
            ${!isEmpty ? `
              <div class="w-full h-2 rounded-full bg-white/5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-[#c5a880] to-[#ff5c8a] transition-all duration-300 shadow-sm" style="width: ${pct}%"></div>
              </div>
            ` : ''}
          </div>

          <div class="flex items-center justify-between pt-2 border-t border-white/5 text-xs font-mono">
            <span class="${isDone ? 'text-emerald-400 font-bold' : 'text-slate-500'}">${isDone ? `共 ${t.progress_current} 张【${isR18 ? 'R-18' : '全年龄'}】原画入库` : `${t.progress_current} / ${t.progress_total} 张`}</span>
            <button class="px-3 py-1.5 rounded-lg bg-white/10 group-hover:bg-[#c5a880] text-white group-hover:text-black font-bold flex items-center gap-1 transition-all">
              <span>进入画廊</span>
              <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');

    lucide.createIcons({ root: container });

    const hasActive = tasks.some(t => ['queued', 'searching', 'downloading', 'processing'].includes(t.status));
    if (hasActive && !AppState.taskPollInterval) {
      AppState.taskPollInterval = setInterval(loadRecentTasks, 1500);
    } else if (!hasActive && AppState.taskPollInterval) {
      clearInterval(AppState.taskPollInterval);
      AppState.taskPollInterval = null;
    }
  } catch (e) {
    console.error(e);
  }
}

async function deleteTaskRecord(taskId, event) {
  if (event) event.stopPropagation();
  try {
    await apiFetch(`${API_BASE}/api/tasks/${taskId}`, { method: 'DELETE' });
    await loadRecentTasks();
  } catch (e) {
    console.error(e);
  }
}

async function clearAllFinishedTasks() {
  try {
    await apiFetch(`${API_BASE}/api/tasks`, { method: 'DELETE' });
    showToast('已清理历史任务列表', 'info');
    await loadRecentTasks();
  } catch (e) {
    console.error(e);
  }
}

// Character Gallery Workbench
async function openCharacterGallery(characterName) {
  AppState.currentCharacter = characterName;
  AppState.selectedImageIds.clear();
  AppState.galleryStatusFilter = 'all';

  document.getElementById('gallery-char-title').innerText = characterName;
  navigate('character');
  updateFabDisplay();

  await loadCharacterNavRibbon();
  await loadCharacterImages(characterName);
}

// Load Top Horizontal Character Switcher Ribbon
async function loadCharacterNavRibbon() {
  const ribbon = document.getElementById('char-nav-ribbon');
  if (!ribbon) return;

  try {
    const res = await apiFetch(`${API_BASE}/api/characters`);
    if (!res.ok) return;
    const chars = await res.json();

    ribbon.innerHTML = chars.map(c => {
      const active = c.name === AppState.currentCharacter;
      return `
        <button 
          onclick="openCharacterGallery('${c.name}')" 
          class="px-4 py-2 rounded-full font-mono text-xs whitespace-nowrap transition-all flex items-center gap-2 border ${active ? 'bg-[#c5a880]/20 text-[#c5a880] border-[#c5a880] font-bold shadow-md' : 'bg-[#13141c] text-slate-400 border-white/10 hover:border-white/20 hover:text-white'}"
        >
          <span>${c.name}</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] ${active ? 'bg-[#c5a880] text-black font-bold' : 'bg-white/10 text-slate-300'}">${c.total_candidates}</span>
        </button>
      `;
    }).join('');
  } catch (e) {
    console.error(e);
  }
}


// Helper Media URL
function getMediaUrl(url) {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.includes('/data/anime-gallery/cache/')) {
    url = url.replace('/data/anime-gallery/cache/', '/api/media/cache/');
  } else if (url.includes('/data/anime-gallery/temp/')) {
    url = url.replace('/data/anime-gallery/temp/', '/api/media/temp/');
  } else if (url.includes('/data/anime-gallery/favorites/')) {
    url = url.replace('/data/anime-gallery/favorites/', '/api/media/favorites/');
  }
  if (url.startsWith('/gallery')) return url;
  return `${API_BASE}${url.startsWith('/') ? '' : '/'}${url}`;
}

// Load Images for Character
async function loadCharacterImages(characterName) {
  try {
    const res = await apiFetch(`${API_BASE}/api/images?character_name=${encodeURIComponent(characterName)}&status=all&limit=400`);
    if (!res.ok) throw new Error('Fetch images failed');
    const images = await res.json();
    AppState.images = images;

    const candCount = images.filter(i => i.status === 'pending').length;
    const favCount = images.filter(i => i.status === 'saved').length;

    const candEl = document.getElementById('gallery-count-candidates');
    if (candEl) candEl.innerText = candCount;
    const favEl = document.getElementById('gallery-count-favorites');
    if (favEl) favEl.innerText = favCount;
    const tabAll = document.getElementById('tab-cnt-all');
    if (tabAll) tabAll.innerText = images.length;
    const tabPending = document.getElementById('tab-cnt-pending');
    if (tabPending) tabPending.innerText = candCount;
    const tabSaved = document.getElementById('tab-cnt-saved');
    if (tabSaved) tabSaved.innerText = favCount;

    renderGalleryFeed();
  } catch (e) {
    showToast(`加载图片失败: ${e.message}`, 'error');
  }
}


async function triggerFetchNextBatch() {
  if (!AppState.currentCharacter) return;
  const limit = getActiveBatchLimit();
  const ratingMode = AppState.workbenchRating || AppState.crawlRating || 'sfw';
  const ratingDesc = ratingMode === 'r18' ? 'R-18 限制级' : '全年龄';

  const btnTop = document.getElementById('btn-fetch-next');
  const btnBottom = document.getElementById('btn-bottom-fetch-next');
  const btnFloating = document.getElementById('floating-side-next-btn');
  const floatingText = document.getElementById('floating-btn-text');

  const setButtonsLoading = (loading, text) => {
    if (btnTop) {
      btnTop.disabled = loading;
      btnTop.innerHTML = loading 
        ? `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>抓取中...</span>` 
        : `<i data-lucide="plus-circle" class="w-4 h-4"></i> <span id="top-btn-fetch-text">抓取下 ${limit} 张</span>`;
      lucide.createIcons({ root: btnTop });
    }
    if (btnBottom) {
      btnBottom.disabled = loading;
      btnBottom.innerHTML = loading 
        ? `<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> <span>${text || '正在并发检索新原画...'}</span>` 
        : `<i data-lucide="download-cloud" class="w-5 h-5"></i> <span>⚡ 抓取下 ${limit} 张新原画</span>`;
      lucide.createIcons({ root: btnBottom });
    }
    if (btnFloating) {
      btnFloating.disabled = loading;
      if (floatingText) floatingText.innerText = loading ? '抓取中...' : `⚡ 抓取下 ${limit} 张`;
    }
  };

  setButtonsLoading(true, '正在启动增量抓取...');
  showToast(`⚡ 正在按【${ratingDesc}】检索【${AppState.currentCharacter}】下一批 ${limit} 张未收录新原画...`, 'info');

  try {
    const res = await apiFetch(`${API_BASE}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character_name: AppState.currentCharacter, limit, rating: ratingMode })
    });
    if (!res.ok) throw new Error('创建增量任务失败');

    const task = await res.json();
    const pollId = setInterval(async () => {
      const tr = await apiFetch(`${API_BASE}/api/tasks/${task.id}`);
      if (tr.ok) {
        const td = await tr.json();
        if (td.progress_message) {
          setButtonsLoading(true, td.progress_message);
        }
        if (td.status === 'completed') {
          clearInterval(pollId);
          setButtonsLoading(false);
          const countGot = td.result_count || limit;
          showToast(`✓ 成功抓取 ${countGot} 张【${ratingDesc}】新原画！已自动过滤历史重复图`, 'success');
          
          await loadCharacterImages(AppState.currentCharacter);

          // Find latest batch and auto-scroll smoothly with precise offset
          setTimeout(() => {
            const batches = AppState.images.map(i => i.batch_number || 1);
            const maxBatch = batches.length > 0 ? Math.max(...batches) : 1;
            smoothScrollToBatch(maxBatch);
          }, 200);

        } else if (td.status === 'failed' || td.status === 'empty') {
          clearInterval(pollId);
          setButtonsLoading(false);
          if (td.status === 'empty') {
            showToast(td.progress_message || '全网暂无更多未收录新图', 'info');
          } else {
            showToast(`任务失败: ${td.error_message}`, 'error');
          }
        }
      }
    }, 1200);

  } catch (e) {
    setButtonsLoading(false);
    showToast(e.message, 'error');
  }
}

// Render Gallery Feed with Separated Batch Group Sections & Capsule Dividers
function renderGalleryFeed() {
  const container = document.getElementById('gallery-feed-container');
  const emptyState = document.getElementById('gallery-empty-state');
  if (!container) return;

  const filtered = (AppState.images || []).filter(img => {
    if (!img) return false;
    if (AppState.galleryStatusFilter === 'pending' && img.status !== 'pending') return false;
    if (AppState.galleryStatusFilter === 'saved' && img.status !== 'saved') return false;
    if (AppState.galleryRatingFilter === 'sfw' && img.rating === 'r18') return false;
    if (AppState.galleryRatingFilter === 'r18' && img.rating !== 'r18') return false;
    return true;
  });

  AppState.filteredImages = filtered;

  if (filtered.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.classList.remove('hidden');
    renderBatchSwitcher();
    return;
  }
  if (emptyState) emptyState.classList.add('hidden');

  // Container is a vertical stack of isolated batch sections
  container.className = 'w-full flex flex-col gap-0';

  // Group images strictly by batch_number
  const batchMap = new Map();
  filtered.forEach(img => {
    const b = img.batch_number || 1;
    if (!batchMap.has(b)) {
      batchMap.set(b, []);
    }
    batchMap.get(b).push(img);
  });

  // Sort batches ascending (Batch 1 on top, Batch 2 below, etc.)
  const sortedBatches = Array.from(batchMap.keys()).sort((a, b) => a - b);

  let gridClass = 'single-feed-container';
  if (AppState.layoutMode === '2col') {
    gridClass = 'grid-2col-container';
  } else if (AppState.layoutMode === 'masonry') {
    gridClass = 'masonry-container';
  }

  let html = '';

  sortedBatches.forEach((batchNum, bIdx) => {
    const batchImages = batchMap.get(batchNum);
    const isBatchR18 = batchImages.some(i => i.rating === 'r18');

    // Extract latest download time for this batch
    let batchTime = '';
    const sampleImgWithTime = batchImages.find(i => i.download_time);
    if (sampleImgWithTime && sampleImgWithTime.download_time) {
      try {
        const dt = new Date(sampleImgWithTime.download_time.replace(' ', 'T'));
        if (!isNaN(dt.getTime())) {
          batchTime = dt.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
        }
      } catch (_) {}
    }
    if (!batchTime) {
      const now = new Date();
      batchTime = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
    }

    // If NOT the first batch (e.g. Batch 2, Batch 3...), render the Divider in between with clear vertical distance!
    if (bIdx > 0) {
      html += `
        <!-- ===== 批次独立分界线：位于上一批下方、下一批上方，层次分明 ===== -->
        <div class="batch-capsule-divider" id="batch-divider-${batchNum}" data-batch="${batchNum}">
          <!-- 贯穿从左到右的发光水平细线 -->
          <div class="batch-capsule-line"></div>

          <!-- 居中浮动圆角胶囊徽章 -->
          <div class="batch-capsule-badge" id="batch-badge-${batchNum}">
            <div class="flex items-center gap-1.5">
              <i data-lucide="sparkles" class="w-4 h-4 text-[#ff9e3b]"></i>
              <span class="text-white text-xs sm:text-sm font-sans font-bold tracking-wide">
                第 <strong class="text-[#c5a880]">${batchNum}</strong> 批全新抓取
              </span>
            </div>

            ${isBatchR18 ? `
              <span class="px-2.5 py-0.5 rounded-full bg-pink-500/20 text-pink-300 border border-pink-500/40 text-[11px] font-bold font-mono flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-pink-400"></span> 🔞 R-18成人向
              </span>
            ` : `
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[11px] font-bold font-mono flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> 🛡️ 全年龄SFW
              </span>
            `}

            <span class="px-2.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold font-mono flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span> 自动去重
            </span>

            <span class="text-xs text-slate-300 font-mono">共 <strong class="text-white font-bold">${batchImages.length}</strong> 张全新作品</span>

            <span class="text-[11px] font-mono text-slate-400 flex items-center gap-1">
              <i data-lucide="clock" class="w-3.5 h-3.5 text-slate-400"></i> ${batchTime}
            </span>

            <button 
              onclick="selectBatchImages(${batchNum}, event)" 
              class="ml-1 px-2.5 py-0.5 rounded-full bg-white/5 hover:bg-[#c5a880]/20 border border-white/10 hover:border-[#c5a880]/40 text-slate-300 hover:text-[#c5a880] transition-all text-[11px] flex items-center gap-1 cursor-pointer active:scale-95"
              title="一键全选/反选本批所有图片"
            >
              <i data-lucide="check-square" class="w-3 h-3 text-[#c5a880]"></i>
              <span>全选本批</span>
            </button>
          </div>
        </div>
      `;
    }

    // ===== 独立批次区块 (Batch Section) =====
    html += `<section class="batch-group-section" id="batch-section-${batchNum}" data-batch="${batchNum}">`;
    html += `<div class="${gridClass}">`;

    // Render cards within this batch
    batchImages.forEach(img => {
      const isSaved = img.status === 'saved';
      const isSelected = AppState.selectedImageIds.has(img.id);
      const indexNum = img.filename.replace(/\.[^/.]+$/, "");
      const imgSource = img.original_source || 'Pixiv';
      const sizeMb = img.file_size ? (img.file_size / (1024*1024)).toFixed(2) + ' MB' : '超清';
      const resText = img.width ? `${img.width} × ${img.height}` : '无损原画';
      const isR18Img = img.rating === 'r18';
      const ratingTag = isR18Img
        ? `<span class="px-2 py-0.5 rounded-md text-[10px] font-mono bg-pink-500/20 text-pink-300 border border-pink-500/40 font-bold flex items-center gap-1"><i data-lucide="flame" class="w-3 h-3 text-pink-400"></i> R-18</span>`
        : `<span class="px-2 py-0.5 rounded-md text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold flex items-center gap-1"><i data-lucide="shield-check" class="w-3 h-3 text-emerald-400"></i> 全年龄</span>`;

      if (AppState.layoutMode === 'single') {
        html += `
          <div class="single-feed-card p-5 sm:p-7 ${isSaved ? 'is-fav' : ''} ${isSelected ? 'selected' : ''}" data-id="${img.id}">
            <!-- Top Info -->
            <div class="flex items-center justify-between gap-3 mb-4">
              <div class="flex items-center gap-2.5">
                <div 
                  class="custom-checkbox ${isSelected ? 'checked' : ''}"
                  onclick="toggleSelectImage(${img.id}, !${isSelected})"
                  title="选择"
                ></div>
                <span class="px-2.5 py-0.5 rounded-lg bg-[#c5a880]/15 text-[#c5a880] border border-[#c5a880]/30 font-mono text-xs font-black">#${indexNum}</span>
                ${ratingTag}
                <span class="text-sm font-serif font-bold text-white truncate max-w-[220px] sm:max-w-md">${img.title || img.filename}</span>
              </div>

              <div class="flex items-center gap-2 font-mono text-xs">
                <span class="px-2 py-0.5 rounded-md bg-white/[0.06] text-slate-400 border border-white/10 font-mono text-[10px]">#第${batchNum}批</span>
                <span class="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-300 font-sans flex items-center gap-1">
                  <i data-lucide="award" class="w-3 h-3 text-[#c5a880]"></i> ${imgSource}
                </span>
                ${isSaved ? `<span class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-sans font-bold flex items-center gap-1"><i data-lucide="check" class="w-3 h-3"></i> 已永久收藏</span>` : ''}
              </div>
            </div>

            <!-- Image Canvas Frame -->
            <div class="image-canvas-frame p-2 sm:p-4 group cursor-pointer" onclick="openLightbox(${img.id})">
              <img 
                src="${getMediaUrl(img.thumbnail_url || img.temp_url)}" 
                alt="${img.title || img.filename}"
                loading="lazy"
                class="w-full max-h-[78vh] object-contain rounded-lg transition-transform duration-300 group-hover:scale-[1.01]"
              />
              <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3 pointer-events-none">
                <span class="px-4 py-2 rounded-xl bg-black/75 backdrop-blur-md text-white font-mono text-xs border border-white/20 flex items-center gap-2 shadow-2xl">
                  <i data-lucide="maximize-2" class="w-4 h-4 text-[#c5a880]"></i> 点击查看超清大图
                </span>
              </div>
            </div>

            <!-- Bottom Actions -->
            <div class="flex items-center justify-between gap-3 mt-4 pt-4 border-t border-white/10">
              <div class="flex items-center gap-3.5 text-xs font-mono text-slate-400">
                <span class="flex items-center gap-1.5"><i data-lucide="maximize" class="w-3.5 h-3.5 text-[#c5a880]"></i> ${resText}</span>
                <span class="flex items-center gap-1.5"><i data-lucide="hard-drive" class="w-3.5 h-3.5 text-slate-500"></i> ${sizeMb}</span>
                ${img.author_name ? `<span class="hidden sm:flex items-center gap-1.5 truncate max-w-[180px]"><i data-lucide="user" class="w-3.5 h-3.5 text-slate-400"></i> 画师: ${img.author_name}</span>` : ''}
              </div>

              <div class="flex items-center gap-2">
                <button 
                  onclick="toggleFavoriteSingle(${img.id}, event)"
                  class="px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${isSaved ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30' : 'bg-[#c5a880] hover:bg-[#e4ccad] text-black font-bold shadow-md'}"
                  title="${isSaved ? '点击取消收藏' : '归档收藏至 /favorites/'}"
                >
                  <i data-lucide="heart" class="w-3.5 h-3.5 ${isSaved ? 'fill-emerald-400 text-emerald-400' : 'fill-black text-black'}"></i>
                  <span>${isSaved ? '已收藏' : '收藏'}</span>
                </button>
                <button 
                  onclick="deleteSingleImage(${img.id}, event)"
                  class="p-2.5 rounded-xl bg-white/5 hover:bg-red-500/20 hover:text-red-300 text-slate-400 border border-white/5 transition-all"
                  title="删除临时图片"
                >
                  <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
                <a 
                  href="${getMediaUrl(img.favorites_url || img.temp_url)}" 
                  download="${img.filename}"
                  target="_blank"
                  class="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5 transition-all"
                  title="下载原图"
                >
                  <i data-lucide="download" class="w-4 h-4"></i>
                </a>
              </div>
            </div>
          </div>
        `;
      } else {
        html += `
          <div class="group relative rounded-2xl overflow-hidden bg-[#13141c] border border-white/10 hover:border-[#c5a880]/50 transition-all duration-300 shadow-lg ${isSaved ? 'is-fav' : ''} ${isSelected ? 'selected' : ''}" data-id="${img.id}">
            <div class="relative overflow-hidden cursor-pointer" onclick="openLightbox(${img.id})">
              <img 
                src="${getMediaUrl(img.thumbnail_url || img.temp_url)}" 
                alt="${img.title || img.filename}"
                loading="lazy"
                class="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-3">
                <div class="flex items-center justify-between">
                  <div 
                    class="custom-checkbox ${isSelected ? 'checked' : ''}"
                    onclick="event.stopPropagation(); toggleSelectImage(${img.id}, !${isSelected})"
                  ></div>
                  <div class="flex items-center gap-1">${ratingTag}</div>
                </div>
                <div class="flex items-center justify-between text-[11px] font-mono text-slate-300">
                  <span>${resText}</span>
                  <span>${sizeMb}</span>
                </div>
              </div>
            </div>

            <div class="p-3 flex flex-col gap-2 border-t border-white/5 bg-[#0f1016]">
              <div class="flex items-center justify-between gap-1.5">
                <span class="text-xs text-white font-serif font-bold truncate flex-1">${img.title || img.filename}</span>
              </div>
              <div class="flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span class="truncate max-w-[120px] text-slate-400 font-sans">by @${img.author_name || 'Pixiv'}</span>
                <span class="px-2 py-0.5 rounded-md bg-white/[0.06] text-slate-400 border border-white/10 font-mono text-[10px]">#第${batchNum}批</span>
              </div>
              <div class="flex items-center justify-between pt-1 border-t border-white/5 gap-1.5">
                <button 
                  onclick="toggleFavoriteSingle(${img.id}, event)" 
                  class="px-3 py-1.5 rounded-lg ${isSaved ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-white/5 hover:bg-[#c5a880] text-slate-300 hover:text-black border border-white/10'} font-bold text-xs flex items-center gap-1.5 transition-all flex-1 justify-center"
                  title="${isSaved ? '已收藏' : '保存'}"
                >
                  <i data-lucide="heart" class="w-3.5 h-3.5 ${isSaved ? 'fill-emerald-400 text-emerald-400' : 'text-slate-400'}"></i>
                  <span>${isSaved ? '已收藏' : '保存'}</span>
                </button>
                <button 
                  onclick="openLightbox(${img.id})" 
                  class="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/10 transition-all"
                  title="查看大图"
                >
                  <i data-lucide="search" class="w-3.5 h-3.5 text-[#00a2ff]"></i>
                </button>
              </div>
            </div>
          </div>
        `;
      }
    });

    html += `</div>`; // close grid
    html += `</section>`; // close batch-group-section
  });

  container.innerHTML = html;
  lucide.createIcons({ root: container });
  renderBatchSwitcher();
}




// ==========================================
// Batch Selection & Image Operations
// ==========================================

// Toggle Single Image Favorite
async function toggleFavoriteImage(imageId) {
  const img = AppState.images.find(i => i.id === imageId);
  if (!img) return;

  const isSaved = img.status === 'saved';
  const method = isSaved ? 'DELETE' : 'POST';

  try {
    const res = await apiFetch(`${API_BASE}/api/images/${imageId}/favorite`, { method });
    if (!res.ok) throw new Error('操作失败');

    img.status = isSaved ? 'pending' : 'saved';
    showToast(isSaved ? '已取消收藏' : '❤️ 已保存至永久收藏目录！', 'success');

    const candCount = AppState.images.filter(i => i.status === 'pending').length;
    const favCount = AppState.images.filter(i => i.status === 'saved').length;
    const candEl = document.getElementById('gallery-count-candidates');
    if (candEl) candEl.innerText = candCount;
    const favEl = document.getElementById('gallery-count-favorites');
    if (favEl) favEl.innerText = favCount;
    const tabSaved = document.getElementById('tab-cnt-saved');
    if (tabSaved) tabSaved.innerText = favCount;
    const tabPending = document.getElementById('tab-cnt-pending');
    if (tabPending) tabPending.innerText = candCount;

    renderGalleryFeed();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

// Delete Single Image
async function deleteSingleImage(imageId, event) {
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }
  try {
    const res = await apiFetch(`${API_BASE}/api/images/${imageId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('删除失败');

    AppState.images = AppState.images.filter(i => i.id !== imageId);
    AppState.selectedImageIds.delete(imageId);
    showToast('图片已删除', 'info');

    const candCount = AppState.images.filter(i => i.status === 'pending').length;
    const favCount = AppState.images.filter(i => i.status === 'saved').length;
    const candEl = document.getElementById('gallery-count-candidates');
    if (candEl) candEl.innerText = candCount;
    const favEl = document.getElementById('gallery-count-favorites');
    if (favEl) favEl.innerText = favCount;
    const tabAll = document.getElementById('tab-cnt-all');
    if (tabAll) tabAll.innerText = AppState.images.length;
    const tabPending = document.getElementById('tab-cnt-pending');
    if (tabPending) tabPending.innerText = candCount;
    const tabSaved = document.getElementById('tab-cnt-saved');
    if (tabSaved) tabSaved.innerText = favCount;

    renderGalleryFeed();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

// Batch Actions
function toggleSelectImage(imageId, checked) {
  if (checked) {
    AppState.selectedImageIds.add(imageId);
  } else {
    AppState.selectedImageIds.delete(imageId);
  }
  updateBatchActionBar();
  renderGalleryFeed();
}

function selectAllImages(selectAll) {
  const visible = AppState.filteredImages || AppState.images;

  if (selectAll) {
    visible.forEach(i => AppState.selectedImageIds.add(i.id));
  } else {
    AppState.selectedImageIds.clear();
  }
  updateBatchActionBar();
  renderGalleryFeed();
}

function updateBatchActionBar() {
  const floatingBar = document.getElementById('floating-batch-bar');
  const countBadge = document.getElementById('floating-selected-count');
  if (!floatingBar || !countBadge) return;

  const count = AppState.selectedImageIds.size;
  if (count > 0) {
    floatingBar.classList.remove('hidden');
    floatingBar.classList.add('flex');
    countBadge.innerText = `已选 ${count} 张`;
  } else {
    floatingBar.classList.add('hidden');
    floatingBar.classList.remove('flex');
  }
}

async function batchSaveSelected() {
  const ids = Array.from(AppState.selectedImageIds);
  if (ids.length === 0) return;

  try {
    const res = await apiFetch(`${API_BASE}/api/images/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_ids: ids, action: 'save' })
    });
    if (!res.ok) throw new Error('批量收藏失败');

    const data = await res.json();
    showToast(`✓ 已成功批量收藏 ${data.count} 张图片！`, 'success');

    AppState.images.forEach(img => {
      if (ids.includes(img.id)) img.status = 'saved';
    });
    AppState.selectedImageIds.clear();
    updateBatchActionBar();

    const candCount = AppState.images.filter(i => i.status === 'pending').length;
    const favCount = AppState.images.filter(i => i.status === 'saved').length;
    const candEl = document.getElementById('gallery-count-candidates');
    if (candEl) candEl.innerText = candCount;
    const favEl = document.getElementById('gallery-count-favorites');
    if (favEl) favEl.innerText = favCount;
    const tabSaved = document.getElementById('tab-cnt-saved');
    if (tabSaved) tabSaved.innerText = favCount;
    const tabPending = document.getElementById('tab-cnt-pending');
    if (tabPending) tabPending.innerText = candCount;

    renderGalleryFeed();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function batchDeleteSelected() {
  const ids = Array.from(AppState.selectedImageIds);
  if (ids.length === 0) return;

  try {
    const res = await apiFetch(`${API_BASE}/api/images/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_ids: ids, action: 'delete' })
    });
    if (!res.ok) throw new Error('批量删除失败');

    const data = await res.json();
    showToast(`已删除 ${data.count} 张图片`, 'info');

    AppState.images = AppState.images.filter(img => !ids.includes(img.id));
    AppState.selectedImageIds.clear();
    updateBatchActionBar();

    const candCount = AppState.images.filter(i => i.status === 'pending').length;
    const favCount = AppState.images.filter(i => i.status === 'saved').length;
    const candEl = document.getElementById('gallery-count-candidates');
    if (candEl) candEl.innerText = candCount;
    const favEl = document.getElementById('gallery-count-favorites');
    if (favEl) favEl.innerText = favCount;
    const tabAll = document.getElementById('tab-cnt-all');
    if (tabAll) tabAll.innerText = AppState.images.length;
    const tabPending = document.getElementById('tab-cnt-pending');
    if (tabPending) tabPending.innerText = candCount;
    const tabSaved = document.getElementById('tab-cnt-saved');
    if (tabSaved) tabSaved.innerText = favCount;

    renderGalleryFeed();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

// Cleanup Modal
function openCleanupModal() {
  const modal = document.getElementById('cleanup-modal');
  const name1 = document.getElementById('modal-char-name');
  if (name1) name1.innerText = AppState.currentCharacter || '';
  const name2 = document.getElementById('modal-char-name-2');
  if (name2) name2.innerText = AppState.currentCharacter || '';
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeCleanupModal() {
  const modal = document.getElementById('cleanup-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

async function confirmCleanup() {
  const char = AppState.currentCharacter;
  if (!char) return;

  const btn = document.getElementById('btn-confirm-cleanup');
  if (btn) {
    btn.disabled = true;
    btn.innerText = '正在清理临时文件...';
  }

  try {
    const res = await apiFetch(`${API_BASE}/api/storage/clean-temp/${encodeURIComponent(char)}`, { method: 'POST' });
    if (!res.ok) throw new Error('清理失败');
    const data = await res.json();

    closeCleanupModal();
    showToast(data.message, 'success');
    await loadCharacterImages(char);
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerText = '确认清理';
    }
  }
}


// Fullscreen Lightbox with Synchronized Filtered List & Exact ID Matching
function getActiveLightboxList() {
  if (AppState.currentView === 'favorites') {
    return AppState.images || [];
  }
  return (AppState.filteredImages && AppState.filteredImages.length > 0) ? AppState.filteredImages : (AppState.images || []);
}

function openLightbox(identifier) {
  const list = getActiveLightboxList();
  if (!list || list.length === 0) return;

  let index = -1;

  // Exact primary key image.id matching (100% accurate)
  if (typeof identifier === 'number' || (typeof identifier === 'string' && /^\d+$/.test(identifier))) {
    const targetId = Number(identifier);
    index = list.findIndex(i => i && i.id === targetId);
  }

  // Fallback to array index if within bounds
  if (index === -1 && typeof identifier === 'number' && identifier >= 0 && identifier < list.length) {
    index = identifier;
  }

  if (index === -1) {
    index = 0;
  }

  AppState.lightboxIndex = index;
  const modal = document.getElementById('lightbox-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    updateLightboxContent();
  }
}

function closeLightbox() {
  const modal = document.getElementById('lightbox-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

function updateLightboxContent() {
  const list = getActiveLightboxList();
  if (list.length === 0) {
    closeLightbox();
    return;
  }
  if (AppState.lightboxIndex >= list.length) {
    AppState.lightboxIndex = list.length - 1;
  }
  const img = list[AppState.lightboxIndex];
  if (!img) return;

  const isSaved = img.status === 'saved';
  const lbImg = document.getElementById('lb-img');
  if (lbImg) lbImg.src = getMediaUrl(img.favorites_url || img.temp_url || img.thumbnail_url);

  const titleEl = document.getElementById('lb-title');
  if (titleEl) titleEl.innerText = img.title || img.filename;

  const authorEl = document.getElementById('lb-author');
  if (authorEl) authorEl.innerText = img.author_name ? `画师: ${img.author_name}` : (img.copyright_info || '');

  const badgeEl = document.getElementById('lb-index-badge');
  if (badgeEl) badgeEl.innerText = `#${img.filename.replace(/\.[^/.]+$/, "")}`;

  const resEl = document.getElementById('lb-res');
  if (resEl) resEl.innerText = img.width ? `${img.width} × ${img.height}` : '无损原画';

  const sizeEl = document.getElementById('lb-size');
  if (sizeEl) sizeEl.innerText = img.file_size ? `${(img.file_size / (1024*1024)).toFixed(2)} MB` : '';

  const srcBadge = document.getElementById('lb-source-badge');
  if (srcBadge) srcBadge.innerText = img.original_source || 'Pixiv';
  
  const srcLink = document.getElementById('lb-source-link');
  if (srcLink) {
    srcLink.href = img.source_url || '#';
    srcLink.style.display = img.source_url ? 'inline-flex' : 'none';
  }

  const downloadBtn = document.getElementById('lb-btn-download');
  if (downloadBtn) {
    downloadBtn.href = `${API_BASE}/api/images/${img.id}/download`;
    downloadBtn.download = `${img.filename}`;
  }

  const saveBtn = document.getElementById('lb-btn-save');
  const saveText = document.getElementById('lb-save-text');
  if (saveBtn && saveText) {
    if (isSaved) {
      saveBtn.className = 'px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold font-mono flex items-center gap-1.5 shadow-md transition-all';
      saveText.innerText = '已收藏 (S)';
    } else {
      saveBtn.className = 'px-3 py-1.5 rounded-lg bg-[#c5a880] hover:bg-[#e4ccad] text-black text-xs font-bold font-mono flex items-center gap-1.5 shadow-md transition-all';
      saveText.innerText = '保存 (S)';
    }
  }
}

function lbNext() {
  const list = getActiveLightboxList();
  if (list.length === 0) return;
  AppState.lightboxIndex = (AppState.lightboxIndex + 1) % list.length;
  updateLightboxContent();
}

function lbPrev() {
  const list = getActiveLightboxList();
  if (list.length === 0) return;
  AppState.lightboxIndex = (AppState.lightboxIndex - 1 + list.length) % list.length;
  updateLightboxContent();
}

async function lbToggleFavorite() {
  const list = getActiveLightboxList();
  const img = list[AppState.lightboxIndex];
  if (!img) return;
  await toggleFavoriteImage(img.id);
  updateLightboxContent();
}

async function lbDeleteCurrent() {
  const list = getActiveLightboxList();
  const img = list[AppState.lightboxIndex];
  if (!img) return;

  if (AppState.currentView === 'favorites') {
    await deleteFavoriteImage(img.id);
  } else {
    await deleteSingleImage(img.id);
  }

  const updatedList = getActiveLightboxList();
  if (updatedList.length > 0) {
    AppState.lightboxIndex = Math.min(AppState.lightboxIndex, updatedList.length - 1);
    updateLightboxContent();
  } else {
    closeLightbox();
  }
}


// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
  const modal = document.getElementById('lightbox-modal');
  const isOpen = modal && !modal.classList.contains('hidden');

  if (isOpen) {
    if (e.key === 'ArrowRight') lbNext();
    else if (e.key === 'ArrowLeft') lbPrev();
    else if (e.key === 'Escape') closeLightbox();
    else if (e.key === 's' || e.key === 'S') lbToggleFavorite();
    else if (e.key === 'Delete' || e.key === 'Backspace') lbDeleteCurrent();
  }
});

// Mobile Touch Swipe Gestures for Lightbox
let touchStartX = 0;
let touchStartY = 0;
let touchEndX = 0;
let touchEndY = 0;

document.addEventListener('touchstart', (e) => {
  const modal = document.getElementById('lightbox-modal');
  if (modal && !modal.classList.contains('hidden')) {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }
}, { passive: true });

document.addEventListener('touchend', (e) => {
  const modal = document.getElementById('lightbox-modal');
  if (modal && !modal.classList.contains('hidden')) {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;
    handleLightboxSwipe();
  }
}, { passive: true });

function handleLightboxSwipe() {
  const diffX = touchEndX - touchStartX;
  const diffY = touchEndY - touchStartY;
  // If horizontal swipe is prominent (> 45px)
  if (Math.abs(diffX) > 45 && Math.abs(diffX) > Math.abs(diffY) * 1.5) {
    if (diffX < 0) {
      lbNext(); // Swipe left -> Next image
    } else {
      lbPrev(); // Swipe right -> Previous image
    }
  }
}

// ==========================================================================
// CHARACTERS LIBRARY & QUICK CRAWL MODAL SYSTEM
// ==========================================================================

function getGameMeta(gameKey) {
  switch (gameKey) {
    case 'blue_archive':
      return { title: '蔚蓝档案', badgeClass: 'game-badge game-badge-blue_archive', dotClass: 'bg-sky-400' };
    case 'wuthering_waves':
      return { title: '鸣潮', badgeClass: 'game-badge game-badge-wuthering_waves', dotClass: 'bg-amber-400' };
    case 'endfield':
      return { title: '终末地', badgeClass: 'game-badge game-badge-endfield', dotClass: 'bg-yellow-400' };
    default:
      return { title: '经典收录', badgeClass: 'game-badge game-badge-other', dotClass: 'bg-slate-400' };
  }
}

function setGameCategoryFilter(game) {
  AppState.activeGameFilter = game || 'all';
  
  ['all', 'blue_archive', 'wuthering_waves', 'endfield'].forEach(g => {
    const btn = document.getElementById(`game-tab-${g}`);
    if (btn) {
      if (g === AppState.activeGameFilter) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    }
  });

  renderFilteredCharacters();
}

function filterCharactersByKeyword(query) {
  AppState.characterKeyword = (query || '').trim().toLowerCase();
  renderFilteredCharacters();
}

async function loadCharactersList() {
  const grid = document.getElementById('characters-grid');
  if (!grid) return;

  try {
    const res = await apiFetch(`${API_BASE}/api/characters`);
    if (!res.ok) return;
    const chars = await res.json();
    AppState.cachedCharacters = chars || [];

    // Update counts across game tabs
    const countAll = chars.length;
    const countBA = chars.filter(c => c.game === 'blue_archive').length;
    const countWW = chars.filter(c => c.game === 'wuthering_waves').length;
    const countEnd = chars.filter(c => c.game === 'endfield').length;

    const elAll = document.getElementById('count-all');
    if (elAll) elAll.innerText = countAll;
    const elBA = document.getElementById('count-blue_archive');
    if (elBA) elBA.innerText = countBA;
    const elWW = document.getElementById('count-wuthering_waves');
    if (elWW) elWW.innerText = countWW;
    const elEnd = document.getElementById('count-endfield');
    if (elEnd) elEnd.innerText = countEnd;
    const elBadge = document.getElementById('char-total-count-badge');
    if (elBadge) elBadge.innerText = `已收录 ${countAll} 位角色`;

    renderFilteredCharacters();
  } catch (e) {
    console.error('Failed to load characters:', e);
  }
}

function renderFilteredCharacters() {
  const grid = document.getElementById('characters-grid');
  if (!grid) return;

  let list = AppState.cachedCharacters || [];

  // Filter by game
  if (AppState.activeGameFilter && AppState.activeGameFilter !== 'all') {
    list = list.filter(c => c.game === AppState.activeGameFilter);
  }

  // Filter by keyword
  if (AppState.characterKeyword) {
    const kw = AppState.characterKeyword;
    list = list.filter(c => {
      const matchName = (c.name || '').toLowerCase().includes(kw);
      const matchSlug = (c.slug || '').toLowerCase().includes(kw);
      const matchAliases = (c.aliases || '').toLowerCase().includes(kw);
      return matchName || matchSlug || matchAliases;
    });
  }

  if (list.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-20 text-center text-slate-400 font-mono text-xs flex flex-col items-center gap-3">
        <div class="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-[#c5a880] text-2xl mb-1 shadow-inner">
          🎨
        </div>
        <h4 class="text-white font-serif font-bold text-base">角色库暂无已抓取角色</h4>
        <p class="text-slate-400 max-w-md leading-relaxed text-xs">
          系统已切换为纯净模式：仅收录您实际抓取过原画的角色。<br>
          请点击右侧【游戏专区】或在首页搜索任意角色发起抓取，下载后将自动在此处展示！
        </p>
        <div class="flex items-center gap-2 mt-2 flex-wrap justify-center">
          <button onclick="openGameRosterModal('wuthering_waves')" class="px-3.5 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 text-xs font-bold transition-all shadow-md active:scale-95">
            ⚡ 挑选鸣潮角色
          </button>
          <button onclick="openGameRosterModal('blue_archive')" class="px-3.5 py-2 rounded-xl bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 text-xs font-bold transition-all shadow-md active:scale-95">
            💙 挑选蔚蓝档案角色
          </button>
          <button onclick="openGameRosterModal('endfield')" class="px-3.5 py-2 rounded-xl bg-yellow-500/15 hover:bg-yellow-500/25 text-yellow-300 border border-yellow-500/30 text-xs font-bold transition-all shadow-md active:scale-95">
            🔶 挑选终末地角色
          </button>
        </div>
      </div>
    `;
    lucide.createIcons({ root: grid });
    return;
  }

  grid.innerHTML = list.map(c => {
    const gameMeta = getGameMeta(c.game);
    const fallbackAvatar = `/static/avatars/${c.slug}.svg`;
    const avatarSrc = c.avatar_url ? getMediaUrl(c.avatar_url) : fallbackAvatar;

    return `
      <div 
        onclick="openCharacterGallery('${c.name}')"
        class="character-card-masonry p-3.5 flex flex-col gap-3 relative cursor-pointer group"
      >
        <!-- Adaptive Cover Image Container (Natural Aspect Ratio) -->
        <div class="character-cover-wrap">
          <img 
            src="${avatarSrc}" 
            alt="${c.name}" 
            loading="lazy"
            onerror="this.src='${fallbackAvatar}'"
            class="character-cover-img" 
          />
          
          <!-- Game Category Pill -->
          <div class="absolute top-2 left-2 z-10">
            <span class="${gameMeta.badgeClass} shadow-md backdrop-blur-md">
              <span class="w-1.5 h-1.5 rounded-full ${gameMeta.dotClass}"></span>
              ${gameMeta.title}
            </span>
          </div>

          <!-- Quick Action Buttons on Hover -->
          <div class="absolute top-2 right-2 z-10 flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
            <button 
              onclick="deleteCharacterRecord(${c.id}, '${c.name}', event)"
              class="p-1.5 rounded-lg bg-black/70 hover:bg-red-500 text-white/70 hover:text-white backdrop-blur-md border border-white/10 transition-all"
              title="清理未收藏的临时候选图"
            >
              <i data-lucide="trash-2" class="w-3 h-3"></i>
            </button>
          </div>
        </div>

        <!-- Character Details & Stats -->
        <div class="flex flex-col gap-1">
          <div class="flex items-center justify-between gap-1">
            <h4 class="text-sm font-serif font-bold text-white group-hover:text-[#c5a880] transition-colors truncate">${c.name}</h4>
          </div>
          
          <div class="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>候选: <strong class="text-slate-200">${c.total_candidates}</strong></span>
            <span>收藏: <strong class="text-[#c5a880]">${c.total_favorites}</strong></span>
          </div>

          <!-- Quick Crawl Action Trigger Button -->
          <button 
            type="button"
            onclick="openQuickCrawlModal('${c.name}', event)"
            class="quick-crawl-trigger-btn w-full mt-1.5 py-1.5 px-2 rounded-xl flex items-center justify-center gap-1.5 font-bold cursor-pointer"
            title="点击一键加抓角色高质量原画"
          >
            <i data-lucide="zap" class="w-3.5 h-3.5 fill-current"></i>
            <span>一键加抓</span>
          </button>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons({ root: grid });
}

// ==========================================================================
// GAME ROSTER SELECTOR MODAL SYSTEM
// ==========================================================================
async function openGameRosterModal(gameKey) {
  const modal = document.getElementById('modal-game-roster');
  const card = document.getElementById('modal-game-roster-card');
  if (!modal || !card) return;

  AppState.rosterGame = gameKey || 'wuthering_waves';
  AppState.rosterKeyword = '';

  const searchInput = document.getElementById('roster-search-input');
  if (searchInput) searchInput.value = '';

  modal.classList.remove('hidden');
  requestAnimationFrame(() => {
    modal.classList.remove('opacity-0');
    card.classList.remove('scale-95');
    card.classList.add('scale-100');
  });

  await switchRosterGame(AppState.rosterGame);
}

function closeGameRosterModal() {
  const modal = document.getElementById('modal-game-roster');
  const card = document.getElementById('modal-game-roster-card');
  if (!modal || !card) return;

  card.classList.remove('scale-100');
  card.classList.add('scale-95');
  modal.classList.add('opacity-0');
  setTimeout(() => {
    modal.classList.add('hidden');
  }, 200);
}

async function switchRosterGame(gameKey) {
  AppState.rosterGame = gameKey;

  // Update tabs
  ['wuthering_waves', 'blue_archive', 'endfield'].forEach(g => {
    const tabId = g === 'wuthering_waves' ? 'roster-tab-ww' : g === 'blue_archive' ? 'roster-tab-ba' : 'roster-tab-endfield';
    const tab = document.getElementById(tabId);
    if (tab) {
      if (g === gameKey) tab.classList.add('active');
      else tab.classList.remove('active');
    }
  });

  // Update Header
  const titleEl = document.getElementById('roster-modal-title');
  const iconEl = document.getElementById('roster-game-icon');
  if (gameKey === 'wuthering_waves') {
    if (titleEl) titleEl.innerHTML = `⚡ 鸣潮 · 全量角色图鉴速抓`;
    if (iconEl) {
      iconEl.className = 'w-11 h-11 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center font-bold text-amber-400 text-lg shadow-inner';
      iconEl.innerText = '⚡';
    }
  } else if (gameKey === 'blue_archive') {
    if (titleEl) titleEl.innerHTML = `💙 蔚蓝档案 · 全量角色图鉴速抓`;
    if (iconEl) {
      iconEl.className = 'w-11 h-11 rounded-xl bg-sky-500/20 border border-sky-500/40 flex items-center justify-center font-bold text-sky-400 text-lg shadow-inner';
      iconEl.innerText = '💙';
    }
  } else {
    if (titleEl) titleEl.innerHTML = `🔶 明日方舟：终末地 · 全量角色图鉴速抓`;
    if (iconEl) {
      iconEl.className = 'w-11 h-11 rounded-xl bg-yellow-500/20 border border-yellow-500/40 flex items-center justify-center font-bold text-yellow-400 text-lg shadow-inner';
      iconEl.innerText = '🔶';
    }
  }

  // Fetch from API
  try {
    const res = await apiFetch(`${API_BASE}/api/characters/catalog?game=${gameKey}`);
    if (res.ok) {
      const data = await res.json();
      AppState.rosterCatalog = data || [];
      const badgeEl = document.getElementById('roster-total-badge');
      if (badgeEl) badgeEl.innerText = `${data.length} 位角色`;
      renderRosterCharacters();
    }
  } catch (e) {
    console.error('Failed to load roster catalog:', e);
  }
}

function filterRosterCharacters(keyword) {
  AppState.rosterKeyword = (keyword || '').trim().toLowerCase();
  renderRosterCharacters();
}

function renderRosterCharacters() {
  const container = document.getElementById('roster-chars-grid');
  if (!container) return;

  let list = AppState.rosterCatalog || [];
  if (AppState.rosterKeyword) {
    const kw = AppState.rosterKeyword;
    list = list.filter(c => {
      const matchName = (c.name || '').toLowerCase().includes(kw);
      const matchSlug = (c.slug || '').toLowerCase().includes(kw);
      const matchAliases = Array.isArray(c.aliases) ? c.aliases.some(a => a.toLowerCase().includes(kw)) : false;
      return matchName || matchSlug || matchAliases;
    });
  }

  if (list.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-500 font-mono text-xs flex flex-col items-center gap-2">
        <i data-lucide="inbox" class="w-8 h-8 text-slate-600"></i>
        <span>未找到匹配的角色</span>
      </div>
    `;
    lucide.createIcons({ root: container });
    return;
  }

  container.innerHTML = list.map(c => {
    const fallbackAvatar = `/static/avatars/${c.slug}.svg`;
    const avatarSrc = c.avatar_url ? getMediaUrl(c.avatar_url) : fallbackAvatar;

    return `
      <div 
        onclick="openQuickCrawlModal('${c.name}', event)"
        class="roster-char-item group relative"
      >
        <div class="w-full aspect-square rounded-xl overflow-hidden bg-black/60 relative border border-white/10 flex items-center justify-center shadow-inner">
          <img 
            src="${avatarSrc}" 
            alt="${c.name}" 
            loading="lazy"
            onerror="this.src='${fallbackAvatar}'"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200" 
          />
          ${c.is_crawled ? `
            <div class="absolute top-1.5 left-1.5 z-10">
              <span class="px-2 py-0.5 rounded-md bg-emerald-500/90 text-black font-extrabold text-[10px] font-mono shadow-md backdrop-blur-md">
                已收录
              </span>
            </div>
          ` : ''}
        </div>

        <div class="flex flex-col gap-1">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-serif font-bold text-white group-hover:text-[#c5a880] transition-colors truncate">${c.name}</h4>
          </div>

          <div class="flex items-center justify-between text-[10px] font-mono">
            ${c.is_crawled ? `
              <span class="text-emerald-400 font-bold">候选: ${c.total_candidates}</span>
              <button 
                onclick="event.stopPropagation(); closeGameRosterModal(); openCharacterGallery('${c.name}')" 
                class="text-[10px] text-[#c5a880] hover:underline cursor-pointer font-bold"
              >
                看画廊 →
              </button>
            ` : `
              <span class="text-slate-400">未收录</span>
              <span class="text-[#c5a880] font-bold">点击抓取 ⚡</span>
            `}
          </div>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons({ root: container });
}

// ==========================================
// QUICK CRAWL MODAL INTERACTION LOGIC
// ==========================================
function openQuickCrawlModal(charName, event) {
  if (event) event.stopPropagation();

  const char = (AppState.cachedCharacters || []).find(c => c.name === charName) || {
    name: charName,
    slug: charName.toLowerCase(),
    game: 'other',
    total_candidates: 0,
    total_favorites: 0
  };

  AppState.quickCrawlTarget = char;

  const modal = document.getElementById('modal-quick-crawl');
  const card = document.getElementById('modal-quick-crawl-card');
  if (!modal || !card) return;

  // Fill in character info
  const nameEl = document.getElementById('qc-char-name');
  if (nameEl) nameEl.innerText = char.name;

  const imgEl = document.getElementById('qc-avatar-img');
  const fallback = `/static/avatars/${char.slug}.svg`;
  if (imgEl) {
    imgEl.src = char.avatar_url ? getMediaUrl(char.avatar_url) : fallback;
    imgEl.onerror = () => { imgEl.src = fallback; };
  }

  const badgeEl = document.getElementById('qc-game-badge');
  if (badgeEl) {
    const meta = getGameMeta(char.game);
    badgeEl.className = meta.badgeClass;
    badgeEl.innerText = meta.title;
  }

  const statsEl = document.getElementById('qc-char-stats');
  if (statsEl) {
    statsEl.innerText = `历史候选: ${char.total_candidates} 张 · 已收藏: ${char.total_favorites} 张`;
  }

  // Restore Rating
  setQuickCrawlRating(AppState.quickCrawlRating || 'sfw');

  // Restore Limit
  setQuickCrawlLimit(AppState.quickCrawlLimit || 50);

  modal.classList.remove('hidden');
  requestAnimationFrame(() => {
    modal.classList.remove('opacity-0');
    card.classList.remove('scale-95');
    card.classList.add('scale-100');
  });

  lucide.createIcons({ root: modal });
}

function closeQuickCrawlModal() {
  const modal = document.getElementById('modal-quick-crawl');
  const card = document.getElementById('modal-quick-crawl-card');
  if (!modal || !card) return;

  card.classList.remove('scale-100');
  card.classList.add('scale-95');
  modal.classList.add('opacity-0');
  setTimeout(() => {
    modal.classList.add('hidden');
  }, 200);
}

function setQuickCrawlRating(rating) {
  AppState.quickCrawlRating = rating;

  const sfwBtn = document.getElementById('qc-rating-sfw');
  const r18Btn = document.getElementById('qc-rating-r18');

  if (sfwBtn && r18Btn) {
    if (rating === 'r18') {
      r18Btn.className = 'batch-rating-pill-btn active-r18';
      sfwBtn.className = 'batch-rating-pill-btn';
    } else {
      sfwBtn.className = 'batch-rating-pill-btn active-sfw';
      r18Btn.className = 'batch-rating-pill-btn';
    }
  }

  const rememberCheckbox = document.getElementById('qc-remember-pref');
  if (rememberCheckbox && rememberCheckbox.checked) {
    localStorage.setItem('aurora_qc_rating', rating);
  }
}

function setQuickCrawlLimit(limit) {
  const num = Math.max(1, Math.min(300, parseInt(limit, 10) || 50));
  AppState.quickCrawlLimit = num;

  const displayEl = document.getElementById('qc-limit-display');
  if (displayEl) displayEl.innerText = num;

  // Update preset buttons
  document.querySelectorAll('[data-qc-limit]').forEach(btn => {
    const btnLimit = parseInt(btn.getAttribute('data-qc-limit'), 10);
    if (btnLimit === num) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  const customInput = document.getElementById('qc-custom-limit');
  if (customInput && ![20, 50, 100, 150, 200].includes(num)) {
    customInput.value = num;
  } else if (customInput && [20, 50, 100, 150, 200].includes(num)) {
    customInput.value = '';
  }

  const rememberCheckbox = document.getElementById('qc-remember-pref');
  if (rememberCheckbox && rememberCheckbox.checked) {
    localStorage.setItem('aurora_qc_limit', num);
  }
}

function onQuickCrawlCustomLimit(val) {
  if (!val) return;
  const num = Math.max(1, Math.min(300, parseInt(val, 10) || 20));
  AppState.quickCrawlLimit = num;

  const displayEl = document.getElementById('qc-limit-display');
  if (displayEl) displayEl.innerText = num;

  document.querySelectorAll('[data-qc-limit]').forEach(btn => {
    btn.classList.remove('active');
  });

  const rememberCheckbox = document.getElementById('qc-remember-pref');
  if (rememberCheckbox && rememberCheckbox.checked) {
    localStorage.setItem('aurora_qc_limit', num);
  }
}

async function executeQuickCrawl() {
  if (!AppState.quickCrawlTarget) return;
  const char = AppState.quickCrawlTarget;
  const limit = AppState.quickCrawlLimit || 50;
  const rating = AppState.quickCrawlRating || 'sfw';

  // Save preferences
  const rememberCheckbox = document.getElementById('qc-remember-pref');
  if (rememberCheckbox && rememberCheckbox.checked) {
    localStorage.setItem('aurora_qc_rating', rating);
    localStorage.setItem('aurora_qc_limit', limit);
  }

  closeQuickCrawlModal();

  // Create crawl task
  try {
    showToast(`🚀 已为【${char.name}】发起抓取 (${limit} 张 · ${rating === 'r18' ? '🔞 R-18' : '🍀 全年龄'})...`, 'success');

    const res = await apiFetch(`${API_BASE}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        character_name: char.name,
        limit: limit,
        rating: rating
      })
    });

    if (res.ok) {
      const task = await res.json();
      showToast(`任务已启动 [${task.id.slice(0, 8)}]，正在高速下载原画并感知去重...`, 'success');
      
      // Auto open character gallery so user immediately sees images stream in
      await openCharacterGallery(char.name);
      startTaskPolling();
    } else {
      const err = await res.json();
      showToast(err.detail || '创建抓取任务失败', 'error');
    }
  } catch (e) {
    showToast('启动抓取失败: ' + e.message, 'error');
  }
}

function openDirectGalleryFromModal() {
  if (!AppState.quickCrawlTarget) return;
  const char = AppState.quickCrawlTarget;
  closeQuickCrawlModal();
  openCharacterGallery(char.name);
}

async function deleteCharacterRecord(charId, charName, event) {
  if (event) event.stopPropagation();
  if (!confirm(`确定要清理角色【${charName}】的临时候选图片吗？\n\n🛡️ 收藏安全保证：\n- 将删除未收藏的候选大图与缓存，腾出磁盘空间；\n- 您在【收藏夹】中保存的所有该角色原画将 100% 永久保留，绝不删除！`)) {
    return;
  }

  try {
    const res = await apiFetch(`${API_BASE}/api/characters/${charId}`, { method: 'DELETE' });
    if (res.ok) {
      const data = await res.json();
      showToast(data.message || `已释放角色【${charName}】的临时空间，收藏已妥善保留`, 'success');
      await loadCharactersList();
      await loadRecentTasks();
    } else {
      const err = await res.json();
      showToast(err.detail || '删除失败', 'error');
    }
  } catch (e) {
    showToast('删除失败: ' + e.message, 'error');
  }
}

// Favorites List
async function loadFavoritesList() {
  try {
    const res = await apiFetch(`${API_BASE}/api/images?status=saved&limit=500`);
    if (!res.ok) return;
    const favs = await res.json();
    AppState.images = favs;
    renderFavoritesFeed();
  } catch (e) {
    console.error(e);
  }
}

function renderFavoritesFeed() {
  const container = document.getElementById('favorites-feed-container');
  if (!container) return;

  if (AppState.images.length === 0) {
    container.innerHTML = `<div class="py-24 text-center text-slate-500 font-mono text-xs">暂无收藏图片，在工作台中点击【保存】即可永久收藏</div>`;
    return;
  }

  if (AppState.favLayoutMode === 'single') {
    container.className = 'single-feed-container';
    container.innerHTML = AppState.images.map((img, idx) => {
      return `
        <div class="single-feed-card p-4 sm:p-6 is-fav" data-id="${img.id}">
          <div class="flex items-center justify-between mb-3 font-mono text-xs">
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded-lg bg-[#c5a880]/20 text-[#c5a880] font-bold">#${img.filename}</span>
              <span class="text-white font-bold">${img.character_name || ''}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-emerald-400 font-bold flex items-center gap-1"><i data-lucide="shield-check" class="w-3.5 h-3.5"></i> 永久资产</span>
              <button 
                onclick="deleteFavoriteImage(${img.id}, event)"
                class="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-white/5 transition-all"
                title="从收藏夹移除"
              >
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>

          <div class="rounded-xl overflow-hidden bg-[#090a0f] cursor-pointer" onclick="openLightbox(${img.id})">
            <img src="${getMediaUrl(img.thumbnail_url || img.favorites_url)}" class="w-full max-h-[85vh] object-contain" />
          </div>

          <div class="mt-4 pt-3 flex items-center justify-between font-mono text-xs">
            <span class="text-slate-400">${img.width} × ${img.height}</span>
            <div class="flex items-center gap-2">
              <button 
                onclick="deleteFavoriteImage(${img.id}, event)"
                class="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-red-500/20 text-slate-400 hover:text-red-300 font-bold flex items-center gap-1 transition-all"
              >
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i> 移除收藏
              </button>
              <a href="${API_BASE}/api/images/${img.id}/download" class="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-[#c5a880] text-white hover:text-black font-bold flex items-center gap-1 transition-all" download>
                <i data-lucide="download" class="w-3.5 h-3.5"></i> 下载原画
              </a>
            </div>
          </div>
        </div>
      `;
    }).join('');
  } else {
    container.className = 'masonry-container';
    container.innerHTML = AppState.images.map((img, idx) => `
      <div class="single-feed-card rounded-xl overflow-hidden is-fav mb-4 relative group" onclick="openLightbox(${img.id})">
        <img src="${getMediaUrl(img.thumbnail_url || img.favorites_url)}" class="w-full object-cover" />
        <button 
          onclick="deleteFavoriteImage(${img.id}, event)"
          class="absolute top-2 right-2 p-1.5 rounded-lg bg-black/70 hover:bg-red-500 text-white backdrop-blur-md transition-all opacity-80 group-hover:opacity-100"
          title="移除收藏"
        >
          <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
        </button>
      </div>
    `).join('');
  }

  lucide.createIcons({ root: container });
}

async function deleteFavoriteImage(imageId, event) {
  if (event) event.stopPropagation();
  try {
    const res = await apiFetch(`${API_BASE}/api/images/${imageId}/unfavorite`, { method: 'POST' });
    if (res.ok) {
      showToast('已从收藏夹移除该图片', 'info');
      AppState.images = AppState.images.filter(img => img.id !== imageId);
      renderFavoritesFeed();
    } else {
      showToast('移除失败', 'error');
    }
  } catch (e) {
    showToast('移除失败: ' + e.message, 'error');
  }
}

// Settings
async function loadSettings() {
  try {
    const res = await apiFetch(`${API_BASE}/api/settings`);
    if (!res.ok) return;
    const settings = await res.json();
    
    if (settings.private_auth_enabled) {
      const val = typeof settings.private_auth_enabled === 'object' ? settings.private_auth_enabled.value : settings.private_auth_enabled;
      const isPrivate = (val === 'true' || val === true);
      const privRadio = document.getElementById('setting-auth-private');
      const pubRadio = document.getElementById('setting-auth-public');
      if (isPrivate && privRadio) privRadio.checked = true;
      if (!isPrivate && pubRadio) pubRadio.checked = true;
      toggleAuthModeUI(isPrivate);
    }
    if (settings.default_crawl_rating) {
      const val = typeof settings.default_crawl_rating === 'object' ? settings.default_crawl_rating.value : settings.default_crawl_rating;
      if (val === 'r18') {
        const r18Radio = document.getElementById('setting-rating-r18');
        if (r18Radio) r18Radio.checked = true;
      } else {
        const sfwRadio = document.getElementById('setting-rating-sfw');
        if (sfwRadio) sfwRadio.checked = true;
      }
    }
    if (settings.pixiv_refresh_token) {
      document.getElementById('setting-pixiv-token').value = settings.pixiv_refresh_token.value || '';
    }
    if (settings.google_photos_client_id) {
      document.getElementById('setting-gp-client-id').value = settings.google_photos_client_id.value || '';
    }
    if (settings.google_photos_client_secret) {
      document.getElementById('setting-gp-client-secret').value = settings.google_photos_client_secret.value || '';
    }
    if (settings.google_photos_refresh_token) {
      document.getElementById('setting-gp-refresh-token').value = settings.google_photos_refresh_token.value || '';
      const statusBadge = document.getElementById('gp-auth-status');
      if (statusBadge && settings.google_photos_refresh_token.value) {
        statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
        statusBadge.innerText = '✓ 已连接授权';
      }
    }
  } catch (e) {
    console.error(e);
  }
}

function toggleAuthModeUI(isPrivate) {
  const badge = document.getElementById('setting-auth-status-badge');
  const desc = document.getElementById('auth-mode-desc');
  if (isPrivate) {
    if (badge) {
      badge.className = 'px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-pink-500/20 text-pink-300 border border-pink-500/30';
      badge.innerText = '🔒 404 隐形防护生效中';
    }
    if (desc) {
      desc.innerHTML = `• <b>当前模式</b>：404 隐形防护模式。外部陌生访客将收到 404 Not Found 页面，彻底隐藏画廊。<br>• <b>访问方式</b>：需使用下方专属激活链接配对授权设备。`;
    }
  } else {
    if (badge) {
      badge.className = 'px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
      badge.innerText = '🌐 全网公开访问已放开';
    }
    if (desc) {
      const currentUrl = window.location.origin + window.location.pathname;
      desc.innerHTML = `• <b>当前模式</b>：全网公开访问已放开！任何人直接访问 <code>${currentUrl}</code> 即可正常浏览。<br>• <b>随时切换</b>：如需重新独占，切换为【404 隐形防护】并保存即可。`;
    }
  }
}

async function connectGoogleOAuth() {
  const gpClientId = document.getElementById('setting-gp-client-id').value.trim();
  const gpClientSecret = document.getElementById('setting-gp-client-secret').value.trim();

  if (!gpClientId || !gpClientSecret) {
    showToast('请先填写 Client ID 和 Client Secret 并点击保存', 'error');
    return;
  }

  // Save first
  await saveSettings();

  try {
    const res = await apiFetch(`${API_BASE}/api/google/auth-url`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || '获取 Google 授权跳转链接失败');
    }
    const data = await res.json();
    // Redirect to Google OAuth consent
    window.location.href = data.auth_url;
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function triggerGooglePhotosSync() {
  showToast('⚡ 正在与 Google 相册云端建立同步...', 'info');
  try {
    const res = await apiFetch(`${API_BASE}/api/settings/google-photos/sync`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.message, 'success');
    } else {
      showToast(data.message, 'error');
    }
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function saveSettings() {
  const pixivToken = document.getElementById('setting-pixiv-token').value.trim();
  const gpClientId = document.getElementById('setting-gp-client-id').value.trim();
  const gpClientSecret = document.getElementById('setting-gp-client-secret').value.trim();
  const gpRefreshToken = document.getElementById('setting-gp-refresh-token').value.trim();
  const defaultRating = document.querySelector('input[name="setting-crawl-rating"]:checked')?.value || 'sfw';
  const privateAuth = document.querySelector('input[name="setting-private-auth"]:checked')?.value || 'false';

  const settingsPayload = {
    pixiv_refresh_token: pixivToken,
    google_photos_client_id: gpClientId,
    google_photos_client_secret: gpClientSecret,
    google_photos_refresh_token: gpRefreshToken,
    default_crawl_rating: defaultRating,
    private_auth_enabled: privateAuth
  };

  try {
    const res = await apiFetch(`${API_BASE}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings: settingsPayload })
    });
    if (!res.ok) throw new Error('保存设置失败');
    
    setCrawlRating(defaultRating);
    toggleAuthModeUI(privateAuth === 'true');
    showToast(privateAuth === 'true' ? '✓ 设置已保存！404 隐形防护模式已开启' : '✓ 设置已保存！全网公开访问已放开', 'success');
  } catch (e) {
    showToast(e.message, 'error');
  }
}



// ============================================================================
// STEALTH 404 & MAGIC LINK ONE-CLICK AUTHORIZATION
// ============================================================================
async function loadMagicLinkInfo() {
  const urlInput = document.getElementById('setting-magic-url');
  if (!urlInput) return;
  try {
    const res = await apiFetch(`${API_BASE}/api/auth/magic_info`);
    if (res.ok) {
      const data = await res.json();
      urlInput.value = data.magic_url || '';
    }
  } catch (e) {
    urlInput.value = '加载失败';
  }
}

function copyMagicLink() {
  const urlInput = document.getElementById('setting-magic-url');
  if (!urlInput || !urlInput.value || urlInput.value.includes('加载')) {
    showToast('专属链接尚未就绪', 'error');
    return;
  }
  navigator.clipboard.writeText(urlInput.value).then(() => {
    showToast('📋 专属授权链接已复制到剪贴板！', 'success');
  }).catch(() => {
    urlInput.select();
    document.execCommand('copy');
    showToast('📋 专属授权链接已复制！', 'success');
  });
}

async function resetMagicLink() {
  if (!confirm('确定要重置并生成新的专属授权链接吗？重置后需使用新链接重新授权新设备。')) return;
  try {
    const res = await apiFetch(`${API_BASE}/api/auth/reset_magic_key`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      const urlInput = document.getElementById('setting-magic-url');
      if (urlInput) urlInput.value = data.magic_url;
      showToast('🎉 新专属授权链接已生成！', 'success');
    } else {
      showToast('重置失败', 'error');
    }
  } catch (e) {
    showToast('网络错误', 'error');
  }
}

async function loadAuthorizedDevices() {
  const listEl = document.getElementById('auth-devices-list');
  const countEl = document.getElementById('auth-devices-count');
  if (!listEl) return;

  try {
    const res = await apiFetch(`${API_BASE}/api/auth/devices`);
    if (res.ok) {
      const devices = await res.json();
      if (countEl) countEl.innerText = devices.length;
      if (devices.length === 0) {
        listEl.innerHTML = `<div class="text-xs text-slate-500 py-2">暂无其他设备</div>`;
        return;
      }
      listEl.innerHTML = devices.map(d => `
        <div class="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between gap-3 text-xs font-mono">
          <div class="flex items-center gap-2.5 min-w-0">
            <i data-lucide="smartphone" class="w-4 h-4 text-[#c5a880] shrink-0"></i>
            <div class="truncate">
              <div class="font-bold text-white truncate">${d.device_name || '个人设备'}</div>
              <div class="text-[10px] text-slate-400">IP: ${d.ip_address || 'Unknown'} · 活跃: ${d.last_active || '刚刚'}</div>
            </div>
          </div>
          <button onclick="revokeDevice(${d.id})" class="px-2.5 py-1 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 text-[11px] font-bold transition-all shrink-0">
            吊销
          </button>
        </div>
      `).join('');
      lucide.createIcons({ root: listEl });
    }
  } catch (e) {
    listEl.innerHTML = `<div class="text-xs text-red-400 py-2">加载设备列表失败</div>`;
  }
}

async function revokeDevice(deviceId) {
  if (!confirm('确定要吊销该设备的访问授权吗？吊销后该设备将无法访问画廊。')) return;
  try {
    const res = await apiFetch(`${API_BASE}/api/auth/devices/${deviceId}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('设备授权已吊销', 'success');
      loadAuthorizedDevices();
    } else {
      showToast('吊销失败', 'error');
    }
  } catch (e) {
    showToast('网络错误', 'error');
  }
}

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
  // 1. Immediate capture of secret key from URL & clean address bar
  const urlParams = new URLSearchParams(window.location.search);
  const magicKey = urlParams.get('key') || urlParams.get('auth_key');
  if (magicKey) {
    localStorage.setItem('aurora_auth_token', magicKey);
    document.cookie = `auth_token=${encodeURIComponent(magicKey)}; max-age=315360000; path=/; samesite=lax`;
    window.history.replaceState({}, '', window.location.pathname);
    showToast('🎉 专属通行证已激活！已永久绑定此设备', 'success');
  }

  if (urlParams.get('auth_success') === 'google_connected') {
    showToast('🎉 Google Photos 账号授权连接成功！已就绪', 'success');
    navigate('settings');
  } else if (urlParams.get('auth_error')) {
    showToast('Google 授权失败，请检查 Client ID 和 Secret 是否填写正确', 'error');
    navigate('settings');
  }

  setCrawlRating(AppState.crawlRating);
  setCharWorkbenchRating(AppState.workbenchRating);
  loadRecentTasks();
  lucide.createIcons();
});
