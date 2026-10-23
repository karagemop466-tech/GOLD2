import {readFile,stat} from 'node:fs/promises';
import path from 'node:path';
import {ROOT,loadJSON,saveReport,SOURCE_HOSTS} from './lib.mjs';
const manifest=await loadJSON('data/site-manifest.json');
const rootPages=['index','solid-gold','solitaire','halo-pave','three-stone-vintage','18k','budget','retailers','prices','flags','methods'].map(p=>p+'.html');
const pages=[...rootPages,...manifest.pages,...['index','rings','calculator','checklist','flagged','sources'].map(p=>'site/'+p+'.html')];
const allowed=new Set([...SOURCE_HOSTS,'www.ecfr.gov','www.jamesallen.com','www.costco.com','github.com']);
const errors=[],external=new Set(),internal=new Set();
const unescape=s=>s.replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll('&#39;',"'").replaceAll('&lt;','<').replaceAll('&gt;','>');
const content=new Map();
const get=async file=>{if(!content.has(file))content.set(file,await readFile(path.join(ROOT,file),'utf8'));return content.get(file);};
for(const page of pages){
 const text=await get(page);
 if(!text.includes('No hallucinations. No invented prices.'))errors.push(page+': missing policy');
 for(const match of text.matchAll(/\b(href|src)="([^"]*)"/g)){
  const link=unescape(match[2]);
  if(link.startsWith('https://')){
   try{const u=new URL(link);if(!allowed.has(u.hostname))errors.push(page+': unlisted external publisher '+u.hostname);external.add(link);}catch{errors.push(page+': bad URL '+link);}
   continue;
  }
  if(/^[a-z][a-z0-9+.-]*:/i.test(link)||link.startsWith('//')){errors.push(page+': unsupported URL scheme '+link);continue;}
  let [part,hash]=link.split('#');part=part.split('?')[0];
  if(part.startsWith('/GOLD2/'))part=part.slice('/GOLD2/'.length);
  else if(part.startsWith('/')){errors.push(page+': unexpected absolute path '+link);continue;}
  let target=part?path.posix.normalize(path.posix.join(link.startsWith('/GOLD2/')?'':path.posix.dirname(page),decodeURIComponent(part))):page;
  if(target==='..'||target.startsWith('../')){errors.push(page+': path escapes site '+link);continue;}
  try{if((await stat(path.join(ROOT,target))).isDirectory())target=path.posix.join(target,'index.html');await stat(path.join(ROOT,target));}catch{errors.push(page+': missing '+link+' -> '+target);continue;}
  internal.add(target);
  if(hash&&target.endsWith('.html')){
   const id=decodeURIComponent(hash);const html=await get(target);
   const escaped=id.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
   if(!new RegExp(`\\bid=["']${escaped}["']`).test(html))errors.push(page+': missing fragment '+link);
  }
 }
 for(const table of text.matchAll(/<tbody>([\s\S]*?)<\/tbody>/g)){
  for(const row of table[1].matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/g)){
   const links=[...row[1].matchAll(/href="(https:[^"]+)"/g)].map(m=>unescape(m[1]));
   if(!links.some(l=>allowed.has(new URL(l).hostname)))errors.push(page+': table row lacks an official publisher link');
  }
 }
}
const report={checkedAt:new Date().toISOString(),pages:pages.length,internalTargets:internal.size,externalPublisherURLs:external.size,errors,limitation:'Local targets/fragments and publisher URL structure only. External reachability is a separate, non-certifying source monitor.'};
await saveReport('links.json',report);
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}
else console.log(`PASS links: ${pages.length} pages, ${internal.size} local targets, ${external.size} external publisher URLs; every data-table row has an official publisher link. External HTTP status is not certified.`);
