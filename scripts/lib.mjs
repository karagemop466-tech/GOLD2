import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {CATEGORIES, REQUIRED_FACTS, finitePositive, freshness, isPurchaseReady, missingRequirements} from '../explore/assets/domain.mjs';
export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const loadJSON = async file => JSON.parse(await readFile(path.join(ROOT, file), 'utf8'));
export async function loadResearch() {
  const [catalog, evidence, review] = await Promise.all([loadJSON('data/catalog.json'), loadJSON('research/evidence.json'), loadJSON('data/review.json')]);
  return {catalog, evidence, review, sourceMap: new Map(evidence.sources.map(s => [s.id, s]))};
}
export const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const escapeAttr = escapeHTML;
export const PRODUCT_HOSTS = Object.freeze({
  automic: ['www.automicgold.com'], catbird: ['www.catbirdnyc.com'], auvere: ['auvere.com'],
  quince: ['www.quince.com'], mene: ['mene.com'], bluenile: ['www.bluenile.com']
});
export const SOURCE_HOSTS = new Set([
  ...Object.values(PRODUCT_HOSTS).flat(), 'consumer.ftc.gov', 'www.gia.edu', 'www.nist.gov',
  'www.lbma.org.uk', 'www.jmbullion.com', 'www.bbb.org', 'www.trustpilot.com'
]);
export function safeSourceURL(value) {
  try {const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password && (!url.port || url.port === '443') && SOURCE_HOSTS.has(url.hostname);}
  catch {return false;}
}
export function hasNumber(text, number) {
  // Numeric token match, not a loose substring (e.g. 726 must not match 1726).
  const normalized = text.replaceAll(',', '').replace(/\s+/g, ' ');
  const token = String(number).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(?<![\\d.])${token}(?![\\d.])`).test(normalized);
}
export function validateResearch({catalog, evidence, review}, now = Date.now()) {
  const errors = [], warnings = [];
  const addError = (where, text) => errors.push(`${where}: ${text}`);
  const sources = new Map();
  for (const s of evidence.sources ?? []) {
    if (!/^[a-z0-9-]+$/.test(s.id) || sources.has(s.id)) addError('sources', `invalid/duplicate id ${s.id}`);
    sources.set(s.id, s);
    if (!safeSourceURL(s.url)) addError(s.id, 'not an allowed HTTPS publisher URL');
    if (freshness(s.observedAt, now) === 'unverified' || freshness(s.observedAt, now) === 'future-dated') addError(s.id, 'invalid/future observation timestamp');
    if (!s.publisher || !s.kind || !s.method || !s.quotes || Object.keys(s.quotes).length === 0) addError(s.id, 'missing provenance');
    for (const quote of Object.values(s.quotes ?? {})) if (typeof quote !== 'string' || !quote.trim()) addError(s.id, 'empty/non-text passage');
    if (!['fetched', 'partial', 'unavailable'].includes(s.access)) addError(s.id, 'unknown access status');
    if (s.access !== 'fetched') warnings.push(`${s.id}: source access ${s.access}`);
  }
  const resolve = (r, where) => {
    const s = sources.get(r?.source);
    if (!s || typeof s.quotes?.[r?.quote] !== 'string') {addError(where, 'missing source/passage reference'); return null;}
    return {source:s, text:s.quotes[r.quote]};
  };
  const ids = new Set();
  const sellerIds = new Set((catalog.sellers ?? []).map(s => s.id));
  for (const p of catalog.products ?? []) {
    if (!/^[a-z0-9-]+$/.test(p.id) || ids.has(p.id)) addError('products', `invalid/duplicate id ${p.id}`);
    ids.add(p.id);
    const primary = sources.get(p.source);
    if (primary?.kind !== 'product') addError(p.id, 'primary source must be a product page');
    if (!sellerIds.has(p.seller) || (primary && !PRODUCT_HOSTS[p.seller]?.includes(new URL(primary.url).hostname))) addError(p.id, 'seller/source mismatch');
    if (!CATEGORIES.some(c => c.id === p.category)) addError(p.id, 'unknown category');
    const name = resolve(p.name, p.id + '.name');
    if (!p.name?.value || name?.text !== p.name.value) addError(p.id, 'name does not match recorded passage');
    if (!p.scope || !Array.isArray(p.flags)) addError(p.id, 'missing configuration scope/flags');
    if (['future-dated','unverified'].includes(freshness(p.observedAt, now))) addError(p.id, 'invalid observation date');
    for (const key of REQUIRED_FACTS) {
      if (!(key in (p.facts ?? {}))) {addError(p.id, `missing nullable field ${key}`); continue;}
      const f = p.facts[key];
      if (f === null) continue;
      if (typeof f !== 'object' || f.value === null || f.value === '') {addError(p.id, `invalid fact ${key}`); continue;}
      const proof = resolve(f, `${p.id}.${key}`);
      if (!proof) continue;
      if (proof.source.kind === 'independent-platform') addError(p.id, `review platforms cannot prove product field ${key}`);
      if (key === 'karat' && (!finitePositive(f.value) || f.value > 24 || !new RegExp(`${f.value}\\s*(?:k\\b|karat)`, 'i').test(proof.text))) addError(p.id, 'karat unsupported by passage');
      if (key === 'solidGold' && (f.value !== true || !/solid\s+(?:\d+\s*(?:k|karat)\s+)?gold/i.test(proof.text))) addError(p.id, 'explicit solid-gold wording missing');
      if (['itemWeightG','netMetalWeightG','fineGoldWeightG'].includes(key) && (!finitePositive(f.value) || !hasNumber(proof.text, f.value))) addError(p.id, `${key} numeric evidence mismatch`);
      if (key === 'declaredPurity' && (!finitePositive(f.value) || f.value > 1 || !hasNumber(proof.text, Number((f.value * 100).toFixed(8))))) addError(p.id, 'declared purity must have explicit percentage evidence');
      if (key === 'stone' && (typeof f.value !== 'string' || !proof.text.includes(f.value))) addError(p.id, 'stone description differs from passage');
      if (['hallmark','makerMark','independentTest','independentInspectionReturnPermission'].includes(key) && typeof f.value !== 'boolean') addError(p.id, `${key} must be boolean or null`);
      if (key === 'netMetalWeightG' && !/(?:gold.alloy.only|net (?:gold|metal)|excluding (?:stones|gemstones))/i.test(proof.text)) addError(p.id, 'net weight needs explicit metal-only basis; item/shipping weight is not admissible');
    }
    if (p.price !== null) {
      const price = p.price;
      if (!finitePositive(price.amount) || price.currency !== 'USD' || !price.scope || !['displayed-option','unbound-display','setting-only'].includes(price.kind)) addError(p.id, 'invalid observed price/scope/currency');
      const proofs = (price.evidence ?? []).map(r => resolve(r, p.id + '.price')).filter(Boolean);
      if (!proofs.some(x => hasNumber(x.text, price.amount))) addError(p.id, 'price amount is not present in cited passage');
      if (!proofs.some(x => /\bUSD\b/.test(x.text))) addError(p.id, 'currency context is not evidenced');
      if (proofs.some(x => x.source.kind === 'independent-platform' || x.source.access === 'unavailable')) addError(p.id, 'price cannot come from a review or unavailable source');
      if (['future-dated','unverified'].includes(freshness(price.observedAt, now))) addError(p.id, 'price timestamp invalid');
      if (freshness(price.observedAt, now, catalog.meta.freshnessHours) === 'stale') warnings.push(`${p.id}: price older than ${catalog.meta.freshnessHours}h; manual refresh required`);
    } else warnings.push(`${p.id}: USD/configured price unverified; blank`);
    if (p.reportedWeight !== null) {
      const w = p.reportedWeight, proof = resolve(w.evidence, p.id + '.reportedWeight');
      if (!finitePositive(w.min) || !finitePositive(w.max) || w.max < w.min || w.unit !== 'g' || w.approximate !== true || !['item','fine-undefined'].includes(w.basis)) addError(p.id, 'invalid reported weight range/basis');
      if (proof && (!hasNumber(proof.text, w.min) || !hasNumber(proof.text, w.max))) addError(p.id, 'weight range not present in passage');
    }
    const missing = missingRequirements(p);
    if (missing.length) warnings.push(`${p.id}: ${missing.join('; ')}`);
    // This dataset is intentionally not independently verified; accidental approvals must stop publication.
    if (isPurchaseReady(p)) addError(p.id, 'purchase-ready status requires a separate documented human/physical review, not this automated dataset');
  }
  for (const s of catalog.sellers ?? []) {
    if (!s.id || !s.name) addError('sellers', 'missing identity');
    for (const key of ['contact','policy']) if (!sources.has(s[key])) addError(s.id, `missing ${key} source`);
    if (s.independent !== null && sources.get(s.independent)?.kind !== 'independent-platform') addError(s.id, 'invalid independent platform reference');
    if (s.returnDays !== null) {
      const proof = resolve(s.returnDays, s.id + '.returnDays');
      if (!Number.isInteger(s.returnDays.value) || s.returnDays.value <= 0 || !proof || !hasNumber(proof.text, s.returnDays.value)) addError(s.id, 'return-day passage mismatch');
    }
  }
  const findingIds = new Set();
  for (const f of review.findings ?? []) {
    if (!f.id || findingIds.has(f.id)) addError('review', `invalid/duplicate finding ${f.id}`);
    findingIds.add(f.id);
    if (!f.title || !f.finding || !f.action || !f.scope || !f.sources?.length) addError(f.id, 'finding lacks context/action/source');
    for (const id of f.sources ?? []) if (!sources.has(id)) addError(f.id, `unknown source ${id}`);
  }
  const ref = catalog.meta?.marketReference;
  const marketProof = resolve({source:ref?.source, quote:ref?.quote}, 'marketReference');
  if (!finitePositive(ref?.amount) || ref?.currency !== 'USD' || ref?.unit !== 'troy ounce' || !marketProof || !hasNumber(marketProof.text, ref.amount)) addError('marketReference', 'dated dealer reference unsupported');
  if (!Number.isFinite(Date.parse(ref?.publishedAt)) || Date.parse(ref.publishedAt) > now + 300000) addError('marketReference', 'invalid/future quote time');
  if (catalog.meta?.benchmark?.amount !== null || catalog.meta?.benchmark?.source !== 'lbma-prices') addError('benchmark', 'no numeric licensed benchmark was established; must remain null');
  if (!catalog.meta?.pricePolicy?.includes('No hallucinations') || !catalog.meta?.scope || catalog.meta?.freshnessHours !== 24) addError('meta', 'missing no-hallucinations/scope/freshness policy');
  return {errors, warnings, counts:{products:ids.size, sources:sources.size, findings:findingIds.size, purchaseReady:catalog.products.filter(isPurchaseReady).length}};
}
export async function saveReport(name, data) {
  await mkdir(path.join(ROOT, 'test-results'), {recursive:true});
  await writeFile(path.join(ROOT, 'test-results', name), JSON.stringify(data, null, 2) + '\n');
}
