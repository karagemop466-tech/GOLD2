import test from 'node:test';
import assert from 'node:assert/strict';
import {loadResearch,validateResearch,escapeHTML,safeSourceURL,hasNumber} from '../scripts/lib.mjs';
const original=await loadResearch();
const check=(mutate)=> {const r=structuredClone({catalog:original.catalog,evidence:original.evidence,review:original.review});mutate(r);return validateResearch(r).errors;};
test('current record has no provenance consistency errors; gaps remain warnings',()=> {
  const r=validateResearch(original);assert.deepEqual(r.errors,[]);assert.ok(r.warnings.length>18);assert.equal(r.counts.products,44);assert.equal(r.counts.purchaseReady,0);
});
test('existing two Blue Nile records and all sixteen extension candidates are retained',()=> {
  const ids=new Set(original.catalog.products.map(p=>p.id));
  for(const id of ['bn-501480w14','bn-501480w14l','ag-natural','ag-24k','av-clean','av-bridge','mene-knot','cb-odile','quince-oval'])assert.ok(ids.has(id));
});
test('combined register covers every root URL exactly once',async()=>{
  const {readdir,readFile}=await import('node:fs/promises');
  const urls=original.catalog.products.map(p=>original.sourceMap.get(p.source).url);
  assert.equal(new Set(urls).size,44);
  const files=(await readdir(new URL('../data/listings/',import.meta.url))).map(file=>'../data/listings/'+file);
  files.push('../data/solid-gold-verified.json');
  for(const file of files){
    const d=JSON.parse(await readFile(new URL(file,import.meta.url),'utf8'));
    for(const p of d.items)assert.equal(urls.filter(u=>u===p.source_url).length,1,p.id);
  }
  assert.equal(original.catalog.products.find(p=>p.id==='ext-be-121h6').category,'settings');
  assert.ok(original.catalog.sellers.some(s=>s.id==='mejuri'));
});
test('invented or mismatched prices are rejected',()=> {
  assert.ok(check(r=>r.catalog.products[0].price.amount=1726).some(e=>e.includes('price amount')));
  assert.ok(check(r=>r.catalog.products[0].price.currency='CAD').some(e=>e.includes('price/scope/currency')));
  assert.ok(check(r=>r.catalog.products[0].price.evidence=[{source:'ag-natural',quote:'price'}]).some(e=>e.includes('currency context')));
});
test('raw displays never become structured currency and current corrections stay bound',()=> {
  const m=original.catalog.products.find(p=>p.id==='mj-bold-eternity');
  assert.equal(m.price,null);assert.equal(m.observedNativeDisplay.text,'From$2,900');assert.equal(m.observedNativeDisplay.currency,null);
  assert.ok(check(r=>r.catalog.products.find(p=>p.id==='mj-bold-eternity').observedNativeDisplay.currency='USD').some(e=>e.includes('raw native display')));
  assert.ok(check(r=>r.catalog.products.find(p=>p.id==='mj-bold-eternity').observedNativeDisplay.text='$2,900').some(e=>e.includes('differs from cited passage')));
  assert.equal(original.catalog.products.find(p=>p.id==='mene-rose').price.amount,1325);
  assert.equal(original.catalog.products.find(p=>p.id==='mene-knot').price.amount,1442);
  assert.match(original.catalog.products.find(p=>p.id==='ext-bn-316238').name.value,/Comfort Fit/);
});
test('Automic variant ranges retain default scope and require HTML plus JSON endpoints',()=> {
  const coffin=original.catalog.products.find(p=>p.id==='ag-coffin');
  const cushion=original.catalog.products.find(p=>p.id==='ag-cushion');
  assert.equal(coffin.price.amount,1910);assert.deepEqual([coffin.observedVariantPriceRange.min,coffin.observedVariantPriceRange.max],[1910,2233]);
  assert.equal(cushion.price.amount,2758);assert.deepEqual([cushion.observedVariantPriceRange.min,cushion.observedVariantPriceRange.max],[2408,3253]);
  assert.ok(check(r=>r.catalog.products.find(p=>p.id==='ag-cushion').observedVariantPriceRange.endpoints.pop()).some(e=>e.includes('minimum/maximum')));
  assert.ok(check(r=>r.catalog.products.find(p=>p.id==='ag-coffin').observedVariantPriceRange.rangeEvidence={source:'ag-coffin',quote:'price'}).some(e=>e.includes('variant JSON')));
});
test('FDJ price and currency passages stay separate and gross weight is not net metal',()=> {
  const p=original.catalog.products.find(p=>p.id==='fdj-gr0001');
  assert.deepEqual(p.price.evidence.map(x=>x.quote),['price','currency']);
  assert.equal(original.sourceMap.get('fdj-gr0001').quotes.price,'$1,299.99');
  assert.equal(original.sourceMap.get('fdj-gr0001').quotes.currency,'USD');
  assert.equal(p.reportedWeight.basis,'item');assert.equal(p.facts.netMetalWeightG,null);
});
test('shipping/item weight cannot be relabeled net alloy weight',()=> {
  assert.ok(check(r=>r.catalog.products[0].facts.netMetalWeightG={value:1.2,source:'ag-natural',quote:'weight'}).some(e=>e.includes('metal-only basis')));
  assert.ok(check(r=>r.catalog.products[0].facts.itemWeightG.value=12).some(e=>e.includes('numeric evidence mismatch')));
});
test('source omissions, duplicate IDs, review-platform facts and seller mismatches fail',()=> {
  assert.ok(check(r=>r.catalog.products[0].facts.karat.source='missing').length);
  assert.ok(check(r=>delete r.catalog.products[0].facts.netMetalWeightG).length);
  assert.ok(check(r=>r.catalog.products[1].id=r.catalog.products[0].id).length);
  assert.ok(check(r=>r.catalog.products[0].facts.karat={value:14,source:'bbb-automic',quote:'name'}).some(e=>e.includes('review platforms')));
  assert.ok(check(r=>r.catalog.products[0].seller='catbird').some(e=>e.includes('seller/source mismatch')));
});
test('no fabricated LBMA quote or unsupported purity substitution',()=> {
  assert.ok(check(r=>r.catalog.meta.benchmark.amount=4039.76).length);
  const i=original.catalog.products.findIndex(p=>p.id==='ag-24k');
  assert.ok(check(r=>r.catalog.products[i].facts.declaredPurity.value=1).some(e=>e.includes('purity')));
});
test('publisher allowlist is exact, HTTPS only, and disallows embedded credentials',()=> {
  for(const url of ['javascript:alert(1)','https://www.automicgold.com.evil.example/a','http://www.automicgold.com/','https://name:pass@www.automicgold.com/']) assert.equal(safeSourceURL(url),false);
  assert.equal(safeSourceURL('https://www.automicgold.com/products/diamond-ring'),true);
});
test('escape rendered fields, and do not match unrelated numeric substrings',()=> {
  assert.equal(escapeHTML('<img src=x onerror="bad">'), '&lt;img src=x onerror=&quot;bad&quot;&gt;');
  assert.equal(hasNumber('€990.00(Setting Only)',990),true);
  assert.equal(hasNumber('€990.01',990),false);assert.equal(hasNumber('1.20g',1.2),true);assert.equal(hasNumber('1.201g',1.2),false);
  assert.equal(hasNumber('$1,726',726),false);assert.equal(hasNumber('$726',726),true);
  assert.equal(hasNumber('11.2 grams',1.2),false);assert.equal(hasNumber('1.2g',1.2),true);
});
