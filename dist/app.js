(() => {
  const condos = window.CONDO_DATA || [];
  const stations = window.MRT_STATIONS || [];
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
  let sortMode = 'distance';
  const yieldOverrides = new Map();
  const markers = new Map();
  const stationMarkers = new Map();
  let walkingLine = null;
  const list = document.getElementById('projectList');
  const detail = document.getElementById('detailPanel');
  const labelFor = c => mode === 'sale' ? `${fmt(c.sale.minimumSqm)}<small>最低 ฿/㎡</small>` : mode === 'rent' ? `${fmt(c.rent.minimumSqm)}<small>最低 ฿/㎡/月</small>` : `${yieldFor(c).toFixed(1)}<small>% 淨投報</small>`;
  function yieldFor(c) {
    if (yieldOverrides.has(c.id)) return yieldOverrides.get(c.id);
    const priceRate = Number(c.sale.minimumSqm || 0);
    const rentRate = Number(c.rent.minimumSqm || 0);
    const useFee = document.getElementById('deductFee')?.checked ?? true;
    const useAgent = document.getElementById('deductAgent')?.checked ?? true;
    if (!priceRate || !rentRate) return 0;
    const feeRate = useFee ? Number(c.fee.rate || 0) * 12 : 0;
    return (rentRate * (12 - (useAgent ? 1 : 0)) - feeRate) / priceRate * 100;
  }
  function icon(c, active = false) {
    return L.divIcon({ className: 'condo-icon' + (active ? ' active' : ''), html: `<span><b class="marker-price">${labelFor(c)}</b><i class="marker-year">完工 ${esc(c.completedYear || '未載明')}</i></span>`, iconSize: [110, 42], iconAnchor: [55, 21] });
  }
  function decodePolyline6(encoded) {
    let index = 0, lat = 0, lng = 0;
    const points = [];
    while (index < encoded.length) {
      const values = [];
      for (let axis = 0; axis < 2; axis++) {
        let result = 0, shift = 0, byte;
        do { byte = encoded.charCodeAt(index++) - 63; result |= (byte & 0x1f) << shift; shift += 5; } while (byte >= 0x20);
        values.push((result & 1) ? ~(result >> 1) : (result >> 1));
      }
      lat += values[0]; lng += values[1];
      points.push([lat / 1e6, lng / 1e6]);
    }
    return points;
  }
  stations.forEach(s => {
    const marker = L.marker([s.lat, s.lng], { title: `MRT ${s.name} ${s.id}`, icon: L.divIcon({ className: 'station-icon', html: `<span><b>M</b><strong>${esc(s.name)}</strong><small>${esc(s.id)}</small></span>`, iconSize: [58, 30], iconAnchor: [14, 15] }), zIndexOffset: 500 }).addTo(map);
    marker.bindPopup(`<strong>MRT ${esc(s.name)}</strong><br>${esc(s.id)} · 藍線站點`);
    stationMarkers.set(s.id, marker);
  });
  condos.forEach(c => {
    if (!Number.isFinite(c.lat) || !Number.isFinite(c.lng)) return;
    const marker = L.marker([c.lat, c.lng], { icon: icon(c) }).addTo(map);
    marker.on('click', () => select(c.id));
    markers.set(c.id, marker);
  });
  function matchesQuery(c) {
    if (!query.trim()) return true;
    const stationName = stations.find(s => s.id === c.nearestMrt?.stationId)?.name || c.station || '';
    const haystack = `${c.name} ${stationName} ${c.completedYear || ''}`.toLowerCase();
    const aliases = {
      '年':'year','完工年':'year','完成年':'year','year':'year',
      '售價':'sale','售價/㎡':'sale','售價單價':'sale','sale':'sale','price':'sale',
      '租金':'rent','月租':'rent','租金/㎡':'rent','月租/㎡':'rent','rent':'rent',
      '距離':'distance','步行':'distance','步行距離':'distance','mrt距離':'distance','distance':'distance',
      '投報':'yield','淨投報':'yield','投報率':'yield','yield':'yield',
      '站':'station','mrt':'station','樓名':'name','name':'name'
    };
    const metrics = { year:Number(c.completedYear), sale:Number(c.sale.minimumSqm), rent:Number(c.rent.minimumSqm), distance:Number(c.nearestMrt?.distanceKm), yield:yieldFor(c) };
    return query.trim().split(/\s+/).every(token => {
      const expr = token.match(/^(.+?)(<=|>=|<|>|=|:)(.+)$/);
      if (!expr) return haystack.includes(token.toLowerCase());
      const field = aliases[expr[1].toLowerCase()];
      if (!field) return haystack.includes(token.toLowerCase());
      const [, , operator, rawValue] = expr;
      if (field === 'name' || field === 'station') return [':','='].includes(operator) && `${field === 'name' ? c.name : stationName}`.toLowerCase().includes(rawValue.toLowerCase());
      const target = metrics[field], value = Number(rawValue);
      if (!Number.isFinite(target) || !Number.isFinite(value)) return false;
      if (operator === ':' || operator === '=') return target === value;
      if (operator === '<') return target < value;
      if (operator === '<=') return target <= value;
      if (operator === '>') return target > value;
      return target >= value;
    });
  }
  function filtered() {
    const shown = condos.filter(matchesQuery);
    const keyFor = c => sortMode === 'distance' ? c.nearestMrt?.distanceKm : sortMode === 'sale' ? c.sale.minimumSqm : sortMode === 'rent' ? c.rent.minimumSqm : yieldFor(c);
    const ranked = sortMode === 'year-new' || sortMode === 'year-old' ? sortMode : null;
    return shown.sort((a, b) => {
      if (ranked) {
        const yearA = Number(a.completedYear), yearB = Number(b.completedYear);
        if (!Number.isFinite(yearA)) return Number.isFinite(yearB) ? 1 : 0;
        if (!Number.isFinite(yearB)) return -1;
        const yearDelta = yearA - yearB;
        return sortMode === 'year-new' ? -yearDelta : yearDelta;
      }
      const delta = Number(keyFor(a) ?? Infinity) - Number(keyFor(b) ?? Infinity);
      return sortMode === 'yield' ? -delta : delta;
    });
  }
  function renderList() {
    const shown = filtered();
    const visibleIds = new Set(shown.map(c => c.id));
    markers.forEach((marker, id) => {
      if (visibleIds.has(id) && !map.hasLayer(marker)) marker.addTo(map);
      else if (!visibleIds.has(id) && map.hasLayer(marker)) map.removeLayer(marker);
    });
    document.getElementById('resultCount').textContent = `${shown.length} 個樣本`;
    document.getElementById('listCount').textContent = String(shown.length).padStart(2, '0');
    list.innerHTML = shown.map((c, i) => { const nearestStation = stations.find(s => s.id === c.nearestMrt?.stationId); return `<article class="project-card ${c.id === selectedId ? 'active' : ''}" data-id="${c.id}" tabindex="0" role="button" aria-label="查看 ${esc(c.name)}"><span class="rank">${String(i + 1).padStart(2, '0')}</span><div class="project-copy"><strong class="project-name">${esc(c.name)}</strong><span class="project-meta">MRT ${esc(nearestStation?.name || c.station)} · 完工 ${c.completedYear}</span><div class="project-values"><span>售/㎡ <b>${fmt(c.sale.minimumSqm)}</b></span><span>租/㎡/月 <b>${fmt(c.rent.minimumSqm)}</b></span><span>🚶 <b>${c.nearestMrt?.distanceKm ?? '—'}</b> km</span></div></div><span class="price-chip">${labelFor(c)}</span></article>`; }).join('') || '<p class="empty-state">沒有符合的樓盤</p>';
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
    const nearest = c.nearestMrt;
    const nearestStation = stations.find(s => s.id === nearest?.stationId);
    detail.classList.remove('empty');
    detail.innerHTML = `<button class="close-detail" aria-label="關閉樓盤資訊">×</button>
      <div class="detail-hero"><div class="detail-topline"><span class="station-pill">最近 MRT ${esc(nearestStation?.name || c.station)}</span><span class="age-pill">${c.completedYear} 完工</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.beds || 2} 房樣本約 ${fmt(c.area, 1)} ㎡ · ${fmt(c.units)} 戶 · ${esc(c.floors || '—')}</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div>
      <section class="walk-section"><div class="walk-main"><span class="walk-symbol">🚶</span><div><span class="metric-label">最近 MRT · ${esc(nearestStation?.name || c.station)}</span><strong>${nearest?.distanceKm ?? '—'} 公里</strong><small>步行約 ${nearest?.minutes ?? '—'} 分鐘 · 路網估算</small></div></div><button id="showWalkingRoute" class="route-button">在地圖顯示路線</button><p class="fee-note">距離以樓盤座標至站點座標估算，實際入口與步行時間可能不同。</p></section>
      <section class="detail-section"><p class="section-label">二手出售 <span>${fmt(c.sale.count)} 筆 · 全房型 · ${esc(c.sale.asOf)}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">平均售價</span><b class="metric-value">${money(c.sale.average)}</b><span class="metric-sub">最低 ${money(c.sale.minimum)}</span></div><div class="metric"><span class="metric-label">售價 / ㎡</span><b class="metric-value">${money(c.sale.averageSqm)}</b><span class="metric-sub">最低 ${money(c.sale.minimumSqm)} / ㎡</span></div></div><div class="unit-price"><span>資料來源：PropertyHub 掛牌</span><b><a href="${esc(c.sale.source)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section rent-section"><p class="section-label">出租市場 <span>${fmt(c.rent.count)} 筆 · 全房型</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">平均月租</span><b class="metric-value">${money(c.rent.average)}</b><span class="metric-sub">最低 ${money(c.rent.minimum)} / 月</span></div><div class="metric"><span class="metric-label">租金 / ㎡</span><b class="metric-value">${money(avgRate)}<small> / 月</small></b><span class="metric-sub">最低 ${money(minRate)} / ㎡ / 月</span></div></div><div class="unit-price"><span>平台廣告數不等於空置戶數</span><b><a href="${esc(c.rent.source)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section"><p class="section-label">管理費參考 <span>需向管委會確認</span></p>${feeText}${c.fee.source ? `<div class="source-links"><a href="${esc(c.fee.source)}" target="_blank" rel="noopener">管理費來源 ↗</a></div>` : ''}</section>
      <section class="detail-section yield-section"><div class="yield-heading"><p class="section-label">年租金報酬試算 <span>最低單價為預設</span></p><div class="yield-value" id="yieldValue">${yieldFor(c).toFixed(2)}<small>% / 年</small></div></div><div class="yield-inputs"><div class="yield-input"><label for="yieldPrice">參考購入總價 (฿)</label><input id="yieldPrice" type="number" min="1" step="50000" value="${Math.round(Number(c.sale.minimumSqm || 0) * Number(c.area || 0))}"></div><div class="yield-input"><label for="yieldRent">參考月租 (฿)</label><input id="yieldRent" type="number" min="0" step="500" value="${Math.round(Number(c.rent.minimumSqm || 0) * Number(c.area || 0))}"></div><div class="yield-input"><label for="yieldArea">室內面積 (㎡)</label><input id="yieldArea" type="number" min="1" step="0.1" value="${Number(c.area || 0).toFixed(1)}"></div><div class="yield-input"><label>參考房型</label><input value="${c.beds || 2} 房" readonly></div></div><div class="yield-options"><label><input id="deductFee" type="checkbox" checked> 扣除管理費</label><label><input id="deductAgent" type="checkbox" checked> 扣除 1 個月仲介管理費</label></div><p class="formula-note">預設以最低售價/㎡及最低租金/㎡估算，再乘樣本面積；勾選時扣除每月管理費與 1 個月仲介管理費。未含稅、維修、裝修、交易成本與貸款。</p><div class="source-links"><a href="${esc(c.sale.source)}" target="_blank" rel="noopener">出售掛牌 ↗</a><a href="${esc(c.rent.source)}" target="_blank" rel="noopener">出租掛牌 ↗</a></div></section>
      <section class="detail-section"><p class="section-label">樓盤資訊 <span>起造資料待補</span></p><p class="fee-note">目前可查到 ${c.completedYear} 年完工；此資料不等同起造日期，起造日尚待逐案核實。樣本座標及售租價格取自公開平台。</p><div class="source-links"><a href="https://www.hipflat.co.th/zh/thailand-projects/condo/bangkok-bm" target="_blank" rel="noopener">Hipflat · 區域有 197 案 ↗</a></div></section>`;
    detail.querySelector('.close-detail').addEventListener('click', () => { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); });
    detail.querySelector('#showWalkingRoute').addEventListener('click', () => {
      if (!nearest?.shape || !nearestStation) return;
      if (walkingLine) map.removeLayer(walkingLine);
      walkingLine = L.polyline(decodePolyline6(nearest.shape), { color: '#12805f', weight: 5, opacity: .9, dashArray: '9 7', lineCap: 'round' }).addTo(map);
      map.fitBounds(walkingLine.getBounds(), { padding: [90, 90], maxZoom: 16 });
      stationMarkers.get(nearest.stationId)?.openPopup();
    });
    ['yieldPrice', 'yieldRent', 'yieldArea', 'deductFee', 'deductAgent'].forEach(id => detail.querySelector(`#${id}`).addEventListener('input', () => {
      const price = Number(detail.querySelector('#yieldPrice').value);
      const rent = Number(detail.querySelector('#yieldRent').value);
      const area = Number(detail.querySelector('#yieldArea').value);
      const fee = detail.querySelector('#deductFee').checked && c.fee.rate && area ? c.fee.rate * area * 12 : 0;
      const agentMonth = detail.querySelector('#deductAgent').checked ? 1 : 0;
      const y = price > 0 && area > 0 ? ((rent * (12 - agentMonth) - fee) / price * 100) : 0;
      yieldOverrides.set(c.id, Number.isFinite(y) ? y : 0);
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
    if (walkingLine) { map.removeLayer(walkingLine); walkingLine = null; }
    if (window.matchMedia('(max-width: 650px)').matches) document.querySelector('.explorer').classList.add('hidden-mobile');
    map.panTo([c.lat, c.lng], { animate: true, duration: .4 });
  }
  function refreshMode() {
    document.querySelectorAll('.segmented button').forEach(b => b.classList.toggle('selected', b.dataset.mode === mode));
    markers.forEach((m, id) => m.setIcon(icon(condos.find(x => x.id === id), id === selectedId)));
    renderList();
  }
  document.querySelectorAll('.segmented button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; refreshMode(); }));
  document.getElementById('sortOrder').addEventListener('change', e => { sortMode = e.target.value; renderList(); });
  document.getElementById('search').addEventListener('input', e => { query = e.target.value.trim(); renderList(); });
  document.getElementById('clearSearch').addEventListener('click', () => { document.getElementById('search').value = ''; query = ''; renderList(); });
  document.getElementById('fitMap').addEventListener('click', () => { const points = [...filtered().map(c => [c.lat,c.lng]), ...stations.map(s => [s.lat,s.lng])]; if (points.length) map.fitBounds(points, { padding: [70, 90], maxZoom: 14 }); });
  document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
  document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
  document.getElementById('locate').addEventListener('click', () => map.setView([13.7824, 100.5763], 14));
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); document.getElementById('search').focus(); } if (e.key === 'Escape') { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); } });
  renderList();
  if (selectedId) { const c = condos.find(x => x.id === selectedId); if (window.matchMedia('(max-width: 650px)').matches) detail.classList.add('empty'); else renderDetail(c); markerFor(selectedId)?.setIcon(icon(c, true)); }
  if (condos.length) {
    const narrow = window.matchMedia('(max-width: 650px)').matches;
    if (narrow) map.setView([13.7824, 100.5763], 12);
    else map.fitBounds([...condos.map(c => [c.lat,c.lng]), ...stations.map(s => [s.lat,s.lng])], { paddingTopLeft: [390, 60], paddingBottomRight: [390, 60], maxZoom: 13 });
  }
  window.addEventListener('resize', () => map.invalidateSize());
})();
