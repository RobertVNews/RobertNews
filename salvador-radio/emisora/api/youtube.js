// ============================================================
// /api/youtube?url=LINK  -> { ok, videoId, title, artist, cover }
// Resuelve un enlace de YouTube usando oEmbed (sin API key).
// ============================================================

function extractVideoId(link) {
  try {
    const u = new URL(link);
    if (u.hostname.includes("youtu.be")) return u.pathname.slice(1).split("/")[0];
    if (u.searchParams.get("v")) return u.searchParams.get("v");
    const m = u.pathname.match(/\/(embed|shorts|live)\/([^/?#]+)/);
    if (m) return m[2];
  } catch {}
  const m2 = String(link).match(/[?&]v=([^&]+)/) || String(link).match(/youtu\.be\/([^?&/]+)/);
  return m2 ? m2[1] : "";
}

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") return res.status(204).end();

  const url = new URL(req.url, "http://x");
  const link = (url.searchParams.get("url") || "").trim();
  if (!link) return res.status(400).json({ ok: false, error: "Falta ?url=" });

  const videoId = extractVideoId(link);
  if (!videoId) return res.status(400).json({ ok: false, error: "Enlace de YouTube no valido" });

  try {
    const oe = `https://www.youtube.com/oembed?format=json&url=${encodeURIComponent(
      "https://www.youtube.com/watch?v=" + videoId
    )}`;
    const r = await fetch(oe, { headers: { Accept: "application/json" } });
    if (!r.ok) {
      // Aun sin metadatos, el video puede reproducirse por su id.
      return res.status(200).json({
        ok: true, videoId,
        title: "YouTube", artist: "YouTube",
        cover: `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`
      });
    }
    const j = await r.json();
    return res.status(200).json({
      ok: true,
      videoId,
      title: j.title || "YouTube",
      artist: j.author_name || "YouTube",
      cover: j.thumbnail_url || `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`
    });
  } catch (e) {
    return res.status(200).json({
      ok: true, videoId,
      title: "YouTube", artist: "YouTube",
      cover: `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`
    });
  }
};
