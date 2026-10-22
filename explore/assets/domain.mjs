// Shared, dependency-free calculation and qualification rules. Inputs are not evidence.
export const TROY_OUNCE_GRAMS = 31.1034768;
export const CATEGORIES = Object.freeze([
  {id: 'natural', name: 'Natural diamonds', eyebrow: '01 / NATURAL', description: 'Natural-diamond rings and two-stage settings. A stone description does not authenticate the metal.'},
  {id: 'lab', name: 'Lab-grown diamonds', eyebrow: '02 / LAB-GROWN', description: 'Lab-grown-diamond options. Compare the exact selected stone, metal, size and complete-ring scope.'},
  {id: 'gemstone', name: 'Gemstones & moissanite', eyebrow: '03 / ALTERNATIVES', description: 'Ruby, sapphire and lab-created moissanite alternatives; no style or durability preference assumed.'},
  {id: 'bands', name: 'Bands & sculptural rings', eyebrow: '04 / ALTERNATIVES', description: 'Plain, decorative and diamond-accent alternatives. Not all are sold as conventional engagement rings.'}
]);
export const REQUIRED_FACTS = Object.freeze([
  'karat', 'solidGold', 'stone', 'itemWeightG', 'netMetalWeightG', 'fineGoldWeightG',
  'declaredPurity', 'hallmark', 'makerMark', 'independentTest', 'independentInspectionReturnPermission'
]);
export const factValue = (product, field) => product.facts[field]?.value ?? null;
export const finitePositive = n => typeof n === 'number' && Number.isFinite(n) && n > 0;
export function nominalFineness(karat) {
  return finitePositive(karat) && karat <= 24 ? karat / 24 : null;
}
export function pricePerGram(usdPerTroyOunce) {
  return finitePositive(usdPerTroyOunce) ? usdPerTroyOunce / TROY_OUNCE_GRAMS : null;
}
export function calculateScenario({weight, fineness, spotPerOz, retail = null, acknowledged = false}) {
  if (!acknowledged) return {ok: false, error: 'Acknowledge that all inputs are conditional assumptions, not verified product facts.'};
  if (!finitePositive(weight) || weight > 100000) return {ok: false, error: 'Enter a positive gold-alloy-only weight of at most 100,000 grams.'};
  if (!finitePositive(fineness) || fineness > 1) return {ok: false, error: 'Enter a fineness greater than 0 and at most 1, or choose a valid karat.'};
  if (!finitePositive(spotPerOz) || spotPerOz > 1e9) return {ok: false, error: 'Enter a positive USD-per-troy-ounce reference of at most 1,000,000,000.'};
  if (retail !== null && (!finitePositive(retail) || retail > 1e12)) return {ok: false, error: 'Optional retail price must be a positive USD amount of at most 1,000,000,000,000.'};
  const fineGrams = weight * fineness;
  const perGram = pricePerGram(spotPerOz);
  const metalValue = fineGrams * perGram;
  const ratio = retail === null ? null : retail / metalValue;
  return {ok: true, fineGrams, perGram, metalValue, ratio,
    difference: retail === null ? null : retail - metalValue,
    classification: 'Conditional calculation only — not a product fact, appraisal, or resale payout'};
}
export function automaticGold(product) {
  // Do not substitute gross/item weight, undefined fine-weight ranges, or nominal karat.
  const weight = factValue(product, 'netMetalWeightG');
  const purity = factValue(product, 'declaredPurity');
  const tested = factValue(product, 'independentTest') === true;
  if (!finitePositive(weight) || !finitePositive(purity) || purity > 1 || !tested) {
    return {fineGrams: null, metalValue: null, reason: 'No independently verified net gold-alloy weight and purity basis. Item grams are not an admissible substitute.'};
  }
  return {fineGrams: weight * purity, metalValue: null, reason: 'Calculated fine-gold mass from documented test inputs; no live benchmark supplied.'};
}
export function isPurchaseReady(product) {
  return finitePositive(factValue(product, 'karat')) && factValue(product, 'solidGold') === true
    && finitePositive(factValue(product, 'netMetalWeightG'))
    && factValue(product, 'hallmark') === true && factValue(product, 'makerMark') === true
    && factValue(product, 'independentTest') === true
    && factValue(product, 'independentInspectionReturnPermission') === true;
}
export function missingRequirements(product) {
  const labels = {
    karat: 'stated karat', solidGold: 'explicit solid gold', netMetalWeightG: 'net gold-alloy grams',
    hallmark: 'candidate karat hallmark', makerMark: 'maker/manufacturer mark',
    independentTest: 'independent purity/weight test', independentInspectionReturnPermission: 'inspection + return permission'
  };
  return Object.entries(labels).filter(([key]) => {
    const v = factValue(product, key);
    return key === 'karat' || key === 'netMetalWeightG' ? !finitePositive(v) : v !== true;
  }).map(([, label]) => label);
}
export function freshness(observedAt, now = Date.now(), hours = 24) {
  const observed = Date.parse(observedAt);
  if (!Number.isFinite(observed) || !Number.isFinite(now)) return 'unverified';
  if (observed > now + 300000) return 'future-dated';
  return now - observed > hours * 3600000 ? 'stale' : 'dated-snapshot';
}
export function parseNumber(value) {
  // Empty, comma-formatted, exponent, hex and non-finite input must never become a fabricated zero/number.
  if (typeof value !== 'string' || !/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(value.trim())) return null;
  const n = Number(value.trim());
  return Number.isFinite(n) ? n : null;
}
