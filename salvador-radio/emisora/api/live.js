// ============================================================
// /api/live  — relay del microfono en vivo por HTTP (segmentos ~1s)
// POST   {id,mime,seq,b64}  -> guarda un segmento (solo locutor)
// GET    ?id=&from=N        -> { chunks:[{seq,b64}], mime, latest, next }
// DELETE ?id=               -> limpia (solo locutor)
//
// ALMACEN: usa un blob de jsonblob dedicado para audio, cuyo id se toma de
//   la variable de entorno  STATION_LIVE_ID.  Crea uno vacio en jsonblob.com
//   (contenido {"chunks":[]}) y pega su id en esa variable.
//   Si STATION_LIVE_ID NO esta definido, el mic-HTTP queda desactivado de forma
//   segura: POST responde {skipped:true} (el cliente lo maneja) y GET va vacio.
//   La voz en vivo por PeerJS (live-stream.js) NO depende de esto y sigue
//   funcionando sin backend.
//
// SEGURIDAD: POST/DELETE requieren x-admin-pass === ADMIN_PASSCODE (si esta
//   definido). GET es publico.
// ============================================================

const JSONBLOB = "https://jsonblob.com/api/jsonBlob";
const KEEP = 8; // segmentos recientes que se conservan

async function readBlob(id) {
  const r = await fetch(`${JSONBLOB}/${encodeURIComponent(id)}`, { headers: { Accept: "application/json" } });
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
    req.on("end", () => { try { resolve(raw ? JSON.parse(raw) : {}); } catch { resolve({}); } });
    req.on("error", () => resolve({}));
  });
}
function authed(req) {
  const passcode = (process.env.ADMIN_PASSCODE || "").trim();
  if (!passcode) return true; // proteccion desactivada
  const given = (req.headers["x-admin-pass"] || "").toString().trim();
  return given && given === passcode;
}

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept, Cache-Control, x-admin-pass");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") return res.status(204).end();

  const LIVE_ID = (process.env.STATION_LIVE_ID || "").trim();

  // Mic-HTTP desactivado: responder de forma segura sin romper el cliente.
  if (!LIVE_ID) {
    if (req.method === "GET") return res.status(200).json({ chunks: [], mime: "", latest: 0, next: 0 });
    if (req.method === "POST") return res.status(200).json({ skipped: true, reason: "STATION_LIVE_ID no configurado" });
    if (req.method === "DELETE") return res.status(200).json({ ok: true });
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    if (req.method === "GET") {
      const url = new URL(req.url, "http://x");
      const from = parseInt(url.searchParams.get("from") || "0", 10) || 0;
      let doc; try { doc = await readBlob(LIVE_ID); } catch { doc = { chunks: [], mime: "" }; }
      const all = Array.isArray(doc.chunks) ? doc.chunks : [];
      const chunks = all.filter((c) => typeof c.seq === "number" && c.seq >= from);
      const latest = all.length ? all[all.length - 1].seq : 0;
      const next = latest + 1;
      return res.status(200).json({ chunks, mime: doc.mime || "audio/webm", latest, next });
    }

    if (req.method === "POST") {
      if (!authed(req)) return res.status(401).json({ error: "no autorizado" });
      const body = await readBody(req);
      if (!body || !body.b64 || typeof body.seq !== "number") return res.status(400).json({ error: "segmento invalido" });
      let doc; try { doc = await readBlob(LIVE_ID); } catch { doc = { chunks: [], mime: "" }; }
      if (!Array.isArray(doc.chunks)) doc.chunks = [];
      doc.mime = body.mime || doc.mime || "audio/webm";
      doc.chunks.push({ seq: body.seq, b64: body.b64 });
      while (doc.chunks.length > KEEP) doc.chunks.shift();
      await writeBlob(LIVE_ID, doc);
      return res.status(200).json({ ok: true, seq: body.seq });
    }

    if (req.method === "DELETE") {
      if (!authed(req)) return res.status(401).json({ error: "no autorizado" });
      try { await writeBlob(LIVE_ID, { chunks: [], mime: "" }); } catch {}
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: "Method not allowed" });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
