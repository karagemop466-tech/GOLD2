import {readFile,readdir} from 'node:fs/promises';
import path from 'node:path';
import {ROOT,loadJSON,saveReport} from './lib.mjs';
const manifest=await loadJSON('data/site-manifest.json');
const rootPages=['index','solid-gold','solitaire','halo-pave','three-stone-vintage','18k','budget','retailers','prices','flags','methods'].map(p=>p+'.html');
const pages=[...rootPages,...manifest.pages,...['index','rings','calculator','checklist','flagged','sources'].map(p=>'site/'+p+'.html')];
const errors=[];
for(const file of pages){
 const text=await readFile(path.join(ROOT,file),'utf8');
 const csp=text.match(/http-equiv="Content-Security-Policy" content="([^"]+)"/i)?.[1];
 if(!csp||!csp.includes("script-src 'self'")||!csp.includes("object-src 'none'")||!csp.includes("base-uri 'none'")||!csp.includes("form-action 'none'"))errors.push(file+': missing restrictive CSP');
 if(/\sstyle=["']/.test(text))errors.push(file+': inline style blocked by CSP');
 if(/unsafe-inline|unsafe-eval/.test(csp??''))errors.push(file+': unsafe CSP exception');
 if(/<[^>]+\son[a-z]+\s*=/i.test(text))errors.push(file+': inline event handler');
 if(/(?:href|src)\s*=\s*["']\s*(?:javascript:|data:|http:|\/\/)/i.test(text))errors.push(file+': dangerous/non-HTTPS URL');
 for(const script of text.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){
  if(!/\bsrc="[^":]+"/.test(script[1])||script[2].trim())errors.push(file+': non-local or inline executable script');
 }
 for(const resource of text.matchAll(/<(?:link|img|iframe|object|embed)\b[^>]*(?:src|href)="([^"]+)"/gi))if(/^(?:https?:)?\/\//.test(resource[1]))errors.push(file+': external runtime resource');
 if(/<iframe|<object|<embed/i.test(text))errors.push(file+': unnecessary embedded active content');
 if(/target="_blank"/.test(text)&&!text.includes('noopener'))errors.push(file+': unsafe opener');
}
const runtime=['explore/assets/app.mjs','explore/assets/domain.mjs','site/app.js','assets/calculator.js'];
for(const file of runtime){
 const text=await readFile(path.join(ROOT,file),'utf8');
 if(/\beval\s*\(|new\s+Function\s*\(|\.innerHTML\s*=|document\.write\s*\(/.test(text))errors.push(file+': unsafe code/HTML sink');
 if(/fetch\s*\(\s*["'`]https?:/i.test(text))errors.push(file+': external runtime fetch');
 if(/localhost|127\.0\.0\.1/.test(text))errors.push(file+': browser-facing loopback URL');
 if(/localStorage|sessionStorage|document\.cookie/.test(text))errors.push(file+': unnecessary persistence');
}
const workflows=await readdir(path.join(ROOT,'.github/workflows'));
for(const file of workflows.filter(f=>/\.ya?ml$/.test(f))){
 const text=await readFile(path.join(ROOT,'.github/workflows',file),'utf8');
 for(const m of text.matchAll(/\buses:\s*([^\s#]+)/g))if(!/@[a-f0-9]{40}$/.test(m[1]))errors.push(file+': action not pinned to a full commit '+m[1]);
 if(/pull_request_target|permissions:\s*write-all/.test(text))errors.push(file+': excessive untrusted workflow permission');
}
async function walk(dir){let files=[];for(const d of await readdir(path.join(ROOT,dir),{withFileTypes:true})){if(d.name.startsWith('.')&&d.name!=='.github')continue;const file=path.posix.join(dir,d.name);if(d.isDirectory())files.push(...await walk(file));else if(/\.(?:mjs|js|json|py|md|ya?ml|html|css|svg)$/.test(d.name))files.push(file);}return files;}
const scanFiles=[...new Set([...(await walk('explore/assets')),...(await walk('data')),...(await walk('research')),...(await walk('scripts')),...(await walk('docs')),...(await walk('tools')),...(await walk('tests')),...(await walk('evidence')),...(await walk('site')),...(await walk('assets')),...(await walk('.github')),'README.md','COORDINATION.md'])];
const secretPatterns=[/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,/gh[pousr]_[A-Za-z0-9]{25,}/,/github_pat_[A-Za-z0-9_]{30,}/,/AKIA[0-9A-Z]{16}/];
for(const file of scanFiles){const text=await readFile(path.join(ROOT,file),'utf8');if(secretPatterns.some(p=>p.test(text)))errors.push(file+': potential credential material');}
const pkg=await loadJSON('package.json');
if(Object.keys(pkg.dependencies??{}).length)errors.push('Runtime must remain dependency-free');
for(const [name,version]of Object.entries(pkg.devDependencies??{}))if(!/^\d+\.\d+\.\d+$/.test(version))errors.push(name+': development dependency not exact-pinned');
const report={checkedAt:new Date().toISOString(),pages:pages.length,runtimeFiles:runtime.length,sourceFilesScanned:scanFiles.length,workflows:workflows.length,errors,limitation:'Static risk checks and an independent npm audit are not a security guarantee or a factual-truth detector.'};
await saveReport('security.json',report);
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}else console.log(`PASS static security: ${pages.length} HTML pages, ${runtime.length} runtime files, ${scanFiles.length} source files and ${workflows.length} pinned workflows. Run npm audit separately; no guarantee of complete security.`);
