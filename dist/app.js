(() => {
  const stations = window.MRT_STATIONS || [];
  const transitLabel = station => station?.line?.startsWith('BTS') ? 'BTS' : station?.line?.startsWith('MRT') ? 'MRT' : station?.line || '捷運';
  const transitColor = station => {
    const line = station?.line || '';
    if (line.includes('Sukhumvit')) return '#70a829';
    if (line.includes('Silom')) return '#008b57';
    if (line.includes('Blue')) return '#0a70af';
    if (line.includes('Purple')) return '#7045a1';
    if (line.includes('Pink')) return '#d72f81';
    if (line.includes('Yellow')) return '#c79a00';
    return '#526c60';
  };
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
  const propertyScoutById = new Map((window.BANGKOK_PROPERTYSCOUT_DETAILS || []).map(row => [Number(row.hipflatId), row]));
  const propertyScoutMarketById = new Map((window.BANGKOK_PROPERTYSCOUT_MARKETS || []).map(row => [Number(row.hipflatId), row]));
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
    const propertyScoutDetail = propertyScoutById.get(Number(project.id)) || {};
    const propertyScoutMarket = propertyScoutMarketById.get(Number(project.id)) || {};
    const citySummary = propertyHubCitySummaryById.get(Number(project.id)) || {};
    if (citySummary.sale) propertyHub.sale = citySummary.sale;
    if (citySummary.rent) propertyHub.rent = citySummary.rent;
    if (!propertyHub.sale && propertyScoutMarket.sale) propertyHub.sale = propertyScoutMarket.sale;
    if (!propertyHub.rent && propertyScoutMarket.rent) propertyHub.rent = propertyScoutMarket.rent;
    const osm = osmById.get(Number(project.id));
    const coordsFromProject = propertyHub.locationVerified && Number.isFinite(propertyHub.lat) && Number.isFinite(propertyHub.lng)
      ? false
      : project.locationVerified && Number.isFinite(project.lat) && Number.isFinite(project.lng);
    const coordsFromPropertyHub = propertyHub.locationVerified && Number.isFinite(propertyHub.lat) && Number.isFinite(propertyHub.lng);
    const coordsFromOsm = !coordsFromProject && osm;
    const coordsFromPropertyScout = !coordsFromPropertyHub && !coordsFromProject && !coordsFromOsm && propertyScoutDetail.locationVerified && Number.isFinite(propertyScoutDetail.lat) && Number.isFinite(propertyScoutDetail.lng);
    const lat = coordsFromPropertyHub ? propertyHub.lat : coordsFromProject ? project.lat : coordsFromOsm ? osm.lat : coordsFromPropertyScout ? propertyScoutDetail.lat : legacy?.lat ?? null;
    const lng = coordsFromPropertyHub ? propertyHub.lng : coordsFromProject ? project.lng : coordsFromOsm ? osm.lng : coordsFromPropertyScout ? propertyScoutDetail.lng : legacy?.lng ?? null;
    const locationVerified = Boolean(coordsFromPropertyHub || coordsFromProject || coordsFromOsm || coordsFromPropertyScout || legacy?.locationVerified);
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
    const rawCompletedYear = Number((propertyScoutMarket.locationVerificationSourceUrl && propertyScoutMarket.completedYear) || propertyHub.completedYear || project.completedYear || propertyScoutMarket.completedYear || legacy?.completedYear || 0);
    const completedYear = rawCompletedYear >= 2400 && rawCompletedYear <= 2700 ? rawCompletedYear - 543 : rawCompletedYear || null;
    return { ...legacy, ...project, ...propertyHub, lat, lng, locationVerified,
      locationSourceUrl: coordsFromPropertyHub ? propertyHub.locationSourceUrl : coordsFromProject ? project.locationSourceUrl : coordsFromOsm ? osm.sourceUrl : coordsFromPropertyScout ? propertyScoutDetail.locationSourceUrl : project.locationSourceUrl || legacy?.locationSourceUrl,
      locationVerificationSourceUrl: coordsFromPropertyScout ? (propertyScoutDetail.locationVerificationSourceUrl || propertyScoutMarket.locationVerificationSourceUrl) : null,
      locationSourceName: coordsFromPropertyHub ? propertyHub.locationSourceName : coordsFromOsm ? 'OpenStreetMap 建物／地址' : coordsFromPropertyScout ? propertyScoutDetail.locationSourceName : project.locationSourceName || legacy?.locationSourceName,
      sale: cleanSale, rent: cleanRent,
      completedYear,
      startedYear: propertyHub.startedYear || project.startedYear || propertyScoutMarket.startedYear || legacy?.startedYear || null,
      fee: propertyHub.fee || project.fee || (Number(propertyScoutMarket.fee) > 0 ? { rate: Number(propertyScoutMarket.fee), status: 'public', note: 'PropertyScout 專案頁公開管理費，請向管委會確認。', source: propertyScoutMarket.sourceUrl } : legacy?.fee || null),
      completedYearSourceUrl: propertyHub.completedYearSourceUrl || (propertyScoutMarket.completedYear ? propertyScoutMarket.sourceUrl : project.completedYearSourceUrl || legacy?.completedYearSourceUrl),
      nearestMrt, station: stations.find(item => item.id === nearestMrt?.stationId)?.name || project.station || legacy?.station || null,
      propertyHubProjectUrl: propertyHub.propertyHubProjectUrl || project.propertyHubProjectUrl || legacy?.propertyHubProjectUrl || null };
  });
  const hasSale = c => Number(c.sale?.minimumSqm) >= 10000 && Number(c.sale?.minimumSqm) <= 2000000;
  const hasRent = c => Number(c.rent?.minimumSqm) >= 100 && Number(c.rent?.minimumSqm) <= 20000;
  const hasYieldData = c => hasSale(c) && hasRent(c);
  const fmt = (n, digits = 0) => n == null || Number.isNaN(Number(n)) ? '—' : Number(n).toLocaleString('en-US', { maximumFractionDigits: digits });
  const sampleCount = market => market.countKind === 'propertyscout_market_summary' ? `${market.sourceName || 'PropertyScout 行情摘要'} · 房型行情統計 ${fmt(market.observedCount)} 戶` : market.countKind === 'matched_city_index' ? `PropertyHub 公開頁比對到 ${fmt(market.observedCount)} 筆掛牌` : market.observedCount ? `${fmt(market.observedCount)} 筆可見樣本 · 平台刊登 ${fmt(market.count)} 筆` : `${fmt(market.count)} 筆 · 全房型`;
  const money = n => n == null ? '—' : `฿${fmt(n)}`;
  const areaFor = c => Number(c.area?.min ?? c.area ?? 1);
  const areaLabel = c => c.area && typeof c.area === 'object' ? `${fmt(c.area.min, 1)}–${fmt(c.area.max, 1)} ㎡樓型範圍` : c.area ? `約 ${fmt(c.area, 1)} ㎡` : '';
  const compactMoney = n => n == null ? '—' : n >= 1000000 ? `฿${(n / 1000000).toFixed(2)}M` : `฿${fmt(n / 1000, 0)}K`;
  const sampleSource = (url, market) => url ? `<a class="sample-source" href="${esc(url)}" target="_blank" rel="noopener" aria-label="${market?.marketSummary ? '開啟Condo行情摘要' : '開啟這筆最低價物件'}" title="${market?.marketSummary ? '開啟Condo行情摘要' : '開啟這筆最低價物件'}" style="color:var(--green);font-weight:700;text-decoration:none;margin-left:4px">${market?.marketSummary ? '行情頁 ↗' : '物件 ↗'}</a>` : '<span class="sample-source-missing" title="目前沒有核對到這筆樣本的個別物件頁">物件連結待補</span>';
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
  const yieldStorageKey = 'bangkokCondoYieldInputs';
  const loadYieldInputs = () => { try { return JSON.parse(localStorage.getItem(yieldStorageKey) || '{}'); } catch { return {}; } };
  const saveYieldInputs = values => { try { localStorage.setItem(yieldStorageKey, JSON.stringify(values)); } catch {} };
  const markers = new Map();
  const stationMarkers = new Map();
  let walkingLine = null;
  const list = document.getElementById('projectList');
  const detail = document.getElementById('detailPanel');
  const labelFor = c => mode === 'sale' ? hasSale(c) ? `${fmt(c.sale.minimumSqm)}<small>${c.sale.marketSummary ? '房型均價低點 ฿/㎡' : '最低 ฿/㎡'}</small>` : '待補資料<small>售價/㎡</small>' : mode === 'rent' ? hasRent(c) ? `${fmt(c.rent.minimumSqm)}<small>${c.rent.marketSummary ? '房型均價低點 ฿/㎡/月' : '最低 ฿/㎡/月'}</small>` : '待補資料<small>租金/㎡/月</small>' : hasYieldData(c) ? `${yieldFor(c).toFixed(1)}<small>% 淨投報</small>` : '待補資料<small>售租資料不足</small>';
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
    const lineColor = transitColor(s);
    const marker = L.marker([s.lat, s.lng], { title: `${s.line} ${s.name} ${s.id}`, icon: L.divIcon({ className: 'station-icon', html: `<span style="--station-color:${lineColor}"><b>M</b><strong>${esc(s.name)}</strong><small>${esc(s.id)}</small></span>`, iconSize: [58, 30], iconAnchor: [14, 15] }), zIndexOffset: 500 }).addTo(map);
    marker.bindPopup(`<strong>${esc(s.name)}</strong><br><span class="station-popup-line"><i style="background:${lineColor}"></i>${esc(s.id)} · ${esc(s.line)}</span><br><a href="${esc(s.sourceUrl)}" target="_blank" rel="noopener">OpenStreetMap 站點來源 ↗</a>`);
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
      .replace(/(?:年)?投報率\s*(<=|>=|<|>|=|:)?\s*([\d,.]+)\s*[%％]/gi, (_, operator, amount) => `投報率${operator || '>='}${amount.replace(/,/g, '')}`)
      .replace(/(\d+)\s*房\s*[,，·]?\s*([\d,.]+)\s*萬\s*(?:元)?\s*(?:內|以下)/gi, (_, beds, amount) => `${beds}房售價<=${Number(amount.replace(/,/g, '')) * 10000}`)
      .replace(/(\d+)\s+房/g, '$1房');
    const aliases = {
      '年':'year','完工年':'year','完成年':'year','year':'year',
      '售價':'sale','售價/㎡':'sale','售價單價':'sale','sale':'sale','price':'sale',
      '總價':'saleTotal','房價':'saleTotal','售價總額':'saleTotal',
      '租金':'rent','月租':'rent','租金/㎡':'rent','月租/㎡':'rent','rent':'rent',
      '距離':'distance','步行':'distance','步行距離':'distance','mrt距離':'distance','distance':'distance',
      '投報':'yield','淨投報':'yield','投報率':'yield','年投報率':'yield','年報酬率':'yield','yield':'yield',
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
      const numericValue = rawValue.replace(/[฿,\s%％]/g, '').match(/^([\d.]+)(萬)?$/i);
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
    const read = id => { const value = document.getElementById(id)?.value; return value === '' || value == null ? null : Number(value); };
    const shown = condos.filter(c => matchesQuery(c) && matchesSidebarFilters(c, read));
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
  let budgetMax = null;
  function matchesSidebarFilters(c, read) {
    if (selectedBedrooms && !(Number(c.sale?.byBedroom?.[selectedBedrooms]?.minimum) > 0)) return false;
    const budget = budgetMax;
    const total = selectedBedrooms ? Number(c.sale?.byBedroom?.[selectedBedrooms]?.minimum) : Number(c.sale?.minimum);
    if (budget != null && (!Number.isFinite(total) || total > budget)) return false;
    const distance = Number(c.nearestMrt?.distanceKm ?? c.nearestMrt?.straightDistanceKm);
    const distanceMax = read('distanceMax');
    if (distanceMax != null && (!Number.isFinite(distance) || distance > distanceMax)) return false;
    const ranges = [
      ['saleMin','saleMax',Number(c.sale?.minimumSqm)],
      ['rentMin','rentMax',Number(c.rent?.minimumSqm)],
      ['yieldMin','yieldMax',yieldFor(c)],
      ['yearMin','yearMax',Number(c.completedYear)],
    ];
    for (const [minId, maxId, value] of ranges) {
      const min = read(minId), max = read(maxId);
      if ((min != null || max != null) && !Number.isFinite(value)) return false;
      if (min != null && value < min) return false;
      if (max != null && value > max) return false;
    }
    return true;
  }
  function renderList() {
    const shown = filtered();
    const visibleIds = new Set(shown.map(c => c.id));
    markers.forEach((marker, id) => {
      if (visibleIds.has(id) && !map.hasLayer(marker)) marker.addTo(map);
      else if (!visibleIds.has(id) && map.hasLayer(marker)) map.removeLayer(marker);
    });
    document.getElementById('resultCount').textContent = `${shown.length} 個 Condo`;
    document.querySelector('.count-pill').textContent = `全市 ${condos.length} 個 Condo`;
    const coverage = {
      locations: condos.filter(c => c.locationVerified && Number.isFinite(c.lat) && Number.isFinite(c.lng)).length,
      sale: condos.filter(hasSale).length,
      saleSamples: condos.filter(c => hasSale(c) && !c.sale.marketSummary).length,
      saleSummaries: condos.filter(c => hasSale(c) && c.sale.marketSummary).length,
      rent: condos.filter(hasRent).length,
      rentSamples: condos.filter(c => hasRent(c) && !c.rent.marketSummary).length,
      rentSummaries: condos.filter(c => hasRent(c) && c.rent.marketSummary).length,
      yield: condos.filter(hasYieldData).length,
    };
    document.getElementById('coverageSummary').textContent = `核實座標 ${coverage.locations.toLocaleString()} · 售樣本 ${coverage.saleSamples.toLocaleString()} + 摘要 ${coverage.saleSummaries.toLocaleString()} · 租樣本 ${coverage.rentSamples.toLocaleString()} + 摘要 ${coverage.rentSummaries.toLocaleString()} · 可估投報 ${coverage.yield.toLocaleString()}`;
    document.getElementById('listCount').textContent = String(shown.length).padStart(2, '0');
    list.innerHTML = shown.map((c, i) => { const nearestStation = stations.find(s => s.id === c.nearestMrt?.stationId); const located = Number.isFinite(c.lat) && Number.isFinite(c.lng); const roomMatch = query.match(/(\d+)\s*房/); const roomListing = roomMatch && c.sale?.byBedroom?.[roomMatch[1]]; const meta = nearestStation ? `${transitLabel(nearestStation)} ${nearestStation.name} · ${c.completedYear ? `完工 ${c.completedYear}` : c.locationVerified ? '座標已核實 · Hipflat 收錄' : 'Hipflat 收錄 · 位置待核'}` : c.locationVerified ? '座標已核實 · Hipflat 收錄' : 'Hipflat 收錄 · 位置待核'; return `<article class="project-card ${c.id === selectedId ? 'active' : ''}" data-id="${c.id}" tabindex="0" role="button" aria-label="查看 ${esc(c.name)}"><span class="rank">${String(i + 1).padStart(2, '0')}</span><div class="project-copy"><strong class="project-name">${esc(c.name)}</strong><span class="project-meta">${esc(meta)}</span><div class="project-values"><span>${roomListing ? `${roomMatch[1]}房總價` : '售/㎡'} <b>${roomListing ? compactMoney(roomListing.minimum) : fmt(c.sale?.minimumSqm)}</b></span><span>租/㎡/月 <b>${fmt(c.rent?.minimumSqm)}</b></span><span>${located ? (c.nearestMrt?.distanceKm != null ? '🚶' : '直線') : '座標'} <b>${located ? ((c.nearestMrt?.distanceKm ?? c.nearestMrt?.straightDistanceKm) ?? '—') + ' km' : '待補'}</b></span></div></div><span class="price-chip">${labelFor(c)}</span></article>`; }).join('') || '<p class="empty-state">沒有符合的 Condo</p>';
    list.querySelectorAll('.project-card').forEach(el => {
      const activate = () => select(Number(el.dataset.id));
      el.addEventListener('click', activate);
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
    });
  }
  function wireDetailSizeToggle() {
    const button = detail.querySelector('#toggleDetailSize');
    if (!button) return;
    button.addEventListener('click', () => {
      const compact = detail.classList.toggle('compact');
      button.setAttribute('aria-expanded', String(!compact));
      button.setAttribute('aria-label', compact ? '展開右側卡片' : '縮小右側卡片');
      button.title = compact ? '展開右側卡片' : '縮小右側卡片';
      button.textContent = compact ? '+' : '−';
    });
  }
  function renderDetail(c) {
    detail.classList.remove('compact');
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
      const projectAreaLabel = station ? `${station.name} ${transitLabel(station)} 周邊` : '曼谷 Condo 名單';
      const nearestLabel = station?.name || (nearest ? c.station : '待核實');
      const fallbackSale = hasSale(c) ? `<section class="detail-section"><p class="section-label">二手出售 <span>${c.sale.marketSummary ? 'PropertyScout 房型行情摘要' : '可核對掛牌樣本'}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.sale.marketSummary ? '專案起售價' : '最低售價'}</span><b class="metric-value">${money(c.sale.minimum)}</b><span class="metric-sub">${sampleSource(c.sale.minimumSourceUrl, c.sale)}</span></div><div class="metric"><span class="metric-label">${c.sale.marketSummary ? '房型均價低點 / ㎡' : '最低售價 / ㎡'}</span><b class="metric-value">${money(c.sale.minimumSqm)}</b><span class="metric-sub">${sampleSource(c.sale.minimumSqmSourceUrl, c.sale)}</span></div></div><div class="source-links"><a href="${esc(c.sale.source || phSale)}" target="_blank" rel="noopener">${esc(c.sale.sourceName || 'PropertyHub 出售來源')} ↗</a></div></section>` : c.hipflatSummary?.saleFrom ? `<section class="detail-section"><p class="section-label">Hipflat 起售參考 <span>專案摘要，非單筆掛牌</span></p><b class="metric-value">${money(c.hipflatSummary.saleFrom)}</b><div class="source-links"><a href="${esc(c.hipflatSummary.source || c.hipflatProjectUrl || hipflatSearch)}" target="_blank" rel="noopener">Hipflat 專案起售來源 ↗</a></div></section>` : '';
      const fallbackRent = hasRent(c) ? `<section class="detail-section rent-section"><p class="section-label">出租市場 <span>${c.rent.marketSummary ? 'PropertyScout 房型行情摘要' : '可核對掛牌樣本'}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.rent.marketSummary ? '專案起租價' : '最低月租'}</span><b class="metric-value">${money(c.rent.minimum)} / 月</b><span class="metric-sub">${sampleSource(c.rent.minimumSourceUrl, c.rent)}</span></div><div class="metric"><span class="metric-label">${c.rent.marketSummary ? '房型均價低點 / ㎡ / 月' : '最低租金 / ㎡ / 月'}</span><b class="metric-value">${money(c.rent.minimumSqm)}</b><span class="metric-sub">${sampleSource(c.rent.minimumSqmSourceUrl, c.rent)}</span></div></div><div class="source-links"><a href="${esc(c.rent.source || phRent)}" target="_blank" rel="noopener">${esc(c.rent.sourceName || 'PropertyHub 出租來源')} ↗</a></div></section>` : c.hipflatSummary?.rentFrom ? `<section class="detail-section rent-section"><p class="section-label">Hipflat 起租參考 <span>專案摘要，非單筆掛牌</span></p><b class="metric-value">${money(c.hipflatSummary.rentFrom)} / 月</b><div class="source-links"><a href="${esc(c.hipflatSummary.source || c.hipflatProjectUrl || hipflatSearch)}" target="_blank" rel="noopener">Hipflat 專案起租來源 ↗</a></div></section>` : '';
      detail.innerHTML = `<button class="close-detail" aria-label="關閉 Condo 資訊">×</button><button class="panel-size-toggle detail-size-toggle" id="toggleDetailSize" type="button" aria-expanded="true" aria-label="縮小右側卡片" title="縮小右側卡片">−</button><div class="detail-hero"><div class="detail-topline"><span class="station-pill">Hipflat · ${esc(projectAreaLabel)}</span><span class="age-pill">${c.completedYear ? `${esc(c.completedYear)} 完工` : c.locationVerified ? '完工年待補 · 座標已核實' : '完工年待補 · 位置待核'}</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.locationVerified ? 'Condo 座標已由公開專案或地圖資料頁核對。' : 'Condo 位置尚待核實。'} 完工年會在取得可靠資料後補上。</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div><section class="walk-section"><div class="walk-main"><span class="walk-symbol">🚇</span><div><span class="metric-label">${nearest?.distanceKm ? `最近${transitLabel(station)}站（步行路網估算）` : `最近${transitLabel(station)}站（直線距離）`}· ${esc(nearestLabel)}</span><strong>${c.locationVerified ? nearest?.distanceKm ? `${nearest.distanceKm} 公里步行路網距離` : `${nearest?.straightDistanceKm ?? '—'} 公里直線距離` : 'Condo 座標待核'}</strong><small>${c.locationVerified ? nearest?.distanceKm ? `步行約 ${Math.max(1, Number(nearest.minutes) || 0)} 分鐘 · Valhalla 路網估算` : '步行路網距離待計算' : '確認 Condo 座標後，再判定最近 MRT 與步行距離'}</small></div></div>${directionsUrl ? `<a class="route-button" href="${directionsUrl}" target="_blank" rel="noopener">Google Maps 步行導航 ↗</a>` : station ? '<button id="showWalkingRoute" class="route-button">查看 MRT 站點</button>' : ''}</section>${fallbackSale}${fallbackRent}<section class="detail-section"><p class="section-label">其他公開房源來源</p><div class="source-links"><a href="${hipflatSearch}" target="_blank" rel="noopener">Hipflat 專案與售租行情 ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a><a href="${phSale}" target="_blank" rel="noopener">PropertyHub 出售 ↗</a><a href="${phRent}" target="_blank" rel="noopener">PropertyHub 出租 ↗</a></div></section><section class="detail-section"><p class="section-label">投報率試算 <span>售租資料不足</span></p><p class="fee-note">補齊同一 Condo 的出售與出租掛牌後，會以每平方米最低單價計算。</p></section><section class="detail-section"><p class="section-label">資料來源</p><div class="source-links"><a href="${esc(c.discoveryUrl)}" target="_blank" rel="noopener">Hipflat 曼谷 Condo 清單 ↗</a>${c.hipflatProjectUrl ? `<a href="${esc(c.hipflatProjectUrl)}" target="_blank" rel="noopener">Hipflat 專案頁 ↗</a>` : ''}${c.locationVerified ? `<a href="${esc(c.locationSourceUrl)}" target="_blank" rel="noopener">座標來源 ↗</a>` : ''}${c.locationVerificationSourceUrl ? `<a href="${esc(c.locationVerificationSourceUrl)}" target="_blank" rel="noopener">地址交叉核實 ↗</a>` : ''}</div></section>`;
      detail.querySelector('.close-detail').addEventListener('click', () => { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); });
      wireDetailSizeToggle();
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
    const savedYield = loadYieldInputs()[c.id] || null;
    const calcPrice = Number(savedYield?.price || Math.round(Number(c.sale.minimumSqm || 0) * areaFor(c)));
    const calcRent = Number(savedYield?.rent || Math.round(Number(c.rent.minimumSqm || 0) * areaFor(c)));
    const calcArea = Number(savedYield?.area || areaFor(c));
    const calcDeductFee = savedYield?.deductFee ?? true;
    const calcDeductAgent = savedYield?.deductAgent ?? true;
    if (savedYield && calcPrice > 0 && calcArea > 0) {
      const annualFee = calcDeductFee && c.fee?.rate ? c.fee.rate * calcArea * 12 : 0;
      yieldOverrides.set(c.id, (calcRent * (12 - (calcDeductAgent ? 1 : 0)) - annualFee) / calcPrice * 100);
    }
    detail.classList.remove('empty');
    const saleLabel = c.sale.marketSummary ? '房型行情摘要' : 'PropertyHub 可見掛牌';
    const rentLabel = c.rent.marketSummary ? '房型行情摘要' : 'PropertyHub 可見掛牌';
    const saleLowLabel = c.sale.marketSummary ? '專案起售價' : '最低樣本';
    const saleLowSqmLabel = c.sale.marketSummary ? '房型均價低點' : '最低樣本';
    const rentLowLabel = c.rent.marketSummary ? '專案起租價' : '最低樣本';
    const rentLowSqmLabel = c.rent.marketSummary ? '房型均價低點' : '最低樣本';
    const yieldUsesSummary = c.sale.marketSummary || c.rent.marketSummary;
    detail.innerHTML = `<button class="close-detail" aria-label="關閉 Condo 資訊">×</button><button class="panel-size-toggle detail-size-toggle" id="toggleDetailSize" type="button" aria-expanded="true" aria-label="縮小右側卡片" title="縮小右側卡片">−</button>
      <div class="detail-hero"><div class="detail-topline"><span class="station-pill">最近${transitLabel(nearestStation)}站 ${esc(nearestStation?.name || c.station)}</span><span class="age-pill">${c.completedYear ? `${esc(c.completedYear)} 完工` : '完工年待補'}</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.beds ? `${c.beds} 房樣本 · ` : ''}${areaLabel(c) ? `${areaLabel(c)} · ` : ''}${c.units ? `${fmt(c.units)} 戶 · ` : ''}${c.floors ? esc(c.floors) : ''}</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div>
      <section class="walk-section"><div class="walk-main"><span class="walk-symbol">🚶</span><div><span class="metric-label">${nearest?.distanceKm != null ? `最近${transitLabel(nearestStation)}站（步行路網估算）` : `最近${transitLabel(nearestStation)}站（直線距離）`}· ${esc(nearestStation?.name || c.station)}</span><strong>${nearest?.distanceKm ?? nearest?.straightDistanceKm ?? '—'} 公里</strong><small>${nearest?.distanceKm != null ? `步行約 ${nearest.minutes} 分鐘 · 路網估算` : '步行路網距離待計算；目前顯示直線距離'}</small></div></div><button id="showWalkingRoute" class="route-button">${nearest?.shape ? '在地圖顯示路線' : 'Google Maps 步行導航 ↗'}</button><p class="fee-note">步行距離由 Valhalla 路網估算，取直線最近 30 個捷運站中最短路徑；實際入口距離可能不同。<a href="${esc(nearest?.sourceUrl || 'https://valhalla1.openstreetmap.de/')}" target="_blank" rel="noopener">路網資料 ↗</a></p></section>
      <section class="detail-section"><p class="section-label">二手出售 <span>${sampleCount(c.sale)} · ${esc(c.sale.asOf || '')}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.sale.marketSummary ? '房型平均售價' : c.sale.observedCount ? '樣本平均售價' : '平均售價'}</span><b class="metric-value">${money(c.sale.average)}</b><span class="metric-sub">${saleLowLabel} ${money(c.sale.minimum)} ${sampleSource(c.sale.minimumSourceUrl, c.sale)}</span></div><div class="metric"><span class="metric-label">${c.sale.marketSummary ? '房型平均售價 / ㎡' : '售價 / ㎡'}</span><b class="metric-value">${money(c.sale.averageSqm)}</b><span class="metric-sub">${saleLowSqmLabel} ${money(c.sale.minimumSqm)} / ㎡ ${sampleSource(c.sale.minimumSqmSourceUrl, c.sale)}</span></div></div>${roomListing?.sourceUrl ? `<p class="room-sample">${roomMatch[1]} 房最低掛牌 ${money(roomListing.minimum)} <a href="${esc(roomListing.sourceUrl)}" target="_blank" rel="noopener">物件 ↗</a></p>` : ''}<div class="unit-price"><span>來源：${saleLabel}</span><b><a href="${esc(saleSampleUrl)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section rent-section"><p class="section-label">出租市場 <span>${sampleCount(c.rent)} · ${esc(c.rent.asOf || '')}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.rent.marketSummary ? '房型平均月租' : c.rent.observedCount ? '樣本平均月租' : '平均月租'}</span><b class="metric-value">${money(c.rent.average)}</b><span class="metric-sub">${rentLowLabel} ${money(c.rent.minimum)} / 月 ${sampleSource(c.rent.minimumSourceUrl, c.rent)}</span></div><div class="metric"><span class="metric-label">${c.rent.marketSummary ? '房型平均租金 / ㎡' : '租金 / ㎡'}</span><b class="metric-value">${money(avgRate)}<small> / 月</small></b><span class="metric-sub">${rentLowSqmLabel} ${money(minRate)} / ㎡ / 月 ${sampleSource(c.rent.minimumSqmSourceUrl, c.rent)}</span></div></div><div class="unit-price"><span>來源：${rentLabel}</span><b><a href="${esc(rentSampleUrl)}" target="_blank" rel="noopener">查看來源 ↗</a></b></div></section>
      <section class="detail-section"><p class="section-label">管理費參考 <span>需向管委會確認</span></p>${feeText}${c.fee?.source ? `<div class="source-links"><a href="${esc(c.fee.source)}" target="_blank" rel="noopener">管理費來源 ↗</a></div>` : ''}</section>
      ${hasYieldData(c) ? `<section class="detail-section yield-section"><div class="yield-heading"><p class="section-label">年租金報酬試算 <span>${yieldUsesSummary ? '含房型行情摘要估算' : '最低單價為預設'}</span></p><div class="yield-value" id="yieldValue">${yieldFor(c).toFixed(2)}<small>% / 年</small></div></div><div class="yield-inputs"><div class="yield-input"><label for="yieldPrice">參考購入總價 (฿)</label><input id="yieldPrice" type="number" min="1" step="50000" value="${calcPrice}"></div><div class="yield-input"><label for="yieldRent">參考月租 (฿)</label><input id="yieldRent" type="number" min="0" step="500" value="${calcRent}"></div><div class="yield-input"><label for="yieldArea">室內面積 (㎡)</label><input id="yieldArea" type="number" min="1" step="0.1" value="${calcArea.toFixed(1)}"></div><div class="yield-input"><label>參考房型</label><input value="${c.beds || '—'} 房" readonly></div></div><div class="yield-options"><label><input id="deductFee" type="checkbox" ${calcDeductFee ? 'checked' : ''}> 扣除管理費</label><label><input id="deductAgent" type="checkbox" ${calcDeductAgent ? 'checked' : ''}> 扣除 1 個月仲介管理費</label><button type="button" id="saveYieldInputs" class="save-yield-button">儲存試算</button><span id="yieldSavedNote" class="yield-saved-note">${savedYield ? '已儲存於此裝置' : ''}</span></div><p class="formula-note">${yieldUsesSummary ? 'PropertyScout 行情摘要以不同房型平均單價估算，不能視為同一戶的售租配對。' : '預設以最低售價/㎡及最低租金/㎡估算。'}只有樓型面積範圍時，參考總價以最小面積示例，仍需用實際房源面積確認。已知管理費才會扣除，勾選時扣 1 個月租金作仲介費；未含稅、維修及交易成本。</p><div class="source-links"><a href="${esc(saleSampleUrl)}" target="_blank" rel="noopener">${c.sale.marketSummary ? '出售行情摘要來源' : '出售掛牌來源'} ↗</a><a href="${esc(rentSampleUrl)}" target="_blank" rel="noopener">${c.rent.marketSummary ? '出租行情摘要來源' : '出租掛牌來源'} ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a><a href="${hipflatSearch}" target="_blank" rel="noopener">Hipflat 專案行情 ↗</a></div></section>` : '<section class="detail-section yield-section"><p class="section-label">投報率試算 <span>售租資料不足</span></p><p class="fee-note">至少需要同一 Condo可核對的出售與出租每平方米單價，才能計算投報率。</p></section>'}
      <section class="detail-section"><p class="section-label">Condo 資訊 <span>${c.completedYear ? `${esc(c.completedYear)} 完工` : '完工年待補'} · ${c.startedYear ? `${esc(c.startedYear)} 起造` : '起造年待補'}</span></p><p class="fee-note">PropertyHub 來源為單筆公開掛牌；PropertyScout 來源為Condo房型行情摘要，連結會開啟該Condo行情頁。Hipflat 提供Condo清單與專案資料。</p><div class="source-links">${c.completedYearSourceUrl || c.propertyHubProjectUrl ? `<a href="${esc(c.completedYearSourceUrl || c.propertyHubProjectUrl)}" target="_blank" rel="noopener">完工與Condo資料來源 ↗</a>` : ''}${c.locationSourceUrl ? `<a href="${esc(c.locationSourceUrl)}" target="_blank" rel="noopener">座標來源 ↗</a>` : ''}${c.locationVerificationSourceUrl ? `<a href="${esc(c.locationVerificationSourceUrl)}" target="_blank" rel="noopener">地址交叉核實 ↗</a>` : ''}<a href="${hipflatSearch}" target="_blank" rel="noopener">搜尋此案 Hipflat 專案與售租行情 ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a></div></section>`;
    detail.querySelector('.close-detail').addEventListener('click', () => { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); });
    wireDetailSizeToggle();
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
    detail.querySelector('#saveYieldInputs')?.addEventListener('click', () => {
      const values = loadYieldInputs();
      values[c.id] = {
        price: Number(detail.querySelector('#yieldPrice').value),
        rent: Number(detail.querySelector('#yieldRent').value),
        area: Number(detail.querySelector('#yieldArea').value),
        deductFee: detail.querySelector('#deductFee').checked,
        deductAgent: detail.querySelector('#deductAgent').checked,
      };
      saveYieldInputs(values);
      detail.querySelector('#yieldSavedNote').textContent = '已儲存於此裝置';
    });
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
  document.getElementById('toggleExplorerSize').addEventListener('click', e => {
    const compact = document.querySelector('.explorer').classList.toggle('compact');
    e.currentTarget.setAttribute('aria-expanded', String(!compact));
    e.currentTarget.setAttribute('aria-label', compact ? '展開左側卡片' : '縮小左側卡片');
    e.currentTarget.title = compact ? '展開左側卡片' : '縮小左側卡片';
    e.currentTarget.textContent = compact ? '+' : '−';
  });
  const searchInput = document.getElementById('search');
  const budgetInput = document.getElementById('budgetInput');
  const filterGroups = [...document.querySelectorAll('.filter-toolbar .filter-group')];
  const closeFilterGroups = except => filterGroups.forEach(group => { if (group !== except) group.open = false; });
  const positionFilterPopover = group => {
    if (window.matchMedia('(max-width: 650px)').matches) return;
    const panel = group.querySelector('.filter-content');
    const bounds = group.getBoundingClientRect();
    panel.style.left = '0'; panel.style.right = 'auto';
    if (bounds.left + panel.offsetWidth > window.innerWidth - 12) {
      panel.style.left = 'auto'; panel.style.right = '0';
    }
  };
  filterGroups.forEach(group => {
    group.addEventListener('toggle', () => {
      if (!group.open) return;
      closeFilterGroups(group);
      positionFilterPopover(group);
    });
    group.addEventListener('focusout', () => setTimeout(() => {
      if (!group.contains(document.activeElement)) group.open = false;
    }, 0));
    group.querySelectorAll('input').forEach(input => input.addEventListener('keydown', event => {
      if (event.key === 'Enter') { event.preventDefault(); input.blur(); group.open = false; }
    }));
  });
  document.addEventListener('pointerdown', event => {
    if (!event.target.closest('.filter-toolbar .filter-group')) closeFilterGroups();
  });
  window.addEventListener('resize', () => filterGroups.forEach(group => { if (group.open) positionFilterPopover(group); }));
  const budgetWanValue = value => {
    const raw = String(value || '').trim().replace(/[฿,\s]/g, '');
    const match = raw.match(/^([\d.]+)(萬)?$/i);
    if (!match) return NaN;
    const amount = Number(match[1]);
    return raw.includes('萬') ? amount : amount / 10000;
  };
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
    button.closest('details').open = false;
    renderList();
  }));
  document.getElementById('applyBedroomFilter').addEventListener('click', () => {
    const amount = budgetInput.value.trim() === '' ? null : Number(budgetInput.value);
    budgetInput.setAttribute('aria-invalid', String(amount != null && (!Number.isFinite(amount) || amount <= 0)));
    if (amount != null && (!Number.isFinite(amount) || amount <= 0)) return;
    budgetMax = amount == null ? null : amount * 10000;
    document.getElementById('applyBedroomFilter').closest('details').open = false;
    renderList();
  });
  ['distanceMax','saleMin','saleMax','rentMin','rentMax','yieldMin','yieldMax','yearMin','yearMax'].forEach(id => {
    document.getElementById(id).addEventListener('input', () => renderList());
  });
  searchInput.addEventListener('input', e => {
    query = e.target.value.trim();
    const roomQuery = query.match(/(?:^|\s)([1-4])\s*房/);
    setBedroomSelection(roomQuery?.[1] || null);
    const budgetQuery = query.match(/[1-4]\s*房(?:售價|總價|房價)(?:<=|<)\s*([\d,.]+萬?)/);
    const naturalBudget = query.match(/[1-4]\s*房\s*([\d,.]+\s*萬)\s*(?:內|以下)/);
    if (budgetQuery) budgetInput.value = String(budgetWanValue(budgetQuery[1]) || '');
    else if (naturalBudget) budgetInput.value = String(budgetWanValue(naturalBudget[1]) || '');
    renderList();
  });
  document.getElementById('clearSearch').addEventListener('click', () => {
    searchInput.value = ''; query = ''; selectedBedrooms = null; budgetInput.removeAttribute('aria-invalid');
    setBedroomSelection(null);
    budgetMax = null;
    ['distanceMax','saleMin','saleMax','rentMin','rentMax','yieldMin','yieldMax','yearMin','yearMax'].forEach(id => { document.getElementById(id).value = ''; });
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



