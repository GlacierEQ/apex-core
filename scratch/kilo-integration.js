#!/usr/bin/env node
/**
 * KiloIntegration
 * ---------------------------------------------------------------------------
 * Core class backing `.kilo/run-integration.js` and `.kilo/test-connections.js`.
 *
 * Responsibilities:
 *   - Load provider configuration from `.kilo/configs/main.json` (or a passed-in object).
 *   - Resolve endpoints that use `${ENV_VAR}` interpolation from the live environment.
 *   - Resolve each provider's API key from its well-known environment variable
 *     (never hard-codes secrets; always reads from `process.env` at runtime).
 *   - `testConnections()` performs a REAL reachability + auth check against each
 *     provider (GET `/models` for keyed APIs, GET `/api/tags` for local Ollama).
 *
 * This module intentionally contains no secrets. Credentials are supplied by the
 * surrounding shell environment only.
 */

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

/** Provider name -> environment variable that holds its API key. */
const PROVIDER_KEY_ENV = {
  'kilo-code': 'KILO_API_KEY',
  'openai': 'OPENAI_API_KEY',
  'anthropic': 'ANTHROPIC_API_KEY',
  'openrouter': 'OPENROUTER_API_KEY',
  'deepseek': 'DEEPSEEK_API_KEY',
  'ollama': null,
};

/** Replace `${VAR}` references with values from `process.env`. */
function resolveEnv(value) {
  if (typeof value !== 'string') return value;
  return value.replace(/\$\{([^}]+)\}/g, (_, name) => process.env[name] ?? '');
}

export default class KiloIntegration {
  /**
   * @param {object} [config] - Optional provider configuration object. When
   *   omitted, `.kilo/configs/main.json` (relative to this module) is loaded.
   */
  constructor(config) {
    if (config && typeof config === 'object') {
      this.config = config;
    } else {
      this.config = KiloIntegration.loadConfig();
    }
  }

  /** Load and parse the default configuration file. */
  static loadConfig() {
    try {
      return JSON.parse(
        readFileSync(join(__dirname, '.kilo', 'configs', 'main.json'), 'utf8'),
      );
    } catch (err) {
      return { providers: {}, optimization: {} };
    }
  }

  /**
   * Build the list of connection descriptors from the configured providers.
   * @returns {Array<object>} connection descriptors
   */
  setupConnections() {
    const providers = this.config?.providers ?? {};
    const connections = [];

    for (const [role, provider] of Object.entries(providers)) {
      if (!provider || typeof provider !== 'object') continue;
      const keyEnv = provider.keyEnv ?? PROVIDER_KEY_ENV[provider.name] ?? null;
      connections.push({
        role,
        name: provider.name,
        endpoint: resolveEnv(provider.endpoint),
        model: provider.model ?? null,
        maxTokens: provider.maxTokens ?? null,
        keyEnv,
        apiKey: keyEnv ? (process.env[keyEnv] || null) : null,
      });
    }

    return connections;
  }

  /**
   * Perform a real reachability + auth probe for each connection.
   * @param {Array<object>} connections - output of `setupConnections()`.
   * @returns {Promise<Array<object>>} per-connection test results
   */
  async testConnections(connections) {
    const results = [];

    for (const conn of connections) {
      const result = {
        role: conn.role,
        name: conn.name,
        endpoint: conn.endpoint || null,
        ok: false,
      };

      if (!conn.endpoint) {
        result.error = `no endpoint configured (set ${conn.keyEnv ? 'endpoint' : 'endpoint'} or env)`;
        results.push(result);
        continue;
      }

      const isLocal = conn.name === 'ollama' || conn.endpoint.startsWith('http://127.0.0.1') || conn.endpoint.startsWith('http://localhost');
      const probePath = isLocal ? '/api/tags' : '/models';
      const url = conn.endpoint.replace(/\/$/, '') + probePath;

      const headers = { Accept: 'application/json' };
      if (conn.apiKey) headers.Authorization = `Bearer ${conn.apiKey}`;

      const startedAt = Date.now();
      try {
        const response = await fetch(url, { method: 'GET', headers });
        const body = await response.text();
        result.status = response.status;
        result.latencyMs = Date.now() - startedAt;
        result.ok = response.ok;
        if (!response.ok) {
          // Surface a short, human-readable reason without dumping huge bodies.
          result.error = `HTTP ${response.status}`;
          const snippet = body.slice(0, 160).replace(/\s+/g, ' ');
          if (snippet) result.detail = snippet;
        }
      } catch (err) {
        result.error = err.message;
        result.latencyMs = Date.now() - startedAt;
      }

      results.push(result);
    }

    return results;
  }

  /**
   * High-level entry point used by `run-integration.js`.
   * @param {object} context - execution context ({ type, format, optimization }).
   * @returns {Promise<object>} optimization + connection test summary
   */
  async optimizeAndConnect(context = {}) {
    const connections = this.setupConnections();
    const testResults = await this.testConnections(connections);
    return {
      context,
      optimization: this.config?.optimization ?? {},
      connections: testResults,
      connected: testResults.length > 0 && testResults.every((r) => r.ok),
    };
  }
}
