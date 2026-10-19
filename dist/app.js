(() => {
  const stations = window.MRT_STATIONS || [];
  const stationsById = new Map(stations.map(station => [station.id, station]));
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
  const verifiedCoordinatesById = new Map((window.BANGKOK_VERIFIED_COORDINATES || []).map(row => [Number(row.hipflatId), row]));
  const marketCrosscheckById = new Map((window.BANGKOK_MARKET_CROSSCHECKS || []).map(row => [Number(row.hipflatId), row]));
  const propertyScoutById = new Map((window.BANGKOK_PROPERTYSCOUT_DETAILS || []).map(row => [Number(row.hipflatId), row]));
  const propertyScoutMarketById = new Map((window.BANGKOK_PROPERTYSCOUT_MARKETS || []).map(row => [Number(row.hipflatId), row]));
  const manualMarketById = new Map((window.BANGKOK_MANUAL_MARKET_SAMPLES || []).map(row => [Number(row.hipflatId), row]));
  const localListingsByProjectId = new Map((window.BANGKOK_LOCAL_LISTINGS || []).map(row => [Number(row.projectId), row]));
  const localListingFreshnessDays = 45;
  const localListingCutoff = Date.now() - localListingFreshnessDays * 24 * 60 * 60 * 1000;
  const hipflatProjects = window.BANGKOK_CONDO_CATALOGUE || window.BANGKOK_HIPFLAT_PROJECTS || [];
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
    const manualMarket = manualMarketById.get(Number(project.id)) || {};
    const verifiedCoordinate = verifiedCoordinatesById.get(Number(project.id)) || {};
    const citySummary = propertyHubCitySummaryById.get(Number(project.id)) || {};
    if (citySummary.sale) propertyHub.sale = citySummary.sale;
    if (citySummary.rent) propertyHub.rent = citySummary.rent;
    if (!propertyHub.sale && propertyScoutMarket.sale) propertyHub.sale = propertyScoutMarket.sale;
    if (!propertyHub.rent && propertyScoutMarket.rent) propertyHub.rent = propertyScoutMarket.rent;
    if (manualMarket.replaceSale === true && manualMarket.sale) propertyHub.sale = manualMarket.sale;
    if (manualMarket.replaceRent === true && manualMarket.rent) propertyHub.rent = manualMarket.rent;
    if (!propertyHub.sale && manualMarket.sale) propertyHub.sale = manualMarket.sale;
    if (!propertyHub.rent && manualMarket.rent) propertyHub.rent = manualMarket.rent;
    const osm = osmById.get(Number(project.id));
    const coordsFromProject = propertyHub.locationVerified && Number.isFinite(propertyHub.lat) && Number.isFinite(propertyHub.lng)
      ? false
      : project.locationVerified && Number.isFinite(project.lat) && Number.isFinite(project.lng);
    const coordsFromPropertyHub = propertyHub.locationVerified && Number.isFinite(propertyHub.lat) && Number.isFinite(propertyHub.lng);
    const coordsFromOsm = !coordsFromProject && osm;
    const coordsFromVerifiedSource = !coordsFromPropertyHub && !coordsFromProject && !coordsFromOsm && verifiedCoordinate.locationVerified && Number.isFinite(verifiedCoordinate.lat) && Number.isFinite(verifiedCoordinate.lng);
    const coordsFromPropertyScout = !coordsFromPropertyHub && !coordsFromProject && !coordsFromOsm && !coordsFromVerifiedSource && propertyScoutDetail.locationVerified && Number.isFinite(propertyScoutDetail.lat) && Number.isFinite(propertyScoutDetail.lng);
    const lat = coordsFromPropertyHub ? propertyHub.lat : coordsFromProject ? project.lat : coordsFromOsm ? osm.lat : coordsFromVerifiedSource ? verifiedCoordinate.lat : coordsFromPropertyScout ? propertyScoutDetail.lat : legacy?.lat ?? null;
    const lng = coordsFromPropertyHub ? propertyHub.lng : coordsFromProject ? project.lng : coordsFromOsm ? osm.lng : coordsFromVerifiedSource ? verifiedCoordinate.lng : coordsFromPropertyScout ? propertyScoutDetail.lng : legacy?.lng ?? null;
    const locationVerified = Boolean(coordsFromPropertyHub || coordsFromProject || coordsFromOsm || coordsFromPropertyScout || coordsFromVerifiedSource || legacy?.locationVerified);
    let nearestMrt = null;
    const walkingRoute = walkingById.get(Number(project.id));
    if (walkingRoute?.stationId) {
      nearestMrt = { ...walkingRoute };
    } else if (Number.isFinite(lat) && Number.isFinite(lng)) {
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
    } else {
      nearestMrt = project.nearestMrt || legacy?.nearestMrt || null;
    }
    const mergeVerifiedSamples = (market, manual) => {
      const additions = (manual?.samples || []).filter(sample => sample?.specialAsset !== true && !/(confirmed_unavailable|future_availability|update_over|over_(?:30d|1y|year)|stale)/i.test(String(sample?.listingStatus || '')));
      market = market || manual || null;
      if (!market) return null;
      const byUrl = new Map((market.samples || []).map(sample => [sample.url, sample]));
      additions.forEach(sample => { if (sample.url) byUrl.set(sample.url, sample); });
      // For each bedroom count with linked listing samples, make its displayed
      // minimum the cheapest current listing and keep that listing's area and URL.
      // This keeps the 2-bedroom filter and yield baseline on the same unit.
      const sampleBeds = sample => {
        const raw = sample?.beds ?? sample?.bedrooms;
        const numeric = Number(raw);
        if (Number.isFinite(numeric) && numeric > 0) return numeric;
        const label = `${sample?.roomType || ''} ${sample?.title || ''}`.toLowerCase();
        const word = label.match(/\b(one|two|three|four|five)\s+bed(?:\s*room)?s?\b/);
        if (word) return ({ one: 1, two: 2, three: 3, four: 4, five: 5 })[word[1]];
        const match = label.match(/(?:^|\D)(\d+)\s*(?:br\b|bed(?:\s*room)?s?\b|房)/i);
        return match ? Number(match[1]) : null;
      };
      const linkedRoomMinimums = new Map();
      [...byUrl.values()].filter(sample => !/(confirmed_unavailable|future_availability|update_over|over_(?:30d|1y|year)|stale)/i.test(String(sample?.listingStatus || '')))
        .forEach(sample => {
          const beds = sampleBeds(sample), price = Number(sample?.price), area = Number(sample?.area);
          if (!beds || !(price > 0) || !(area > 0) || !sample.url) return;
          const key = String(beds), current = linkedRoomMinimums.get(key);
          if (!current || price < current.minimum) linkedRoomMinimums.set(key, { minimum: price, area, minimumArea: area, priceSqm: price / area, minimumSqm: price / area, sourceUrl: sample.url, minimumSourceUrl: sample.url });
        });
      const byBedroom = { ...(market.byBedroom || {}) };
      linkedRoomMinimums.forEach((listing, beds) => { byBedroom[beds] = { ...(byBedroom[beds] || {}), ...listing }; });
      const direct = additions.filter(sample => sample.url && Number(sample.price) > 0 && Number(sample.area) > 0);
      const lowestTotal = direct.reduce((best, sample) => !best || Number(sample.price) < Number(best.price) ? sample : best, null);
      const lowestRate = direct.reduce((best, sample) => !best || Number(sample.price) / Number(sample.area) < Number(best.price) / Number(best.area) ? sample : best, null);
      const baseTotal = Number(market.minimum || 0);
      const baseRate = Number(market.minimumSqm || 0);
      // When a direct listing ties a summary's low, prefer the listing URL so
      // visitors can open the exact unit behind the displayed minimum.
      const nextTotal = lowestTotal && (!baseTotal || Number(lowestTotal.price) <= baseTotal) ? lowestTotal : null;
      const nextRate = lowestRate && (!baseRate || Number(lowestRate.price) / Number(lowestRate.area) <= baseRate) ? lowestRate : null;
      return { ...market, samples: [...byUrl.values()], byBedroom,
        ...(nextTotal ? { minimum: Number(nextTotal.price), minimumArea: Number(nextTotal.area), minimumSourceUrl: nextTotal.url, minimumSampleUpdated: nextTotal.updated || null } : {}),
        ...(nextRate ? { minimumSqm: Number((Number(nextRate.price) / Number(nextRate.area)).toFixed(2)), minimumSqmSourceUrl: nextRate.url, minimumSqmSampleUpdated: nextRate.updated || null } : {}) };
    };
    const mergedSale = mergeVerifiedSamples(propertyHub.sale || project.sale || legacy?.sale || null, manualMarket.sale);
    const mergedRent = mergeVerifiedSamples(propertyHub.rent || project.rent || legacy?.rent || null, manualMarket.rent);
    const localListings = (localListingsByProjectId.get(Number(project.id))?.listings || []).filter(row => {
      const observedAt = Date.parse(row.observedAt || '');
      return Number.isFinite(observedAt) && observedAt >= localListingCutoff && observedAt <= Date.now() + 24 * 60 * 60 * 1000;
    });
    const withLocalListings = (market, kind) => {
      const additions = localListings.filter(row => row.kind === kind && Number(row.price) > 0 && Number(row.area) > 0);
      if (!additions.length) return market;
      const base = market || {};
      const byUrl = new Map((base.samples || []).map(row => [row.url, row]));
      additions.forEach(row => byUrl.set(row.url, { id: row.id, price: row.price, area: row.area, beds: row.bedrooms, priceSqm: row.priceSqm, title: row.title, url: row.url, updated: row.observedAt, sourceName: row.sourceName }));
      const samples = [...byUrl.values()];
      const baseCount = Number(base.observedCount || base.count || 0);
      const freshAdditions = additions.filter(row => !(base.samples || []).some(sample => sample.url === row.url));
      const addedCount = freshAdditions.length;
      const mean = (oldMean, newValues, count) => {
        const values = newValues.map(Number).filter(value => value > 0);
        return values.length ? Math.round(((Number(oldMean || 0) * count) + values.reduce((sum, value) => sum + value, 0)) / (count + values.length)) : oldMean;
      };
      const newPriceSqm = freshAdditions.map(row => row.priceSqm);
      const minPriceSqm = Math.min(...newPriceSqm.filter(value => value > 0), Number(base.minimumSqm || Infinity));
      const minTotal = Math.min(...freshAdditions.map(row => Number(row.price)), Number(base.minimum || Infinity));
      const minSqmListing = freshAdditions.filter(row => Number(row.priceSqm) === minPriceSqm).sort((a, b) => a.price - b.price)[0];
      const minTotalListing = freshAdditions.find(row => Number(row.price) === minTotal);
      const byBedroom = { ...(base.byBedroom || {}) };
      freshAdditions.filter(row => Number(row.bedrooms) > 0).forEach(row => {
        const key = String(row.bedrooms), current = byBedroom[key] || {};
        const rowSqm = Number(row.priceSqm), rowPrice = Number(row.price);
        if (!Number(current.minimum) || rowPrice < Number(current.minimum)) byBedroom[key] = { ...current, minimum: rowPrice, area: Number(row.area), minimumArea: Number(row.area), priceSqm: rowSqm, minimumSqm: rowSqm, sourceUrl: row.url, minimumSourceUrl: row.url, count: Number(current.count || 0) + 1 };
        else byBedroom[key] = { ...current, count: Number(current.count || 0) + 1 };
      });
      return { ...base, samples, count: baseCount + addedCount, observedCount: baseCount + addedCount,
        average: mean(base.average, freshAdditions.map(row => row.price), baseCount),
        averageSqm: mean(base.averageSqm, freshAdditions.map(row => row.priceSqm), baseCount),
        minimum: minTotal, minimumSqm: minPriceSqm,
        byBedroom,
        minimumSourceUrl: minTotalListing?.url || base.minimumSourceUrl,
        minimumSqmSourceUrl: minSqmListing?.url || base.minimumSqmSourceUrl,
        minimumSampleUpdated: minTotalListing?.observedAt || base.minimumSampleUpdated,
        minimumSqmSampleUpdated: minSqmListing?.observedAt || base.minimumSqmSampleUpdated,
        sourceName: '本機每日房源提醒', asOf: additions.map(row => row.observedAt).sort().at(-1) || base.asOf };
    };
    const localSale = withLocalListings(mergedSale, 'sale');
    const localRent = withLocalListings(mergedRent, 'rent');
    const cleanSale = localSale && Number(localSale.minimumSqm) >= 10000 && Number(localSale.minimumSqm) <= 2000000 ? localSale : null;
    const cleanRent = localRent && Number(localRent.minimumSqm) >= 50 && Number(localRent.minimumSqm) <= 20000 ? localRent : null;
    const rawCompletedYear = Number((propertyScoutMarket.locationVerificationSourceUrl && propertyScoutMarket.completedYear) || propertyHub.completedYear || project.completedYear || propertyScoutMarket.completedYear || manualMarket.completedYear || legacy?.completedYear || 0);
    const completedYear = rawCompletedYear >= 2400 && rawCompletedYear <= 2700 ? rawCompletedYear - 543 : rawCompletedYear || null;
    return { ...legacy, ...project, ...propertyHub, lat, lng, locationVerified,
      manualSaleSamples: (manualMarket.sale?.samples || []).filter(sample => sample.specialAsset === true),
      verifiedMarketSamples: {
        sale: (manualMarket.sale?.samples || []).filter(sample => sample.specialAsset !== true && sample.url && Number(sample.price) > 0 && Number(sample.area) > 0),
        rent: (manualMarket.rent?.samples || []).filter(sample => sample.specialAsset !== true && sample.url && Number(sample.price) > 0 && Number(sample.area) > 0),
      },
      locationSourceUrl: coordsFromPropertyHub ? propertyHub.locationSourceUrl : coordsFromProject ? project.locationSourceUrl : coordsFromOsm ? osm.sourceUrl : coordsFromVerifiedSource ? verifiedCoordinate.sourceUrl : coordsFromPropertyScout ? propertyScoutDetail.locationSourceUrl : project.locationSourceUrl || legacy?.locationSourceUrl,
      locationVerificationSourceUrl: coordsFromVerifiedSource ? (verifiedCoordinate.corroborationSourceUrl || verifiedCoordinate.verificationSourceUrl) : coordsFromPropertyScout ? (propertyScoutDetail.locationVerificationSourceUrl || propertyScoutMarket.locationVerificationSourceUrl) : coordsFromPropertyHub ? propertyHub.locationVerificationSourceUrl || null : coordsFromOsm ? propertyScoutDetail.locationVerificationSourceUrl || propertyScoutMarket.locationVerificationSourceUrl || null : null,
      locationSourceName: coordsFromPropertyHub ? propertyHub.locationSourceName : coordsFromOsm ? 'OpenStreetMap 建物／地址' : coordsFromVerifiedSource ? verifiedCoordinate.sourceName : coordsFromPropertyScout ? propertyScoutDetail.locationSourceName : project.locationSourceName || legacy?.locationSourceName,
      sale: cleanSale, rent: cleanRent, localListings,
      completedYear,
      startedYear: propertyHub.startedYear || project.startedYear || propertyScoutMarket.startedYear || legacy?.startedYear || null,
      fee: propertyHub.fee || project.fee || manualMarket.fee || (Number(propertyScoutMarket.fee) > 0 ? { rate: Number(propertyScoutMarket.fee), status: 'public', note: 'PropertyScout 專案頁公開管理費，請向管委會確認。', source: propertyScoutMarket.sourceUrl } : legacy?.fee || null),
      completedYearSourceUrl: propertyHub.completedYearSourceUrl || (propertyScoutMarket.completedYear ? propertyScoutMarket.sourceUrl : manualMarket.completedYearSourceUrl || project.completedYearSourceUrl || legacy?.completedYearSourceUrl),
      nearestMrt, station: stationsById.get(nearestMrt?.stationId)?.name || project.station || legacy?.station || null,
      propertyHubProjectUrl: propertyHub.propertyHubProjectUrl || project.propertyHubProjectUrl || legacy?.propertyHubProjectUrl || null };
  });
  const condosById = new Map(condos.map(condo => [condo.id, condo]));
  const hasSale = c => Number(c.sale?.minimumSqm) >= 10000 && Number(c.sale?.minimumSqm) <= 2000000;
  const hasRent = c => Number(c.rent?.minimumSqm) >= 50 && Number(c.rent?.minimumSqm) <= 20000;
  const hasYieldData = c => hasSale(c) && hasRent(c);
  const fmt = (n, digits = 0) => n == null || Number.isNaN(Number(n)) ? '—' : Number(n).toLocaleString('en-US', { maximumFractionDigits: digits });
  const sampleCount = market => market.countKind === 'propertyscout_market_summary' ? `${market.sourceName || 'PropertyScout 行情摘要'} · 房型行情統計 ${fmt(market.observedCount)} 戶` : market.countKind === 'matched_city_index' ? `PropertyHub 公開頁比對到 ${fmt(market.observedCount)} 筆掛牌` : market.observedCount ? `${fmt(market.observedCount)} 筆可見樣本 · 平台刊登 ${fmt(market.count)} 筆` : `${fmt(market.count)} 筆 · 全房型`;
  const money = n => n == null ? '—' : `฿${fmt(n)}`;
  const areaFor = c => Number(c.area?.min ?? c.area ?? 1);
  const bedroomRows = market => {
    const summaries = Object.fromEntries((market?.bedroomRates || []).filter(row => Number(row.beds) > 0).map(row => {
      const average = Number(row.average || 0), averageSqm = Number(row.averageSqm || 0);
      // Bedroom-rate rows are averages, not minimum listings. Leave minimum
      // unset unless a source explicitly supplies a verified minimum record.
      return [String(row.beds), { ...row, average, averageSqm, area: average > 0 && averageSqm > 0 ? average / averageSqm : 0, marketSummary: true }];
    }));
    // Preserve room types from market summaries while letting a verified
    // same-bedroom listing supply the lower linked purchase price and area.
    return Object.fromEntries(Object.entries({ ...summaries, ...(market?.byBedroom || {}) }).map(([beds, row]) => [
      beds, { ...(summaries[beds] || {}), ...row },
    ]));
  };
  const bedroomCountForSample = sample => {
    const raw = sample?.beds ?? sample?.bedrooms;
    const numeric = Number(raw);
    if (Number.isFinite(numeric) && numeric > 0) return numeric;
    const roomType = String(sample?.roomType || '').toLowerCase().replace(/[_-]+/g, ' ');
    const wordCount = roomType.match(/\b(one|two|three|four|five)\s+bed(?:\s*room)?s?\b/);
    if (wordCount) return ({ one: 1, two: 2, three: 3, four: 4, five: 5 })[wordCount[1]];
    const label = `${roomType} ${sample?.title || ''}`;
    const match = label.match(/(?:^|\D)(\d+)\s*(?:br\b|bed(?:\s*room)?s?\b|房)/i);
    return match ? Number(match[1]) : null;
  };
  const yieldDefaultsFor = (c, beds = null) => {
    const saleRooms = bedroomRows(c.sale), rentRooms = bedroomRows(c.rent);
    const saleSamples = c.sale?.samples || [];
    const rentSamples = c.rent?.samples || [];
    // Fresh asking-price samples remain useful when availability has not been
    // independently confirmed. Exclude unavailable, future-dated, and stale
    // listings, while retaining recently updated listings marked unconfirmed.
    const yieldSampleIsCurrent = sample => !/(confirmed_unavailable|future_availability|update_over|over_(?:30d|1y|year)|stale)/i.test(String(sample?.listingStatus || ''));
    const yieldSourceIsCurrent = (samples, url) => {
      const linkedSample = samples.find(sample => sample.url === url);
      return !linkedSample || yieldSampleIsCurrent(linkedSample);
    };
    saleSamples.filter(yieldSampleIsCurrent).forEach(sample => {
      const count = bedroomCountForSample(sample);
      if (!count || !(Number(sample.price) > 0) || !(Number(sample.area) > 0)) return;
      const key = String(count), current = saleRooms[key] || {};
      // A direct listing is the authoritative source for both total price and
      // its matching floor area. Prefer it on ties so a summary cannot leave a
      // different unit's area attached to the same minimum price.
      if (!(Number(current.minimum) > 0) || Number(sample.price) <= Number(current.minimum)) {
        saleRooms[key] = { ...current, beds: count, minimum: Number(sample.price), minimumArea: Number(sample.area), area: Number(sample.area), minimumSourceUrl: sample.url, sourceUrl: sample.url };
      }
    });
    rentSamples.filter(yieldSampleIsCurrent).forEach(sample => {
      const count = bedroomCountForSample(sample), price = Number(sample.price), area = Number(sample.area);
      if (!count || !(price > 0) || !(area > 0) || !sample.url) return;
      const key = String(count), current = rentRooms[key] || {}, sampleRate = price / area;
      const summaryUrl = current.minimumSqmSourceUrl || current.sourceUrl;
      const currentRate = yieldSourceIsCurrent(rentSamples, summaryUrl) ? Number(current.minimumSqm || current.averageSqm || (current.minimum && current.area ? current.minimum / current.area : 0)) : 0;
      if (!(currentRate > 0) || current.marketSummary === true || sampleRate < currentRate) {
        rentRooms[key] = { ...current, beds: count, minimum: price, area, minimumSqm: sampleRate, minimumSourceUrl: sample.url, minimumSqmSourceUrl: sample.url, sourceUrl: sample.url, marketSummary: false };
      }
    });
    const roomOptions = Object.entries(saleRooms).filter(([, row]) => Number(row.minimum || row.average) > 0);
    // Prefer the lowest two-bedroom sale whenever one is available. If the
    // project has no two-bedroom sale, use the lowest bedroom count with both
    // sale and rent data rather than mixing different room types.
    const comparableRoomOptions = Object.keys(saleRooms)
      .filter(key => Number(saleRooms[key]?.minimum || saleRooms[key]?.average) > 0
        && Number(rentRooms[key]?.minimumSqm || rentRooms[key]?.averageSqm || 0) > 0)
      .sort((a, b) => Number(a) - Number(b));
    const defaultRoom = saleRooms['2'] && Number(saleRooms['2']?.minimum || saleRooms['2']?.average) > 0
      ? '2' : comparableRoomOptions[0] || null;
    // An explicit room choice must never silently fall back to another room type.
    const chosenBeds = beds ? (saleRooms[String(beds)] ? String(beds) : null) : defaultRoom;
    if ((beds && !chosenBeds) || (!beds && !chosenBeds)) return { price: 0, area: 0, rent: 0, beds: String(beds || '2'), isRoomStart: false, isRoomAverage: false, saleSourceUrl: null, rentSourceUrl: null, roomOptions };
    const room = chosenBeds ? saleRooms[chosenBeds] : null;
    const roomListings = chosenBeds ? saleSamples.filter(sample => yieldSampleIsCurrent(sample) && bedroomCountForSample(sample) === Number(chosenBeds) && Number(sample.price) > 0 && Number(sample.area) > 0 && sample.url) : [];
    // Use the lowest verified total price for the selected bedroom count, including two-bedroom listings.
    // Keep price, floor area, and source URL from the same listing together;
    // bedroom summaries are valid only when they provide all three.
    const roomSummaryMinimum = Number(room?.minimum || 0);
    // Bedroom summary minima are usable only when the data explicitly binds
    // that price, area and URL to one individual listing. Generic `area` fields
    // can describe a room-type average and must not be paired with a minimum.
    const summaryArea = Number(room?.minimumArea || 0);
    const summaryUrl = room?.minimumSourceUrl || room?.sourceUrl || null;
    const isDirectListingUrl = url => typeof url === 'string' && /\/(?:ads|listings|property|property-for-sale|property-for-rent)\//i.test(url);
    // Only use a bedroom summary as a candidate when its source points to an
    // individual listing. A project or market-summary page can have a minimum
    // value, but it cannot prove which two-bedroom unit supplied that price.
    const summaryCandidate = roomSummaryMinimum > 0 && summaryArea > 0 && isDirectListingUrl(summaryUrl) && yieldSourceIsCurrent(saleSamples, summaryUrl)
      ? { price: roomSummaryMinimum, area: summaryArea, url: summaryUrl }
      : null;
    const listingCandidates = roomListings.map(sample => ({ price: Number(sample.price), area: Number(sample.area), url: sample.url }));
    // Compare the room summary's lowest linked listing with the individual
    // samples. The summary can include a cheaper two-bedroom listing that is
    // not present in the limited sample array, so don't ignore it just because
    // another same-room listing is available.
    const roomSample = [...listingCandidates, ...(summaryCandidate ? [summaryCandidate] : [])]
      .filter(sample => Number(sample.price) > 0 && Number(sample.area) > 0 && sample.url)
      .sort((a, b) => Number(a.price) - Number(b.price) || Number(Boolean(b.url)) - Number(Boolean(a.url)))[0] || null;
    const selectedRoomMinimum = Number(roomSample?.price || 0);
    // A two-bedroom estimate must be backed by the lowest linked listing.
    // Do not label an average as the lowest total when the listing is missing.
    const roomAveragePrice = chosenBeds !== '2' && !selectedRoomMinimum && Number(room?.average) > 0 ? Number(room.average) : 0;
    const roomAverageArea = roomAveragePrice > 0 && Number(room?.averageSqm) > 0 ? roomAveragePrice / Number(room.averageSqm) : 0;
    const lowestSaleSample = (c.sale?.samples || []).find(sample => sample.url === c.sale?.minimumSourceUrl)
      || (c.sale?.samples || []).find(sample => Number(sample.price) === Number(c.sale?.minimum));
    // When the bedroom summary points to an individual listing, use that
    // listing's price and floor area together so ROI never mixes two units.
    // Fall back to the bedroom summary only when its listing is absent from
    // the cached sample array (for example, a summary-only market source).
    const salePrice = Number(selectedRoomMinimum || roomAveragePrice || (!chosenBeds ? c.sale?.minimum : 0) || 0);
    const saleArea = Number((roomSample?.area) || (!selectedRoomMinimum ? roomAverageArea : null) || (!chosenBeds ? c.sale?.minimumArea || lowestSaleSample?.area : null) || 0);
    const roomRent = chosenBeds ? rentRooms[chosenBeds] : null;
    const roomRentUrl = roomRent?.minimumSqmSourceUrl || roomRent?.sourceUrl;
    const roomRentRate = roomRent && yieldSourceIsCurrent(rentSamples, roomRentUrl) ? Number(roomRent.minimumSqm || (roomRent.minimum && roomRent.area ? roomRent.minimum / roomRent.area : 0) || roomRent.averageSqm || 0) : 0;
    const rentFallbackBed = chosenBeds && !(roomRentRate > 0)
      ? Object.entries(rentRooms).filter(([, row]) => Number(row.minimumSqm || row.averageSqm || 0) > 0).sort((a, b) => Number(a[1].minimumSqm || a[1].averageSqm || 0) - Number(b[1].minimumSqm || b[1].averageSqm || 0))[0]?.[0] || null
      : null;
    // Use the room-type low rent rate per sqm with the area of the lowest-
    // priced sale listing. Fall back to the room average only when no low rate exists.
    // A bedroom-specific yield must use a rent rate for the same bedroom count.
    // Do not silently substitute another room type or a project-wide minimum.
    const rentRate = roomRentRate;
    return {
      price: salePrice || Math.round(Number(c.sale?.minimumSqm || 0) * saleArea),
      area: saleArea,
      rent: Math.round(rentRate * saleArea),
      beds: chosenBeds || room?.beds || c.beds || null,
      isRoomStart: Boolean(selectedRoomMinimum), isRoomAverage: Boolean(!selectedRoomMinimum && roomAveragePrice),
      saleSourceUrl: roomSample?.url || (!room ? c.sale?.minimumSourceUrl : null),
      rentSourceUrl: roomRent?.minimumSqmSourceUrl || roomRent?.sourceUrl || c.rent?.minimumSqmSourceUrl || c.rent?.minimumSourceUrl,
      rentFallback: Boolean(rentFallbackBed), rentFallbackBeds: rentFallbackBed,
      roomOptions,
    };
  };
  const areaLabel = c => c.area && typeof c.area === 'object' ? `${fmt(c.area.min, 1)}–${fmt(c.area.max, 1)} ㎡樓型範圍` : c.area ? `約 ${fmt(c.area, 1)} ㎡` : '';
  const compactMoney = n => n == null ? '—' : n >= 1000000 ? `฿${(n / 1000000).toFixed(2)}M` : `฿${fmt(n / 1000, 0)}K`;
  const sampleSource = (url, market) => {
    if (!url) return '<span class="sample-source-missing" title="目前沒有核對到這筆樣本的個別物件頁">物件連結待補</span>';
    const sourceSample = market?.samples?.find(sample => sample.url === url);
    const isSummaryLink = market?.marketSummary === true && !sourceSample;
    const updated = isSummaryLink ? '' : sourceSample?.updated || (String(url) === String(market?.minimumSqmSourceUrl || '')
      ? market?.minimumSqmSampleUpdated : market?.minimumSampleUpdated);
    const dateLabel = updated ? ` · 更新 ${esc(String(updated).slice(0, 10))}` : '';
    const listingStatus = sourceSample?.listingStatus;
    const availabilityLabel = listingStatus === 'future_availability' ? ` · 預計 ${esc(sourceSample?.availableFrom || '未提供日期')} 開始出租` : listingStatus === 'confirmed_unavailable' ? ' · 目前不可租，歷史樣本' : listingStatus === 'availability_unconfirmed_stale_over_year' ? ' · 歷史樣本，超過一年未更新，現況待確認' : listingStatus === 'availability_unconfirmed_update_over_30d' ? ' · 超過 30 日未更新，現況待確認' : listingStatus === 'availability_unconfirmed_update_under_30d' ? ' · 30 日內更新，現況仍請確認' : listingStatus === 'availability_unconfirmed_date_unknown' ? ' · 未提供更新日，現況待確認' : listingStatus === 'availability_unconfirmed_date_conflict' ? ' · 刊登租期日期矛盾，現況待確認' : '';
    const label = isSummaryLink ? '行情頁 ↗' : '物件 ↗';
    return `<a class="sample-source" href="${esc(url)}" target="_blank" rel="noopener" aria-label="${isSummaryLink ? '開啟Condo行情摘要' : '開啟這筆最低價物件'}" title="${updated ? `房源更新日 ${esc(String(updated).slice(0, 10))}` : isSummaryLink ? '開啟Condo行情摘要' : '開啟這筆最低價物件'}${availabilityLabel}" style="color:var(--green);font-weight:700;text-decoration:none;margin-left:4px">${label}${dateLabel}${availabilityLabel}</a>`;
  };
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
  // Refresh auto-generated baselines when new exact listings arrive while
  // keeping values the user intentionally edited and saved.
  // Recompute generated baselines against the lowest linked same-bedroom sale
  // and keep its area paired with that same listing. User-edited values that
  // do not match an old generated baseline remain intact.
  const yieldStorageKey = 'bangkokCondoYieldInputsV147';
  const loadYieldInputs = () => {
    try {
      const current = localStorage.getItem(yieldStorageKey);
      if (current) return JSON.parse(current);
      let previous = {};
      for (let version = 146; version >= 5; version--) {
        const stored = localStorage.getItem(`bangkokCondoYieldInputsV${version}`);
        if (stored) { previous = JSON.parse(stored); break; }
      }
      const recalculated = {};
      condos.forEach(c => {
        const old = previous[c.id] || {};
        const previousBeds = String(old.beds || '2');
        // Migrate generated values to the current default room policy (lowest
        // two-bedroom sale when available); customized values remain intact.
        const defaults = yieldDefaultsFor(c, null);
        const oldSaleRoom = c.sale?.byBedroom?.[previousBeds] || {};
        const oldRentRoom = c.rent?.byBedroom?.[previousBeds] || {};
        const saleCandidates = [
          ...Object.values(bedroomRows(c.sale)).flatMap(row => [
            { price: Number(row.minimum), area: Number(row.area) },
            { price: Number(row.average), area: Number(row.average) / Number(row.averageSqm) },
          ]),
          ...(c.sale?.samples || []).filter(sample => bedroomCountForSample(sample) === Number(previousBeds)).map(sample => ({ price: Number(sample.price), area: Number(sample.area) })),
          { price: Number(c.sale?.minimum), area: Number(c.sale?.minimumArea) },
        ].filter(candidate => candidate.price > 0 && candidate.area > 0);
        const rentRates = [
          ...Object.values(bedroomRows(c.rent)).flatMap(row => [Number(row.minimumSqm), Number(row.averageSqm), Number(row.minimum) / Number(row.area)]),
          Number(oldRentRoom.minimumSqm), Number(oldRentRoom.averageSqm),
          ...(c.rent?.samples || []).filter(sample => bedroomCountForSample(sample) === Number(previousBeds) && Number(sample.price) > 0 && Number(sample.area) > 0).map(sample => Number(sample.price) / Number(sample.area)),
          Number(c.rent?.minimumSqm),
        ].filter(rate => rate > 0);
        const oldSaleMatches = saleCandidates.some(candidate => Number(old.price) === candidate.price && Number(old.area) === candidate.area);
        // Older saved baselines sometimes paired a valid low total with a
        // different listing's area. Recognize that generated pattern so the
        // migration can replace it with the price and area from one listing.
        const knownSalePrices = saleCandidates.map(candidate => candidate.price);
        const knownSaleAreas = [
          ...saleCandidates.map(candidate => candidate.area),
          Number(oldSaleRoom.area), Number(c.sale?.minimumArea),
        ].filter(area => area > 0);
        const oldSaleMatchesGeneratedParts = knownSalePrices.includes(Number(old.price)) && knownSaleAreas.includes(Number(old.area));
        const oldRentMatches = rentRates.some(rate => Math.abs(Number(old.rent) - Math.round(rate * Number(old.area))) <= 1);
        const wasAutoBaseline = (oldSaleMatches || oldSaleMatchesGeneratedParts) && oldRentMatches;
        if (!(Number(defaults.price) > 0) || !(Number(defaults.area) > 0) || !(Number(defaults.rent) > 0)) {
          if (old.price > 0 && old.rent > 0 && old.area > 0 && !wasAutoBaseline) recalculated[c.id] = old;
          return;
        }
        // Prior versions could save a two-bedroom baseline from a linked
        // listing that was not the cheapest in that room type. Re-select the
        // current lowest two-bedroom listing when the saved amount matches a
        // known two-bedroom listing price, while preserving custom amounts.
        const knownTwoBedroomPrices = [
          Number(c.sale?.byBedroom?.['2']?.minimum),
          ...(c.sale?.samples || []).filter(sample => bedroomCountForSample(sample) === 2).map(sample => Number(sample.price)),
        ].filter(price => price > 0);
        const savedMatchesTwoBedroomListing = previousBeds === '2' && knownTwoBedroomPrices.includes(Number(old.price));
        const useRefreshedBaseline = !old.price || wasAutoBaseline || savedMatchesTwoBedroomListing;
        recalculated[c.id] = {
          price: useRefreshedBaseline ? defaults.price : Number(old.price),
          rent: useRefreshedBaseline ? defaults.rent : Number(old.rent),
          area: useRefreshedBaseline ? defaults.area : Number(old.area),
          beds: useRefreshedBaseline ? String(defaults.beds || '2') : previousBeds,
          deductFee: old.deductFee ?? true,
          deductAgent: old.deductAgent ?? true,
        };
      });
      localStorage.setItem(yieldStorageKey, JSON.stringify(recalculated));
      return recalculated;
    } catch { return {}; }
  };
  const saveYieldInputs = values => { try { localStorage.setItem(yieldStorageKey, JSON.stringify(values)); } catch {} };
  const calculateNetYield = (c, { price, rent, area, deductFee = true, deductAgent = true }) => {
    const purchasePrice = Number(price), monthlyRent = Number(rent), floorArea = Number(area);
    if (!(purchasePrice > 0) || !(floorArea > 0)) return 0;
    const annualRent = monthlyRent * (12 - (deductAgent ? 1 : 0));
    const annualCommonFee = deductFee ? Number(c.fee?.rate || 0) * floorArea * 12 : 0;
    const result = (annualRent - annualCommonFee) / purchasePrice * 100;
    return Number.isFinite(result) ? result : 0;
  };
  const markers = new Map();
  let currentShown = [];
  const MAX_VISIBLE_MARKERS = 500;
  const LIST_PAGE_SIZE = 60;
  let visibleProjectCount = LIST_PAGE_SIZE;
  const stationMarkers = new Map();
  let walkingLine = null;
  const list = document.getElementById('projectList');
  const detail = document.getElementById('detailPanel');
  const labelFor = c => mode === 'sale' ? hasSale(c) ? `${fmt(c.sale.minimumSqm)}<small>${c.sale.marketSummary ? '房型均價低點 ฿/㎡' : '最低 ฿/㎡'}</small>` : '待補資料<small>售價/㎡</small>' : mode === 'rent' ? hasRent(c) ? `${fmt(c.rent.minimumSqm)}<small>${c.rent.marketSummary ? '房型均價低點 ฿/㎡/月' : '最低 ฿/㎡/月'}</small>` : '待補資料<small>租金/㎡/月</small>' : Number.isFinite(yieldFor(c)) ? `${yieldFor(c).toFixed(1)}<small>% 淨投報</small>` : '待補資料<small>兩房售價樣本不足</small>';
  function yieldFor(c) {
    if (!hasYieldData(c)) return null;
    if (yieldOverrides.has(c.id)) return yieldOverrides.get(c.id);
    const saved = loadYieldInputs()[c.id];
    const defaults = yieldDefaultsFor(c, saved?.beds || null);
    const price = Number(saved?.price ?? defaults.price);
    const rent = Number(saved?.rent ?? defaults.rent);
    const area = Number(saved?.area ?? defaults.area);
    if (!(price > 0) || !(rent > 0) || !(area > 0) || defaults.rentFallback) return null;
    return calculateNetYield(c, { price, rent, area, deductFee: saved?.deductFee ?? true, deductAgent: saved?.deductAgent ?? true });
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
  function syncVisibleMarkers(extraId = selectedId) {
    const bounds = map.getBounds();
    const center = map.getCenter();
    const candidates = currentShown.filter(c => Number.isFinite(c.lat) && Number.isFinite(c.lng) && bounds.contains([c.lat, c.lng]));
    candidates.sort((a, b) => Math.hypot(a.lat - center.lat, (a.lng - center.lng) * Math.cos(center.lat * Math.PI / 180)) - Math.hypot(b.lat - center.lat, (b.lng - center.lng) * Math.cos(center.lat * Math.PI / 180)));
    const visible = new Set(candidates.slice(0, MAX_VISIBLE_MARKERS).map(c => c.id));
    if (extraId != null) {
      const selected = condosById.get(extraId);
      if (selected && Number.isFinite(selected.lat) && Number.isFinite(selected.lng) && bounds.contains([selected.lat, selected.lng])) visible.add(extraId);
    }
    markers.forEach((marker, id) => {
      if (visible.has(id) && !map.hasLayer(marker)) marker.addTo(map);
      else if (!visible.has(id) && map.hasLayer(marker)) map.removeLayer(marker);
    });
    visible.forEach(id => {
      if (markers.has(id)) return;
      const condo = condosById.get(id);
      if (!condo) return;
      const marker = L.marker([condo.lat, condo.lng], { icon: icon(condo, id === selectedId) }).addTo(map);
      marker.on('click', () => select(condo.id));
      markers.set(id, marker);
    });
  }
  map.on('moveend', () => syncVisibleMarkers());
  function matchesQuery(c) {
    if (!query.trim()) return true;
    const stationName = stationsById.get(c.nearestMrt?.stationId)?.name || c.station || '';
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
    const lowriseMode = document.getElementById('lowriseOnly')?.value || 'all';
    const shown = condos.filter(c => matchesQuery(c) && matchesSidebarFilters(c, read, lowriseMode));
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
  const lowriseSummary = document.querySelector('#lowriseOnly')?.closest('.filter-group')?.querySelector('summary span');
  const updateLowriseSummary = () => {
    if (!lowriseSummary) return;
    const mode = document.getElementById('lowriseOnly').value;
    const knownFloors = condos.filter(c => Number.isFinite(Number(c.floors)) && c.floors !== '' && c.floors != null);
    const matches = knownFloors.filter(c => mode === 'yes' ? Number(c.floors) <= 8 : mode === 'no' ? Number(c.floors) > 8 : true).length;
    lowriseSummary.textContent = mode === 'yes' ? `8 樓以下 · ${matches}` : mode === 'no' ? `超過 8 樓 · ${matches}` : `樓層不限 · ${matches}`;
  };
  let budgetMax = null;
  function matchesSidebarFilters(c, read, lowriseMode) {
    const floorCount = c.floors == null || c.floors === '' ? NaN : Number(c.floors);
    if (lowriseMode !== 'all' && !Number.isFinite(floorCount)) return false;
    if (lowriseMode === 'yes' && floorCount > 8) return false;
    if (lowriseMode === 'no' && floorCount <= 8) return false;
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
    currentShown = shown;
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
    const cards = shown.slice(0, visibleProjectCount).map((c, i) => { const nearestStation = stationsById.get(c.nearestMrt?.stationId); const located = Number.isFinite(c.lat) && Number.isFinite(c.lng); const roomMatch = query.match(/(\d+)\s*房/); const roomListing = roomMatch && c.sale?.byBedroom?.[roomMatch[1]]; const meta = nearestStation ? `${transitLabel(nearestStation)} ${nearestStation.name} · ${c.completedYear ? `完工 ${c.completedYear}` : c.locationVerified ? '座標已核實 · Hipflat 收錄' : 'Hipflat 收錄 · 位置待核'}` : c.locationVerified ? '座標已核實 · Hipflat 收錄' : 'Hipflat 收錄 · 位置待核'; return `<article class="project-card ${c.id === selectedId ? 'active' : ''}" data-id="${c.id}" tabindex="0" role="button" aria-label="查看 ${esc(c.name)}"><span class="rank">${String(i + 1).padStart(2, '0')}</span><div class="project-copy"><strong class="project-name">${esc(c.name)}</strong><span class="project-meta">${esc(meta)}</span><div class="project-values"><span>${roomListing ? `${roomMatch[1]}房總價` : '售/㎡'} <b>${roomListing ? compactMoney(roomListing.minimum) : fmt(c.sale?.minimumSqm)}</b></span><span>租/㎡/月 <b>${fmt(c.rent?.minimumSqm)}</b></span><span>${located ? (c.nearestMrt?.distanceKm != null ? '🚶' : '直線') : '座標'} <b>${located ? ((c.nearestMrt?.distanceKm ?? c.nearestMrt?.straightDistanceKm) ?? '—') + ' km' : '待補'}</b></span></div></div><span class="price-chip">${labelFor(c)}</span></article>`; }).join('');
    const more = shown.length > visibleProjectCount ? `<button class="load-more-projects" type="button">載入更多 Condo（${(shown.length - visibleProjectCount).toLocaleString()}）</button>` : '';
    list.innerHTML = cards + more || '<p class="empty-state">沒有符合的 Condo</p>';
    syncVisibleMarkers();
  }
  list.addEventListener('click', event => {
    if (event.target.closest('.load-more-projects')) { const scrollTop = list.scrollTop; visibleProjectCount = Math.min(currentShown.length, visibleProjectCount + LIST_PAGE_SIZE); renderList(); list.scrollTop = scrollTop; return; }
    const card = event.target.closest('.project-card');
    if (card) select(Number(card.dataset.id));
  });
  list.addEventListener('keydown', event => {
    const card = event.target.closest('.project-card');
    if (card && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); select(Number(card.dataset.id)); }
  });
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
    const manualSaleSection = c.manualSaleSamples?.length ? `<section class="detail-section"><p class="section-label">特殊出售掛牌 <span>不納入一般行情／投報</span></p><div class="source-links">${c.manualSaleSamples.map(row => `<a href="${esc(row.url)}" target="_blank" rel="noopener">${esc(row.sourceName || '來源')} · ${esc(row.title || c.name)} · ฿${fmt(row.price)} · ${fmt(row.area, 2)} ㎡ · ฿${fmt(row.priceSqm)} / ㎡ ↗</a>`).join('')}</div><p class="fee-note">此為銀行資產特惠售價，與一般市場掛牌差異較大；保留原始物件來源，暫不納入平均售價、最低市場單價及投報率。</p></section>` : '';
    if (!hasSale(c) || !hasRent(c)) {
      const query = encodeURIComponent(`${c.name} condo Bangkok`);
      const ddSale = `https://www.google.com/search?q=site%3Addproperty.com+${query}+for+sale`;
      const ddRent = `https://www.google.com/search?q=site%3Addproperty.com+${query}+for+rent`;
      const phSale = c.propertyHubSaleUrl || `https://www.google.com/search?q=site%3Apropertyhub.in.th+${query}+for+sale`;
      const phRent = c.propertyHubRentUrl || `https://www.google.com/search?q=site%3Apropertyhub.in.th+${query}+for+rent`;
      const hipflatSearch = c.hipflatProjectUrl || `https://www.google.com/search?q=site%3Ahipflat.co.th%2Fzh%2Fprojects+${query}`;
      const marketCrosscheck = marketCrosscheckById.get(Number(c.id)) || null;
      const nearest = c.nearestMrt;
      const station = stationsById.get(nearest?.stationId);
      const directionsUrl = station && c.locationVerified ? `https://www.google.com/maps/dir/?api=1&origin=${c.lat},${c.lng}&destination=${station.lat},${station.lng}&travelmode=walking` : null;
      detail.classList.remove('empty');
      const projectAreaLabel = station ? `${station.name} ${transitLabel(station)} 周邊` : '曼谷 Condo 名單';
      const nearestLabel = station?.name || (nearest ? c.station : '待核實');
      const fallbackSale = hasSale(c) ? `<section class="detail-section"><p class="section-label">二手出售 <span>${c.sale.marketSummary ? 'PropertyScout 房型行情摘要' : '可核對掛牌樣本'}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.sale.marketSummary ? '專案起售價' : '最低售價'}</span><b class="metric-value">${money(c.sale.minimum)}</b><span class="metric-sub">${sampleSource(c.sale.minimumSourceUrl, c.sale)}</span></div><div class="metric"><span class="metric-label">${c.sale.marketSummary ? '房型均價低點 / ㎡' : '最低售價 / ㎡'}</span><b class="metric-value">${money(c.sale.minimumSqm)}</b><span class="metric-sub">${sampleSource(c.sale.minimumSqmSourceUrl, c.sale)}</span></div></div><div class="source-links"><a href="${esc(c.sale.source || phSale)}" target="_blank" rel="noopener">${esc(c.sale.sourceName || 'PropertyHub 出售來源')} ↗</a></div></section>` : c.hipflatSummary?.saleFrom ? `<section class="detail-section"><p class="section-label">Hipflat 起售參考 <span>專案摘要，非單筆掛牌</span></p><b class="metric-value">${money(c.hipflatSummary.saleFrom)}</b><div class="source-links"><a href="${esc(c.hipflatSummary.source || c.hipflatProjectUrl || hipflatSearch)}" target="_blank" rel="noopener">Hipflat 專案起售來源 ↗</a></div></section>` : '';
      const fallbackRent = hasRent(c) ? `<section class="detail-section rent-section"><p class="section-label">出租市場 <span>${c.rent.marketSummary ? 'PropertyScout 房型行情摘要' : '可核對掛牌樣本'}</span></p><div class="metric-grid"><div class="metric"><span class="metric-label">${c.rent.marketSummary ? '專案起租價' : '最低月租'}</span><b class="metric-value">${money(c.rent.minimum)} / 月</b><span class="metric-sub">${sampleSource(c.rent.minimumSourceUrl, c.rent)}</span></div><div class="metric"><span class="metric-label">${c.rent.marketSummary ? '房型均價低點 / ㎡ / 月' : '最低租金 / ㎡ / 月'}</span><b class="metric-value">${money(c.rent.minimumSqm)}</b><span class="metric-sub">${sampleSource(c.rent.minimumSqmSourceUrl, c.rent)}</span></div></div><div class="source-links"><a href="${esc(c.rent.source || phRent)}" target="_blank" rel="noopener">${esc(c.rent.sourceName || 'PropertyHub 出租來源')} ↗</a></div></section>` : c.hipflatSummary?.rentFrom ? `<section class="detail-section rent-section"><p class="section-label">Hipflat 起租參考 <span>專案摘要，非單筆掛牌</span></p><b class="metric-value">${money(c.hipflatSummary.rentFrom)} / 月</b><div class="source-links"><a href="${esc(c.hipflatSummary.source || c.hipflatProjectUrl || hipflatSearch)}" target="_blank" rel="noopener">Hipflat 專案起租來源 ↗</a></div></section>` : '';
      const verifiedSaleSamples = c.verifiedMarketSamples?.sale || [];
      const verifiedRentSamples = c.verifiedMarketSamples?.rent || [];
      const verifiedSampleLink = (sample, kind) => {
        const statusLabel = sample.listingStatus === 'confirmed_unavailable'
          ? kind === 'rent' && sample.availableUntil ? ` · 已過租期 ${esc(sample.availableUntil)}` : ' · 歷史掛牌'
          : '';
        return `<a href="${esc(sample.url)}" target="_blank" rel="noopener">${esc(sample.sourceName || '房源')} ${kind === 'sale' ? '出售' : '出租'} · ${sample.beds ? `${fmt(sample.beds)} 房 · ` : ''}${money(sample.price)}${kind === 'rent' ? ' / 月' : ''} · ${fmt(sample.area, 1)} ㎡ · ฿${fmt(Number(sample.price) / Number(sample.area))} / ㎡${kind === 'rent' ? ' / 月' : ''}${sample.updated ? ` · 更新 ${esc(String(sample.updated).slice(0, 10))}` : ''}${statusLabel} ↗</a>`;
      };
      const verifiedMarketSamplesHtml = verifiedSaleSamples.length || verifiedRentSamples.length ? `<section class="detail-section"><p class="section-label">可核對單筆掛牌 <span>${verifiedSaleSamples.length} 售 · ${verifiedRentSamples.length} 租</span></p><div class="source-links">${verifiedSaleSamples.map(sample => verifiedSampleLink(sample, 'sale')).join('')}${verifiedRentSamples.map(sample => verifiedSampleLink(sample, 'rent')).join('')}</div><p class="fee-note">連結可開啟個別物件頁；平台更新時間不等於現況保證，請向刊登者確認是否仍在架。</p></section>` : '';
      const crossSaleRows = marketCrosscheck?.sale?.listings || [];
      const crossRentRows = marketCrosscheck?.rent?.listings || [];
      const marketCrosscheckHtml = marketCrosscheck ? `<section class="detail-section"><p class="section-label">${esc(marketCrosscheck.sourceName || 'DDproperty')} 單筆掛牌核對 <span>${fmt(crossSaleRows.length)} 售 · ${fmt(crossRentRows.length)} 租 · ${esc(marketCrosscheck.asOf || '')}</span></p><p class="fee-note">此平台單筆掛牌獨立列出，未併入其他來源的行情均值；不同平台可能刊登同一房源。刊登頁面的在架狀態仍請向刊登者確認。</p>${crossSaleRows.length ? `<div class="source-links">${crossSaleRows.map(row => `<a href="${esc(row.url)}" target="_blank" rel="noopener">${esc(marketCrosscheck.sourceName || 'PropertyHub')} 出售 · ${row.bedrooms ? `${fmt(row.bedrooms)} 房 · ` : ''}${money(row.price)} · ${fmt(row.area, 1)} ㎡ · ${money(row.priceSqm)} / ㎡ · ${esc(row.listedAt || '')}${row.statusLabel ? ` · ${esc(row.statusLabel)}` : ''} ↗</a>`).join('')}</div>` : ''}${crossRentRows.length ? `<div class="source-links">${crossRentRows.map(row => `<a href="${esc(row.url)}" target="_blank" rel="noopener">${esc(marketCrosscheck.sourceName || 'DDproperty')} 出租 · ${row.bedrooms ? `${fmt(row.bedrooms)} 房 · ` : ''}${money(row.price)} / 月 · ${fmt(row.area, 1)} ㎡ · ${money(row.priceSqm)} / ㎡ / 月 · ${esc(row.listedAt || '')}${row.statusLabel ? ` · ${esc(row.statusLabel)}` : ''} ↗</a>`).join('')}</div>` : ''}${marketCrosscheck.projectSourceUrl ? `<div class="source-links"><a href="${esc(marketCrosscheck.projectSourceUrl)}" target="_blank" rel="noopener">${esc(marketCrosscheck.sourceName || 'DDproperty')} 出售專案掛牌頁${marketCrosscheck.sale?.activeListingCount === 0 ? ' · 目前出售 0 筆' : ''} ↗</a>${marketCrosscheck.rent?.sourceUrl ? `<a href="${esc(marketCrosscheck.rent.sourceUrl)}" target="_blank" rel="noopener">${esc(marketCrosscheck.sourceName || 'DDproperty')} 出租專案頁 · ${fmt(marketCrosscheck.rent?.activeListingCount || 0)} 筆 ↗</a>` : ''}</div>` : ''}${marketCrosscheck.availabilitySources?.length ? `<p class="fee-note">其他平台：${marketCrosscheck.availabilitySources.map(source => `${esc(source.sourceName)}：${esc(source.statusLabel)}`).join(' · ')}</p><div class="source-links">${marketCrosscheck.availabilitySources.map(source => `<a href="${esc(source.url)}" target="_blank" rel="noopener">${esc(source.sourceName)} 核對來源 ↗</a>`).join('')}</div>` : ''}</section>` : '';
      detail.innerHTML = `<button class="close-detail" aria-label="關閉 Condo 資訊">×</button><button class="panel-size-toggle detail-size-toggle" id="toggleDetailSize" type="button" aria-expanded="true" aria-label="縮小右側卡片" title="縮小右側卡片">−</button><div class="detail-hero"><div class="detail-topline"><span class="station-pill">Hipflat · ${esc(projectAreaLabel)}</span><span class="age-pill">${c.completedYear ? `${esc(c.completedYear)} 完工` : c.locationVerified ? '完工年待補 · 座標已核實' : '完工年待補 · 位置待核'}</span></div><h2 class="detail-title">${esc(c.name)}</h2><p class="detail-caption">${c.locationVerified ? 'Condo 座標已由公開專案或地圖資料頁核對。' : 'Condo 位置尚待核實。'} 完工年會在取得可靠資料後補上。</p><a class="review-link" href="${reviewsUrl(c)}" target="_blank" rel="noopener"><span>◎</span> 在 Google Maps 查看評論 <span>↗</span></a></div><section class="walk-section"><div class="walk-main"><span class="walk-symbol">🚇</span><div><span class="metric-label">${nearest?.distanceKm ? `最近${transitLabel(station)}站（步行路網估算）` : `最近${transitLabel(station)}站（直線距離）`}· ${esc(nearestLabel)}</span><strong>${c.locationVerified ? nearest?.distanceKm ? `${nearest.distanceKm} 公里步行路網距離` : `${nearest?.straightDistanceKm ?? '—'} 公里直線距離` : 'Condo 座標待核'}</strong><small>${c.locationVerified ? nearest?.distanceKm ? `步行約 ${Math.max(1, Number(nearest.minutes) || 0)} 分鐘 · Valhalla 路網估算` : '步行路網距離待計算' : '確認 Condo 座標後，再判定最近 MRT 與步行距離'}</small></div></div>${directionsUrl ? `<a class="route-button" href="${directionsUrl}" target="_blank" rel="noopener">Google Maps 步行導航 ↗</a>` : station ? '<button id="showWalkingRoute" class="route-button">查看 MRT 站點</button>' : ''}</section>${fallbackSale}${fallbackRent}${verifiedMarketSamplesHtml}${marketCrosscheckHtml}${manualSaleSection}<section class="detail-section"><p class="section-label">其他公開房源來源</p><div class="source-links"><a href="${hipflatSearch}" target="_blank" rel="noopener">Hipflat 專案與售租行情 ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a><a href="${phSale}" target="_blank" rel="noopener">PropertyHub 出售 ↗</a><a href="${phRent}" target="_blank" rel="noopener">PropertyHub 出租 ↗</a></div></section><section class="detail-section"><p class="section-label">投報率試算 <span>售租資料不足</span></p><p class="fee-note">補齊同一 Condo 的出售與出租掛牌後，會以每平方米最低單價計算。</p></section><section class="detail-section"><p class="section-label">資料來源</p><div class="source-links"><a href="${esc(c.discoveryUrl)}" target="_blank" rel="noopener">Hipflat 曼谷 Condo 清單 ↗</a>${c.hipflatProjectUrl ? `<a href="${esc(c.hipflatProjectUrl)}" target="_blank" rel="noopener">Hipflat 專案頁 ↗</a>` : ''}${c.locationVerified ? `<a href="${esc(c.locationSourceUrl)}" target="_blank" rel="noopener">座標來源 ↗</a>` : ''}${c.locationVerificationSourceUrl ? `<a href="${esc(c.locationVerificationSourceUrl)}" target="_blank" rel="noopener">地址交叉核實 ↗</a>` : ''}</div></section>`;
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
    const nearestStation = stationsById.get(nearest?.stationId);
    const savedYield = loadYieldInputs()[c.id] || null;
    const yieldDefaults = yieldDefaultsFor(c, savedYield?.beds || null);
    const calcPrice = Number(savedYield?.price ?? yieldDefaults.price);
    const calcRent = Number(savedYield?.rent ?? yieldDefaults.rent);
    const calcArea = Number(savedYield?.area ?? yieldDefaults.area);
    const calcDeductFee = savedYield?.deductFee ?? true;
    const calcDeductAgent = savedYield?.deductAgent ?? true;
    const localListingSection = c.localListings?.length ? `<section class="detail-section"><p class="section-label">本機每日房源提醒 <span>${c.localListings.length} 筆已配對</span></p><div class="source-links">${c.localListings.slice(0, 8).map(row => `<a href="${esc(row.url)}" target="_blank" rel="noopener">${esc(row.kind === 'sale' ? '出售' : '出租')} · ${esc(row.title || c.name)}${row.price ? ` · ฿${fmt(row.price)}${row.kind === 'rent' ? ' / 月' : ''}` : ''}${row.area ? ` · ${fmt(row.area, 1)} ㎡` : ''} ↗</a>`).join('')}</div><p class="fee-note">資料由本機匯入的平台新房源提醒整理；未保存聯絡人資料。每日更新時間依本機電腦排程。</p></section>` : '';
    if (savedYield && calcPrice > 0 && calcArea > 0) yieldOverrides.delete(c.id);
    detail.classList.remove('empty');
    const saleLabel = c.sale.marketSummary ? '房型行情摘要' : `${c.sale.sourceName || 'PropertyHub'} 可見掛牌`;
    const rentLabel = c.rent.marketSummary ? '房型行情摘要' : `${c.rent.sourceName || 'PropertyHub'} 可見掛牌`;
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
      ${localListingSection}
      ${manualSaleSection}
      <section class="detail-section"><p class="section-label">管理費參考 <span>需向管委會確認</span></p>${feeText}${c.fee?.source ? `<div class="source-links"><a href="${esc(c.fee.source)}" target="_blank" rel="noopener">管理費來源 ↗</a></div>` : ''}</section>
      ${hasYieldData(c) ? `<section class="detail-section yield-section"><div class="yield-heading"><p class="section-label">年租金報酬試算 <span>${yieldDefaults.beds && !(yieldDefaults.rent > 0) ? '待補同房型租盤' : yieldDefaults.beds === '2' && !(yieldDefaults.price > 0) ? '兩房最低掛牌待補' : yieldDefaults.isRoomStart ? `${yieldDefaults.beds || ''} 房最低總價` : yieldDefaults.isRoomAverage ? `${yieldDefaults.beds || ''} 房平均售價估算` : yieldUsesSummary ? '房型行情摘要估算' : '最低價格估算'}</span></p><div class="yield-value" id="yieldValue">${Number.isFinite(yieldFor(c)) ? yieldFor(c).toFixed(2) : '待補'}<small>${Number.isFinite(yieldFor(c)) ? '% / 年' : yieldDefaults.beds && !(yieldDefaults.rent > 0) ? '需補同房型租金' : '可比房型售價樣本不足'}</small></div></div><div class="yield-inputs"><div class="yield-input"><label for="yieldPrice">參考購入總價 (฿)</label><input id="yieldPrice" type="number" min="1" step="50000" value="${calcPrice}"><button type="button" id="useLowestYieldSample" class="use-lowest-yield-button" ${yieldDefaults.beds && !(yieldDefaults.price > 0) ? 'disabled' : ''}>套用 ${esc(yieldDefaults.beds || '選擇房型')} 房最低總價基準</button></div><div class="yield-input"><label for="yieldRent">參考月租 (฿)</label><input id="yieldRent" type="number" min="0" step="500" value="${calcRent}"></div><div class="yield-input"><label for="yieldArea">室內面積 (㎡)</label><input id="yieldArea" type="number" min="1" step="0.1" value="${calcArea.toFixed(1)}"></div><div class="yield-input"><label for="yieldBeds">參考房型</label><select id="yieldBeds">${yieldDefaults.beds && !yieldDefaults.roomOptions.some(([bed]) => String(bed) === String(yieldDefaults.beds)) ? `<option value="${esc(yieldDefaults.beds)}" selected disabled>${esc(yieldDefaults.beds)} 房最低掛牌待補</option>` : ''}${yieldDefaults.roomOptions.map(([bed]) => `<option value="${esc(bed)}" ${String(yieldDefaults.beds) === String(bed) ? 'selected' : ''}>${bed} 房${Number(bed) >= 5 ? '以上' : ''}</option>`).join('') || '<option value="">房型未提供</option>'}</select></div></div><p class="formula-note">預設採兩房最低出售掛牌；若沒有兩房出售資料，才選擇有售租資料的最低房型。購入總價、室內面積與來源連結都取自同房型最低總價的同一筆物件。切換房型或按下按鈕會套用該房型最低總價基準。月租以同房型租金單價乘上這筆物件面積；沒有同房型租盤時不跨房型代入，需補同房型租金或自行輸入假設。淨年投報率＝（月租 × 扣除仲介月數後的年租月數 − 年管理費）÷ 購入總價；管理費僅在已查得時扣除。${c.fee?.rate ? '' : '此案管理費尚未核實，試算暫未扣除管理費。'} 可自行修改並儲存，未含稅、維修與交易成本。</p><div class="yield-options"><label><input id="deductFee" type="checkbox" ${calcDeductFee ? 'checked' : ''}> 扣除管理費</label><label><input id="deductAgent" type="checkbox" ${calcDeductAgent ? 'checked' : ''}> 扣除 1 個月仲介管理費</label><button type="button" id="saveYieldInputs" class="save-yield-button">儲存試算</button><span id="yieldSavedNote" class="yield-saved-note">${savedYield ? '已儲存於此裝置' : ''}</span></div><div class="source-links"><a href="${esc(yieldDefaults.saleSourceUrl || saleSampleUrl)}" target="_blank" rel="noopener">${yieldDefaults.beds ? `${esc(yieldDefaults.beds)} 房${yieldDefaults.isRoomStart ? '最低總價' : '房型售價估算'}來源` : '購入基準來源'} ↗</a><a href="${esc(yieldDefaults.rentSourceUrl || rentSampleUrl)}" target="_blank" rel="noopener">${yieldDefaults.rentFallback ? `${esc(yieldDefaults.rentFallbackBeds)} 房租金單價估算來源` : yieldDefaults.beds ? `${esc(yieldDefaults.beds)} 房租金單價來源` : '租金基準來源'} ↗</a><a href="${ddSale}" target="_blank" rel="noopener">DDproperty 出售 ↗</a><a href="${ddRent}" target="_blank" rel="noopener">DDproperty 出租 ↗</a><a href="${hipflatSearch}" target="_blank" rel="noopener">Hipflat 專案行情 ↗</a></div></section>` : '<section class="detail-section yield-section"><p class="section-label">投報率試算 <span>售租資料不足</span></p><p class="fee-note">至少需要同一 Condo可核對的出售與出租每平方米單價，才能計算投報率。</p></section>'}
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
    const recalculateYield = () => {
      const price = Number(detail.querySelector('#yieldPrice').value);
      const rent = Number(detail.querySelector('#yieldRent').value);
      const area = Number(detail.querySelector('#yieldArea').value);
      if (!(price > 0) || !(rent > 0) || !(area > 0)) {
        yieldOverrides.delete(c.id);
        detail.querySelector('#yieldValue').innerHTML = '待補<small>請填入有效售租與面積</small>';
        markers.forEach((m, markerId) => m.setIcon(icon(condosById.get(markerId), markerId === selectedId)));
        renderList();
        return;
      }
      const y = calculateNetYield(c, { price, rent, area, deductFee: detail.querySelector('#deductFee').checked, deductAgent: detail.querySelector('#deductAgent').checked });
      yieldOverrides.set(c.id, y);
      detail.querySelector('#yieldValue').innerHTML = `${y.toFixed(2)}<small>% / 年</small>`;
      markers.forEach((m, markerId) => m.setIcon(icon(condosById.get(markerId), markerId === selectedId)));
      renderList();
    };
    ['yieldPrice', 'yieldRent', 'yieldArea', 'deductFee', 'deductAgent'].forEach(id => detail.querySelector(`#${id}`)?.addEventListener('input', recalculateYield));
    detail.querySelector('#useLowestYieldSample')?.addEventListener('click', () => {
      const defaults = yieldDefaultsFor(c, detail.querySelector('#yieldBeds').value || yieldDefaults.beds || '2');
      if (defaults.beds) detail.querySelector('#yieldBeds').value = defaults.beds;
      detail.querySelector('#yieldPrice').value = defaults.price;
      detail.querySelector('#yieldArea').value = Number(defaults.area || 0).toFixed(1);
      detail.querySelector('#yieldRent').value = defaults.rent;
      detail.querySelector('#useLowestYieldSample').textContent = `套用 ${defaults.beds || '所選'} 房最低總價基準`;
      const baselineLabel = detail.querySelector('.yield-heading .section-label span');
      if (baselineLabel) baselineLabel.textContent = defaults.isRoomStart ? `${defaults.beds} 房最低掛牌總價` : defaults.isRoomAverage ? `${defaults.beds} 房平均售價估算` : `${defaults.beds || '所選'} 房最低總價樣本待補`;
      const yieldSourceLinks = detail.querySelectorAll('.yield-section .source-links a');
      if (yieldSourceLinks[0] && defaults.saleSourceUrl) yieldSourceLinks[0].href = defaults.saleSourceUrl;
      if (yieldSourceLinks[1] && defaults.rentSourceUrl) yieldSourceLinks[1].href = defaults.rentSourceUrl;
      recalculateYield();
      const values = loadYieldInputs();
      values[c.id] = {
        price: Number(detail.querySelector('#yieldPrice').value),
        rent: Number(detail.querySelector('#yieldRent').value),
        area: Number(detail.querySelector('#yieldArea').value),
        beds: detail.querySelector('#yieldBeds').value || null,
        deductFee: detail.querySelector('#deductFee').checked,
        deductAgent: detail.querySelector('#deductAgent').checked,
      };
      saveYieldInputs(values);
      const savedNote = detail.querySelector('#yieldSavedNote');
      if (savedNote) savedNote.textContent = `${defaults.beds || '所選'} 房最低總價基準已更新並儲存`;
    });
    detail.querySelector('#yieldBeds')?.addEventListener('change', event => {
      const defaults = yieldDefaultsFor(c, event.currentTarget.value || null);
      yieldOverrides.delete(c.id);
      detail.querySelector('#yieldPrice').value = defaults.price;
      detail.querySelector('#yieldArea').value = defaults.area.toFixed(1);
      detail.querySelector('#yieldRent').value = defaults.rent;
      detail.querySelector('#useLowestYieldSample').textContent = `套用 ${defaults.beds || '所選'} 房最低總價基準`;
      const baselineLabel = detail.querySelector('.yield-heading .section-label span');
      if (baselineLabel) baselineLabel.textContent = defaults.isRoomStart ? `${defaults.beds} 房最低總價` : defaults.isRoomAverage ? `${defaults.beds} 房平均售價估算` : `${defaults.beds || '可用'} 房資料不足，使用可用基準`;
      const yieldSourceLinks = detail.querySelectorAll('.yield-section .source-links a');
      if (yieldSourceLinks[0] && defaults.saleSourceUrl) yieldSourceLinks[0].href = defaults.saleSourceUrl;
      if (yieldSourceLinks[1] && defaults.rentSourceUrl) yieldSourceLinks[1].href = defaults.rentSourceUrl;
      recalculateYield();
    });
    detail.querySelector('#saveYieldInputs')?.addEventListener('click', () => {
      const values = loadYieldInputs();
      values[c.id] = {
        price: Number(detail.querySelector('#yieldPrice').value),
        rent: Number(detail.querySelector('#yieldRent').value),
        area: Number(detail.querySelector('#yieldArea').value),
        beds: detail.querySelector('#yieldBeds').value || null,
        deductFee: detail.querySelector('#deductFee').checked,
        deductAgent: detail.querySelector('#deductAgent').checked,
      };
      saveYieldInputs(values);
      detail.querySelector('#yieldSavedNote').textContent = '已儲存於此裝置';
    });
  }
  function markerFor(id) { return markers.get(id); }
  function select(id) {
    const c = condosById.get(id);
    if (!c) return;
    selectedId = id;
    markers.forEach((m, markerId) => m.setIcon(icon(condosById.get(markerId), markerId === id)));
    renderList();
    renderDetail(c);
    if (walkingLine) { map.removeLayer(walkingLine); walkingLine = null; }
    if (window.matchMedia('(max-width: 650px)').matches) document.querySelector('.explorer').classList.add('hidden-mobile');
    if (Number.isFinite(c.lat) && Number.isFinite(c.lng)) map.panTo([c.lat, c.lng], { animate: true, duration: .4 });
    else { const station = stationsById.get(c.nearestMrt?.stationId); if (station) map.panTo([station.lat, station.lng], { animate: true, duration: .4 }); }
  }
  function refreshMode() {
    document.querySelectorAll('.segmented button').forEach(b => b.classList.toggle('selected', b.dataset.mode === mode));
    markers.forEach((m, id) => m.setIcon(icon(condosById.get(id), id === selectedId)));
    renderList();
  }
  document.querySelectorAll('.segmented button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; refreshMode(); }));
  document.getElementById('sortOrder').addEventListener('change', e => { sortMode = e.target.value; visibleProjectCount = LIST_PAGE_SIZE; renderList(); });
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
    const panel = group.querySelector('.filter-content');
    if (window.matchMedia('(max-width: 850px)').matches) {
      const toolbarBottom = document.querySelector('.filter-toolbar').getBoundingClientRect().bottom;
      const maxTop = window.innerHeight - panel.offsetHeight - 12;
      panel.style.left = '8px'; panel.style.right = '8px';
      panel.style.top = `${Math.max(8, Math.min(toolbarBottom + 6, maxTop))}px`;
      return;
    }
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
    visibleProjectCount = LIST_PAGE_SIZE;
    button.closest('details').open = false;
    renderList();
  }));
  document.getElementById('applyBedroomFilter').addEventListener('click', () => {
    const amount = budgetInput.value.trim() === '' ? null : Number(budgetInput.value);
    budgetInput.setAttribute('aria-invalid', String(amount != null && (!Number.isFinite(amount) || amount <= 0)));
    if (amount != null && (!Number.isFinite(amount) || amount <= 0)) return;
    budgetMax = amount == null ? null : amount * 10000;
    visibleProjectCount = LIST_PAGE_SIZE;
    document.getElementById('applyBedroomFilter').closest('details').open = false;
    renderList();
  });
  ['distanceMax','saleMin','saleMax','rentMin','rentMax','yieldMin','yieldMax','yearMin','yearMax'].forEach(id => {
    document.getElementById(id).addEventListener('input', () => { visibleProjectCount = LIST_PAGE_SIZE; renderList(); });
  });
  document.getElementById('lowriseOnly').addEventListener('change', () => { updateLowriseSummary(); visibleProjectCount = LIST_PAGE_SIZE; renderList(); });
  searchInput.addEventListener('input', e => {
    query = e.target.value.trim();
    visibleProjectCount = LIST_PAGE_SIZE;
    const roomQuery = query.match(/(?:^|\s)([1-4])\s*房/);
    setBedroomSelection(roomQuery?.[1] || null);
    const budgetQuery = query.match(/[1-4]\s*房(?:售價|總價|房價)(?:<=|<)\s*([\d,.]+萬?)/);
    const naturalBudget = query.match(/[1-4]\s*房\s*([\d,.]+\s*萬)\s*(?:內|以下)/);
    if (budgetQuery) budgetInput.value = String(budgetWanValue(budgetQuery[1]) || '');
    else if (naturalBudget) budgetInput.value = String(budgetWanValue(naturalBudget[1]) || '');
    renderList();
  });
  document.getElementById('clearSearch').addEventListener('click', () => {
    searchInput.value = ''; query = ''; visibleProjectCount = LIST_PAGE_SIZE; selectedBedrooms = null; budgetInput.removeAttribute('aria-invalid');
    setBedroomSelection(null);
    budgetMax = null;
    ['distanceMax','saleMin','saleMax','rentMin','rentMax','yieldMin','yieldMax','yearMin','yearMax'].forEach(id => { document.getElementById(id).value = ''; });
    document.getElementById('lowriseOnly').value = 'all';
    updateLowriseSummary();
    renderList();
  });
  document.getElementById('fitMap').addEventListener('click', () => { const points = [...filtered().filter(c => Number.isFinite(c.lat) && Number.isFinite(c.lng)).map(c => [c.lat,c.lng]), ...stations.map(s => [s.lat,s.lng])]; if (points.length) map.fitBounds(points, { padding: [70, 90], maxZoom: 14 }); });
  document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
  document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
  document.getElementById('locate').addEventListener('click', () => map.setView([13.7563, 100.5018], 11));
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); document.getElementById('search').focus(); } if (e.key === 'Escape') { detail.classList.add('empty'); document.querySelector('.explorer').classList.remove('hidden-mobile'); } });
  renderList();
  updateLowriseSummary();
  updateMarkerDensity();
  if (selectedId) { const c = condosById.get(selectedId); if (window.matchMedia('(max-width: 650px)').matches) detail.classList.add('empty'); else renderDetail(c); markerFor(selectedId)?.setIcon(icon(c, true)); }
  if (condos.length) {
    const narrow = window.matchMedia('(max-width: 650px)').matches;
    if (narrow) map.setView([13.7563, 100.5018], 10);
    else map.fitBounds([...condos.filter(c => Number.isFinite(c.lat) && Number.isFinite(c.lng)).map(c => [c.lat,c.lng]), ...stations.map(s => [s.lat,s.lng])], { paddingTopLeft: [390, 60], paddingBottomRight: [390, 60], maxZoom: 13 });
  }
  window.addEventListener('resize', () => map.invalidateSize());
  document.getElementById('startupLoader')?.remove();
})();

