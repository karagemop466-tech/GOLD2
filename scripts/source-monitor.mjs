// Reachability/identity signals only. Never writes catalog or source observations.
import {createHash} from 'node:crypto';
import {loadResearch,safeSourceURL,saveReport} from './lib.mjs';
const {catalog,evidence}=await loadResearch();
const tasks=[...evidence.sources],results=[];
async function check(source){
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),15000);
 const result={id:source.id,url:source.url,recordedAccess:source.access,recordedObservation:source.observedAt,checkedAt:new Date().toISOString()};
 try{
  let url=source.url,response;
  for(let i=0;i<6;i++){
   if(!safeSourceURL(url))throw new Error('Redirect left the reviewed HTTPS publisher allowlist');
   response=await fetch(url,{redirect:'manual',signal:controller.signal,headers:{'User-Agent':'GOLD2-evidence-monitor/1.0; non-commercial research; no automated price updates'}});
   if([301,302,303,307,308].includes(response.status)){
    const next=response.headers.get('location');await response.body?.cancel();
    if(!next)throw new Error('Redirect lacks a location');url=new URL(next,url).href;response=null;
   }else break;
  }
  if(!response)throw new Error('Too many redirects');
  result.finalURL=url;result.status=response.status;
  const chunks=[];let size=0;const cap=1024*1024;
  if(response.body){for await(const chunk of response.body){size+=chunk.length;chunks.push(chunk);if(size>=cap){result.truncated=true;break;}}}
  const bytes=Buffer.concat(chunks).subarray(0,cap);result.sampleSHA256=createHash('sha256').update(bytes).digest('hex');result.sampleBytes=bytes.length;
  const content=bytes.toString('utf8').replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').toLowerCase();
  const product=catalog.products.find(p=>p.source===source.id);
  if(product){
   const words=product.name.value.toLowerCase().match(/[a-z]{4,}/g)??[];
   result.identityWordsMatched=words.filter(w=>content.includes(w)).length;
   result.identityWordsChecked=words.length;
  }
  result.signal=response.ok?'reachable — content not fact-certified':'HTTP issue — manual recheck needed';
 }catch(error){result.signal='unconfirmed — request failed';result.error=error.message;}
 finally{clearTimeout(timeout);results.push(result);}
}
await Promise.all(Array.from({length:4},async()=>{while(tasks.length)await check(tasks.shift());}));
results.sort((a,b)=>a.id.localeCompare(b.id));
const issues=results.filter(r=>!(r.status>=200&&r.status<300)||r.identityWordsMatched===0);
await saveReport('source-monitor.json',{checkedAt:new Date().toISOString(),checks:results.length,issues:issues.length,results,limitation:'HTTP/identity-word signals and a capped-page sample hash are not factual/price verification. Bot blocks, regional/JavaScript content and live panels cause false alarms. No baseline-content comparison or observation timestamp update is performed. Never purchase without directly rechecking the source and exact configuration.'});
console.log(`Source monitor completed: ${results.length} URLs; ${issues.length} HTTP/identity signals need review. Report: test-results/source-monitor.json. No facts or prices updated.`);
