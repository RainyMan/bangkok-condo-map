(() => {
  const stations = window.MRT_STATIONS || [];
  const transitLabel = station => station?.line?.startsWith('BTS') ? 'BTS' : station?.line?.startsWith('MRT') ? 'MRT' : station?.line || '捷運';
  const legacyRows = [...(window.CONDO_DATA || []), ...(window.CATALOGUE_PROJECTS || []), ...(window.HUAI_KHWANG_PROJECTS || [])];
  const normalizeName = value => String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
  const legacyByName = new Map();
  legacyRows.forEach(row => { const key = normalizeName(row.name); if (!legacyByName.has(key)) legacyByName.set(key, []); legacyByName.get(key).push(row); });
  const osmById = new Map((window.BANGKOK_OSM_LOCATIONS || []).map(row => [Number(row.id), row]));
  const walkingById = new Map((window.BANGKOK_WALK_ROUTES || []).map(row => [Number(row.id), row]));
  const propertyHubById = new Map((window.BANGKOK_PROPERTYHUB_PROJECTS || []).map(row => [Number(row.id), row]));
  const propertyHubDetailsById = new Map((window.BANGKOK_PROPERTYHUB_DETAILS || []).map(row => [String(row.propertyHubProjectId), row]));
  const propertyHubGuessedDetailsById = new Map((window.BANGKOK_PROPERTYHUB_GUESSED_DETAILS || []).map(row => [Number(row.hipflatProjectId), row]));
  const propertyHubCitySummaryById = new Map((window.BANGKOK_PROPERTYHUB_CITY_SUMMARIES || []).map(row => [Number(row.id), row]));
  const hipflatProjects = window.BANGKOK_HIPFLAT_PROJECTS || [];
  const matchedLegacy = new Set();
  const condos = hipflatProjects.map(project => {
    const candidates = legacyByName.get(normalizeName(project.name)) || [];
    const legacy = candidates.length === 1 ? candidates[0] : null;
    if (legacy) matchedLegacy.add(legacy.id);
    const propertyHubBase = propertyHubById.get(Number(project.id)) || {};
    const propertyHubDetail = propertyHubDetailsById.get(String(propertyHubBase.propertyHubProjectId || '')) || {};
    const propertyHubGuessedDetail = propertyHubGuessedDetailsById.get(Number(project.id)) || {};
    const propertyHub = { ...propertyHubBase, ...propertyHubGuessedDetail, ...propertyHubDetail };
    const citySummary = propertyHubCitySummaryById.get(Number(project.id)) || {};
    if (citySummary.sale) propertyHub.sale = citySummary.sale;
    if (citySummary.rent) propertyHub.rent = citySummary.rent;
    const osm = osmById.get(Number(project.id));
    const coordsFromProject = propertyHub.locationVerified && Number.isFinite(propertyHub.lat) && Number.isFinite(propertyHub.lng)
      ? false
      : project.locationVerified && Number.isFinite(project.lat) && Number.isFinite(project.lng);
    const coordsFromPropertyHub = propertyHub.locationVerified && Number.isFinite(propertyHub.lat) && Number.isFinite(propertyHub.lng);
    const coordsFromOsm = !coordsFromProject && osm;
    const lat = coordsFromPropertyHub ? propertyHub.lat : coordsFromProject ? project.lat : coordsFromOsm ? osm.lat : legacy?.lat ?? null;
    const lng = coordsFromPropertyHub ? propertyHub.lng : coordsFromProject ? project.lng : coordsFromOsm ? osm.lng : legacy?.lng ?? null;
    const locationVerified = Boolean(coordsFromPropertyHub || coordsFromProject || coordsFromOsm || legacy?.locationVerified);
    let nearestMrt = null;
    if (Number.isFinite(lat) && Number.isFinite(lng)) {
      let best = null;
      for (const station of stations) {
        const rad = Math.PI / 180, dLat = (station.lat - lat) * rad, dLng = (station.lng - lng) * rad;
        const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat * rad) * Math.cos(station.lat * rad) * Math.sin(dLng / 2) ** 2;
        const km = 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        if (!best || km < best.straightDistanceKm) best = { stationId: station.id, straightDistanceKm: Number(km.toFixed(2)) };
      }
      nearestMrt = best;
      const oldRoutes = project.walkRoutes || legacy?.walkRoutes || {};
      const matchedRoute = oldRoutes[best?.stationId];
      if (matchedRoute) nearestMrt = { ...nearestMrt, ...matchedRoute, stationId: best.stationId, straightDistanceKm: best.straightDistanceKm };
      const walkingRoute = walkingById.get(Number(project.id));
      if (walkingRoute) nearestMrt = { ...nearestMrt, ...walkingRoute };
    } else {
      nearestMrt = project.nearestMrt || legacy?.nearestMrt || null;
    }
    const mergedSale = propertyHub.sale || project.sale || legacy?.sale || null;
    const mergedRent = propertyHub.rent || project.rent || legacy?.rent || null;
    const cleanSale = mergedSale && Number(mergedSale.minimumSqm) >= 10000 && Number(mergedSale.minimumSqm) <= 2000000 ? mergedSale : null;
    const cleanRent = mergedRent && Number(mergedRent.minimumSqm) >= 100 && Number(mergedRent.minimumSqm) <= 20000 ? mergedRent : null;
    const rawCompletedYear = Number(propertyHub.completedYear || project.completedYear || legacy?.completedYear || 0);
    const completedYear = rawCompletedYear >= 2400 && rawCompletedYear <= 2700 ? rawCompletedYear - 543 : rawCompletedYear || null;
    return { ...legacy, ...project, ...propertyHub, lat, lng, locationVerified,
      locationSourceUrl: coordsFromPropertyHub ? propertyHub.locationSourceUrl : coordsFromProject ? project.locationSourceUrl : coordsFromOsm ? osm.sourceUrl : project.locationSourceUrl || legacy?.locationSourceUrl,
      locationSourceName: coordsFromPropertyHub ? propertyHub.locationSourceName : coordsFromOsm ? 'OpenStreetMap 建物／地址' : project.locationSourceName || legacy?.locationSourceName,
      sale: cleanSale, rent: cleanRent,
      fee: propertyHub.fee || project.fee || legacy?.fee || null,
      completedYear,
      nearestMrt, station: stations.find(item => item.id === nearestMrt?.stationId)?.name || project.station || legacy?.station || null,
      propertyHubProjectUrl: propertyHub.propertyHubProjectUrl || project.propertyHubProjectUrl || legacy?.propertyHubProjectUrl || null };
  });
  const hasSale = c => Number(c.sale?.minimumSqm) >= 10000 && Number(c.sale?.minimumSqm) <= 2000000;
  const hasRent = c => Number(c.rent?.minimumSqm) >= 100 && Number(c.rent?.minimumSqm) <= 20000;
  const hasYieldData = c => hasSale(c) && hasRent(c);
  const fmt = (n, digits = 0) => n == null || Number.isNaN(Number(n)) ? '—' : Number(n).toLocaleString('en-US', { maximumFractionDigits: digits });
  const sampleCount = market => market.countKind === 'matched_city_index' ? `PropertyHub 公開頁比對到 ${fmt(market.observedCount)} 筆掛牌` : market.observedCount ? `${fmt(market.observedCount)} 筆可見樣本 · 平台刊登 ${fmt(market.count)} 筆` : `${fmt(market.count)} 筆 · 全房型`;
  const money = n => n == null ? '—' : `฿${fmt(n)}`;
  const areaFor = c => Number(c.area?.min ?? c.area ?? 1);
  const areaLabel = c => c.area && typeof c.area === 'object' ? `${fmt(c.area.min, 1)}–${fmt(c.area.max, 1)} ㎡樓型範圍` : c.area ? `約 ${fmt(c.area, 1)} ㎡` : '';
  const compactMoney = n => n == null ? '—' : n >= 1000000 ? `฿${(n / 1000000).toFixed(2)}M` : `฿${fmt(n / 1000, 0)}K`;
  const sampleSource = url => url ? `<a class="sample-source" href="${esc(url)}" target="_blank" rel="noopener" aria-label="開啟這筆最低價物件" title="開啟這筆最低價物件" style="color:var(--green);font-weight:700;text-decoration:none;margin-left:4px">物件 ↗</a>` : '<span class="sample-source-missing" title="目前沒有核對到這筆樣本的個別物件頁">物件連結待補</span>';
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const reviewsUrl = c => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${c.name} condo ${c.address || 'Bangkok Thailand'}`)}`;
  const map = L.map('map', { zoomControl: false, scrollWheelZoom: true }).setView([13.7563, 100.5018], 11);
  const mapElement = document.getElementById('map');
  const updateMarkerDensity = () => mapElement.classList.toggle('low-zoom', map.getZoom() < 15);
  map.on('zoomend', updateMarkerDensity);
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
  const labelFor = c => mode === 'sale' ? hasSale(c) ? `${fmt(c.sale.minimumSqm)}<small>最低 ฿/㎡</small>` : '待補資料<small>售價/㎡</small>' : mode === 'rent' ? hasRent(c) ? `${fmt(c.rent.minimumSqm)}<small>最低 ฿/㎡/月</small>` : '待補資料<small>租金/㎡/月</small>' : hasYieldData(c) ? `${yieldFor(c).toFixed(1)}<small>% 淨投報</small>` : '待補資料<small>售租資料不足</small>';
  function yieldFor(c) {
    if (!hasYieldData(c)) return 0;
    if (yieldOverrides.has(c.id)) return yieldOverrides.get(c.id);
    const priceRate = Number(c.sale.minimumSqm || 0);
    const rentRate = Number(c.rent.minimumSqm || 0);
    const useFee = document.getElementById('deductFee')?.checked ?? true;
    const useAgent = document.getElementById('deductAgent')?.checked ?? true;
    if (!priceRate || !rentRate) return 0;
    const feeRate = useFee ? Number(c.fee?.rate || 0) * 12 : 0;
    return (rentRate * (12 - (useAgent ? 1 : 0)) - feeRate) / priceRate * 100;
  }
  function icon(c, active = false) {
    return L.divIcon({ className: 'condo-icon' + (active ? ' active' : ''), html: `<span><b class="marker-price">${labelFor(c)}</b></span>`, iconSize: [110, 30], iconAnchor: [55, 15] });
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
    const marker = L.marker([s.lat, s.lng], { title: `${s.line} ${s.name} ${s.id}`, icon: L.divIcon({ className: 'station-icon', html: `<span><b>M</b><strong>${esc(s.name)}</strong><small>${esc(s.id)}</small></span>`, iconSize: [58, 30], iconAnchor: [14, 15] }), zIndexOffset: 500 }).addTo(map);
    marker.bindPopup(`<strong>${esc(s.name)}</strong><br>${esc(s.id)} · ${esc(s.line)}<br><a href="${esc(s.sourceUrl)}" target="_blank" rel="noopener">OpenStreetMap 站點來源 ↗</a>`);
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
    const normalizedQuery = query.trim()
      .replace(/(\d+)\s*房\s*[,，·]?\s*([\d,.]+)\s*萬\s*(?:元)?\s*(?:內|以下)/gi, (_, beds, amount) => `${beds}房售價<=${Number(amount.replace(/,/g, '')) * 10000}`)
      .replace(/(\d+)\s+房/g, '$1房');
    const aliases = {
      '年':'year','完工年':'year','完成年':'year','year':'year',
      '售價':'sale','售價/㎡':'sale','售價單價':'sale','sale':'sale','price':'sale',
      '總價':'saleTotal','房價':'saleTotal','售價總額':'saleTotal',
      '租金':'rent','月租':'rent','租金/㎡':'rent','月租/㎡':'rent','rent':'rent',
      '距離':'distance','步行':'distance','步行距離':'distance','mrt距離':'distance','distance':'distance',
      '投報':'yield','淨投報':'yield','投報率':'yield','yield':'yield',
      '站':'station','mrt':'station','樓名':'name','name':'name'
    };
    const metrics = { year:Number(c.completedYear), sale:Number(c.sale?.minimumSqm), saleTotal:Number(c.sale?.minimum), rent:Number(c.rent?.minimumSqm), distance:Number(c.nearestMrt?.distanceKm ?? c.nearestMrt?.straightDistanceKm), yield:yieldFor(c) };
    return normalizedQuery.split(/\s+/).every(token => {
      const roomOnly = token.match(/^(\d+)\s*房$/);
      if (roomOnly) return Number(c.sale?.byBedroom?.[roomOnly[1]]?.minimum) > 0;
      const expr = token.match(/^(.+?)(<=|>=|<|>|=|:)(.+)$/);
      if (!expr) return haystack.includes(token.toLowerCase());
      const bedroomPrice = expr[1].toLowerCase().match(/^(\d+)房(?:售價|總價|房價)$/);
      const field = aliases[expr[1].toLowerCase()];
      if (!field && !bedroomPrice) return haystack.includes(token.toLowerCase());
      const [, , operator, rawValue] = expr;
      if (field === 'name' || field === 'station') return [':','='].includes(operator) && `${field === 'name' ? c.name : stationName}`.toLowerCase().includes(rawValue.toLowerCase());
      const target = bedroomPrice ? Number(c.sale?.byBedroom?.[bedroomPrice[1]]?.minimum) : metrics[field];
      const numericValue = rawValue.replace(/[฿,\s]/g, '').match(/^([\d.]+)(萬)?$/i);
      const value = numericValue ? Number(numericValue[1]) * (numericValue[2] ? 10000 : 1) : NaN;
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
    const keyFor = c => sortMode === 'distance' ? (c.nearestMrt?.distanceKm ?? c.nearestMrt?.straightDistanceKm) : sortMode === 'sale' ? c.sale?.minimumSqm : sortMode === 'rent' ? c.rent?.minimumSqm : yieldFor(c);
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
    document.getElementById('resultCount').textContent = `${shown.length} 個樓盤`;
    document.querySelector('.count-pill').textContent = `${condos.length} 個樓盤`;
    const coverage = {
      locations: condos.filter(c => c.locationVerified && Number.isFinite(c.lat) && Number.isFinite(c.lng)).length,
      sale: condos.filter(hasSale).length,
      rent: condos.filter(hasRent).length,
      yield: condos.filter(hasYieldData).length,
    };
    document.getElementById('coverageSummary').textContent = `核實座標 ${coverage.locations.toLocaleString()} · 出售樣本 ${coverage.sale.toLocaleString()} · 出租樣本 ${coverage.rent.toLocaleString()} · 可算投報 ${coverage.yield.toLocaleString()}`;
    document.getElementById('listCount').textContent = String(shown.length).padStart(2, '0');
    list.innerHTML = shown.map((c, i) => { const nearestStation = stations.find(s => s.id === c.nearestMrt?.stationId); const located = Number.isFinite(c.lat) && Number.isFinite(c.lng); const roomMatch = query.match(/(\d+)\s*房/); const roomListing = roomMatch && c.sale?.byBedroom?.[roomMatch[1]]; const meta = nearestStation ? `${transitLabel(nearestStation)} ${nearestStation.name} · ${c.completedYear ? `完工 ${c.completedYear}` : c.locationVerified ? '座標已核實 · Hipflat 收錄' : 'Hipflat 收錄 · 位置待核'}` : c.locationVerified ? '座標已核實 · Hipflat 收錄' : 'Hipflat 收錄 · 位置待核'; return `<article class="project-card ${c.id === selectedId ? 'active' : ''}" data-id="${c.id}" tabindex="0" role="button" aria-label="查看 ${esc(c.name)}"><span class="rank">${String(i + 1).padStart(2, '0')}</span><div class="project-copy"><strong class="project-name">${esc(c.name)}</strong><span class="project-meta">${esc(meta)}</span><div class="project-values"><span>${roomListing ? `${roomMatch[1]}房總價` : '售/㎡'} <b>${roomListing ? compactMoney(roomListing.minimum) : fmt(c.sale?.minimumSqm)}</b></span><span>租/㎡/月 <b>${fmt(c.rent?.minimumSqm)}</b></span><span>${located ? (c.nearestMrt?.distanceKm != null ? '🚶' : '直線') : '座標'} <b>${located ? ((c.nearestMrt?.distanceKm ?? c.nearestMrt?.straightDistanceKm) ?? '—') + ' km' : '待補'}</b></span></div></div><span class="price-chip">${labelFor(c)}</span></article>`; }).join('') || '<p class="empty-state">沒有符合的樓盤</p>';
    list.querySelectorAll('.project-card').forEach(el => {
      const activate = () => select(Number(el.dataset.id));
      el.addEventListener('click', activate);
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
    });
  }
  function renderDetail(c) {
    if (!hasSale(c) || !hasRent(c)) {
      const query = encodeURIComponent(`${c.name} condo Bangkok`);
      const ddSale = `https://www.google.com/search?q=site%3Addproperty.com+${query}+for+sale`;
      const ddRent = `https://www.google.com/search?q=site%3Addproperty.com+${query}+for+rent`;
      const phSale = c.propertyHubSaleUrl || `https://www.google.com/search?q=site%3Apropertyhub.in.th+${query}+for+sale`;
      const phRent = c.propertyHubRentUrl || `https://www.google.com/search?q=site%3Apropertyhub.in.th+${query}+for+rent`;
      const hipflatSearch = c.hipflatProjectUrl || `https://www.google.com/search?q=site%3Ahipflat.co.th%2Fzh%2Fprojects+${query}`;
      const nearest = c.nearestMrt;
      const station = stations.find(s => s.id === nearest?.stationId);
      const directionsUrl = station && c.locationVerified ? `https://www.google.com/maps/dir/?api=1&origin=${c.lat},${c.lng}&destination=${station.lat},${station.lng}&travelmode=walking` : null;
      detail.classList.remove('empty');
      const projectAreaLabel = station ? `${station.name} ${transitLabel(station)} 周邊` : '曼谷樓盤名單';
      const nearestLabel = station?.name || (nearest ? c.station : '待核實');
      const fallbackSale = hasSale(c) ? `<section class="detail-section"><p class="section-label">二手出售 <span>可核對掛牌樣本</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">最低售價</span><b class="metric-value">${money(c.sale.minimum)}</b><span class="metric-sub">${sampleSource(c.sale.minimumSourceUrl)}</span></div><div class="metric"><span class="metric-label">最低售價 / ㎡</span><b class="metric-value">${money(c.sale.minimumSqm)}</b><span class="metric-sub">${sampleSource(c.sale.minimumSqmSourceUrl)}</span></div></div><div class="source-links"><a href="${esc(c.sale.source || phSale)}" target="_blank" rel="noopener">PropertyHub 出售來源 ↗</a></div></section>` : c.hipflatSummary?.saleFrom ? `<section class="detail-section"><p class="section-label">Hipflat 起售參考 <span>專案摘要，非單筆掛牌</span></p><b class="metric-value">${money(c.hipflatSummary.saleFrom)}</b><div class="source-links"><a href="${esc(c.hipflatSummary.source || c.hipflatProjectUrl || hipflatSearch)}" target="_blank" rel="noopener">Hipflat 專案起售來源 ↗</a></div></section>` : '';
      const fallbackRent = hasRent(c) ? `<section class="detail-section rent-section"><p class="section-label">出租市場 <span>可核對掛牌樣本</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">最低月租</span><b class="metric-value">${money(c.rent.minimum)} / 月</b><span class="metric-sub">${sampleSource(c.rent.minimumSourceUrl)}</span></div><div class="metric"><span class="metric-label">最低租金 / ㎡ / 月</span><b class="metric-value">${money(c.rent.minimumSqm)}</b><span class="metric-sub">${sampleSource(c.rent.minimumSqmSourceUrl)}</span></div></div><div class="source-links"><a href="${esc(c.rent.source || phRent)}" target="_blank" rel="noopener">PropertyHub 出租來源 ↗</a></div></section>` : c.hipflatSummary?.rentFrom ? `<section class="detail-section rent-section"><p class="section-label">Hipflat 起租參考 <span>專案摘要，非單筆掛牌</span></p><b class="metric-value">${money(c.hipflatSummary.rentFrom)} / 月</b><div class="source-links"><a href="${esc(c.hipflatSummary.source || c.hipflatProjectUrl || hipflatSearch)}" target="_blank" rel="noopener">Hipflat 專案起租來源 ↗</a></div></section>` : '';
      detail.innerHTML = `<button class="close-detail" aria-label="關閉樓盤資訊">×</button><div class="detail-hero"><div class="detail-topline"><span class="station-pill">Hipflat · ${esc(projectAreaLabel)}</span><span class="age-pill">${c.completedYear ? `${esc(c.completedYear)} 完工` : c.locationVerified ? '完工年待補 · 座標已核實' : '完工年待補 · 位置待核'}</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.locationVerified ? '樓盤座標已由公開樓盤或地圖資料頁核對。' : '樓盤位置尚待核實。'} 完工年會在取得可靠資料後補上。</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div><section class="walk-section"><div class="walk-main"><span class="walk-symbol">🚇</span><div><span class="metric-label">${nearest?.distanceKm ? `最近${transitLabel(station)}站（步行路網估算）` : `最近${transitLabel(station)}站（直線距離）`}· ${esc(nearestLabel)}</span><strong>${c.locationVerified ? nearest?.distanceKm ? `${nearest.distanceKm} 公里步行路網距離` : `${nearest?.straightDistanceKm ?? '—'} 公里直線距離` : '樓盤座標待核'}</strong><small>${c.locationVerified ? nearest?.distanceKm ? `步行約 ${Math.max(1, Number(nearest.minutes) || 0)} 分鐘 · Valhalla 路網估算` : '步行路網距離待計算' : '確認樓盤座標後，再判定最近 MRT 與步行距離'}</small></div></div>${directionsUrl ? `<a class="route-button" href="${directionsUrl}" target="_blank" rel="noopener">Google Maps 步行導航 ↗</a>` : station ? '<button id="showWalkingRoute" class="route-button">查看 MRT 站點</button>' : ''}</section>${fallbackSale}${fallbackRent}<section class="detail-section"><p class="section-label">其他公開房源來源</p><div class="source-links"><a href="${hipflatSearch}" target="_blank" rel="noopener">Hipflat 專案與售租行情 ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a><a href="${phSale}" target="_blank" rel="noopener">PropertyHub 出售 ↗</a><a href="${phRent}" target="_blank" rel="noopener">PropertyHub 出租 ↗</a></div></section><section class="detail-section"><p class="section-label">投報率試算 <span>售租資料不足</span></p><p class="fee-note">補齊同一樓盤的出售與出租掛牌後，會以每平方米最低單價計算。</p></section><section class="detail-section"><p class="section-label">資料來源</p><div class="source-links"><a href="${esc(c.discoveryUrl)}" target="_blank" rel="noopener">Hipflat 曼谷樓盤清單 ↗</a>${c.hipflatProjectUrl ? `<a href="${esc(c.hipflatProjectUrl)}" target="_blank" rel="noopener">Hipflat 專案頁 ↗</a>` : ''}${c.locationVerified ? `<a href="${esc(c.locationSourceUrl)}" target="_blank" rel="noopener">座標來源 ↗</a>` : ''}</div></section>`;
      detail.querySelector('.close-detail').addEventListener('click', () => { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); });
      detail.querySelector('#showWalkingRoute')?.addEventListener('click', () => { if (station) { map.setView([station.lat, station.lng], 16); stationMarkers.get(station.id)?.openPopup(); } });
      return;
    }
    const avgRate = c.rent?.averageSqm;
    const minRate = c.rent?.minimumSqm;
    const ddSale = `https://www.google.com/search?q=site%3Addproperty.com+${encodeURIComponent(c.name)}+for+sale`;
    const ddRent = `https://www.google.com/search?q=site%3Addproperty.com+${encodeURIComponent(c.name)}+for+rent`;
    const hipflatSearch = `https://www.google.com/search?q=site%3Ahipflat.co.th%2Fzh%2Fprojects+${encodeURIComponent(c.name)}`;
    const saleSampleUrl = c.sale.source || c.propertyHubSaleUrl || ddSale;
    const rentSampleUrl = c.rent.source || c.propertyHubRentUrl || ddRent;
    const roomMatch = query.match(/(\d+)\s*房/);
    const roomListing = roomMatch && c.sale?.byBedroom?.[roomMatch[1]];
    const feeText = c.fee?.rate ? `<div class="fee-row"><strong class="fee-number">฿${fmt(c.fee.rate)} <small>/ ㎡ / 月*</small></strong><span class="age-pill">${c.fee.status === 'historical_indicative' ? '歷史參考' : '公開刊載'}</span></div><p class="fee-note">${esc(c.fee.note || '')}</p>` : '<p class="fee-note">尚未查得可用管理費資料。</p>';
    const addr = `${c.name} condo ${c.address || 'Bangkok Thailand'}`;
    const nearest = c.nearestMrt;
    const nearestStation = stations.find(s => s.id === nearest?.stationId);
    detail.classList.remove('empty');
    detail.innerHTML = `<button class="close-detail" aria-label="關閉樓盤資訊">×</button>
      <div class="detail-hero"><div class="detail-topline"><span class="station-pill">最近${transitLabel(nearestStation)}站 ${esc(nearestStation?.name || c.station)}</span><span class="age-pill">${c.completedYear ? `${esc(c.completedYear)} 完工` : '完工年待補'}</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.beds ? `${c.beds} 房樣本 · ` : ''}${areaLabel(c) ? `${areaLabel(c)} · ` : ''}${c.units ? `${fmt(c.units)} 戶 · ` : ''}${c.floors ? esc(c.floors) : ''}</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div>
      <section class="walk-section"><div class="walk-main"><span class="walk-symbol">🚶</span><div><span class="metric-label">${nearest?.distanceKm != null ? `最近${transitLabel(nearestStation)}站（步行路網估算）` : `最近${transitLabel(nearestStation)}站（直線距離）`}· ${esc(nearestStation?.name || c.station)}</span><strong>${nearest?.distanceKm ?? nearest?.straightDistanceKm ?? '—'} 公里</strong><small>${nearest?.distanceKm != null ? `步行約 ${nearest.minutes} 分鐘 · 路網估算` : '步行路網距離待計算；目前顯示直線距離'}</small></div></div><button id="showWalkingRoute" class="route-button">${nearest?.shape ? '在地圖顯示路線' : 'Google Maps 步行導航 ↗'}</button><p class="fee-note">步行距離由 Valhalla 路網估算，取直線最近 30 個捷運站中最短路徑；實際入口距離可能不同。<a href="${esc(nearest?.sourceUrl || 'https://valhalla1.openstreetmap.de/')}" target="_blank" rel="noopener">路網資料 ↗</a></p></section>
      <section class="detail-section"><p class="section-label">二手出售 <span>${sampleCount(c.sale)} · ${esc(c.sale.asOf || '')}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.sale.observedCount ? '樣本平均售價' : '平均售價'}</span><b class="metric-value">${money(c.sale.average)}</b><span class="metric-sub">最低樣本 ${money(c.sale.minimum)} ${sampleSource(c.sale.minimumSourceUrl)}</span></div><div class="metric"><span class="metric-label">售價 / ㎡</span><b class="metric-value">${money(c.sale.averageSqm)}</b><span class="metric-sub">最低樣本 ${money(c.sale.minimumSqm)} / ㎡ ${sampleSource(c.sale.minimumSqmSourceUrl)}</span></div></div>${roomListing?.sourceUrl ? `<p class="room-sample">${roomMatch[1]} 房最低掛牌 ${money(roomListing.minimum)} <a href="${esc(roomListing.sourceUrl)}" target="_blank" rel="noopener">物件 ↗</a></p>` : ''}<div class="unit-price"><span>來源：PropertyHub 可見掛牌</span><b><a href="${esc(saleSampleUrl)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section rent-section"><p class="section-label">出租市場 <span>${sampleCount(c.rent)} · ${esc(c.rent.asOf || '')}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.rent.observedCount ? '樣本平均月租' : '平均月租'}</span><b class="metric-value">${money(c.rent.average)}</b><span class="metric-sub">最低樣本 ${money(c.rent.minimum)} / 月 ${sampleSource(c.rent.minimumSourceUrl)}</span></div><div class="metric"><span class="metric-label">租金 / ㎡</span><b class="metric-value">${money(avgRate)}<small> / 月</small></b><span class="metric-sub">最低樣本 ${money(minRate)} / ㎡ / 月 ${sampleSource(c.rent.minimumSqmSourceUrl)}</span></div></div><div class="unit-price"><span>來源：PropertyHub 可見掛牌</span><b><a href="${esc(rentSampleUrl)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section"><p class="section-label">管理費參考 <span>需向管委會確認</span></p>${feeText}${c.fee?.source ? `<div class="source-links"><a href="${esc(c.fee.source)}" target="_blank" rel="noopener">管理費來源 ↗</a></div>` : ''}</section>
      ${hasYieldData(c) ? `<section class="detail-section yield-section"><div class="yield-heading"><p class="section-label">年租金報酬試算 <span>最低單價為預設</span></p><div class="yield-value" id="yieldValue">${yieldFor(c).toFixed(2)}<small>% / 年</small></div></div><div class="yield-inputs"><div class="yield-input"><label for="yieldPrice">參考購入總價 (฿)</label><input id="yieldPrice" type="number" min="1" step="50000" value="${Math.round(Number(c.sale.minimumSqm || 0) * areaFor(c))}"></div><div class="yield-input"><label for="yieldRent">參考月租 (฿)</label><input id="yieldRent" type="number" min="0" step="500" value="${Math.round(Number(c.rent.minimumSqm || 0) * areaFor(c))}"></div><div class="yield-input"><label for="yieldArea">室內面積 (㎡)</label><input id="yieldArea" type="number" min="1" step="0.1" value="${areaFor(c).toFixed(1)}"></div><div class="yield-input"><label>參考房型</label><input value="${c.beds || '—'} 房" readonly></div></div><div class="yield-options"><label><input id="deductFee" type="checkbox" checked> 扣除管理費</label><label><input id="deductAgent" type="checkbox" checked> 扣除 1 個月仲介管理費</label></div><p class="formula-note">預設以最低售價/㎡及最低租金/㎡估算；只有樓型面積範圍時，參考總價以最小面積示例，仍需用實際房源面積確認。已知管理費才會扣除，勾選時扣 1 個月租金作仲介費；未含稅、維修及交易成本。</p><div class="source-links"><a href="${esc(saleSampleUrl)}" target="_blank" rel="noopener">出售掛牌來源 ↗</a><a href="${esc(rentSampleUrl)}" target="_blank" rel="noopener">出租掛牌來源 ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a><a href="${hipflatSearch}" target="_blank" rel="noopener">Hipflat 專案行情 ↗</a></div></section>` : '<section class="detail-section yield-section"><p class="section-label">投報率試算 <span>售租資料不足</span></p><p class="fee-note">至少需要同一樓盤可核對的出售與出租每平方米單價，才能計算投報率。</p></section>'}
      <section class="detail-section"><p class="section-label">樓盤資訊 <span>${c.completedYear ? `${esc(c.completedYear)} 完工` : '完工年待補'} · 起造年待補</span></p><p class="fee-note">售租樣本依 PropertyHub 曼谷搜尋頁掛牌整理，按樓盤名稱唯一比對；最低價連結可直達單筆物件。平台刊登總數僅供參考。Hipflat 提供樓盤資料與售租行情。</p><div class="source-links">${c.completedYearSourceUrl || c.propertyHubProjectUrl ? `<a href="${esc(c.completedYearSourceUrl || c.propertyHubProjectUrl)}" target="_blank" rel="noopener">完工與樓盤資料來源 ↗</a>` : ''}${c.locationSourceUrl ? `<a href="${esc(c.locationSourceUrl)}" target="_blank" rel="noopener">座標來源 ↗</a>` : ''}<a href="${hipflatSearch}" target="_blank" rel="noopener">搜尋此案 Hipflat 專案與售租行情 ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a></div></section>`;
    detail.querySelector('.close-detail').addEventListener('click', () => { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); });
    detail.querySelector('#showWalkingRoute').addEventListener('click', () => {
      if (!nearestStation) return;
      if (!nearest?.shape && Number.isFinite(c.lat) && Number.isFinite(c.lng)) {
        const url = `https://www.google.com/maps/dir/?api=1&origin=${c.lat},${c.lng}&destination=${nearestStation.lat},${nearestStation.lng}&travelmode=walking`;
        window.open(url, '_blank', 'noopener');
        return;
      }
      if (!nearest?.shape) return;
      if (walkingLine) map.removeLayer(walkingLine);
      walkingLine = L.polyline(decodePolyline6(nearest.shape), { color: '#12805f', weight: 5, opacity: .9, dashArray: '9 7', lineCap: 'round' }).addTo(map);
      map.fitBounds(walkingLine.getBounds(), { padding: [90, 90], maxZoom: 16 });
      stationMarkers.get(nearest.stationId)?.openPopup();
    });
    ['yieldPrice', 'yieldRent', 'yieldArea', 'deductFee', 'deductAgent'].forEach(id => detail.querySelector(`#${id}`)?.addEventListener('input', () => {
      const price = Number(detail.querySelector('#yieldPrice').value);
      const rent = Number(detail.querySelector('#yieldRent').value);
      const area = Number(detail.querySelector('#yieldArea').value);
      const fee = detail.querySelector('#deductFee').checked && c.fee?.rate && area ? c.fee.rate * area * 12 : 0;
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
    if (Number.isFinite(c.lat) && Number.isFinite(c.lng)) map.panTo([c.lat, c.lng], { animate: true, duration: .4 });
    else { const station = stations.find(s => s.id === c.nearestMrt?.stationId); if (station) map.panTo([station.lat, station.lng], { animate: true, duration: .4 }); }
  }
  function refreshMode() {
    document.querySelectorAll('.segmented button').forEach(b => b.classList.toggle('selected', b.dataset.mode === mode));
    markers.forEach((m, id) => m.setIcon(icon(condos.find(x => x.id === id), id === selectedId)));
    renderList();
  }
  document.querySelectorAll('.segmented button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; refreshMode(); }));
  document.getElementById('sortOrder').addEventListener('change', e => { sortMode = e.target.value; renderList(); });
  const searchInput = document.getElementById('search');
  const budgetInput = document.getElementById('budgetInput');
  let selectedBedrooms = null;
  const setBedroomSelection = beds => {
    selectedBedrooms = beds;
    document.querySelectorAll('[data-bedrooms]').forEach(option => {
      const selected = option.dataset.bedrooms === beds;
      option.classList.toggle('selected', selected);
      option.setAttribute('aria-pressed', String(selected));
    });
  };
  document.querySelectorAll('[data-bedrooms]').forEach(button => button.addEventListener('click', () => {
    setBedroomSelection(button.dataset.bedrooms);
  }));
  document.getElementById('applyBedroomFilter').addEventListener('click', () => {
    const rawBudget = budgetInput.value.trim().replace(/[฿,\s]/g, '');
    const amount = rawBudget.match(/^([\d.]+)萬?$/i);
    const budget = amount ? Number(amount[1]) * (rawBudget.includes('萬') ? 10000 : 1) : NaN;
    budgetInput.setAttribute('aria-invalid', String(!Number.isFinite(budget) || budget <= 0));
    if (!selectedBedrooms || !Number.isFinite(budget) || budget <= 0) return;
    searchInput.value = `${selectedBedrooms}房售價<=${budget}`;
    query = searchInput.value;
    renderList();
  });
  searchInput.addEventListener('input', e => {
    query = e.target.value.trim();
    const roomQuery = query.match(/(?:^|\s)([1-4])\s*房/);
    setBedroomSelection(roomQuery?.[1] || null);
    const budgetQuery = query.match(/[1-4]\s*房(?:售價|總價|房價)(?:<=|<)\s*([\d,.]+萬?)/);
    const naturalBudget = query.match(/[1-4]\s*房\s*([\d,.]+\s*萬)\s*(?:內|以下)/);
    if (budgetQuery) budgetInput.value = budgetQuery[1];
    else if (naturalBudget) budgetInput.value = naturalBudget[1].replace(/\s/g, '');
    renderList();
  });
  document.getElementById('clearSearch').addEventListener('click', () => {
    searchInput.value = ''; query = ''; selectedBedrooms = null; budgetInput.removeAttribute('aria-invalid');
    setBedroomSelection(null);
    renderList();
  });
  document.getElementById('fitMap').addEventListener('click', () => { const points = [...filtered().filter(c => Number.isFinite(c.lat) && Number.isFinite(c.lng)).map(c => [c.lat,c.lng]), ...stations.map(s => [s.lat,s.lng])]; if (points.length) map.fitBounds(points, { padding: [70, 90], maxZoom: 14 }); });
  document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
  document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
  document.getElementById('locate').addEventListener('click', () => map.setView([13.7563, 100.5018], 11));
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); document.getElementById('search').focus(); } if (e.key === 'Escape') { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); } });
  renderList();
  updateMarkerDensity();
  if (selectedId) { const c = condos.find(x => x.id === selectedId); if (window.matchMedia('(max-width: 650px)').matches) detail.classList.add('empty'); else renderDetail(c); markerFor(selectedId)?.setIcon(icon(c, true)); }
  if (condos.length) {
    const narrow = window.matchMedia('(max-width: 650px)').matches;
    if (narrow) map.setView([13.7563, 100.5018], 10);
    else map.fitBounds([...condos.filter(c => Number.isFinite(c.lat) && Number.isFinite(c.lng)).map(c => [c.lat,c.lng]), ...stations.map(s => [s.lat,s.lng])], { paddingTopLeft: [390, 60], paddingBottomRight: [390, 60], maxZoom: 13 });
  }
  window.addEventListener('resize', () => map.invalidateSize());
})();
