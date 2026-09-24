// ============================================================
// Live HTTP mic — segmentos COMPLETOS de ~1s (PC + móvil)
// Cada trozo es un archivo webm/mp4 válido (no fragmentos MSE).
// Así el oyente puede reproducir sin MediaSource.
// ============================================================
window.HttpLive = (function () {
  "use strict";

  function defaultId() {
    try {
      var c = window.APP_CONFIG || {};
      return (c.STATION_SYNC_ID && String(c.STATION_SYNC_ID).trim()) || "019f80b0-f9db-78be-95d7-ddf99254048e";
    } catch (e) {
      return "019f80b0-f9db-78be-95d7-ddf99254048e";
    }
  }

  // Clave del panel (solo publicador). El servidor la valida en POST/DELETE.
  function adminPass() {
    try {
      if (window.__ADMIN_PASS) return String(window.__ADMIN_PASS);
      var s = window.sessionStorage && sessionStorage.getItem("ser_admin_pass");
      return s ? String(s) : "";
    } catch (e) { return ""; }
  }

  function pickMime() {
    var types = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/mp4",
      "audio/ogg;codecs=opus"
    ];
    if (!window.MediaRecorder) return "";
    for (var i = 0; i < types.length; i++) {
      try {
        if (MediaRecorder.isTypeSupported(types[i])) return types[i];
      } catch (e) {}
    }
    return "";
  }

  function bufToB64(buf) {
    var bytes = new Uint8Array(buf);
    var chunk = 0x8000;
    var str = "";
    for (var i = 0; i < bytes.length; i += chunk) {
      str += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    return btoa(str);
  }

  function b64ToBuf(b64) {
    var bin = atob(b64);
    var len = bin.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    return bytes.buffer;
  }

  function liveApiUrl(id) {
    var origin = "";
    try {
      origin = (window.location && window.location.origin) || "";
    } catch (e) {}
    return origin + "/api/live?id=" + encodeURIComponent(id || defaultId());
  }

  function isMobile() {
    try {
      return /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || "");
    } catch (e) {
      return false;
    }
  }

  // ---------- PUBLICADOR: segmentos completos ----------
  function Publisher(opts) {
    opts = opts || {};
    this.id = opts.id || defaultId();
    this.stream = null;
    this.seq = 0;
    this.mime = "";
    this.active = false;
    this._onStatus = null;
    this._loopTimer = null;
    this._watch = null;
    this._vis = null;
    this._recording = false;
    this._fail = 0;
    this._ok = 0;
    this._lastOkAt = 0;
    this._segMs = 1000;
  }

  Publisher.prototype.onStatus = function (fn) {
    this._onStatus = fn;
  };
  Publisher.prototype._status = function (msg, type) {
    if (this._onStatus) this._onStatus(msg, type);
  };

  /** Graba UN segmento completo (archivo válido) */
  Publisher.prototype._recordSegment = function () {
    var self = this;
    return new Promise(function (resolve) {
      if (!self.active || !self.stream) {
        resolve(null);
        return;
      }
      // pistas vivas
      try {
        self.stream.getAudioTracks().forEach(function (t) {
          try {
            t.enabled = true;
          } catch (e) {}
        });
      } catch (e) {}

      var mime = self.mime || pickMime() || "audio/webm";
      var rec;
      try {
        rec = new MediaRecorder(self.stream, {
          mimeType: mime,
          audioBitsPerSecond: isMobile() ? 48000 : 64000
        });
        self.mime = rec.mimeType || mime;
      } catch (e1) {
        try {
          rec = new MediaRecorder(self.stream);
          self.mime = rec.mimeType || mime;
        } catch (e2) {
          resolve(null);
          return;
        }
      }

      var parts = [];
      rec.ondataavailable = function (ev) {
        if (ev.data && ev.data.size) parts.push(ev.data);
      };
      rec.onerror = function () {
        try {
          rec.stop();
        } catch (e) {}
        resolve(null);
      };
      rec.onstop = function () {
        if (!parts.length) {
          resolve(null);
          return;
        }
        resolve(new Blob(parts, { type: self.mime || "audio/webm" }));
      };

      try {
        rec.start(); // SIN timeslice → un solo blob completo al stop
      } catch (eS) {
        resolve(null);
        return;
      }
      setTimeout(function () {
        try {
          if (rec.state !== "inactive") rec.stop();
        } catch (e) {
          resolve(null);
        }
      }, self._segMs);
    });
  };

  Publisher.prototype._postBlob = async function (blob) {
    if (!blob || blob.size < 100) return false;
    var self = this;
    var buf = await blob.arrayBuffer();
    if (!buf || !buf.byteLength) return false;
    var b64 = bufToB64(buf);
    self.seq += 1;
    var seq = self.seq;
    var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    var to = setTimeout(function () {
      try {
        if (ctrl) ctrl.abort();
      } catch (e) {}
    }, 10000);
    try {
      var headers = { "Content-Type": "application/json", Accept: "application/json" };
      var ap = adminPass();
      if (ap) headers["x-admin-pass"] = ap;
      var r = await fetch(liveApiUrl(self.id), {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          id: self.id,
          mime: self.mime,
          seq: seq,
          b64: b64
        }),
        cache: "no-store",
        signal: ctrl ? ctrl.signal : undefined
      });
      clearTimeout(to);
      if (!r.ok) {
        if (r.status === 400) return false;
        throw new Error("HTTP " + r.status);
      }
      var j = await r.json().catch(function () {
        return {};
      });
      if (j && j.skipped) return false;
      self._fail = 0;
      self._ok++;
      self._lastOkAt = Date.now();
      if (seq === 1 || seq % 5 === 0) {
        self._status("Mic al aire · seg " + seq, "ok");
      }
      return true;
    } catch (err) {
      clearTimeout(to);
      self._fail++;
      if (self._fail <= 3 || self._fail % 8 === 0) {
        self._status("Reintentando mic…", "err");
      }
      return false;
    }
  };

  Publisher.prototype._loop = async function () {
    var self = this;
    if (!self.active || self._recording) return;
    self._recording = true;
    try {
      // resume audio contexts
      try {
        if (window.__serStudioAudioCtx && window.__serStudioAudioCtx.state === "suspended") {
          await window.__serStudioAudioCtx.resume();
        }
      } catch (e) {}

      var blob = await self._recordSegment();
      if (self.active && blob && blob.size >= 100) {
        await self._postBlob(blob);
      }
    } catch (e) {
      // continue
    }
    self._recording = false;
    if (self.active) {
      // siguiente segmento casi sin hueco
      self._loopTimer = setTimeout(function () {
        self._loop();
      }, 30);
    }
  };

  Publisher.prototype.start = async function (stream) {
    var self = this;
    await this.stop({ soft: true }); // no DELETE si soft
    if (!stream) throw new Error("Sin stream de mic");
    if (!window.MediaRecorder) throw new Error("MediaRecorder no soportado");

    try {
      stream.getAudioTracks().forEach(function (t) {
        try {
          t.enabled = true;
        } catch (e) {}
      });
    } catch (e) {}

    this.stream = stream;
    this.mime = pickMime() || "audio/webm";
    this.active = true;
    this._fail = 0;
    this._ok = 0;
    this._segMs = isMobile() ? 900 : 1000;
    if (!this.seq) this.seq = 0;
    this._lastOkAt = Date.now();

    // watchdog
    this._watch = setInterval(function () {
      try {
        if (!self.active) return;
        if (Date.now() - self._lastOkAt > 5000 && !self._recording) {
          self._status("Reconectando mic…", "err");
          self._loop();
        }
        try {
          if (window.__serStudioAudioCtx && window.__serStudioAudioCtx.state === "suspended") {
            window.__serStudioAudioCtx.resume();
          }
        } catch (e) {}
      } catch (eW) {}
    }, 2500);

    this._vis = function () {
      if (document.visibilityState !== "visible") return;
      if (!self.active) return;
      try {
        if (window.__serStudioAudioCtx && window.__serStudioAudioCtx.state === "suspended") {
          window.__serStudioAudioCtx.resume();
        }
      } catch (e) {}
      if (!self._recording) self._loop();
    };
    document.addEventListener("visibilitychange", this._vis);

    this._status("Mic HTTP activo (segmentos)", "ok");
    this._loop();
    return { mime: this.mime, id: this.id };
  };

  Publisher.prototype.softRestart = async function (stream) {
    if (stream) this.stream = stream;
    if (!this.active) return this.start(this.stream);
    if (!this._recording) this._loop();
    return { mime: this.mime, id: this.id };
  };

  Publisher.prototype.stop = async function (opts) {
    opts = opts || {};
    this.active = false;
    this._recording = false;
    if (this._loopTimer) {
      clearTimeout(this._loopTimer);
      this._loopTimer = null;
    }
    if (this._watch) {
      clearInterval(this._watch);
      this._watch = null;
    }
    if (this._vis) {
      try {
        document.removeEventListener("visibilitychange", this._vis);
      } catch (e) {}
      this._vis = null;
    }
    if (!opts.soft) {
      try {
        var headers = {};
        var ap = adminPass();
        if (ap) headers["x-admin-pass"] = ap;
        await fetch(liveApiUrl(this.id), { method: "DELETE", headers: headers, cache: "no-store" });
      } catch (e) {}
      this._status("Mic detenido", "");
    }
  };

  // ---------- OYENTE: cola de segmentos completos ----------
  function Listener(opts) {
    opts = opts || {};
    this.id = opts.id || defaultId();
    this.audio = null;
    this.from = 0;
    this.active = false;
    this._poll = null;
    this._queue = [];
    this._playing = false;
    this._onStatus = null;
    this.mime = "audio/webm";
    this._url = "";
    this._empty = 0;
    this._lastPlayAt = 0;
  }

  Listener.prototype.onStatus = function (fn) {
    this._onStatus = fn;
  };
  Listener.prototype._status = function (msg) {
    if (this._onStatus) this._onStatus(msg);
  };

  Listener.prototype.connect = async function (audioEl) {
    await this.disconnect();
    this.audio = audioEl;
    this.active = true;
    this.from = 0;
    this._queue = [];
    this._playing = false;
    this._empty = 0;

    try {
      audioEl.setAttribute("playsinline", "");
      audioEl.setAttribute("webkit-playsinline", "");
      audioEl.playsInline = true;
      audioEl.autoplay = true;
      audioEl.muted = false;
      audioEl.volume = 1;
    } catch (e) {}

    var self = this;
    this._poll = setInterval(function () {
      self._tick();
    }, 700);
    await this._tick();
    this._status("▶ Mic sintonizado");
  };

  Listener.prototype._tick = async function () {
    if (!this.active) return;
    try {
      var r = await fetch(liveApiUrl(this.id) + "&from=" + this.from + "&_=" + Date.now(), {
        cache: "no-store",
        headers: { Accept: "application/json" }
      });
      if (!r.ok) return;
      var data = await r.json();
      if (!data || !data.chunks || !data.chunks.length) {
        this._empty++;
        if (this._empty > 12) {
          this.from = Math.max(0, (data && data.latest ? data.latest - 2 : 0));
          this._empty = 0;
        }
        return;
      }
      this._empty = 0;
      if (data.mime) this.mime = data.mime;
      for (var i = 0; i < data.chunks.length; i++) {
        var c = data.chunks[i];
        if (!c || !c.b64) continue;
        if (typeof c.seq === "number" && c.seq < this.from) continue;
        var buf = null;
        try {
          buf = b64ToBuf(c.b64);
        } catch (e) {
          continue;
        }
        if (!buf || buf.byteLength < 100) continue;
        this._queue.push({ buf: buf, mime: data.mime || this.mime, seq: c.seq });
        while (this._queue.length > 8) this._queue.shift();
        if (typeof c.seq === "number") this.from = c.seq + 1;
      }
      if (typeof data.next === "number" && data.next > this.from) this.from = data.next;
      this._playNext();
    } catch (e) {}
  };

  Listener.prototype._playNext = function () {
    var self = this;
    if (!this.active || this._playing) return;
    if (!this._queue.length) return;
    var item = this._queue.shift();
    if (!item || !item.buf) {
      this._playNext();
      return;
    }
    this._playing = true;
    var blob = new Blob([item.buf], { type: item.mime || this.mime || "audio/webm" });
    var url = URL.createObjectURL(blob);
    if (this._url) {
      try {
        URL.revokeObjectURL(this._url);
      } catch (e) {}
    }
    this._url = url;
    var el = this.audio;
    if (!el) {
      this._playing = false;
      return;
    }
    var done = false;
    var finish = function () {
      if (done) return;
      done = true;
      self._playing = false;
      try {
        el.onended = null;
        el.onerror = null;
      } catch (e) {}
      // encadenar siguiente segmento
      setTimeout(function () {
        self._playNext();
      }, 20);
    };
    try {
      el.onended = finish;
      el.onerror = finish;
      el.src = url;
      el.muted = false;
      el.volume = 1;
      var p = el.play();
      if (p && p.then) {
        p.then(function () {
          self._lastPlayAt = Date.now();
          self._status("▶ Voz en vivo");
        }).catch(function () {
          el.muted = true;
          el.play()
            .then(function () {
              el.muted = false;
              self._lastPlayAt = Date.now();
            })
            .catch(finish);
        });
      }
      // failsafe duración ~ segmento
      setTimeout(function () {
        if (!done) finish();
      }, 1600);
    } catch (e2) {
      finish();
    }
  };

  Listener.prototype.disconnect = async function () {
    this.active = false;
    if (this._poll) {
      clearInterval(this._poll);
      this._poll = null;
    }
    this._queue = [];
    this._playing = false;
    if (this._url) {
      try {
        URL.revokeObjectURL(this._url);
      } catch (e) {}
      this._url = "";
    }
    if (this.audio && this.audio.id === "micPlayer") {
      try {
        this.audio.pause();
        this.audio.removeAttribute("src");
        this.audio.load();
      } catch (e) {}
    }
  };

  return {
    Publisher: Publisher,
    Listener: Listener,
    pickMime: pickMime,
    defaultId: defaultId
  };
})();
