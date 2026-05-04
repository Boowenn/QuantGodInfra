import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../cloudflare/src/index.js';

const TOKEN = 'test-token-123';

function createEnv(token = TOKEN) {
  const store = new Map();
  return {
    QG_INGEST_TOKEN: token,
    QG_STATE: {
      async get(key) {
        return store.has(key) ? store.get(key) : null;
      },
      async put(key, value) {
        store.set(key, value);
      }
    },
    ASSETS: {
      async fetch() {
        return new Response('asset fallback', { status: 404 });
      }
    }
  };
}

function snapshot(seq = 0) {
  return {
    runtime: { tradeStatus: `STATUS_${seq}` },
    account: { login: 186054398 },
    watchlist: 'USDJPYc',
    seq
  };
}

function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.token) {
    headers.set('authorization', `Bearer ${options.token}`);
  }
  if (options.json) {
    headers.set('content-type', 'application/json');
  }
  return new Request(`https://quantgod.example${path}`, {
    method: options.method || 'GET',
    headers,
    body: options.json ? JSON.stringify(options.json) : options.body
  });
}

async function readJson(response) {
  return JSON.parse(await response.text());
}

async function ingest(env, seq) {
  return worker.fetch(
    request('/api/ingest', {
      method: 'POST',
      token: TOKEN,
      json: snapshot(seq)
    }),
    env
  );
}

test('fails closed when token is not configured', async () => {
  const env = createEnv('');
  const response = await worker.fetch(request('/api/health'), env);
  assert.equal(response.status, 503);
  const body = await readJson(response);
  assert.equal(body.error, 'WORKER_NOT_CONFIGURED');
});

test('rejects ingest without a valid token', async () => {
  const env = createEnv();
  const response = await worker.fetch(request('/api/ingest', { method: 'POST', json: snapshot(1) }), env);
  assert.equal(response.status, 401);
});

test('stores latest snapshot after authorized ingest', async () => {
  const env = createEnv();
  const ingestResponse = await ingest(env, 1);
  assert.equal(ingestResponse.status, 200);

  const latestResponse = await worker.fetch(request('/api/latest'), env);
  assert.equal(latestResponse.status, 200);
  const body = await readJson(latestResponse);
  assert.equal(body.runtime.tradeStatus, 'STATUS_1');
  assert.equal(body.account.login, 186054398);
  assert.equal(body.seq, 1);
});

test('protects snapshot history with token and only allows GET', async () => {
  const env = createEnv();
  await ingest(env, 1);

  const unauthorized = await worker.fetch(request('/api/history'), env);
  assert.equal(unauthorized.status, 401);

  const wrongMethod = await worker.fetch(request('/api/history', { method: 'POST', token: TOKEN }), env);
  assert.equal(wrongMethod.status, 405);

  const authorized = await worker.fetch(request('/api/history', { token: TOKEN }), env);
  assert.equal(authorized.status, 200);
  const body = await readJson(authorized);
  assert.equal(body.ok, true);
  assert.equal(body.count, 1);
});

test('returns ring history in chronological order with the newest 24 snapshots', async () => {
  const env = createEnv();
  for (let i = 0; i < 26; i++) {
    const response = await ingest(env, i);
    assert.equal(response.status, 200);
  }

  const historyResponse = await worker.fetch(request('/api/history', { token: TOKEN }), env);
  assert.equal(historyResponse.status, 200);
  const body = await readJson(historyResponse);
  assert.equal(body.count, 24);
  assert.deepEqual(body.snapshots.map((row) => row.seq), Array.from({ length: 24 }, (_, i) => i + 2));
});

test('validates ingest payload has required core fields', async () => {
  const env = createEnv();
  const response = await worker.fetch(
    request('/api/ingest', { method: 'POST', token: TOKEN, json: { runtime: {} } }),
    env
  );
  assert.equal(response.status, 400);
  const body = await readJson(response);
  assert.equal(body.error, 'MISSING_CORE_FIELDS');
});
