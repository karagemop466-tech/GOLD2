import test from 'node:test';
import assert from 'node:assert/strict';
import {TROY_OUNCE_GRAMS,nominalFineness,pricePerGram,calculateScenario,automaticGold,isPurchaseReady,parseNumber,freshness} from '../explore/assets/domain.mjs';
import {loadResearch} from '../scripts/lib.mjs';
const {catalog} = await loadResearch();
test('NIST conversion uses troy ounces, not ordinary ounces',()=> {
  assert.equal(TROY_OUNCE_GRAMS,31.1034768);
  assert.equal(pricePerGram(TROY_OUNCE_GRAMS),1); // Synthetic unit identity, not a market quote.
});
test('nominal karat and explicit fineness are distinct',()=> {
  assert.equal(nominalFineness(14),14/24); assert.notEqual(nominalFineness(14),0.585);
  assert.equal(nominalFineness(24),1); assert.notEqual(nominalFineness(24),0.9999);
  for (const input of [0,-1,25,Infinity,NaN,null,undefined,'14']) assert.equal(nominalFineness(input),null);
});
test('conditional calculations require explicit acknowledgement',()=> {
  assert.equal(calculateScenario({weight:11,fineness:0.9999,spotPerOz:catalog.meta.marketReference.amount}).ok,false);
});
test('documented conditional preset uses unrounded inputs and has no automatic catalog effect',()=> {
  const result=calculateScenario({weight:11,fineness:0.9999,spotPerOz:catalog.meta.marketReference.amount,retail:3520,acknowledged:true});
  assert.equal(result.ok,true);assert.equal(result.fineGrams,11*0.9999);
  assert.equal(result.metalValue,11*0.9999*(4039.76/31.1034768));
  assert.equal(result.ratio,3520/result.metalValue);
  assert.match(result.classification,/Conditional/);
});
test('invalid or excessive numbers never produce gold values',()=> {
  const valid={weight:11,fineness:0.9999,spotPerOz:4039.76,acknowledged:true};
  for (const field of ['weight','fineness','spotPerOz']) for (const v of [0,-1,NaN,Infinity,-Infinity,'1',null,undefined]) assert.equal(calculateScenario({...valid,[field]:v}).ok,false,field+' '+v);
  assert.equal(calculateScenario({...valid,fineness:1.01}).ok,false);
  assert.equal(calculateScenario({...valid,weight:100001}).ok,false);
  assert.equal(calculateScenario({...valid,spotPerOz:1e10}).ok,false);
  assert.equal(calculateScenario({...valid,retail:-1}).ok,false);
  assert.equal(calculateScenario({...valid}).ratio,null);
});
test('all products block automatic fine-gold and valuation; no gross-weight fallback',()=> {
  assert.equal(catalog.products.length,32);
  for (const p of catalog.products) {
    assert.equal(automaticGold(p).fineGrams,null,p.id);
    assert.equal(automaticGold(p).metalValue,null,p.id);
    assert.equal(isPurchaseReady(p),false,p.id);
  }
  const p=structuredClone(catalog.products[0]);p.facts.itemWeightG.value=100;
  assert.equal(automaticGold(p).fineGrams,null);
});
test('numeric form parsing never converts missing input to zero',()=> {
  for (const s of ['',' ','1e3','Infinity','NaN','0x10','1,000','-1','+1','11g','<script>','1.2.3']) assert.equal(parseNumber(s),null,s);
  assert.equal(parseNumber('0'),0);assert.equal(parseNumber('.5'),0.5);assert.equal(parseNumber(' 11.25 '),11.25);
});
test('stale and future observations are explicit and never refreshed implicitly',()=> {
  const then='2026-10-22T23:09:00Z',t=Date.parse(then);
  assert.equal(freshness(then,t),'dated-snapshot');
  assert.equal(freshness(then,t+24*3600000),'dated-snapshot');
  assert.equal(freshness(then,t+24*3600000+1),'stale');
  assert.equal(freshness(then,t-6*60000),'future-dated');
  assert.equal(freshness('not-a-date',t),'unverified');
});
