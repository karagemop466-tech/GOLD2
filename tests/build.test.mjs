import test from'node:test';
import assert from'node:assert/strict';
import{execFile}from'node:child_process';
import{promisify}from'node:util';
import{readFile}from'node:fs/promises';
import{createHash}from'node:crypto';
import path from'node:path';
import{ROOT,loadJSON}from'../scripts/lib.mjs';
const exec=promisify(execFile);
async function fingerprint(){const m=await loadJSON('data/site-manifest.json');const h=createHash('sha256');for(const f of [...m.pages,'data/site-manifest.json'])h.update(await readFile(path.join(ROOT,f)));return h.digest('hex');}
test('static build is deterministic and does not renew observation timestamps',async()=>{
 const before=await readFile(path.join(ROOT,'data/catalog.json'),'utf8');
 await exec(process.execPath,['scripts/build.mjs'],{cwd:ROOT});const first=await fingerprint();
 await exec(process.execPath,['scripts/build.mjs'],{cwd:ROOT});assert.equal(await fingerprint(),first);
 assert.equal(await readFile(path.join(ROOT,'data/catalog.json'),'utf8'),before);
});
