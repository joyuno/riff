#!/usr/bin/env node
// riff-browse.mjs — gstack `browse` 어휘를 모방한 경량 브라우저 러너 (Playwright MCP 불필요)
//
// gstack의 `$B <command>`와 동일한 사용감: 한 명령 = 한 동작, 데몬이 페이지/요소맵/콘솔을
// 메모리에 유지하므로 두 번째 명령부터 ~100ms. 외부 MCP 서버도, 58MB 컴파일 바이너리도 없다.
// 유일한 의존성은 프로젝트의 playwright (없으면 `npx playwright install chromium`).
//
// 사용:
//   node riff-browse.mjs start [--headed]      # 데몬 기동, 포트를 .riff/session/에 기록
//   node riff-browse.mjs goto <url>
//   node riff-browse.mjs snapshot [-i] [-o shot.png]   # -i: 클릭/입력 가능 요소에 @e1.. 라벨
//   node riff-browse.mjs click @e5
//   node riff-browse.mjs fill @e3 "user@example.com"
//   node riff-browse.mjs text [selector]       # 보이는 텍스트
//   node riff-browse.mjs console [--errors]     # 콘솔 메시지(에러만 필터)
//   node riff-browse.mjs network [--errors]     # 4xx/5xx 응답
//   node riff-browse.mjs js "await fetch('/api/x').then(r=>r.status)"
//   node riff-browse.mjs links                  # 페이지 내 링크 맵
//   node riff-browse.mjs wait "주문 완료" [ms]
//   node riff-browse.mjs screenshot <path>
//   node riff-browse.mjs cookie-import <file>   # storageState JSON 주입
//   node riff-browse.mjs status
//   node riff-browse.mjs stop
//
// 상태(쿠키/로그인)는 .riff/session/state.json에 storageState로 영속 → 다음 저니에서 재로그인 불필요.

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const SESSION_DIR = path.resolve(process.env.RIFF_SESSION_DIR || '.riff/session');
const PORT_FILE = path.join(SESSION_DIR, 'riff-browse-port');
const STATE_FILE = path.join(SESSION_DIR, 'state.json');

// ───────────────────────────── 클라이언트 (대부분의 호출) ─────────────────────────────
function readPort() {
  try { return parseInt(fs.readFileSync(PORT_FILE, 'utf-8').trim(), 10); } catch { return null; }
}

function callDaemon(cmd, args) {
  return new Promise((resolve, reject) => {
    const port = readPort();
    if (!port) return reject(new Error('데몬 미기동 — 먼저 `node riff-browse.mjs start`'));
    const body = JSON.stringify({ cmd, args });
    const req = http.request(
      { host: '127.0.0.1', port, path: '/cmd', method: 'POST',
        headers: { 'content-type': 'application/json', 'content-length': Buffer.byteLength(body) } },
      (res) => {
        let buf = '';
        res.on('data', (d) => (buf += d));
        res.on('end', () => resolve(buf));
      },
    );
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ───────────────────────────── 데몬 (start) ─────────────────────────────
async function startDaemon(headed) {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
  const { chromium } = await import('playwright');
  const browser = await chromium.launch({ headless: !headed });
  const ctxOpts = {};
  if (fs.existsSync(STATE_FILE)) ctxOpts.storageState = STATE_FILE;
  const context = await browser.newContext(ctxOpts);
  const page = await context.newPage();

  const consoleLog = []; // {type, text}
  const network = [];    // {status, url, method}
  page.on('console', (m) => consoleLog.push({ type: m.type(), text: m.text() }));
  page.on('pageerror', (e) => consoleLog.push({ type: 'error', text: String(e) }));
  context.on('response', (r) => {
    const s = r.status();
    if (s >= 400) network.push({ status: s, url: r.url(), method: r.request().method() });
  });

  // 스냅샷이 부여한 @eN → 페이지 DOM의 data-riff-ref 속성으로 고정 (재호출 간 안정)
  async function snapshot(interactive, outPath) {
    let lines = [];
    if (interactive) {
      const els = await page.evaluate(() => {
        const sel = 'a,button,input,select,textarea,[role=button],[role=link],[role=tab],[onclick],[contenteditable=true]';
        const out = [];
        let n = 0;
        for (const el of document.querySelectorAll(sel)) {
          const r = el.getBoundingClientRect();
          const style = getComputedStyle(el);
          if (r.width === 0 || r.height === 0 || style.visibility === 'hidden' || style.display === 'none') continue;
          n += 1;
          const ref = 'e' + n;
          el.setAttribute('data-riff-ref', ref);
          const role = el.getAttribute('role') || el.tagName.toLowerCase();
          const name = (el.getAttribute('aria-label') || el.getAttribute('placeholder') ||
                        el.value || el.innerText || el.getAttribute('name') || '').trim().slice(0, 60);
          out.push(`@${ref} ${role} "${name}"`);
        }
        return out;
      });
      lines = els;
    } else {
      const t = await page.evaluate(() => document.body.innerText.slice(0, 4000));
      lines = [t];
    }
    if (outPath) await page.screenshot({ path: outPath, fullPage: false });
    return lines.join('\n');
  }

  const server = http.createServer((req, res) => {
    let buf = '';
    req.on('data', (d) => (buf += d));
    req.on('end', async () => {
      let out = '';
      try {
        const { cmd, args } = JSON.parse(buf || '{}');
        const a = args || [];
        switch (cmd) {
          case 'goto':
            await page.goto(a[0], { waitUntil: 'domcontentloaded', timeout: 30000 });
            out = `OK ${page.url()}`;
            break;
          case 'snapshot': {
            const interactive = a.includes('-i');
            const oi = a.indexOf('-o');
            const outPath = oi >= 0 ? a[oi + 1] : null;
            out = await snapshot(interactive, outPath);
            break;
          }
          case 'click':
            await page.locator(`[data-riff-ref="${a[0].replace('@', '')}"]`).first().click({ timeout: 10000 });
            out = `OK clicked ${a[0]}`;
            break;
          case 'fill':
            await page.locator(`[data-riff-ref="${a[0].replace('@', '')}"]`).first().fill(a[1] ?? '', { timeout: 10000 });
            out = `OK filled ${a[0]}`;
            break;
          case 'text':
            out = a[0] ? await page.locator(a[0]).first().innerText()
                       : await page.evaluate(() => document.body.innerText.slice(0, 4000));
            break;
          case 'console': {
            const list = a.includes('--errors') ? consoleLog.filter((m) => m.type === 'error') : consoleLog;
            out = list.length ? list.map((m) => `[${m.type}] ${m.text}`).join('\n') : '(none)';
            break;
          }
          case 'network': {
            out = network.length ? network.map((r) => `${r.status} ${r.method} ${r.url}`).join('\n') : '(no 4xx/5xx)';
            break;
          }
          case 'js':
            out = JSON.stringify(await page.evaluate(`(async () => { return ${a[0]} })()`));
            break;
          case 'links': {
            const links = await page.evaluate(() =>
              [...document.querySelectorAll('a[href]')].map((x) => `${x.innerText.trim().slice(0, 40)} -> ${x.getAttribute('href')}`).slice(0, 80));
            out = links.join('\n');
            break;
          }
          case 'wait':
            await page.getByText(a[0]).first().waitFor({ timeout: a[1] ? parseInt(a[1], 10) : 5000 });
            out = `OK saw "${a[0]}"`;
            break;
          case 'screenshot':
            await page.screenshot({ path: a[0], fullPage: false });
            out = `OK ${a[0]}`;
            break;
          case 'cookie-import':
            await context.addCookies(JSON.parse(fs.readFileSync(a[0], 'utf-8')).cookies || []);
            out = 'OK cookies imported';
            break;
          case 'status':
            out = `Mode: ${headed ? 'headed' : 'headless'}\nURL: ${page.url()}\nConsole errors: ${consoleLog.filter((m) => m.type === 'error').length}\nNetwork 4xx/5xx: ${network.length}`;
            break;
          case 'stop':
            await context.storageState({ path: STATE_FILE });
            res.end('OK stopping');
            await browser.close();
            try { fs.unlinkSync(PORT_FILE); } catch {}
            server.close(() => process.exit(0));
            return;
          default:
            out = `unknown command: ${cmd}`;
        }
      } catch (e) {
        out = `ERROR ${String(e.message || e)}`;
      }
      res.end(out);
    });
  });

  server.listen(0, '127.0.0.1', () => {
    fs.writeFileSync(PORT_FILE, String(server.address().port));
    console.log(`riff-browse 데몬 기동 (port ${server.address().port}, ${headed ? 'headed' : 'headless'})`);
  });
}

// ───────────────────────────── 진입점 ─────────────────────────────
const [, , cmd, ...args] = process.argv;
if (cmd === 'start') {
  await startDaemon(args.includes('--headed'));
} else if (!cmd) {
  console.log('usage: node riff-browse.mjs <start|goto|snapshot|click|fill|text|console|network|js|links|wait|screenshot|cookie-import|status|stop> ...');
  process.exit(1);
} else {
  try {
    process.stdout.write(await callDaemon(cmd, args));
    process.stdout.write('\n');
  } catch (e) {
    console.error(String(e.message || e));
    process.exit(1);
  }
}
