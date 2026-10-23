import http from 'node:http';
import path from 'node:path';
import {readFile, stat, realpath} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {ROOT} from './lib.mjs';
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.md':'text/plain; charset=utf-8','.txt':'text/plain; charset=utf-8'};
export function createPreviewServer(root = ROOT) {
  return http.createServer(async (req,res) => {
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Referrer-Policy','no-referrer');
    res.setHeader('Cache-Control','no-store');
    if (!['GET','HEAD'].includes(req.method)) {res.setHeader('Allow','GET, HEAD');res.writeHead(405);return res.end('Method not allowed');}
    try {
      const raw = (req.url ?? '/').split('?')[0];
      if (raw.length > 4096 || !raw.startsWith('/')) throw new Error('Invalid URL');
      let pathname = decodeURIComponent(raw);
      if (pathname.includes('\\') || pathname.includes('\0') || pathname.includes('%') || pathname.split('/').some(p => p.startsWith('.') || p === 'node_modules')) {
        res.writeHead(403);return res.end('Not public');
      }
      if (pathname === '/GOLD2') {res.writeHead(302,{Location:'/GOLD2/'});return res.end();}
      if (pathname.startsWith('/GOLD2/')) pathname = pathname.slice('/GOLD2'.length);
      let filename = path.resolve(root, '.' + pathname);
      const inside = candidate => candidate === root || candidate.startsWith(root + path.sep);
      if (!inside(filename)) {res.writeHead(403);return res.end('Not public');}
      let info;
      try {info = await stat(filename);} catch {}
      if (info?.isDirectory()) filename = path.join(filename,'index.html');
      let status = 200;
      try {
        if (!inside(await realpath(filename))) {res.writeHead(403);return res.end('Not public');}
        if (!(await stat(filename)).isFile()) throw new Error('Not a file');
      } catch {filename = path.join(root,'explore/404.html');status = 404;}
      const type = types[path.extname(filename)];
      if (!type) {res.writeHead(403);return res.end('Not public');}
      const data = await readFile(filename);
      res.writeHead(status,{'Content-Type':type,'Content-Length':data.length});
      res.end(req.method === 'HEAD' ? undefined : data);
    } catch {res.writeHead(400);res.end('Bad request');}
  });
}
if (path.resolve(process.argv[1] ?? '') === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT ?? 4173);
  const server = createPreviewServer();
  server.listen(port,'0.0.0.0',() => console.log(`GOLD research dashboard listening on 0.0.0.0:${server.address().port}`));
  for (const signal of ['SIGINT','SIGTERM']) process.on(signal,()=>server.close(()=>process.exit(0)));
}
