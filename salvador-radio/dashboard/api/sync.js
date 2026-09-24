// ============================================================
// /api/sync  — estado compartido de la emisora (jsonblob)
// GET  ?id=BLOB            -> documento completo { state, schedule, requests, brand, updatedAt }
// PUT  ?id=BLOB  body:{}   -> mezcla parcial y guarda
//
// SEGURIDAD:
//   - GET es publico (oyentes leen).
//   - PUT requiere cabecera  x-admin-pass === process.env.ADMIN_PASSCODE
//     EXCEPTO cuando el cuerpo solo trae { requests } (peticiones de canciones
//     de los oyentes), que se permite sin clave.
//   - Si ADMIN_PASSCODE NO esta definido en el entorno, se permite todo
//     (compatibilidad con el comportamiento anterior). Define la variable en
//     Vercel para activar la proteccion.
// ============================================================

const JSONBLOB = "https://jsonblob.com/api/jsonBlob";
const DEFAULT_ID = "019f80b0-f9db-78be-95d7-ddf99254048e";

function defaultDoc() {
  return {
    state: {
      onAir: false, mode: "", source: "",
      testSignal: { enabled: false, at: 0 },
      nowPlaying: null,
      live: { active: false, peerId: "" },
      city: { active: false },
      auto24: { enabled: false, index: 0 }
    },
    schedule: [],
    requests: [],
    brand: "SALVADOR ENTREGAS",
    updatedAt: Date.now()
  };
}

async function readBlob(id) {
  const r = await fetch(`${JSONBLOB}/${encodeURIComponent(id)}`, {
    headers: { Accept: "application/json" }
  });
  if (!r.ok) throw new Error("blob-read " + r.status);
  return r.json();
}

async function writeBlob(id, doc) {
  const r = await fetch(`${JSONBLOB}/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(doc)
  });
  if (!r.ok) throw new Error("blob-write " + r.status);
  return true;
}

function readBody(req) {
  return new Promise((resolve) => {
    if (req.body && typeof req.body === "object") return resolve(req.body);
    let raw = "";
    req.on("data", (c) => (raw += c));
    req.on("end", () => {
      try { resolve(raw ? JSON.parse(raw) : {}); } catch { resolve({}); }
    });
    req.on("error", () => resolve({}));
  });
}

// Solo toca peticiones de oyentes (permitido sin clave)
function isRequestsOnly(partial) {
  const keys = Object.keys(partial || {});
  return keys.length === 1 && keys[0] === "requests";
}

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept, Cache-Control, x-admin-pass");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") return res.status(204).end();

  const url = new URL(req.url, "http://x");
  const id = (url.searchParams.get("id") || DEFAULT_ID).trim();
  const passcode = (process.env.ADMIN_PASSCODE || "").trim();

  try {
    if (req.method === "GET") {
      let doc;
      try { doc = await readBlob(id); }
      catch { doc = defaultDoc(); try { await writeBlob(id, doc); } catch {} }
      return res.status(200).json(doc);
    }

    if (req.method === "PUT" || req.method === "POST") {
      const partial = await readBody(req);

      // Autorizacion
      if (passcode) {
        const given = (req.headers["x-admin-pass"] || "").toString().trim();
        const authed = given && given === passcode;
        if (!authed && !isRequestsOnly(partial)) {
          return res.status(401).json({ error: "Clave del panel incorrecta o ausente" });
        }
      }

      let doc;
      try { doc = await readBlob(id); } catch { doc = defaultDoc(); }

      // Mezcla: top-level assign + state sub-merge (igual que el cliente)
      const next = Object.assign({}, doc, partial);
      if (partial && partial.state) {
        next.state = Object.assign({}, doc.state || {}, partial.state);
      }
      next.updatedAt = Date.now();

      await writeBlob(id, next);
      return res.status(200).json(next);
    }

    return res.status(405).json({ error: "Method not allowed" });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
