#!/usr/bin/env node
// Publish a Patreon post the way James would in a browser, because Patreon's
// API cannot create posts. Uses the creator's logged-in session cookie
// (resolved by scripts/cs_secrets.py from 1Password) in a real Chromium.
//
//   node scripts/patreon_post.mjs --title "..." --body-file post.html \
//        [--image images/album/a.jpg --image images/album/b.jpg] [--dry-run]
//
// --dry-run fills everything in, saves tmp-build/patreon-post.png, and does
// not publish. A run reads the screenshot before publishing for real.
// Exit codes: 0 published (or dry run complete), 2 not logged in (cookie
// expired), 3 the editor did not look as expected (screenshot saved), 1 other.

import { execFileSync } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

// Playwright is installed globally in the sandbox; resolve it through
// require so NODE_PATH (set by bootstrap_run.sh to `npm root -g`) applies.
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const opt = { images: [], dryRun: false, title: '', bodyFile: '', audience: 'public' };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--title') opt.title = args[++i];
  else if (a === '--body-file') opt.bodyFile = args[++i];
  else if (a === '--image') opt.images.push(resolve(args[++i]));
  else if (a === '--audience') opt.audience = args[++i]; // public | patrons
  else if (a === '--dry-run') opt.dryRun = true;
}
if (!opt.title || !opt.bodyFile) {
  console.error('usage: patreon_post.mjs --title T --body-file F [--image PATH]... [--audience public|patrons] [--dry-run]');
  process.exit(1);
}
const bodyHtml = readFileSync(opt.bodyFile, 'utf8');

// Resolve the session cookie without ever printing it.
let cookie = process.env.PATREON_SESSION_COOKIE || '';
if (!cookie) {
  try {
    cookie = execFileSync('python3', ['scripts/cs_secrets.py', 'get', 'patreon_session'], { encoding: 'utf8' }).trim();
  } catch (e) {
    console.error('secrets: could not resolve patreon_session (see stderr above)');
    process.exit(2);
  }
}
if (!cookie) { console.error('ERROR: no Patreon session cookie available'); process.exit(2); }

mkdirSync('tmp-build', { recursive: true });
const shot = (name) => page.screenshot({ path: `tmp-build/${name}.png`, fullPage: true }).catch(() => {});

// The sandbox routes outbound HTTPS through a local proxy whose CA is in
// the system and NSS trust stores; Chromium only uses it if told to.
const proxyServer = process.env.HTTPS_PROXY || process.env.https_proxy || '';
const browser = await chromium.launch({ headless: true, ...(proxyServer ? { proxy: { server: proxyServer } } : {}) });
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36',
  viewport: { width: 1280, height: 900 },
});
await context.addCookies([{ name: 'session_id', value: cookie, domain: '.patreon.com', path: '/', httpOnly: true, secure: true }]);
const page = await context.newPage();

try {
  await page.goto('https://www.patreon.com/posts/new', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(4000);
  if (/\/login/.test(page.url()) || await page.getByRole('button', { name: /log in/i }).first().isVisible().catch(() => false)) {
    await shot('patreon-not-logged-in');
    console.error('NOT LOGGED IN: the session cookie has expired; refresh it in 1Password');
    process.exit(2);
  }

  // Title: Patreon's editor exposes a title field with a placeholder like "Title".
  const title = page.getByPlaceholder(/title/i).first();
  if (!(await title.isVisible().catch(() => false))) {
    await shot('patreon-editor-unexpected');
    console.error('EDITOR UNEXPECTED: no title field found; see tmp-build/patreon-editor-unexpected.png');
    process.exit(3);
  }
  await title.fill(opt.title);

  // Body: the first large contenteditable after the title.
  const editors = page.locator('[contenteditable="true"]');
  const body = editors.nth((await editors.count()) > 1 ? 1 : 0);
  await body.click();
  // Type plain text lines; Patreon's editor converts blank lines to paragraphs.
  const plain = bodyHtml.replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>/gi, '\n\n').replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').trim();
  await body.type(plain, { delay: 5 });

  // Images: any file input on the page accepts uploads.
  if (opt.images.length) {
    const input = page.locator('input[type="file"]').first();
    await input.setInputFiles(opt.images);
    await page.waitForTimeout(6000 + 2000 * opt.images.length);
  }

  // Audience: default is whatever the creator last used; "public" is the
  // choice for growth posts, "patrons" for patron-only updates.
  const audience = page.getByText(opt.audience === 'public' ? /^public$|everyone/i : /paid members|all members|patrons/i).first();
  if (await audience.isVisible().catch(() => false)) await audience.click().catch(() => {});

  await shot('patreon-post');
  if (opt.dryRun) { console.log('DRY RUN: filled in; screenshot at tmp-build/patreon-post.png'); process.exit(0); }

  const publish = page.getByRole('button', { name: /^publish( now)?$/i }).first();
  if (!(await publish.isVisible().catch(() => false))) {
    console.error('EDITOR UNEXPECTED: no Publish button; see tmp-build/patreon-post.png');
    process.exit(3);
  }
  await publish.click();
  await page.waitForTimeout(6000);
  await shot('patreon-published');
  const url = page.url();
  console.log(`PUBLISHED: ${url}`);
  process.exit(0);
} catch (e) {
  await shot('patreon-error');
  console.error(`ERROR: ${e.message}`);
  process.exit(1);
} finally {
  await browser.close();
}
