(() => {
  const condos = window.CONDO_DATA || [];
  const fmt = (n, digits = 0) => n == null || Number.isNaN(Number(n)) ? '—' : Number(n).toLocaleString('en-US', { maximumFractionDigits: digits });
  const money = n => n == null ? '—' : `฿${fmt(n)}`;
  const compactMoney = n => n == null ? '—' : n >= 1000000 ? `฿${(n / 1000000).toFixed(2)}M` : `฿${fmt(n / 1000, 0)}K`;
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const reviewsUrl = c => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${c.name} condo Huai Khwang Bangkok`)}`;
  const map = L.map('map', { zoomControl: false, scrollWheelZoom: true }).setView([13.7824, 100.5763], 14);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
  let mode = 'sale';
  let selectedId = condos[0]?.id;
  let query = '';
  const markers = new Map();
  const list = document.getElementById('projectList');
  const detail = document.getElementById('detailPanel');
  const labelFor = c => mode === 'sale' ? `${fmt(c.sale.averageSqm)}<small>฿/㎡</small>` : mode === 'rent' ? `${fmt(c.rent.averageSqm)}<small>฿/㎡</small>` : `${yieldFor(c).toFixed(1)}<small>%</small>`;
  const valueFor = c => mode === 'sale' ? c.sale.averageSqm : mode === 'rent' ? c.rent.averageSqm : yieldFor(c);
  function yieldFor(c) {
    const price = Number(c.samplePrice || c.sale.average || 0);
    const rent = Number(c.rent.comparableRent || c.rent.average || 0);
    const area = Number(c.area || c.rent.comparableArea || 0);
    const useFee = document.getElementById('deductFee')?.checked ?? true;
    const useAgent = document.getElementById('deductAgent')?.checked ?? true;
    if (!price || !rent) return 0;
    const annualRent = rent * (12 - (useAgent ? 1 : 0));
    const fee = useFee && c.fee.rate && area ? c.fee.rate * area * 12 : 0;
    return (annualRent - fee) / price * 100;
  }
  function icon(c, active = false) {
    return L.divIcon({ className: 'condo-icon' + (active ? ' active' : ''), html: `<span>${labelFor(c)}</span>`, iconSize: [92, 34], iconAnchor: [46, 17] });
  }
  condos.forEach(c => {
    if (!Number.isFinite(c.lat) || !Number.isFinite(c.lng)) return;
    const marker = L.marker([c.lat, c.lng], { icon: icon(c) }).addTo(map);
    marker.on('click', () => select(c.id));
    markers.set(c.id, marker);
  });
  function filtered() { return condos.filter(c => c.name.toLowerCase().includes(query.toLowerCase())); }
  function renderList() {
    const shown = filtered();
    document.getElementById('resultCount').textContent = `${shown.length} 個樣本`;
    document.getElementById('listCount').textContent = String(shown.length).padStart(2, '0');
    list.innerHTML = shown.map((c, i) => `<article class="project-card ${c.id === selectedId ? 'active' : ''}" data-id="${c.id}" tabindex="0" role="button" aria-label="查看 ${esc(c.name)}"><span class="rank">${String(i + 1).padStart(2, '0')}</span><div class="project-copy"><strong class="project-name">${esc(c.name)}</strong><span class="project-meta">${esc(c.station)} · 完工 ${c.completedYear}</span><div class="project-values"><span>售 <b>${compactMoney(c.sale.average)}</b></span><span>租 <b>${compactMoney(c.rent.average)}</b></span></div></div><span class="price-chip">${labelFor(c)}</span></article>`).join('') || '<p class="empty-state">沒有符合的樓盤</p>';
    list.querySelectorAll('.project-card').forEach(el => {
      const activate = () => select(Number(el.dataset.id));
      el.addEventListener('click', activate);
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
    });
  }
  function renderDetail(c) {
    const avgRate = c.rent.averageSqm;
    const minRate = c.rent.minimumSqm;
    const feeText = c.fee.rate ? `<div class="fee-row"><strong class="fee-number">฿${fmt(c.fee.rate)} <small>/ ㎡ / 月*</small></strong><span class="age-pill">${c.fee.status === 'historical_indicative' ? '歷史參考' : '公開刊載'}</span></div><p class="fee-note">${esc(c.fee.note || '')}</p>` : '<p class="fee-note">尚未查得可用管理費資料。</p>';
    const addr = `${c.name} condo Huai Khwang Bangkok`;
    detail.classList.remove('empty');
    detail.innerHTML = `<button class="close-detail" aria-label="關閉樓盤資訊">×</button>
      <div class="detail-hero"><div class="detail-topline"><span class="station-pill">MRT ${esc(c.station)}</span><span class="age-pill">${c.completedYear} 完工</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.beds || 2} 房樣本約 ${fmt(c.area, 1)} ㎡ · ${fmt(c.units)} 戶 · ${esc(c.floors || '—')}</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div>
      <section class="detail-section"><p class="section-label">二手出售 <span>${fmt(c.sale.count)} 筆 · 全房型 · ${esc(c.sale.asOf)}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">平均售價</span><b class="metric-value">${money(c.sale.average)}</b><span class="metric-sub">最低 ${money(c.sale.minimum)}</span></div><div class="metric"><span class="metric-label">售價 / ㎡</span><b class="metric-value">${money(c.sale.averageSqm)}</b><span class="metric-sub">最低 ${money(c.sale.minimumSqm)} / ㎡</span></div></div><div class="unit-price"><span>資料來源：PropertyHub 掛牌</span><b><a href="${esc(c.sale.source)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section rent-section"><p class="section-label">出租市場 <span>${fmt(c.rent.count)} 筆 · 全房型</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">平均月租</span><b class="metric-value">${money(c.rent.average)}</b><span class="metric-sub">最低 ${money(c.rent.minimum)} / 月</span></div><div class="metric"><span class="metric-label">租金 / ㎡</span><b class="metric-value">${money(avgRate)}<small> / 月</small></b><span class="metric-sub">最低 ${money(minRate)} / ㎡ / 月</span></div></div><div class="unit-price"><span>平台廣告數不等於空置戶數</span><b><a href="${esc(c.rent.source)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section"><p class="section-label">管理費參考 <span>需向管委會確認</span></p>${feeText}${c.fee.source ? `<div class="source-links"><a href="${esc(c.fee.source)}" target="_blank" rel="noopener">管理費來源 ↗</a></div>` : ''}</section>
      <section class="detail-section yield-section"><div class="yield-heading"><p class="section-label">年租金報酬試算 <span>2 房可比樣本</span></p><div class="yield-value" id="yieldValue">${yieldFor(c).toFixed(2)}<small>% / 年</small></div></div><div class="yield-inputs"><div class="yield-input"><label for="yieldPrice">參考購入價 (฿)</label><input id="yieldPrice" type="number" min="1" step="50000" value="${Math.round(c.samplePrice || c.sale.average)}"></div><div class="yield-input"><label for="yieldRent">月租金 (฿)</label><input id="yieldRent" type="number" min="0" step="500" value="${Math.round(c.rent.comparableRent || c.rent.average)}"></div><div class="yield-input"><label for="yieldArea">室內面積 (㎡)</label><input id="yieldArea" type="number" min="1" step="0.1" value="${Number(c.area || c.rent.comparableArea || 0).toFixed(1)}"></div><div class="yield-input"><label>參考房型</label><input value="${c.beds || 2} 房可比租屋" readonly></div></div><div class="yield-options"><label><input id="deductFee" type="checkbox" checked> 扣除管理費</label><label><input id="deductAgent" type="checkbox" checked> 扣除 1 個月仲介管理費</label></div><p class="formula-note">以可比租屋月租 × 11 個月，扣除管理費後 ÷ 參考購入價。未含稅、維修、裝修、交易成本與貸款。管理費月計為估算假設時會另行提示。</p><div class="source-links"><a href="${esc(c.sale.source)}" target="_blank" rel="noopener">出售掛牌 ↗</a><a href="${esc(c.rent.source)}" target="_blank" rel="noopener">出租掛牌 ↗</a></div></section>
      <section class="detail-section"><p class="section-label">樓盤資訊 <span>起造資料待補</span></p><p class="fee-note">目前可查到 ${c.completedYear} 年完工；此資料不等同起造日期，起造日尚待逐案核實。樣本座標及售租價格取自公開平台。</p><div class="source-links"><a href="https://www.hipflat.co.th/zh/thailand-projects/condo/bangkok-bm" target="_blank" rel="noopener">Hipflat · 區域有 197 案 ↗</a></div></section>`;
    detail.querySelector('.close-detail').addEventListener('click', () => { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); });
    ['yieldPrice', 'yieldRent', 'yieldArea', 'deductFee', 'deductAgent'].forEach(id => detail.querySelector(`#${id}`).addEventListener('input', () => {
      const price = Number(detail.querySelector('#yieldPrice').value);
      const rent = Number(detail.querySelector('#yieldRent').value);
      const area = Number(detail.querySelector('#yieldArea').value);
      const fee = detail.querySelector('#deductFee').checked && c.fee.rate && area ? c.fee.rate * area * 12 : 0;
      const agentMonth = detail.querySelector('#deductAgent').checked ? 1 : 0;
      const y = price > 0 ? ((rent * (12 - agentMonth) - fee) / price * 100) : 0;
      detail.querySelector('#yieldValue').innerHTML = `${Number.isFinite(y) ? y.toFixed(2) : '0.00'}<small>% / 年</small>`;
      markers.forEach((m, markerId) => m.setIcon(icon(condos.find(x => x.id === markerId), markerId === selectedId)));
      renderList();
    }));
  }
  function markerFor(id) { return markers.get(id); }
  function select(id) {
    const c = condos.find(x => x.id === id);
    if (!c) return;
    selectedId = id;
    markers.forEach((m, markerId) => m.setIcon(icon(condos.find(x => x.id === markerId), markerId === id)));
    renderList();
    renderDetail(c);
    if (window.matchMedia('(max-width: 650px)').matches) document.querySelector('.explorer').classList.add('hidden-mobile');
    map.panTo([c.lat, c.lng], { animate: true, duration: .4 });
  }
  function refreshMode() {
    document.querySelectorAll('.segmented button').forEach(b => b.classList.toggle('selected', b.dataset.mode === mode));
    markers.forEach((m, id) => m.setIcon(icon(condos.find(x => x.id === id), id === selectedId)));
    renderList();
  }
  document.querySelectorAll('.segmented button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; refreshMode(); }));
  document.getElementById('search').addEventListener('input', e => { query = e.target.value.trim(); renderList(); });
  document.getElementById('clearSearch').addEventListener('click', () => { document.getElementById('search').value = ''; query = ''; renderList(); });
  document.getElementById('fitMap').addEventListener('click', () => { const points = condos.filter(c => !query || c.name.toLowerCase().includes(query.toLowerCase())).map(c => [c.lat,c.lng]); if (points.length) map.fitBounds(points, { padding: [70, 90], maxZoom: 15 }); });
  document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
  document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
  document.getElementById('locate').addEventListener('click', () => map.setView([13.7824, 100.5763], 14));
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); document.getElementById('search').focus(); } if (e.key === 'Escape') { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); } });
  renderList();
  if (selectedId) { const c = condos.find(x => x.id === selectedId); if (window.matchMedia('(max-width: 650px)').matches) detail.classList.add('empty'); else renderDetail(c); markerFor(selectedId)?.setIcon(icon(c, true)); }
  if (condos.length) {
    const narrow = window.matchMedia('(max-width: 650px)').matches;
    if (narrow) map.setView([13.7824, 100.5763], 12);
    else map.fitBounds(condos.map(c => [c.lat,c.lng]), { paddingTopLeft: [390, 60], paddingBottomRight: [390, 60], maxZoom: 14 });
  }
  window.addEventListener('resize', () => map.invalidateSize());
})();
