import test from 'node:test';
import assert from 'node:assert/strict';
import {loadResearch,validateResearch,escapeHTML,safeSourceURL,hasNumber} from '../scripts/lib.mjs';
const original=await loadResearch();
const check=(mutate)=> {const r=structuredClone({catalog:original.catalog,evidence:original.evidence,review:original.review});mutate(r);return validateResearch(r).errors;};
test('current record has no provenance consistency errors; gaps remain warnings',()=> {
  const r=validateResearch(original);assert.deepEqual(r.errors,[]);assert.ok(r.warnings.length>18);assert.equal(r.counts.products,32);assert.equal(r.counts.purchaseReady,0);
});
test('existing two Blue Nile records and all sixteen extension candidates are retained',()=> {
  const ids=new Set(original.catalog.products.map(p=>p.id));
  for(const id of ['bn-501480w14','bn-501480w14l','ag-natural','ag-24k','av-clean','av-bridge','mene-knot','cb-odile','quince-oval'])assert.ok(ids.has(id));
});
test('combined register covers every original root URL exactly once',async()=>{
  const {readdir,readFile}=await import('node:fs/promises');
  const urls=original.catalog.products.map(p=>original.sourceMap.get(p.source).url);
  assert.equal(new Set(urls).size,32);
  for(const file of await readdir(new URL('../data/listings/',import.meta.url))){
    const d=JSON.parse(await readFile(new URL('../data/listings/'+file,import.meta.url),'utf8'));
    for(const p of d.items)assert.equal(urls.filter(u=>u===p.source_url).length,1,p.id);
  }
  assert.equal(original.catalog.products.find(p=>p.id==='ext-be-121h6').category,'settings');
});
test('invented or mismatched prices are rejected',()=> {
  assert.ok(check(r=>r.catalog.products[0].price.amount=1726).some(e=>e.includes('price amount')));
  assert.ok(check(r=>r.catalog.products[0].price.currency='CAD').some(e=>e.includes('price/scope/currency')));
  assert.ok(check(r=>r.catalog.products[0].price.evidence=[{source:'ag-natural',quote:'price'}]).some(e=>e.includes('currency context')));
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
