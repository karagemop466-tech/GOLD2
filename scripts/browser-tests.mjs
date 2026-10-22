import {chromium as playwrightChromium,expect} from '@playwright/test';
import chromium, {inflate,setupLambdaEnvironment} from '@sparticuz/chromium';
import {fileURLToPath} from 'node:url';
import AxeBuilder from '@axe-core/playwright';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';
import {ROOT,loadResearch,loadJSON,saveReport} from './lib.mjs';
import {createPreviewServer} from './serve.mjs';
import {calculateScenario} from '../explore/assets/domain.mjs';

const server=createPreviewServer();
await new Promise(resolve=>server.listen(0,'0.0.0.0',resolve));
const origin='http://127.0.0.1:'+server.address().port;
const base=origin+'/GOLD2/';
const dashboard=base+'explore/';
const errors=[],violations=[],requests=[];
let browser;
try{
 // The npm bundle supplies NSS/NSPR for minimal Debian sandboxes as well as Lambda.
 const packageDir=path.dirname(fileURLToPath(import.meta.resolve('@sparticuz/chromium')));
 const libs=await inflate(path.resolve(packageDir,'../bin/al2023.tar.br'));
 setupLambdaEnvironment(path.join(libs,'lib'));
 const args=chromium.args.filter(a=>!['--disable-web-security','--allow-running-insecure-content','--disable-site-isolation-trials','--single-process'].includes(a)&&!a.startsWith('--disable-features='));
 browser=await playwrightChromium.launch({headless:true,executablePath:await chromium.executablePath(),args});
 const context=await browser.newContext({viewport:{width:1440,height:1050}});
 const page=await context.newPage();
 page.on('pageerror',error=>errors.push(error.message));
 page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
 page.on('request',request=>{if(!request.url().startsWith(origin+'/'))requests.push(request.url());});
 const manifest=await loadJSON('data/site-manifest.json');
 const routes=manifest.pages.map(p=>p==='index.html'?'':p.replace(/index\.html$/,''));
 for(const route of routes){
  const response=await page.goto(base+route,{waitUntil:'networkidle'});
  expect(response.status()).toBe(200);await expect(page.locator('#policy-heading')).toHaveText('No hallucinations. No invented prices.');
  const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  for(const v of result.violations)violations.push({route,id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);
  expect(overflow,'desktop page overflow '+route).toBe(false);
 }
 await page.goto(dashboard,{waitUntil:'networkidle'});
 await mkdir(path.join(ROOT,'test-results'),{recursive:true});
 await page.screenshot({path:path.join(ROOT,'test-results/desktop.png'),fullPage:true});
 // All researched entries and their primary publisher links are available without filtering.
 await page.goto(dashboard+'catalog/',{waitUntil:'networkidle'});
 await expect(page.locator('#research-table tbody tr')).toHaveCount(32);
 await expect(page.locator('#research-table tbody tr a.source-link')).toHaveCount(32);
 await page.locator('#catalog-search').fill('ruby');
 await expect(page.locator('#filter-status')).toHaveText('1 of 32 entries shown');
 await page.locator('#catalog-search').fill('<img src=x onerror=alert(1)>');
 await expect(page.locator('#filter-status')).toHaveText('0 of 32 entries shown');
 await expect(page.locator('#no-results')).toBeVisible();
 await page.locator('#clear-filters').click();
 await page.locator('#category-filter').selectOption('gemstone');
 await expect(page.locator('#filter-status')).toHaveText('3 of 32 entries shown');
 await page.locator('#seller-filter').selectOption('catbird');
 await expect(page.locator('#filter-status')).toHaveText('0 of 32 entries shown');
 await page.locator('#clear-filters').click();
 await expect(page.locator('#filter-status')).toHaveText('32 of 32 entries shown');
 // Every documented product blocks automatic valuation, including the mixed-metal listing.
 const {catalog}=await loadResearch();
 await page.goto(dashboard+'calculator/',{waitUntil:'networkidle'});
 for(const p of catalog.products){
  await page.locator('#ring-choice').selectOption(p.id);
  await expect(page.locator('#auto-fine')).toHaveText('');
  await expect(page.locator('#auto-value')).toHaveText('');
  await expect(page.locator('#automatic-reason')).toContainText('No independently verified');
 }
 await page.locator('#scenario-mode').click();
 await page.locator('#scenario-form button[type=submit]').click();
 await expect(page.locator('#scenario-error')).toContainText('Acknowledge');
 await page.locator('#load-source-scenario').click();
 await expect(page.locator('#scenario-provenance')).toContainText('NET basis is NOT established');
 await expect(page.locator('#scenario-ack')).not.toBeChecked();
 await expect(page.locator('#scenario-output')).toBeHidden();
 await page.locator('#scenario-ack').check();
 await page.locator('#scenario-form button[type=submit]').click();
 const result=calculateScenario({weight:11,fineness:0.9999,spotPerOz:catalog.meta.marketReference.amount,retail:3520,acknowledged:true});
 await expect(page.locator('#scenario-fine')).toHaveText('10.9989 g');
 await expect(page.locator('#scenario-value')).toHaveText(new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(result.metalValue)+' USD');
 await expect(page.locator('#scenario-output')).toBeVisible();
 const conditionalAxe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
 for(const v of conditionalAxe.violations)violations.push({route:'calculator/conditional',id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))});
 await page.locator('#scenario-weight').fill('Infinity');
 await expect(page.locator('#scenario-output')).toBeHidden();
 await page.locator('#scenario-form button[type=submit]').click();
 await expect(page.locator('#scenario-error')).toContainText('positive gold-alloy-only weight');
 // Do not require an optional retail assumption. Nominal 14/24 remains distinct from 0.585.
 await page.locator('#scenario-weight').fill('11');
 await page.locator('#purity-basis').selectOption('nominal');
 await page.locator('#scenario-karat').fill('14');
 await page.locator('#scenario-retail').fill('');
 await page.locator('#scenario-form button[type=submit]').click();
 await expect(page.locator('#scenario-ratio')).toHaveText('');
 await expect(page.locator('#scenario-fine')).toHaveText('6.416667 g');
 await page.screenshot({path:path.join(ROOT,'test-results/calculator.png'),fullPage:true});
 // Staleness is a clock-based warning, not a silent price refresh.
 const stalePage=await context.newPage();
 await stalePage.clock.install({time:new Date('2026-11-24T00:00:00Z')});
 await stalePage.goto(dashboard+'catalog/',{waitUntil:'networkidle'});
 await expect(stalePage.locator('[data-observed]').first()).toHaveText('stale snapshot — recheck');
 await stalePage.close();
 // Responsive layout and the /GOLD2/ prefix are exercised in a real browser.
 const mobileContext=await browser.newContext({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1});
 const mobile=await mobileContext.newPage();
 for(const route of ['', 'catalog/','calculator/','review/']){
  await mobile.goto(dashboard+route,{waitUntil:'networkidle'});
  expect(await mobile.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1),'mobile overflow '+route).toBe(false);
  const a=await new AxeBuilder({page:mobile}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  for(const v of a.violations)violations.push({route:'mobile/'+route,id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))});
 }
 await mobile.goto(dashboard,{waitUntil:'networkidle'});await mobile.screenshot({path:path.join(ROOT,'test-results/mobile.png'),fullPage:true});
 await mobileContext.close();
 // Static research is complete without JavaScript; calculator never invents a fallback result.
 const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:1280,height:900}});
 const staticPage=await noJs.newPage();
 await staticPage.goto(dashboard+'catalog/');await expect(staticPage.locator('#research-table tbody tr')).toHaveCount(32);
 await staticPage.goto(dashboard+'calculator/');expect(await staticPage.locator('noscript').evaluate(n=>n.textContent)).toContain('Product gold values remain blank');
 await noJs.close();
 // Retained dashboard remains functional and its CommonJS unit tests remain compatible.
 for(const route of ['site/','site/rings.html','site/calculator.html','site/checklist.html','site/flagged.html','site/sources.html']){
  const r=await page.goto(base+route,{waitUntil:'networkidle'});expect(r.status()).toBe(200);await expect(page.locator('body')).toContainText('No hallucinations. No invented prices.');
 }
 for(const root of ['index','solitaire','halo-pave','three-stone-vintage','18k','budget','retailers','prices','flags','methods']){
  const response=await page.goto(base+root+'.html',{waitUntil:'networkidle'});expect(response.status()).toBe(200);
  await expect(page.locator('main')).toContainText('No hallucinations. No invented prices.');
  await expect(page.locator('main a[href="explore/"]')).toHaveCount(1);
  expect(await page.locator('script:not([src])').count()).toBe(0);
  const css=await page.locator('body').evaluate(el=>getComputedStyle(el).fontFamily);expect(css).toContain('system-ui');
 }
 await page.goto(base+'prices.html');await expect(page.locator('input')).toHaveCount(0);await expect(page.locator('a[href="explore/calculator/"]')).toBeVisible();
 await context.close();
 if(requests.length)errors.push('Unexpected external runtime requests: '+requests.join(', '));
 if(violations.length)errors.push(`${violations.length} automated accessibility violations (see report)`);
 if(errors.length)throw new Error(errors.join('\n'));
 console.log(`PASS browser: ${routes.length} expanded pages + 16 preserved/root pages, desktop/mobile, all 32 automatic gates, filters, conditional calculator, stale warning, no-JS research and zero external runtime requests. Automated axe checks found no WCAG A/AA violations in exercised states; this is not a full accessibility certification.`);
}catch(error){errors.push(error.message);console.error(error.stack??error);process.exitCode=1;}
finally{
 await saveReport('browser.json',{checkedAt:new Date().toISOString(),errors:[...new Set(errors)],violations,externalRuntimeRequests:requests,limitation:'Chromium and automated axe checks only. Not a cross-browser, manual assistive-technology, factual-truth or physical-product certification.'});
 if(browser)await browser.close();
 await new Promise(resolve=>server.close(resolve));
}
