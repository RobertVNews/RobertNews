// ============================================================
// CONFIGURACION DE LA EMISORA (archivo PUBLICO — no poner secretos aqui)
// La clave del panel YA NO va aqui: se valida en el servidor (env ADMIN_PASSCODE).
// ============================================================
window.APP_CONFIG = {

  // --- Identidad (marca pública) ---
  SCHOOL_NAME: "SALVADOR ENTREGAS",
  STATION_NAME: "SALVADOR ENTREGAS",
  STATION_TAGLINE: "La voz del colegio",
  SCHOOL_ADDRESS: "Barranquilla",
  SCHOOL_CONTACT: "contacto@colegio.edu.co",
  SCHOOL_SOCIAL: "@SalvadorEntregas",
  // Escudo del colegio (redondo en oyentes y panel)
  SCHOOL_LOGO: "assets/escudo-colegio-sm.jpg",
  SCHOOL_LOGO_SM: "assets/escudo-colegio-sm.jpg",

  // --- Firebase (Firestore) — opcional ---
  FIREBASE_CONFIG: {
    apiKey: "TU_API_KEY",
    authDomain: "TU_PROYECTO.firebaseapp.com",
    projectId: "TU_PROYECTO",
    storageBucket: "TU_PROYECTO.appspot.com",
    messagingSenderId: "TU_SENDER_ID",
    appId: "TU_APP_ID"
  },

  // --- Spotify (Client ID es público por diseño) ---
  SPOTIFY_CLIENT_ID: "0f0dbd9faa024075b819f35a2a159822",
  // DEBE coincidir EXACTO con el dominio del DASHBOARD en Spotify Dashboard → Redirect URIs (sin / al final)
  SPOTIFY_REDIRECT_URI: "https://TU-DASHBOARD.vercel.app/",
  SPOTIFY_PLAYLIST_ID: "",
  SPOTIFY_SCOPES: [
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-top-read",
    "user-read-email",
    "user-read-private",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing"
  ].join(" "),

  // --- Acceso al panel ---
  // La clave NO se guarda aqui (era publica y cualquiera la leia).
  // Se configura como variable de entorno ADMIN_PASSCODE en Vercel y el
  // servidor la valida en /api/sync y /api/live. El locutor la escribe al entrar.
  // ADMIN_PASSCODE: (definido en el servidor, NO aqui)

  // --- Emisión ciudad: Stream Hub + túnel Cloudflare ---
  // IMPORTANTE: este hub NO es Icecast. NO sirve una URL /radio de audio HTTP.
  // /radio y /status devuelven HTML/JSON de estado. El audio real va por WebSocket:
  //   CITY_RELAY_WS = wss://tu-tunel.trycloudflare.com
  // Deja CITY_STREAM_URL vacío salvo que tengas un MP3/Icecast/HLS real.
  CITY_STREAM_URL: "",
  CITY_RELAY_WS: "",
  CITY_MODE_DEFAULT: false,

  // Señal de prueba (MP3 en Vercel) — funciona sin hub/túnel
  TEST_SIGNAL_ENABLED: false,
  TEST_SIGNAL_URL: "/test-signal.mp3",

  // Canal de sintonía FIJO — admin y oyentes deben usar el mismo ID
  // (jsonblob vía /api/sync). Si se borra el blob, el API recrea.
  STATION_SYNC_ID: "019f80b0-f9db-78be-95d7-ddf99254048e"
};
