import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';

// Prevent future builds from silently dropping the review's critical limitation.
test('every public dashboard page discloses unverified current prices', async () => {
  const roots = ['.', 'site', 'dashboard', 'explore'];
  let checked = 0;
  async function walk(dir, recurse) {
    for (const entry of await readdir(dir, {withFileTypes:true})) {
      const path = `${dir}/${entry.name}`;
      if (entry.isDirectory() && recurse) await walk(path, true);
      if (!entry.isFile() || !entry.name.endsWith('.html')) continue;
      const html = await readFile(path, 'utf8');
      assert.ok(html.includes('Freshness review · 2026-11-11'), path);
      assert.ok(html.includes('Current prices and availability are unverified.'), path);
      assert.ok(html.includes('flags.html#freshness-review'), path);
      checked++;
    }
  }
  for (const dir of roots) await walk(dir, dir === 'explore');
  assert.equal(checked, 46);
  const flags = await readFile('flags.html', 'utf8');
  assert.ok(flags.includes('id="freshness-review"'));
  assert.ok(flags.includes('No live official product, policy, gold-price, or regulatory page was retrieved'));
});
