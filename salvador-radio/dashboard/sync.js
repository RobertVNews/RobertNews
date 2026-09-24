// ============================================================
// Sincronización multi-dispositivo — SOLO mismo origen (/api/sync)
// No llama a jsonblob desde el navegador (evita CORS / Failed to fetch)
// ============================================================
window.StationSync = (function () {
  "use strict";
  var LS_ID = "ser_sync_blob_id_v1";
  var LS_CACHE = "ser_sync_cache_v1";
  var DEFAULT_ID = "019f80b0-f9db-78be-95d7-ddf99254048e";
  var lastError = "";
  var online = true;

  function configId() {
    try {
      var c = window.APP_CONFIG || {};
      return (c.STATION_SYNC_ID && String(c.STATION_SYNC_ID).trim()) || DEFAULT_ID;
    } catch (e) {
      return DEFAULT_ID;
    }
  }

  function getId() {
    var fixed = configId();
    try { localStorage.setItem(LS_ID, fixed); } catch (e) {}
    return fixed;
  }

  function setId(id) {
    try { localStorage.setItem(LS_ID, id); } catch (e) {}
  }

  // Clave del panel (solo en memoria/sesión del locutor; nunca en config.js público)
  function adminPass() {
    try {
      if (window.__ADMIN_PASS) return String(window.__ADMIN_PASS);
      var s = window.sessionStorage && sessionStorage.getItem("ser_admin_pass");
      return s ? String(s) : "";
    } catch (e) { return ""; }
  }

  function apiUrl(id) {
    // Ruta relativa = mismo origen siempre (evita fallos raros de origin)
    return "/api/sync?id=" + encodeURIComponent(id || getId()) + "&_=" + Date.now();
  }

  function readLocalCache() {
    try {
      var raw = localStorage.getItem(LS_CACHE);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeLocalCache(doc) {
    try {
      localStorage.setItem(LS_CACHE, JSON.stringify(doc));
    } catch (e) {}
  }

  function slimPartial(partial) {
    partial = partial || {};
    var out = Object.assign({}, partial);
    if (out.state && typeof out.state === "object") {
      out.state = Object.assign({}, out.state);
      var np = out.state.nowPlaying;
      if (np && typeof np === "object") {
        out.state.nowPlaying = Object.assign({}, np);
        delete out.state.nowPlaying.mp3DataUrl;
        delete out.state.nowPlaying.audioData;
        if (out.state.nowPlaying.cover && String(out.state.nowPlaying.cover).indexOf("data:") === 0) {
          // data-URL de carátula no se envía por red (pesa demasiado)
          out.state.nowPlaying.cover = "local";
        }
      }
    }
    return out;
  }

  function fetchWithTimeout(url, opts, ms) {
    ms = ms || 10000;
    var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    var timer = null;
    var options = Object.assign({}, opts || {});
    if (ctrl) options.signal = ctrl.signal;
    return new Promise(function (resolve, reject) {
      timer = setTimeout(function () {
        try { if (ctrl) ctrl.abort(); } catch (e) {}
        reject(new Error("timeout"));
      }, ms);
      fetch(url, options).then(function (res) {
        clearTimeout(timer);
        resolve(res);
      }).catch(function (err) {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  async function request(method, partial) {
    var id = getId();
    var url = apiUrl(id);
    var opts = {
      method: method,
      headers: {
        Accept: "application/json",
        "Cache-Control": "no-cache"
      },
      credentials: "same-origin",
      cache: "no-store"
    };
    if (method === "PUT" || method === "POST") {
      opts.headers["Content-Type"] = "application/json";
      // Autorización: el servidor valida esta clave contra ADMIN_PASSCODE (env).
      // Los oyentes no la tienen, así que solo pueden leer (GET).
      var ap = adminPass();
      if (ap) opts.headers["x-admin-pass"] = ap;
      opts.body = JSON.stringify(slimPartial(partial) || {});
    }

    var lastErr = null;
    for (var attempt = 0; attempt < 3; attempt++) {
      try {
        var res = await fetchWithTimeout(url, opts, 10000);
        var text = await res.text();
        var data = null;
        try { data = text ? JSON.parse(text) : null; } catch (e) { data = null; }
        if (!res.ok) {
          lastErr = new Error((data && data.error) || ("HTTP " + res.status));
          // 401/403 = clave del panel incorrecta o ausente: no reintentar
          if (res.status === 401 || res.status === 403) throw lastErr;
          // reintentar 5xx
          if (res.status >= 500) {
            await new Promise(function (r) { setTimeout(r, 300 * (attempt + 1)); });
            continue;
          }
          throw lastErr;
        }
        online = true;
        lastError = "";
        if (data && typeof data === "object") writeLocalCache(data);
        return data;
      } catch (e) {
        lastErr = e;
        await new Promise(function (r) { setTimeout(r, 350 * (attempt + 1)); });
      }
    }
    online = false;
    lastError = (lastErr && lastErr.message) || "Failed to fetch";
    throw new Error(lastError);
  }

  async function create(data) {
    var id = getId();
    try { await push(data || { state: {}, schedule: [], requests: [] }); } catch (e) {}
    return id;
  }

  async function ensureId() {
    return getId();
  }

  async function pull() {
    try {
      var data = await request("GET");
      // GET devuelve el documento completo
      if (data && data.state !== undefined) return data;
      if (data && data.ok && data.state) {
        return { state: data.state, schedule: data.schedule || [], requests: data.requests || [] };
      }
      return data;
    } catch (e) {
      var cache = readLocalCache();
      if (cache) return cache;
      return null;
    }
  }

  async function push(partial) {
    var id = getId();
    try {
      await request("PUT", partial);
      // Actualizar cache local merge
      var cache = readLocalCache() || { state: {}, schedule: [], requests: [] };
      var next = Object.assign({}, cache, partial, { updatedAt: Date.now() });
      if (partial && partial.state) {
        next.state = Object.assign({}, cache.state || {}, partial.state);
      }
      writeLocalCache(next);
      return id;
    } catch (e) {
      // Guardar local para no perder el clic del DJ
      try {
        var cache2 = readLocalCache() || { state: {}, schedule: [], requests: [] };
        var next2 = Object.assign({}, cache2, partial, { updatedAt: Date.now() });
        if (partial && partial.state) {
          next2.state = Object.assign({}, cache2.state || {}, partial.state);
        }
        writeLocalCache(next2);
      } catch (e2) {}
      throw e;
    }
  }

  async function pushRequest(req) {
    var data = (await pull()) || { requests: [] };
    var list = Array.isArray(data.requests) ? data.requests : [];
    list.unshift(req);
    await push({ requests: list.slice(0, 80) });
  }

  function publicUrl(origin) {
    var base = origin || window.location.origin;
    try {
      if (/salvadorentregaradio\.vercel\.app/i.test(base)) {
        base = "https://salvador-entregas.vercel.app";
      }
    } catch (e) {}
    return base.replace(/\/$/, "") + "/";
  }

  function status() {
    return { online: online, lastError: lastError, id: getId() };
  }

  return {
    getId: getId,
    setId: setId,
    ensureId: ensureId,
    pull: pull,
    push: push,
    pushRequest: pushRequest,
    publicUrl: publicUrl,
    create: create,
    status: status
  };
})();
