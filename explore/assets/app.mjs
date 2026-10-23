import {automaticGold, factValue, freshness, parseNumber, nominalFineness, calculateScenario} from './domain.mjs';

// Static content remains readable without JavaScript. No cookies, storage, analytics, or third-party requests.
for (const el of document.querySelectorAll('[data-observed]')) {
  const state = freshness(el.dataset.observed);
  if (state === 'stale') {el.textContent = 'stale snapshot — recheck'; el.classList.add('stale');}
  else if (state === 'future-dated' || state === 'unverified') {el.textContent = 'timestamp needs review'; el.classList.add('stale');}
}
const search = document.querySelector('#catalog-search');
if (search) {
  const category = document.querySelector('#category-filter');
  const seller = document.querySelector('#seller-filter');
  const rows = [...document.querySelectorAll('#research-table tbody tr')];
  const status = document.querySelector('#filter-status');
  function filter() {
    const query = search.value.trim().toLowerCase();
    let shown = 0;
    for (const row of rows) {
      const match = row.dataset.search.includes(query)
        && (category.value === 'all' || row.dataset.category === category.value)
        && (seller.value === 'all' || row.dataset.seller === seller.value);
      row.hidden = !match;
      if (match) shown++;
    }
    status.textContent = `${shown} of ${rows.length} entries shown`;
    document.querySelector('#no-results').hidden = shown !== 0;
  }
  search.addEventListener('input', filter);
  category.addEventListener('change', filter);
  seller.addEventListener('change', filter);
  document.querySelector('#clear-filters').addEventListener('click', () => {
    search.value = ''; category.value = seller.value = 'all'; filter(); search.focus();
  });
}

const choice = document.querySelector('#ring-choice');
if (choice) {
  const byId = id => document.getElementById(id);
  const money = n => new Intl.NumberFormat('en-US', {style:'currency', currency:'USD'}).format(n);
  const decimal = n => new Intl.NumberFormat('en-US', {maximumFractionDigits:6}).format(n);
  const allowedProducts = new Set(['www.automicgold.com','www.catbirdnyc.com','auvere.com','www.quince.com','mene.com','www.bluenile.com','www.zales.com','www.vrai.com','www.brilliantearth.com']);
  const toggleMode = isScenario => {
    byId('automatic-panel').hidden = isScenario;
    byId('scenario-panel').hidden = !isScenario;
    byId('automatic-mode').setAttribute('aria-pressed', String(!isScenario));
    byId('scenario-mode').setAttribute('aria-pressed', String(isScenario));
  };
  byId('automatic-mode').addEventListener('click', () => toggleMode(false));
  byId('scenario-mode').addEventListener('click', () => toggleMode(true));
  let catalog, sources;
  const form = byId('scenario-form');
  const resetOutput = () => {byId('scenario-output').hidden = true; byId('scenario-error').hidden = true;};
  const updateBasis = () => {
    byId('karat-field').hidden = byId('purity-basis').value !== 'nominal';
    byId('fineness-field').hidden = byId('purity-basis').value !== 'declared';
    resetOutput();
  };
  byId('purity-basis').addEventListener('change', updateBasis);
  form.addEventListener('input', () => {
    resetOutput();
    byId('scenario-provenance').textContent = 'User-edited conditional inputs. These are assumptions, not verified product facts. Recheck the source of any reference price.';
  });
  function updateAutomatic() {
    const p = catalog.products.find(p => p.id === choice.value);
    if (!p) throw new Error('Product record missing');
    const result = automaticGold(p);
    const karat = factValue(p, 'karat'), item = factValue(p, 'itemWeightG');
    byId('auto-karat').textContent = karat === null ? '' : `${karat}K · seller claim`;
    byId('auto-item').textContent = item === null ? '' : `${item} g · not net gold`;
    byId('auto-net').textContent = factValue(p, 'netMetalWeightG') ?? '';
    byId('auto-fine').textContent = result.fineGrams === null ? '' : decimal(result.fineGrams);
    byId('auto-value').textContent = '';
    byId('automatic-reason').textContent = result.reason;
    const s = sources.find(s => s.id === p.source);
    const url = new URL(s.url);
    if (url.protocol !== 'https:' || !allowedProducts.has(url.hostname)) throw new Error('Unexpected product publisher');
    const link = document.createElement('a');
    link.href = s.url; link.textContent = 'Official product page ↗'; link.rel = 'noopener noreferrer'; link.className = 'source-link';
    byId('automatic-source').replaceChildren(link);
  }
  byId('load-source-scenario').addEventListener('click', () => {
    if (!catalog) return;
    const p = catalog.products.find(p => p.id === 'ag-24k');
    byId('scenario-weight').value = String(factValue(p, 'itemWeightG'));
    byId('purity-basis').value = 'declared';
    byId('scenario-fineness').value = String(factValue(p, 'declaredPurity'));
    byId('scenario-spot').value = String(catalog.meta.marketReference.amount);
    byId('scenario-retail').value = String(p.price.amount);
    byId('scenario-ack').checked = false;
    updateBasis();
    byId('scenario-provenance').textContent = `Conditional preset: assumes all of Automic Gold’s approximately ${factValue(p,'itemWeightG')}g ITEM weight is gold alloy. This NET basis is NOT established. Seller-declared ${(factValue(p,'declaredPurity')*100).toFixed(2)}% purity is not an assay. Retail is a dated default display. Reference: JM Bullion body/table ask, 22 Oct 2026 23:09 UTC; conflicting header flagged. Acknowledge the assumptions before calculating.`;
  });
  byId('use-reference').addEventListener('click', () => {
    if (!catalog) return;
    byId('scenario-spot').value = String(catalog.meta.marketReference.amount);
    resetOutput();
    byId('scenario-provenance').textContent = 'Loaded the dated JM Bullion body/table ask: 22 Oct 2026, 23:09 UTC. Header conflict is flagged. This is not live or an LBMA benchmark. Other inputs remain explicit assumptions.';
  });
  form.addEventListener('submit', event => {
    event.preventDefault(); resetOutput();
    const weight = parseNumber(byId('scenario-weight').value);
    const basis = byId('purity-basis').value;
    const fineness = basis === 'nominal' ? nominalFineness(parseNumber(byId('scenario-karat').value))
      : basis === 'declared' ? parseNumber(byId('scenario-fineness').value) : null;
    const spotPerOz = parseNumber(byId('scenario-spot').value);
    const retailText = byId('scenario-retail').value.trim();
    const retail = retailText === '' ? null : parseNumber(retailText);
    const result = retailText !== '' && retail === null
      ? {ok:false,error:'Optional retail price must be a plain positive decimal USD amount.'}
      : calculateScenario({weight,fineness,spotPerOz,retail,acknowledged:byId('scenario-ack').checked});
    if (!result.ok) {
      byId('scenario-error').textContent = result.error; byId('scenario-error').hidden = false;
      return;
    }
    byId('scenario-fine').textContent = decimal(result.fineGrams) + ' g';
    byId('scenario-per-gram').textContent = money(result.perGram) + ' USD';
    byId('scenario-value').textContent = money(result.metalValue) + ' USD';
    byId('scenario-ratio').textContent = result.ratio === null ? '' : decimal(result.ratio) + '×';
    byId('scenario-output').hidden = false;
  });
  Promise.all([
    fetch(new URL('../data/catalog.json', import.meta.url)).then(r => {if (!r.ok) throw new Error('Catalog unavailable'); return r.json();}),
    fetch(new URL('../research/evidence.json', import.meta.url)).then(r => {if (!r.ok) throw new Error('Evidence unavailable'); return r.json();})
  ]).then(([c,e]) => {
    catalog = c; sources = e.sources;
    updateAutomatic(); choice.addEventListener('change', updateAutomatic);
  }).catch(() => {
    byId('automatic-reason').textContent = 'Research data could not be loaded. No gold calculation has been made; use the static catalog and sources.';
    byId('load-source-scenario').disabled = true; byId('use-reference').disabled = true;
  });
}
