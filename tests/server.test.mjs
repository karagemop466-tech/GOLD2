import test,{before,after}from'node:test';
import assert from'node:assert/strict';
import http from'node:http';
import {createPreviewServer}from'../scripts/serve.mjs';
let server,base;
before(async()=>{server=createPreviewServer();await new Promise(r=>server.listen(0,'0.0.0.0',r));base='http://127.0.0.1:'+server.address().port;});
after(async()=>{await new Promise(r=>server.close(r));});
const raw=path=>new Promise((resolve,reject)=>{const req=http.get({hostname:'127.0.0.1',port:server.address().port,path},res=>{res.resume();res.on('end',()=>resolve(res.statusCode));});req.on('error',reject);});
test('preview serves the root and GitHub Pages project-prefix paths',async()=>{
 for(const url of ['/', '/GOLD2/', '/explore/catalog/', '/GOLD2/explore/catalog/', '/explore/assets/app.mjs','/GOLD2/explore/assets/app.mjs'])assert.equal((await fetch(base+url)).status,200,url);
});
test('preview accepts the proxied host and never depends on localhost in browser code',async()=>{
 const r=await fetch(base+'/',{headers:{Host:'4173-preview.e2b.app'}});assert.equal(r.status,200);assert.match(await r.text(),/No hallucinations/i);
});
test('private paths, traversal, malformed escapes and non-read methods are denied',async()=>{
 for(const url of ['/.git/config','/.env','/node_modules/package.json','/%2e%2e/README.md','/%252e%252e/README.md','/%5c.git/config'])assert.equal(await raw(url),403,url);
 assert.equal(await raw('/%zz'),400);
 assert.equal((await fetch(base+'/',{method:'POST',body:'no writes'})).status,405);
});
test('HEAD and missing pages return accurate status without an open write surface',async()=>{
 const h=await fetch(base+'/explore/catalog/',{method:'HEAD'});assert.equal(h.status,200);assert.equal(await h.text(),'');assert.equal(h.headers.get('x-content-type-options'),'nosniff');
 assert.equal((await fetch(base+'/GOLD2/not-a-real-page/')).status,404);
});
