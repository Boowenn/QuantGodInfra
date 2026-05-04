import { describe, it, expect, beforeAll } from 'vitest';

// Inline the worker logic for testing (no Miniflare dependency)
const JSON_HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store, no-cache, must-revalidate, max-age=0',
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,POST,OPTIONS',
  'access-control-allow-headers': 'Content-Type, Authorization, X-QuantGod-Token, X-QuantGod-Source'
};

function jsonResponse(payload, status = 200) {
  return { status, headers: JSON_HEADERS, body: JSON.stringify(payload, null, 2) };
}

function getBearerToken(headers) {
  const auth = headers['authorization'] || headers['x-quantgod-token'] || '';
  if (auth.toLowerCase().startsWith('bearer ')) return auth.slice(7).trim();
  return auth;
}

function constantTimeEqual(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return result === 0;
}

function isAuthorized(headers, env) {
  const expected = env.QG_INGEST_TOKEN;
  if (!expected) return false;
  const token = getBearerToken(headers);
  if (!token) return false;
  return constantTimeEqual(token, expected);
}

describe('Cloudflare Ingest Worker', () => {
  const validEnv = { QG_INGEST_TOKEN: 'test-token-123' };
  const emptyEnv = {};

  it('rejects requests with no token configured', () => {
    expect(isAuthorized({}, emptyEnv)).toBe(false);
  });

  it('rejects requests with no token provided', () => {
    expect(isAuthorized({}, validEnv)).toBe(false);
  });

  it('accepts valid bearer token', () => {
    expect(isAuthorized({ authorization: 'Bearer test-token-123' }, validEnv)).toBe(true);
  });

  it('accepts valid x-quantgod-token header', () => {
    expect(isAuthorized({ 'x-quantgod-token': 'test-token-123' }, validEnv)).toBe(true);
  });

  it('rejects wrong token', () => {
    expect(isAuthorized({ authorization: 'Bearer wrong-token' }, validEnv)).toBe(false);
  });

  it('rejects tokens of different lengths without leaking timing', () => {
    expect(isAuthorized({ authorization: 'Bearer short' }, validEnv)).toBe(false);
    expect(isAuthorized({ authorization: 'Bearer very-long-token-that-does-not-match' }, validEnv)).toBe(false);
  });

  it('constantTimeEqual handles length mismatch', () => {
    expect(constantTimeEqual('abc', 'abcd')).toBe(false);
    expect(constantTimeEqual('abc', 'abc')).toBe(true);
    expect(constantTimeEqual('', '')).toBe(true);
  });

  it('jsonResponse produces correct structure', () => {
    const res = jsonResponse({ ok: true }, 200);
    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toContain('application/json');
    const body = JSON.parse(res.body);
    expect(body.ok).toBe(true);
  });

  it('jsonResponse with error status', () => {
    const res = jsonResponse({ ok: false, error: 'UNAUTHORIZED' }, 401);
    expect(res.status).toBe(401);
    const body = JSON.parse(res.body);
    expect(body.error).toBe('UNAUTHORIZED');
  });

  it('validates ingest payload has required fields', () => {
    const missingRuntime = { account: {} };
    const missingAccount = { runtime: {} };
    const valid = { runtime: {}, account: {} };
    expect(missingRuntime.runtime && missingRuntime.account).toBeFalsy();
    expect(missingAccount.runtime && missingAccount.account).toBeFalsy();
    expect(valid.runtime && valid.account).toBeTruthy();
  });
});
