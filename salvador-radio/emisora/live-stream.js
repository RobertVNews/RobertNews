// ============================================================
// Streaming en vivo WebRTC (PeerJS) — 1 locutor → muchos oyentes
// El audio sale del mic o de la pestaña/sistema del control.
// ============================================================
window.LiveStream = (function(){
  "use strict";

  var PEER_HOST = {
    host: "0.peerjs.com",
    secure: true,
    port: 443,
    // STUN extra: menos cortes detrás de NAT/colegio
    config: {
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" },
        { urls: "stun:stun2.l.google.com:19302" },
        { urls: "stun:global.stun.twilio.com:3478" }
      ]
    },
    debug: 0
  };

  function loadPeerJs(){
    return new Promise(function(resolve, reject){
      if(window.Peer) return resolve(window.Peer);
      var s = document.createElement("script");
      s.src = "https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js";
      s.onload = function(){ resolve(window.Peer); };
      s.onerror = function(){ reject(new Error("No se pudo cargar PeerJS")); };
      document.head.appendChild(s);
    });
  }

  function safeId(raw){
    var id = String(raw || ("ser" + Date.now()));
    id = id.replace(/[^a-zA-Z0-9]/g, "");
    if(id.length < 6) id = id + "radio" + Math.random().toString(36).slice(2, 8);
    return id.slice(0, 48);
  }

  // ---------- BROADCASTER (admin) ----------
  function Broadcaster(){
    this.peer = null;
    this.stream = null;
    this.peerId = null;
    this.calls = [];
    this._onStatus = null;
  }

  Broadcaster.prototype.onStatus = function(fn){ this._onStatus = fn; };
  Broadcaster.prototype._status = function(msg, type){
    if(this._onStatus) this._onStatus(msg, type);
  };

  Broadcaster.prototype.start = async function(opts){
    opts = opts || {};
    var self = this;
    await this.stop();

    var Peer = await loadPeerJs();
    var mode = opts.mode || "mic"; // mic | tab

    if(mode === "tab"){
      // Comparte pestaña/ventana: elige la de Spotify y marca "Compartir audio"
      self.stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        }
      });
      // Si solo queremos audio, igual necesitamos el track de video a veces para que el navegador entregue audio
      var vtracks = self.stream.getVideoTracks();
      // dejamos video silencioso en el aire (oyentes solo usan audio)
      vtracks.forEach(function(t){ t.enabled = true; });
      if(!self.stream.getAudioTracks().length){
        self.stream.getTracks().forEach(function(t){ t.stop(); });
        throw new Error("No se capturó audio. Al compartir, marca «Compartir audio de la pestaña» (Chrome).");
      }
    } else {
      // Mic del dispositivo (PC o celular Samsung/Android)
      var micConstraints = [
        {
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1
          },
          video: false
        },
        { audio: true, video: false }
      ];
      var micErr = null;
      self.stream = null;
      for (var mi = 0; mi < micConstraints.length; mi++) {
        try {
          self.stream = await navigator.mediaDevices.getUserMedia(micConstraints[mi]);
          break;
        } catch (e) {
          micErr = e;
        }
      }
      if (!self.stream) {
        throw new Error(
          "No se abrió el mic del celular. En Chrome: permiso de micrófono → Permitir. " +
          ((micErr && micErr.message) || "")
        );
      }
    }

    self.stream.getTracks().forEach(function(track){
      track.addEventListener("ended", function(){
        self._status("Captura detenida por el sistema", "err");
        self.stop();
      });
    });

    var preferredId = safeId(opts.peerId || ("serlive" + Math.random().toString(36).slice(2, 10)));

    self.peer = new Peer(preferredId, PEER_HOST);

    await new Promise(function(resolve, reject){
      var done = false;
      self.peer.on("open", function(id){
        done = true;
        self.peerId = id;
        resolve(id);
      });
      self.peer.on("error", function(err){
        if(done) {
          self._status("Peer: " + (err.type || err.message), "err");
          return;
        }
        // reintento con id aleatorio
        try{ self.peer.destroy(); }catch(e){}
        self.peer = new Peer(PEER_HOST);
        self.peer.on("open", function(id){
          done = true;
          self.peerId = id;
          resolve(id);
        });
        self.peer.on("error", function(e2){
          if(!done) reject(e2);
        });
      });
    });

    self._wireIncomingCalls();
    self._status("En vivo · ID " + self.peerId, "ok");
    return { peerId: self.peerId, mode: mode };
  };

  /** Emite un MediaStream ya mezclado (canción+mic) por PeerJS — sin hub ni túnel */
  Broadcaster.prototype.startWithStream = async function(mediaStream, opts){
    opts = opts || {};
    var self = this;
    await this.stop();
    if(!mediaStream || !mediaStream.getAudioTracks || !mediaStream.getAudioTracks().length){
      throw new Error("Sin audio para transmitir");
    }
    self.stream = mediaStream;
    self._callsWired = false;
    self.stream.getTracks().forEach(function(track){
      track.addEventListener("ended", function(){
        // No tumbar toda la emisión por un track; el estudio puede reponer
        self._status("Aviso: una pista de audio terminó", "err");
      });
    });

    var Peer = await loadPeerJs();
    var preferredId = safeId(opts.peerId || ("serlive" + Math.random().toString(36).slice(2, 10)));
    self.peer = new Peer(preferredId, PEER_HOST);

    await new Promise(function(resolve, reject){
      var done = false;
      self.peer.on("open", function(id){
        done = true;
        self.peerId = id;
        resolve(id);
      });
      self.peer.on("error", function(err){
        if(done){
          self._status("Peer: " + (err.type || err.message), "err");
          return;
        }
        try{ self.peer.destroy(); }catch(e){}
        self.peer = new Peer(PEER_HOST);
        self.peer.on("open", function(id){
          done = true;
          self.peerId = id;
          resolve(id);
        });
        self.peer.on("error", function(e2){
          if(!done) reject(e2);
        });
      });
    });

    self._wireIncomingCalls();
    self._status("▶ En vivo (nube) · " + self.peerId, "ok");
    return { peerId: self.peerId, mode: "stream" };
  };

  Broadcaster.prototype._wireIncomingCalls = function(){
    var self = this;
    if(!self.peer) return;
    // Evitar handlers duplicados
    if(self._callsWired) return;
    self._callsWired = true;
    self.peer.on("call", function(call){
      try{
        call.answer(self.stream);
        self.calls.push(call);
        self._watchCall(call);
        call.on("close", function(){
          self.calls = self.calls.filter(function(c){ return c !== call; });
          self._status("Oyentes: " + self.calls.length, "ok");
        });
        call.on("error", function(){
          self.calls = self.calls.filter(function(c){ return c !== call; });
        });
        self._status("Oyentes conectados: " + self.calls.length, "ok");
      }catch(e){
        console.error(e);
      }
    });
    // Mantener peer despierto
    if(self._pingTimer) clearInterval(self._pingTimer);
    self._pingTimer = setInterval(function(){
      try{
        if(!self.peer || self.peer.destroyed) return;
        // re-answer calls que se quedaron sin track
        (self.calls || []).forEach(function(call){
          try{
            var pc = call.peerConnection || call._pc;
            if(!pc) return;
            if(pc.connectionState === "failed" || pc.iceConnectionState === "failed"){
              if(pc.restartIce) pc.restartIce();
            }
          }catch(e){}
        });
      }catch(e){}
    }, 4000);
  };

  Broadcaster.prototype._watchCall = function(call){
    try{
      var pc = call.peerConnection || call._pc;
      if(!pc || !pc.addEventListener) return;
      pc.addEventListener("connectionstatechange", function(){
        try{
          var st = pc.connectionState;
          if(st === "failed" || st === "disconnected"){
            if(pc.restartIce) pc.restartIce();
          }
        }catch(e){}
      });
      pc.addEventListener("iceconnectionstatechange", function(){
        try{
          var st = pc.iceConnectionState;
          if(st === "failed" || st === "disconnected"){
            if(pc.restartIce) pc.restartIce();
          }
        }catch(e){}
      });
    }catch(e){}
  };

  Broadcaster.prototype.setMuted = function(muted){
    if(!this.stream) return false;
    this.stream.getAudioTracks().forEach(function(t){
      t.enabled = !muted;
    });
    this._status(muted ? "Mic MUTE (oyentes en silencio de tu voz)" : "Mic ABIERTO", muted ? "err" : "ok");
    return !!muted;
  };

  Broadcaster.prototype.isMuted = function(){
    if(!this.stream) return false;
    var tracks = this.stream.getAudioTracks();
    if(!tracks.length) return false;
    return !tracks[0].enabled;
  };

  Broadcaster.prototype.getListenerCount = function(){
    return (this.calls && this.calls.length) || 0;
  };

  Broadcaster.prototype.stop = async function(){
    var self = this;
    if(self._pingTimer){
      try{ clearInterval(self._pingTimer); }catch(e){}
      self._pingTimer = null;
    }
    self._callsWired = false;
    self.calls.forEach(function(c){ try{ c.close(); }catch(e){} });
    self.calls = [];
    // No hacemos stop() de los tracks del MediaStream externo:
    // puede ser un stream de AudioContext (canción) que el Studio reutiliza/limpia él.
    self.stream = null;
    if(self.peer){
      try{ self.peer.destroy(); }catch(e){}
      self.peer = null;
    }
    self.peerId = null;
    self._status("Streaming detenido", "");
  };

  Broadcaster.prototype.isLive = function(){
    return !!(this.peer && this.stream && this.peerId);
  };

  // ---------- LISTENER (público) ----------
  function Listener(){
    this.peer = null;
    this.call = null;
    this._onStatus = null;
  }

  Listener.prototype.onStatus = function(fn){ this._onStatus = fn; };
  Listener.prototype._status = function(msg){
    if(this._onStatus) this._onStatus(msg);
  };

  Listener.prototype.connect = async function(broadcasterId, audioEl){
    var self = this;
    await this.disconnect();
    if(!broadcasterId) throw new Error("Sin emisor en vivo");
    self._broadcasterId = broadcasterId;
    self._audioEl = audioEl;

    var Peer = await loadPeerJs();
    self.peer = new Peer(PEER_HOST);

    await new Promise(function(resolve, reject){
      var t = setTimeout(function(){ reject(new Error("Timeout PeerJS")); }, 12000);
      self.peer.on("open", function(){ clearTimeout(t); resolve(); });
      self.peer.on("error", function(err){ clearTimeout(t); reject(err); });
    });

    // Llamada solo-recepción: algunos navegadores exigen un stream local vacío
    var empty = null;
    try{
      var ctx = new (window.AudioContext || window.webkitAudioContext)();
      if(ctx.state === "suspended") await ctx.resume();
      var dest = ctx.createMediaStreamDestination();
      empty = dest.stream;
      self._emptyCtx = ctx;
    }catch(e){}

    self.call = self.peer.call(broadcasterId, empty || undefined);

    if(!self.call){
      throw new Error("No se pudo llamar al emisor. ¿Sigue transmitiendo?");
    }

    return await new Promise(function(resolve, reject){
      var settled = false;
      var timer = setTimeout(function(){
        if(!settled){
          settled = true;
          reject(new Error("Tiempo de espera: el control no respondió. ¿Está transmitiendo?"));
        }
      }, 18000);

      function attachRemote(remote){
        if(audioEl){
          // No pegar stream vacío (deja el player “playing” en silencio)
          try{
            var atracks = remote && remote.getAudioTracks ? remote.getAudioTracks() : [];
            if(!atracks || !atracks.length){
              self._status("Stream sin audio — se mantiene MP3", "err");
              return;
            }
          }catch(e0){}
          try{
            // Quitar src de MP3 solo al tener audio WebRTC real
            try{ audioEl.removeAttribute("src"); audioEl.src = ""; }catch(e1){}
            audioEl.srcObject = remote;
            audioEl.autoplay = true;
            audioEl.playsInline = true;
            audioEl.setAttribute("playsinline", "");
            audioEl.volume = 1;
            audioEl.muted = false;
            audioEl.defaultMuted = false;
          }catch(e){}
          var p = audioEl.play();
          function unmute(){
            try{
              audioEl.muted = false;
              audioEl.defaultMuted = false;
              audioEl.volume = 1;
              audioEl.removeAttribute("muted");
            }catch(e){}
            return audioEl.play().catch(function(){});
          }
          if(p && p.then){
            p.then(function(){ return unmute(); }).catch(function(){
              try{
                // último recurso: muted→play→unmute (política autoplay)
                audioEl.muted = true;
                audioEl.play().then(function(){
                  setTimeout(unmute, 80);
                }).catch(function(){});
              }catch(e){}
            });
          }
          if(self._stallWatch) clearInterval(self._stallWatch);
          var lastT = 0;
          var stuck = 0;
          self._stallWatch = setInterval(function(){
            try{
              if(!audioEl || !self._broadcasterId) return;
              // Reanudar si se pausó solo
              if(audioEl.paused && audioEl.srcObject){
                audioEl.muted = true;
                audioEl.play().then(function(){ audioEl.muted = false; }).catch(function(){});
              }
              // Si el currentTime no avanza ~2.5s con stream, reconectar
              var t = audioEl.currentTime || 0;
              if(audioEl.srcObject && !audioEl.paused){
                if(Math.abs(t - lastT) < 0.05){
                  stuck++;
                  if(stuck >= 3){
                    stuck = 0;
                    self._status("");
                    self._scheduleReconnect();
                  }
                } else {
                  stuck = 0;
                  self._reconnectAttempts = 0;
                }
              }
              lastT = t;
            }catch(e){}
          }, 900);
        }
        self._status("");
      }

      self.call.on("stream", function(remote){
        if(settled){
          // stream renovado
          attachRemote(remote);
          return;
        }
        settled = true;
        clearTimeout(timer);
        attachRemote(remote);
        resolve(remote);
      });

      self.call.on("error", function(err){
        if(settled){
          self._status("Error de enlace — reintentando…");
          self._scheduleReconnect();
          return;
        }
        settled = true;
        clearTimeout(timer);
        reject(err);
      });

      self.call.on("close", function(){
        self._status("Conexión cerrada — reintentando…");
        self._scheduleReconnect();
      });
    });
  };

  Listener.prototype._scheduleReconnect = function(){
    var self = this;
    if(self._reconnectTimer) return;
    if(!self._broadcasterId || !self._audioEl) return;
    if(self._reconnectAttempts == null) self._reconnectAttempts = 0;
    if(self._reconnectAttempts >= 30){
      self._status("");
      return;
    }
    self._reconnectAttempts++;
    // Reintento rápido al inicio, luego un poco más espaciado
    var delay = self._reconnectAttempts < 6 ? 900 : 2000;
    self._reconnectTimer = setTimeout(function(){
      self._reconnectTimer = null;
      self.connect(self._broadcasterId, self._audioEl).then(function(){
        self._reconnectAttempts = 0;
        self._status("");
      }).catch(function(){
        self._scheduleReconnect();
      });
    }, delay);
  };

  Listener.prototype.disconnect = async function(){
    if(this._stallWatch){
      try{ clearInterval(this._stallWatch); }catch(e){}
      this._stallWatch = null;
    }
    if(this._reconnectTimer){
      try{ clearTimeout(this._reconnectTimer); }catch(e){}
      this._reconnectTimer = null;
    }
    this._reconnectAttempts = 0;
    if(this.call){ try{ this.call.close(); }catch(e){} this.call = null; }
    if(this.peer){ try{ this.peer.destroy(); }catch(e){} this.peer = null; }
    if(this._emptyCtx){
      try{ this._emptyCtx.close(); }catch(e){}
      this._emptyCtx = null;
    }
  };

  return { Broadcaster: Broadcaster, Listener: Listener, safeId: safeId };
})();
