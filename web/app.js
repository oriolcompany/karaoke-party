const viewLanding = document.getElementById("view-landing");
const viewTitle = document.getElementById("view-title");
const viewMenu = document.getElementById("view-menu");
const viewStage = document.getElementById("view-stage");
const landingEnterBtn = document.getElementById("landingEnterBtn");
const landingStatus = document.getElementById("landingStatus");
const titleRootInput = document.getElementById("titleRootInput");
const titleBrowseBtn = document.getElementById("titleBrowseBtn");
const titleStartBtn = document.getElementById("titleStartBtn");
const titleStartForm = document.getElementById("titleStartForm");
const titleStatus = document.getElementById("titleStatus");
const browseRootBtn = document.getElementById("browseRootBtn");
const coverTrack = document.getElementById("coverTrack");
const songGrid = document.getElementById("songGrid");
const coverflow = document.getElementById("coverflow");
const browsePanel = document.getElementById("browsePanel");
const searchEl = document.getElementById("search");
const rootInput = document.getElementById("rootInput");
const loadBtn = document.getElementById("loadBtn");
const retryLyricsBtn = document.getElementById("retryLyricsBtn");
const resyncLyricsMissingBtn = document.getElementById("resyncLyricsMissingBtn");
const syncLyricsWhisperBtn = document.getElementById("syncLyricsWhisperBtn");
const resyncCoverBtn = document.getElementById("resyncCoverBtn");
const backBtn = document.getElementById("backBtn");
const player = document.getElementById("player");
const previewPlayers = [
  document.getElementById("previewPlayer"),
  Object.assign(new Audio(), { preload: "auto" }),
];
const lyricsEl = document.getElementById("lyrics");
const kStackEl = document.getElementById("kStack") || lyricsEl;
const lineCurrentEl = document.getElementById("lineCurrent");
const lineNextEl = document.getElementById("lineNext");
const songTitle = document.getElementById("songTitle");
const songArtist = document.getElementById("songArtist");
const lyricsStatus = document.getElementById("lyricsStatus");
const libraryMeta = document.getElementById("libraryMeta");
const playBtn = document.getElementById("playBtn");
const coverArtist = document.getElementById("coverArtist");
const coverTitle = document.getElementById("coverTitle");
const coverIndex = document.getElementById("coverIndex");
const coverPrev = document.getElementById("coverPrev");
const coverNext = document.getElementById("coverNext");
const singBtn = document.getElementById("singBtn");
const pasteLyricsBtn = document.getElementById("pasteLyricsBtn");
const stagePasteLyricsBtn = document.getElementById("stagePasteLyricsBtn");
const lyricsPasteModal = document.getElementById("lyricsPasteModal");
const lyricsPasteCloseBtn = document.getElementById("lyricsPasteCloseBtn");
const lyricsPasteCancelBtn = document.getElementById("lyricsPasteCancelBtn");
const lyricsPasteSaveBtn = document.getElementById("lyricsPasteSaveBtn");
const lyricsPasteInput = document.getElementById("lyricsPasteInput");
const lyricsPasteMeta = document.getElementById("lyricsPasteMeta");
const lyricsPasteStatus = document.getElementById("lyricsPasteStatus");
const lyricsPasteTitle = document.getElementById("lyricsPasteTitle");
const modeCoverBtn = document.getElementById("modeCover");
const modeGridBtn = document.getElementById("modeGrid");
const syncStatusBtn = document.getElementById("syncStatusBtn");
const syncQueueMeta = document.getElementById("syncQueueMeta");
const settingsBtn = document.getElementById("settingsBtn");
const settingsModal = document.getElementById("settingsModal");
const settingsCloseBtn = document.getElementById("settingsCloseBtn");
const librarySettingsStatus = document.getElementById("librarySettingsStatus");
const lyricsSyncSettingsStatus = document.getElementById("lyricsSyncSettingsStatus");
const whisperModelStatus = document.getElementById("whisperModelStatus");
const libraryBrowseSongBtn = document.getElementById("libraryBrowseSongBtn");
const libraryBrowseAlbumBtn = document.getElementById("libraryBrowseAlbumBtn");
const lyricsFilterLyricsBtn = document.getElementById("lyricsFilterLyricsBtn");
const lyricsFilterHiddenBtn = document.getElementById("lyricsFilterHiddenBtn");
const lyricsFilterAllBtn = document.getElementById("lyricsFilterAllBtn");
const muteOffBtn = document.getElementById("muteOffBtn");
const muteOnBtn = document.getElementById("muteOnBtn");
const lyricsLayoutStackBtn = document.getElementById("lyricsLayoutStackBtn");
const lyricsLayoutDualBtn = document.getElementById("lyricsLayoutDualBtn");
const auraParticlesOnBtn = document.getElementById("auraParticlesOnBtn");
const auraParticlesOffBtn = document.getElementById("auraParticlesOffBtn");
const audioModeToggle = document.getElementById("audioModeToggle");
const audioModeOriginalBtn = document.getElementById("audioModeOriginalBtn");
const audioModeInstrumentalBtn = document.getElementById("audioModeInstrumentalBtn");
const audioModeStatus = document.getElementById("audioModeStatus");
const videoStatus = document.getElementById("videoStatus");
const videoModeToggle = document.getElementById("videoModeToggle");
const videoModeOnBtn = document.getElementById("videoModeOnBtn");
const videoModeCoverBtn = document.getElementById("videoModeCoverBtn");
const videoModeAuraBtn = document.getElementById("videoModeAuraBtn");
const videoModeOffBtn = document.getElementById("videoModeOffBtn");
const stageVideoEl = document.getElementById("stageVideo");
const stageCoverEl = document.getElementById("stageCover");
const stageAuraEl = document.getElementById("stageAura");
const stageAuraCanvas = document.getElementById("stageAuraCanvas");
const stageCoverArt = document.getElementById("stageCoverArt");
const stageCoverBlur = document.getElementById("stageCoverBlur");
const stageVideoDimEl = document.getElementById("stageVideoDim");
const generateStemsBtn = document.getElementById("generateStemsBtn");
const stemsSettingsStatus = document.getElementById("stemsSettingsStatus");
const searchYoutubeMissingBtn = document.getElementById("searchYoutubeMissingBtn");
const searchYoutubeAllBtn = document.getElementById("searchYoutubeAllBtn");
const youtubeSettingsStatus = document.getElementById("youtubeSettingsStatus");
const cacheSongSearch = document.getElementById("cacheSongSearch");
const cacheSongSelect = document.getElementById("cacheSongSelect");
const cacheSongMeta = document.getElementById("cacheSongMeta");
const cacheFlags = document.getElementById("cacheFlags");
const cacheScopeLyrics = document.getElementById("cacheScopeLyrics");
const cacheScopeAligned = document.getElementById("cacheScopeAligned");
const cacheScopeStems = document.getElementById("cacheScopeStems");
const cacheScopeCover = document.getElementById("cacheScopeCover");
const cacheScopeYoutube = document.getElementById("cacheScopeYoutube");
const cacheClearBtn = document.getElementById("cacheClearBtn");
const cacheResyncBtn = document.getElementById("cacheResyncBtn");
const cacheClearAllBtn = document.getElementById("cacheClearAllBtn");
const cacheExportBtn = document.getElementById("cacheExportBtn");
const cacheImportBtn = document.getElementById("cacheImportBtn");
const cacheImportFile = document.getElementById("cacheImportFile");
const cacheSettingsStatus = document.getElementById("cacheSettingsStatus");
const albumBackBtn = document.getElementById("albumBackBtn");

const GENERIC_COVER = "/album-generic.png";
const COVER_VISIBLE = 4;
const VIEW_MODE_KEY = "karaoke-browse-mode";
const ALIGN_MODE_KEY = "karaoke-align-mode";
const LIBRARY_BROWSE_KEY = "karaoke-library-browse";
const LYRICS_FILTER_KEY = "karaoke-lyrics-filter";
const LYRICS_LAYOUT_KEY = "karaoke-lyrics-layout";
const AURA_PARTICLES_KEY = "karaoke-aura-particles";
const AUDIO_MODE_KEY = "karaoke-audio-mode";
const STAGE_VIDEO_KEY = "karaoke-stage-video";
const STAGE_BG_KEY = "karaoke-stage-bg";
const MUTE_KEY = "karaoke-muted";
let coverBust = 0;

function loadLyricsLayout() {
  const stored = localStorage.getItem(LYRICS_LAYOUT_KEY);
  return stored === "dual" ? "dual" : "stack";
}

function loadAuraParticlesEnabled() {
  return localStorage.getItem(AURA_PARTICLES_KEY) !== "0";
}

function loadAudioMode() {
  return localStorage.getItem(AUDIO_MODE_KEY) === "instrumental" ? "instrumental" : "original";
}

const STAGE_BG_MODES = new Set(["video", "cover", "aura", "stage"]);

function loadStageBgMode() {
  const stored = localStorage.getItem(STAGE_BG_KEY);
  if (STAGE_BG_MODES.has(stored)) return stored;
  return localStorage.getItem(STAGE_VIDEO_KEY) === "0" ? "stage" : "video";
}

function loadLyricsFilterMode() {
  const stored = localStorage.getItem(LYRICS_FILTER_KEY);
  if (stored === "lyrics" || stored === "hidden" || stored === "all") return stored;
  // legacy toggle: karaoke-show-hidden-only
  if (localStorage.getItem("karaoke-show-hidden-only") === "1") return "hidden";
  return "lyrics";
}

const ICON_SYNCED =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.2 16.6 5.4 12.8l1.4-1.4 2.4 2.4 7-7 1.4 1.4z"/></svg>`;
const ICON_CLOCK =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zm0 2a6 6 0 1 1 0 12 6 6 0 0 1 0-12zm-.8 2.5h1.6v4.2l3.2 1.9-.8 1.3-4-2.4V8.5z"/></svg>`;
const ICON_QUEUE =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 6h16v2H4zm0 5h16v2H4zm0 5h10v2H4z"/></svg>`;
const ICON_RUNNING =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 14h2v4H4zm3.5-4h2v8h-2zm3.5-5h2v13h-2zm3.5 3h2v10h-2zm3.5 2h2v8h-2z"/></svg>`;

function loadAlignMode() {
  const stored = localStorage.getItem(ALIGN_MODE_KEY);
  if (stored === "off" || stored === "status" || stored === "synced") return stored;
  // legacy toggle
  if (localStorage.getItem("karaoke-show-align") === "1") return "status";
  return "off";
}

let playableTracks = [];
let hiddenTracks = [];
let pendingTracks = [];
let tracks = [];
let filteredTracks = [];
let filteredAlbums = [];
let selectedIndex = 0;
let previewToken = 0;
let previewActive = 0;
let previewFadeTimer = 0;
const PREVIEW_FADE_IN_MS = 90;
let previewCtx = null;
let previewGains = [null, null];
let previewMasterGain = null;
let previewGraphReady = false;
let uiSfxCtx = null;
let lastCoverTickAt = 0;
let browseMode = localStorage.getItem(VIEW_MODE_KEY) === "grid" ? "grid" : "cover";
let libraryBrowseMode =
  localStorage.getItem(LIBRARY_BROWSE_KEY) === "album" ? "album" : "song";
let lyricsFilterMode = loadLyricsFilterMode();
let audioMuted = localStorage.getItem(MUTE_KEY) === "1";
let lyricsLayout = loadLyricsLayout();
let auraParticlesEnabled = loadAuraParticlesEnabled();
let audioMode = loadAudioMode();
let stageBgMode = loadStageBgMode();
let bootLibraryReady = false;
let bootWork = Promise.resolve();
let landingEntering = false;
let stemsAvailable = false;
let stemsJobTimer = 0;
let stemsBulkTimer = 0;
let youtubeBulkTimer = 0;
let openedAlbum = null;
let alignMode = loadAlignMode();
let currentId = null;
let lyricLines = [];
let lastLyricsPlain = "";
let lyricsPasteTrackId = "";
let lyricsAligned = false;
let activeLineIndex = -1;
let wordNodes = [];
let lineSwapTimer = null;
let dualRefreshTimer = null;
/** @type {{ slotEl: HTMLElement, line: object } | null} */
let dualPending = null;
let rafId = 0;
let alignPollTimer = 0;
let alignToken = 0;
let stageOutroTimer = 0;
let youtubeToken = 0;
let youtubeApiPromise = null;
let youtubePlayer = null;
let youtubeCurrent = null;
let youtubeWantedId = "";
let youtubeEmbedOk = false;
let lastYoutubeSync = 0;
const YOUTUBE_DRIFT_SEC = 0.45;

/** @type {string[]} */
const syncQueue = [];
const syncQueuedIds = new Set();
let syncActiveId = null;
let syncRunning = false;
let syncLastError = "";
let syncProgress = 0;
let syncPhase = "";
let syncStemPhase = "";
let syncTotalQueued = 0;
let syncCompleted = 0;

async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || res.statusText);
  }
  return res.json();
}

function formatDuration(seconds) {
  if (!seconds) return "";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${m}:${s}`;
}

function stopAlignPoll() {
  if (alignPollTimer) {
    clearInterval(alignPollTimer);
    alignPollTimer = 0;
  }
  alignToken += 1;
}

function clearStageOutro() {
  if (stageOutroTimer) {
    clearTimeout(stageOutroTimer);
    stageOutroTimer = 0;
  }
  viewStage.classList.remove("is-outro");
}

function setTitleStatus(message, kind) {
  if (!titleStatus) return;
  titleStatus.textContent = message || "";
  titleStatus.classList.toggle("is-error", kind === "error");
  titleStatus.classList.toggle("is-running", kind === "running");
}

function setLandingStatus(message, kind) {
  if (!landingStatus) return;
  landingStatus.textContent = message || "";
  landingStatus.classList.toggle("is-error", kind === "error");
  landingStatus.classList.toggle("is-running", kind === "running");
}

function isLandingVisible() {
  return Boolean(viewLanding && !viewLanding.classList.contains("hidden"));
}

function showLanding() {
  clearStageOutro();
  viewLanding?.classList.remove("hidden");
  viewTitle?.classList.add("hidden");
  viewMenu.classList.add("hidden");
  viewStage.classList.add("hidden");
  document.body.classList.add("mode-title");
  document.body.classList.remove("mode-stage");
  viewStage.classList.remove("is-live");
  player.pause();
  teardownYoutubeBackdrop();
  stopTicker();
  stopAlignPoll();
  currentId = null;
  updatePlayButton();
  landingEnterBtn?.focus();
  syncAuraEngine();
}

function showTitleScreen() {
  clearStageOutro();
  viewLanding?.classList.add("hidden");
  viewTitle?.classList.remove("hidden");
  viewMenu.classList.add("hidden");
  viewStage.classList.add("hidden");
  document.body.classList.add("mode-title");
  document.body.classList.remove("mode-stage");
  viewStage.classList.remove("is-live");
  player.pause();
  teardownYoutubeBackdrop();
  stopTicker();
  stopAlignPoll();
  currentId = null;
  updatePlayButton();
  titleRootInput?.focus();
  syncAuraEngine();
}

function showMenu() {
  clearStageOutro();
  viewLanding?.classList.add("hidden");
  viewTitle?.classList.add("hidden");
  viewMenu.classList.remove("hidden");
  viewStage.classList.add("hidden");
  document.body.classList.remove("mode-title");
  document.body.classList.remove("mode-stage");
  viewStage.classList.remove("is-live");
  player.pause();
  teardownYoutubeBackdrop();
  stopTicker();
  stopAlignPoll();
  currentId = null;
  updatePlayButton();
  renderSongs(searchEl.value);
  syncAuraEngine();
}

function beginStageOutro() {
  clearStageOutro();
  viewStage.classList.remove("is-live");
  viewStage.classList.add("is-outro");
  pauseYoutubePlayer();
  stopTicker();
  updatePlayButton();
  const trackId = currentId;
  stageOutroTimer = setTimeout(() => {
    stageOutroTimer = 0;
    if (currentId !== trackId) return;
    showMenu();
  }, 500);
}

function previewSlots() {
  return {
    current: previewPlayers[previewActive],
    next: previewPlayers[1 - previewActive],
    currentGain: previewGains[previewActive],
    nextGain: previewGains[1 - previewActive],
    currentIndex: previewActive,
    nextIndex: 1 - previewActive,
  };
}

function applyLyricsLayout() {
  const dual = lyricsLayout === "dual";
  lyricsLayoutStackBtn?.classList.toggle("is-active", !dual);
  lyricsLayoutDualBtn?.classList.toggle("is-active", dual);
  lyricsLayoutStackBtn?.setAttribute("aria-pressed", dual ? "false" : "true");
  lyricsLayoutDualBtn?.setAttribute("aria-pressed", dual ? "true" : "false");
  lyricsEl?.classList.toggle("is-dual", dual);
  lyricsEl?.classList.toggle("is-stack", !dual);
}

function setLyricsLayout(mode) {
  lyricsLayout = mode === "dual" ? "dual" : "stack";
  localStorage.setItem(LYRICS_LAYOUT_KEY, lyricsLayout);
  applyLyricsLayout();
  if (lyricLines.length) {
    const index = Math.max(0, activeLineIndex);
    activeLineIndex = -1;
    setActiveLine(index);
  }
}

function applyAuraParticles() {
  const on = auraParticlesEnabled;
  auraParticlesOnBtn?.classList.toggle("is-active", on);
  auraParticlesOffBtn?.classList.toggle("is-active", !on);
  auraParticlesOnBtn?.setAttribute("aria-pressed", on ? "true" : "false");
  auraParticlesOffBtn?.setAttribute("aria-pressed", on ? "false" : "true");
  viewStage?.classList.toggle("aura-no-particles", !on);
  if (!on) auraParticles = [];
  else if (auraRunning && !auraParticles.length) {
    seedAuraParticles(Math.min(240, Math.floor((auraW * auraH) / 9000) + 90));
  }
}

function setAuraParticlesEnabled(enabled) {
  auraParticlesEnabled = Boolean(enabled);
  localStorage.setItem(AURA_PARTICLES_KEY, auraParticlesEnabled ? "1" : "0");
  applyAuraParticles();
}

function audioUrlFor(trackId, mode) {
  const base = `/api/audio/${encodeURI(trackId)}`;
  return mode === "instrumental" ? `${base}?mode=instrumental` : base;
}

function setStemStatus(text) {
  if (audioModeStatus) audioModeStatus.textContent = text || "";
}

function setVideoStatus(text) {
  if (videoStatus) videoStatus.textContent = text || "";
}

function applyAudioModeButtons() {
  const instrumental = audioMode === "instrumental";
  audioModeOriginalBtn?.classList.toggle("is-active", !instrumental);
  audioModeInstrumentalBtn?.classList.toggle("is-active", instrumental);
  audioModeOriginalBtn?.setAttribute("aria-pressed", instrumental ? "false" : "true");
  audioModeInstrumentalBtn?.setAttribute("aria-pressed", instrumental ? "true" : "false");
  if (audioModeToggle) audioModeToggle.hidden = !stemsAvailable;
}

function coverUrlFor(trackId) {
  const bust = coverBust ? `?t=${coverBust}` : "";
  return trackId ? `/api/cover/${encodeURI(trackId)}${bust}` : GENERIC_COVER;
}

function setStageCover(trackId) {
  const url = coverUrlFor(trackId);
  for (const img of [stageCoverArt, stageCoverBlur]) {
    if (!img) continue;
    img.onerror = () => {
      img.onerror = null;
      img.src = GENERIC_COVER;
    };
    img.src = url;
  }
}

function youtubeVideoReady() {
  return Boolean(youtubeCurrent?.found && youtubeCurrent?.video_id && youtubeEmbedOk);
}

const AURA_RIBBONS = [
  { rgb: [255, 45, 106], amp: 0.12, freq: 1.15, speed: 0.32, width: 6, phase: 0.2, y: 0.18 },
  { rgb: [255, 225, 74], amp: 0.1, freq: 0.82, speed: -0.24, width: 4, phase: 1.7, y: 0.8 },
  { rgb: [61, 231, 255], amp: 0.11, freq: 1.4, speed: 0.41, width: 4, phase: 3.1, y: 0.14 },
  { rgb: [255, 120, 60], amp: 0.09, freq: 0.62, speed: -0.18, width: 7, phase: 4.4, y: 0.86 },
];

let auraRaf = 0;
let auraRunning = false;
let auraCtx = null;
let auraW = 0;
let auraH = 0;
let auraDpr = 1;
let auraParticles = [];
let auraT0 = 0;

function auraReduceMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function auraLive() {
  return Boolean(viewStage?.classList.contains("is-live"));
}

function seedAuraParticles(count) {
  auraParticles = Array.from({ length: count }, () => ({
    x: Math.random(),
    y: Math.random(),
    z: 0.35 + Math.random() * 0.65,
    vx: (Math.random() - 0.5) * 0.00035,
    vy: -0.00012 - Math.random() * 0.00028,
    hue: Math.floor(Math.random() * 3),
  }));
}

function resizeAuraCanvas() {
  if (!stageAuraCanvas || !stageAuraEl) return;
  const rect = stageAuraEl.getBoundingClientRect();
  auraDpr = Math.min(window.devicePixelRatio || 1, 1.5);
  auraW = Math.max(1, Math.floor(rect.width));
  auraH = Math.max(1, Math.floor(rect.height));
  stageAuraCanvas.width = Math.floor(auraW * auraDpr);
  stageAuraCanvas.height = Math.floor(auraH * auraDpr);
  auraCtx = stageAuraCanvas.getContext("2d", { alpha: false });
  if (auraCtx) auraCtx.setTransform(auraDpr, 0, 0, auraDpr, 0, 0);
}

function drawAuraRibbon(t, spec, live) {
  if (!auraCtx) return;
  const steps = 48;
  const [r, g, b] = spec.rgb;
  const energy = live ? 1.35 : 1;
  auraCtx.beginPath();
  for (let i = 0; i <= steps; i += 1) {
    const u = i / steps;
    const x = u * auraW;
    const wave =
      Math.sin(u * Math.PI * 2 * spec.freq + t * spec.speed + spec.phase) * spec.amp +
      Math.sin(u * Math.PI * 5.2 + t * spec.speed * 0.55) * spec.amp * 0.35;
    const y = auraH * (spec.y + wave * energy * 0.55);
    if (i === 0) auraCtx.moveTo(x, y);
    else auraCtx.lineTo(x, y);
  }
  auraCtx.strokeStyle = `rgba(${r},${g},${b},${live ? 0.28 : 0.18})`;
  auraCtx.lineWidth = spec.width * (live ? 1.25 : 1);
  auraCtx.lineCap = "round";
  auraCtx.stroke();
}

function drawAuraFrame(ts) {
  if (!auraCtx || !auraW) return;
  const t = (ts - auraT0) / 1000;
  const live = auraLive();
  auraCtx.globalCompositeOperation = "source-over";
  auraCtx.fillStyle = "rgba(3, 2, 8, 0.22)";
  auraCtx.fillRect(0, 0, auraW, auraH);

  auraCtx.globalCompositeOperation = "lighter";
  for (const spec of AURA_RIBBONS) drawAuraRibbon(t, spec, live);

  if (!auraParticlesEnabled) return;

  const palette = [
    [255, 45, 106],
    [255, 225, 74],
    [61, 231, 255],
  ];
  for (const p of auraParticles) {
    p.x += p.vx * (live ? 1.8 : 1) + Math.sin(t * 0.6 + p.y * 12) * 0.00012;
    p.y += p.vy * (live ? 1.6 : 1);
    if (p.y < -0.04) p.y = 1.04;
    if (p.x < -0.04) p.x = 1.04;
    if (p.x > 1.04) p.x = -0.04;
    const [r, g, b] = palette[p.hue];
    const s = (live ? 2.0 : 1.4) * p.z;
    auraCtx.fillStyle = `rgba(${r},${g},${b},${0.12 + p.z * 0.32})`;
    auraCtx.beginPath();
    auraCtx.arc(p.x * auraW, p.y * auraH, s, 0, Math.PI * 2);
    auraCtx.fill();
  }
}

function tickAura(ts) {
  if (!auraRunning) return;
  drawAuraFrame(ts);
  auraRaf = requestAnimationFrame(tickAura);
}

function stopAuraEngine() {
  auraRunning = false;
  if (auraRaf) {
    cancelAnimationFrame(auraRaf);
    auraRaf = 0;
  }
}

function startAuraEngine() {
  if (!stageAuraCanvas) return;
  resizeAuraCanvas();
  if (auraCtx) {
    auraCtx.setTransform(auraDpr, 0, 0, auraDpr, 0, 0);
    auraCtx.fillStyle = "#030208";
    auraCtx.fillRect(0, 0, auraW, auraH);
  }
  if (auraParticlesEnabled && !auraParticles.length) {
    seedAuraParticles(Math.min(240, Math.floor((auraW * auraH) / 9000) + 90));
  }
  if (!auraT0) auraT0 = performance.now();
  if (auraReduceMotion()) {
    if (auraCtx) {
      auraCtx.fillStyle = "#030208";
      auraCtx.fillRect(0, 0, auraW, auraH);
      drawAuraFrame(auraT0);
    }
    return;
  }
  if (auraRunning) return;
  auraRunning = true;
  auraRaf = requestAnimationFrame(tickAura);
}

function syncAuraEngine() {
  const on =
    stageBgMode === "aura" && viewStage && !viewStage.classList.contains("hidden");
  if (on) startAuraEngine();
  else stopAuraEngine();
}

window.addEventListener("resize", () => {
  if (!auraRunning && stageBgMode !== "aura") return;
  resizeAuraCanvas();
});

function applyVideoModeButtons() {
  const videoReady = youtubeVideoReady();
  const videoOn = stageBgMode === "video" && videoReady;
  const coverOn = stageBgMode === "cover";
  const auraOn = stageBgMode === "aura";
  videoModeOnBtn?.classList.toggle("is-active", videoOn);
  videoModeCoverBtn?.classList.toggle("is-active", coverOn);
  videoModeAuraBtn?.classList.toggle("is-active", auraOn);
  videoModeOffBtn?.classList.toggle("is-active", stageBgMode === "stage");
  videoModeOnBtn?.setAttribute("aria-pressed", videoOn ? "true" : "false");
  videoModeCoverBtn?.setAttribute("aria-pressed", coverOn ? "true" : "false");
  videoModeAuraBtn?.setAttribute("aria-pressed", auraOn ? "true" : "false");
  videoModeOffBtn?.setAttribute("aria-pressed", stageBgMode === "stage" ? "true" : "false");
  if (videoModeOnBtn) {
    videoModeOnBtn.disabled = !videoReady;
    videoModeOnBtn.title = videoReady
      ? ""
      : youtubeCurrent?.found
        ? "El videoclip encara s’està carregant"
        : "Encara no hi ha videoclip";
  }
  if (videoModeToggle) videoModeToggle.hidden = false;
  viewStage?.classList.toggle("has-video", videoOn);
  viewStage?.classList.toggle("has-cover", coverOn);
  viewStage?.classList.toggle("has-aura", auraOn);
  if (stageVideoEl) stageVideoEl.setAttribute("aria-hidden", videoOn ? "false" : "true");
  if (stageCoverEl) stageCoverEl.setAttribute("aria-hidden", coverOn ? "false" : "true");
  if (stageAuraEl) stageAuraEl.setAttribute("aria-hidden", auraOn ? "false" : "true");
  if (stageVideoDimEl) {
    stageVideoDimEl.setAttribute("aria-hidden", videoOn || coverOn || auraOn ? "false" : "true");
  }
  syncAuraEngine();
}

function setStageBgMode(mode) {
  if (mode === "video" && !youtubeVideoReady()) return;
  stageBgMode = STAGE_BG_MODES.has(mode) ? mode : "stage";
  localStorage.setItem(STAGE_BG_KEY, stageBgMode);
  applyVideoModeButtons();
  if (stageBgMode === "video" && youtubeCurrent?.video_id) {
    const ids = youtubeCandidateIds(youtubeCurrent);
    const tryNext = (index) => {
      if (index >= ids.length) {
        youtubeEmbedOk = false;
        applyVideoModeButtons();
        return;
      }
      ensureYoutubePlayer(ids[index])
        .then(() => {
          youtubeCurrent = { ...youtubeCurrent, video_id: ids[index] };
          applyVideoModeButtons();
          syncYoutubeToAudio();
        })
        .catch(() => tryNext(index + 1));
    };
    tryNext(0);
  } else {
    pauseYoutubePlayer();
  }
}

function loadYoutubeApi() {
  if (window.YT && window.YT.Player) return Promise.resolve();
  if (youtubeApiPromise) return youtubeApiPromise;
  youtubeApiPromise = new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      youtubeApiPromise = null;
      reject(new Error("YouTube API timeout"));
    }, 12000);
    const previous = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      clearTimeout(timer);
      if (typeof previous === "function") previous();
      resolve();
    };
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.async = true;
    script.onerror = () => {
      clearTimeout(timer);
      youtubeApiPromise = null;
      reject(new Error("YouTube API"));
    };
    document.head.appendChild(script);
  });
  return youtubeApiPromise;
}

function youtubePlayerVars() {
  return {
    autoplay: 1,
    cc_load_policy: 0,
    controls: 0,
    disablekb: 1,
    enablejsapi: 1,
    fs: 0,
    iv_load_policy: 3,
    modestbranding: 1,
    mute: 1,
    origin: window.location.origin,
    playsinline: 1,
    rel: 0,
    widget_referrer: window.location.href,
  };
}

function lockYoutubeReferrer(root) {
  const nodes = root?.querySelectorAll?.("iframe") || [];
  for (const el of nodes) {
    // YouTube 153 if the embed request has no Referer. Keep this on the
    // iframe *before* it navigates; YT.Player may clone the node.
    el.setAttribute("referrerpolicy", "origin");
    try {
      el.referrerPolicy = "origin";
    } catch {
      /* ignore */
    }
  }
}

function buildYoutubeIframe() {
  const iframe = document.createElement("iframe");
  iframe.id = "stageVideoHost";
  iframe.title = "Videoclip";
  iframe.setAttribute("referrerpolicy", "origin");
  iframe.referrerPolicy = "origin";
  iframe.setAttribute(
    "allow",
    "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  );
  iframe.setAttribute("allowfullscreen", "");
  iframe.setAttribute("frameborder", "0");
  return iframe;
}

function resetYoutubeHost() {
  if (youtubePlayer) {
    try {
      youtubePlayer.destroy();
    } catch {
      /* ignore */
    }
    youtubePlayer = null;
  }
  youtubeWantedId = "";
  youtubeEmbedOk = false;
  const frame = stageVideoEl?.querySelector(".stage-video-frame");
  if (!frame) return null;
  frame.innerHTML = "";
  const iframe = buildYoutubeIframe();
  frame.appendChild(iframe);
  lockYoutubeReferrer(frame);
  return iframe;
}

function muteYoutubePlayer(target) {
  const playerYt = target || youtubePlayer;
  if (!playerYt) return;
  try {
    if (typeof playerYt.mute === "function") playerYt.mute();
    if (typeof playerYt.setVolume === "function") playerYt.setVolume(0);
  } catch {
    /* ignore */
  }
}

function pauseYoutubePlayer() {
  if (!youtubePlayer || typeof youtubePlayer.pauseVideo !== "function") return;
  try {
    youtubePlayer.pauseVideo();
  } catch {
    /* ignore */
  }
}

function teardownYoutubeBackdrop() {
  youtubeToken += 1;
  youtubeCurrent = null;
  pauseYoutubePlayer();
  resetYoutubeHost();
  setVideoStatus("");
  applyVideoModeButtons();
}

function youtubePlayerReady() {
  return Boolean(
    youtubePlayer &&
      typeof youtubePlayer.getPlayerState === "function" &&
      typeof youtubePlayer.seekTo === "function"
  );
}

function syncYoutubeToAudio() {
  if (stageBgMode !== "video" || !youtubeCurrent?.video_id || !youtubePlayerReady()) return;
  muteYoutubePlayer();
  const audioPlaying = !player.paused && !player.ended;
  const t = Number(player.currentTime) || 0;
  let ytTime = 0;
  let state = -1;
  try {
    ytTime = Number(youtubePlayer.getCurrentTime()) || 0;
    state = youtubePlayer.getPlayerState();
  } catch {
    return;
  }
  const YT = window.YT;
  const playing = YT ? YT.PlayerState.PLAYING : 1;
  const buffering = YT ? YT.PlayerState.BUFFERING : 3;
  if (state !== buffering && Math.abs(ytTime - t) > YOUTUBE_DRIFT_SEC) {
    try {
      youtubePlayer.seekTo(t, true);
    } catch {
      /* ignore */
    }
  }
  try {
    if (audioPlaying && state !== playing) youtubePlayer.playVideo();
    else if (!audioPlaying && state === playing) youtubePlayer.pauseVideo();
  } catch {
    /* ignore */
  }
}

function youtubeStatePlaying(state) {
  const YT = window.YT;
  const playing = YT ? YT.PlayerState.PLAYING : 1;
  const buffering = YT ? YT.PlayerState.BUFFERING : 3;
  return state === playing || state === buffering;
}

function createYoutubePlayer(videoId, host) {
  return loadYoutubeApi().then(
    () =>
      new Promise((resolve, reject) => {
        const iframe = resetYoutubeHost();
        if (!iframe || !window.YT?.Player) {
          reject(new Error("YouTube host"));
          return;
        }
        youtubeWantedId = videoId;
        let settled = false;
        const timer = setTimeout(() => {
          if (settled) return;
          settled = true;
          youtubeEmbedOk = false;
          reject(new Error("YouTube player timeout"));
        }, 8000);
        const finish = (err, player) => {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          if (err) {
            youtubeEmbedOk = false;
            reject(err);
          } else {
            youtubeEmbedOk = true;
            resolve(player);
          }
        };
        try {
          const domain = host || "www.youtube.com";
          youtubePlayer = new window.YT.Player(iframe, {
            videoId,
            host: `https://${domain}`,
            playerVars: youtubePlayerVars(),
            events: {
              onReady: (event) => {
                if (youtubeWantedId !== videoId) return;
                lockYoutubeReferrer(stageVideoEl);
                muteYoutubePlayer(event.target);
                // onReady fires even with error 153 / "video no disponible".
                // Only accept the embed once media actually buffers.
                try {
                  event.target.mute();
                  event.target.playVideo();
                } catch {
                  /* ignore */
                }
              },
              onStateChange: (event) => {
                muteYoutubePlayer(event.target);
                if (youtubeWantedId !== videoId) return;
                if (youtubeStatePlaying(event.data)) finish(null, event.target);
              },
              onError: (event) => {
                youtubeEmbedOk = false;
                applyVideoModeButtons();
                finish(new Error(`YouTube embed ${event?.data ?? ""}`.trim()));
              },
            },
          });
          lockYoutubeReferrer(stageVideoEl);
        } catch (err) {
          finish(err);
        }
      })
  );
}

function ensureYoutubePlayer(videoId) {
  if (!videoId) return Promise.reject(new Error("no video"));
  if (youtubeWantedId === videoId && youtubePlayerReady() && youtubeEmbedOk) {
    return Promise.resolve(youtubePlayer);
  }
  return createYoutubePlayer(videoId, "www.youtube.com").catch(() =>
    createYoutubePlayer(videoId, "www.youtube-nocookie.com")
  );
}

function youtubeCandidateIds(payload) {
  const ids = [];
  for (const value of [payload?.video_id, ...(payload?.candidates || [])]) {
    const id = String(value || "").trim();
    if (id && !ids.includes(id)) ids.push(id);
  }
  return ids;
}

async function loadYoutubeBackdrop(trackId) {
  const token = ++youtubeToken;
  youtubeCurrent = null;
  pauseYoutubePlayer();
  resetYoutubeHost();
  applyVideoModeButtons();
  setVideoStatus("Cercant videoclip…");
  try {
    const payload = await api(`/api/youtube?track_id=${encodeURIComponent(trackId)}`);
    if (token !== youtubeToken || currentId !== trackId) return;
    const ids = youtubeCandidateIds(payload);
    if (!payload?.found || !ids.length) {
      youtubeCurrent = null;
      applyVideoModeButtons();
      setVideoStatus(
        payload?.source === "error" || payload?.source === "unavailable"
          ? "No s’ha pogut cercar el videoclip"
          : "No s’ha trobat videoclip"
      );
      return;
    }
    youtubeCurrent = payload;
    applyVideoModeButtons();
    let loaded = false;
    for (const videoId of ids) {
      if (token !== youtubeToken || currentId !== trackId) return;
      try {
        await ensureYoutubePlayer(videoId);
        if (token !== youtubeToken || currentId !== trackId) return;
        youtubeCurrent = { ...payload, video_id: videoId };
        loaded = true;
        break;
      } catch {
        /* try next candidate / host */
      }
    }
    if (!loaded) {
      youtubeEmbedOk = false;
      setVideoStatus("Videoclip trobat, però YouTube no l’ha pogut mostrar");
      applyVideoModeButtons();
      return;
    }
    applyVideoModeButtons();
    if (stageBgMode === "video") {
      syncYoutubeToAudio();
    } else {
      pauseYoutubePlayer();
    }
    setVideoStatus("");
  } catch {
    if (token !== youtubeToken || currentId !== trackId) return;
    youtubeCurrent = null;
    applyVideoModeButtons();
    setVideoStatus("No s’ha pogut cercar el videoclip");
  }
}

function applyStemsAvailability(data) {
  stemsAvailable = !!data.stems_available;
  applyAudioModeButtons();
  applyYoutubeBulkAvailability(data);
  if (!generateStemsBtn) return;
  const bulk = data.stems || {};
  if (!stemsAvailable) {
    generateStemsBtn.disabled = true;
    setSettingsStatus(
      stemsSettingsStatus,
      'Separació no instal·lada · pip install -e ".[stems]"',
      "error"
    );
    return;
  }
  if (bulk.running) {
    generateStemsBtn.disabled = true;
    pollStemsBulk();
  } else {
    generateStemsBtn.disabled = !data.root || !playableTracks.length;
  }
}

function markTrackInstrumental(trackId) {
  const track = tracks.find((t) => t.id === trackId);
  if (track) track.has_instrumental = true;
  const playable = playableTracks.find((t) => t.id === trackId);
  if (playable) playable.has_instrumental = true;
}

function stopStemPoll() {
  if (stemsJobTimer) {
    clearInterval(stemsJobTimer);
    stemsJobTimer = 0;
  }
}

async function swapAudioSource(mode) {
  if (!currentId) return;
  const wasPlaying = !player.paused && !player.ended;
  const at = player.currentTime;
  player.src = audioUrlFor(currentId, mode);
  const restore = () => {
    player.removeEventListener("loadedmetadata", restore);
    if (at > 0.15) {
      try {
        player.currentTime = at;
      } catch {
        /* seeking before metadata is ready is not fatal */
      }
    }
  };
  player.addEventListener("loadedmetadata", restore);
  if (wasPlaying) await player.play().catch(() => {});
  updatePlayButton();
}

function pollStemJob(jobId, trackId) {
  stopStemPoll();
  stemsJobTimer = setInterval(async () => {
    try {
      const job = await api(`/api/stems/${encodeURIComponent(jobId)}`);
      if (currentId !== trackId) {
        stopStemPoll();
        return;
      }
      if (job.status === "done") {
        stopStemPoll();
        markTrackInstrumental(trackId);
        setStemStatus("");
        if (audioMode === "instrumental") await swapAudioSource("instrumental");
        return;
      }
      if (job.status === "error") {
        stopStemPoll();
        setStemStatus(job.error || "No s’ha pogut generar la pista instrumental");
        return;
      }
      const pct = Math.round((job.progress || 0) * 100);
      const phase = job.phase === "queued" ? "a la cua" : job.phase || "";
      setStemStatus(`Generant pista instrumental… ${pct}% ${phase}`.trim());
    } catch {
      stopStemPoll();
    }
  }, 1200);
}

async function requestInstrumental(trackId) {
  setStemStatus("Preparant la pista instrumental…");
  try {
    const job = await api("/api/stems", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_id: trackId }),
    });
    if (job.status === "unavailable") {
      setStemStatus(job.error || "Separació no disponible");
      return;
    }
    if (job.ready || job.status === "done") {
      markTrackInstrumental(trackId);
      setStemStatus("");
      if (audioMode === "instrumental") await swapAudioSource("instrumental");
      return;
    }
    if (job.job_id) pollStemJob(job.job_id, trackId);
  } catch (err) {
    setStemStatus(err.message || "Error en generar la pista instrumental");
  }
}

async function setAudioMode(mode, { persist = true } = {}) {
  audioMode = mode === "instrumental" ? "instrumental" : "original";
  if (persist) localStorage.setItem(AUDIO_MODE_KEY, audioMode);
  applyAudioModeButtons();
  if (!currentId) return;
  if (audioMode === "original") {
    stopStemPoll();
    setStemStatus("");
    await swapAudioSource("original");
    return;
  }
  const track = tracks.find((t) => t.id === currentId);
  if (track?.has_instrumental) {
    setStemStatus("");
    await swapAudioSource("instrumental");
    return;
  }
  await requestInstrumental(currentId);
}

function startStemsGeneration() {
  if (!generateStemsBtn) return;
  generateStemsBtn.disabled = true;
  setSettingsStatus(stemsSettingsStatus, "Encuant la generació d’instrumentals…", "running");
  api("/api/library/stems/generate", { method: "POST" })
    .then((res) => {
      if (!res.queued) {
        setSettingsStatus(
          stemsSettingsStatus,
          "Totes les cançons ja tenen pista instrumental",
          "ok"
        );
        generateStemsBtn.disabled = false;
        return;
      }
      pollStemsBulk();
    })
    .catch((err) => {
      setSettingsStatus(stemsSettingsStatus, err.message || "Error en generar", "error");
      generateStemsBtn.disabled = false;
    });
}

function pollStemsBulk() {
  if (stemsBulkTimer) return;
  stemsBulkTimer = setInterval(async () => {
    try {
      const state = await api("/api/library/stems");
      const done = state.done || 0;
      const total = state.total || 0;
      if (!state.running) {
        clearInterval(stemsBulkTimer);
        stemsBulkTimer = 0;
        if (generateStemsBtn) generateStemsBtn.disabled = false;
        const failed = state.failed || 0;
        const reason = failed && state.error ? ` · ${state.error}` : "";
        setSettingsStatus(
          stemsSettingsStatus,
          failed
            ? `Instrumentals generats · ${done - failed}/${total} (${failed} amb error)${reason}`
            : `Instrumentals generats · ${done}/${total}`,
          failed ? "error" : "ok"
        );
        loadLibrary().catch(() => {});
        return;
      }
      const current = state.current ? ` · ${state.current}` : "";
      setSettingsStatus(
        stemsSettingsStatus,
        `Generant instrumentals… ${done}/${total}${current}`,
        "running"
      );
    } catch {
      clearInterval(stemsBulkTimer);
      stemsBulkTimer = 0;
      if (generateStemsBtn) generateStemsBtn.disabled = false;
    }
  }, 2000);
}

function youtubeBulkLabel(state) {
  const done = state.done || 0;
  const total = state.total || 0;
  const found = state.found || 0;
  const skipped = state.skipped || 0;
  const missed = state.missed || 0;
  const errors = state.errors || 0;
  const overwrite = state.scope === "all";
  const current = state.current ? ` · ${state.current}` : "";
  if (state.running) {
    const verb = overwrite ? "Tornant a cercar-ho tot" : "Cercant videoclips";
    return `${verb}… ${done}/${total}${current}`;
  }
  if (!total && skipped) {
    return `Totes les cançons ja tenen videoclip · ${skipped} omeses`;
  }
  if (!total) {
    return "No hi ha cançons per cercar";
  }
  const bits = overwrite
    ? [`${found} clips · ${done}/${total}`]
    : [`${found} clips nous · ${done}/${total}`];
  if (skipped) bits.push(`${skipped} ja en tenien`);
  if (missed) bits.push(`${missed} sense vídeo`);
  if (errors) bits.push(`${errors} amb error`);
  return bits.join(" · ");
}

function setYoutubeSearchButtonsDisabled(disabled) {
  if (searchYoutubeMissingBtn) searchYoutubeMissingBtn.disabled = disabled;
  if (searchYoutubeAllBtn) searchYoutubeAllBtn.disabled = disabled;
}

function applyYoutubeBulkAvailability(data) {
  const bulk = data.youtube || {};
  const available = bulk.available !== false;
  if (!searchYoutubeMissingBtn && !searchYoutubeAllBtn) return;
  if (!available) {
    setYoutubeSearchButtonsDisabled(true);
    setSettingsStatus(
      youtubeSettingsStatus,
      "Cerca de videoclips no disponible",
      "error"
    );
    return;
  }
  if (bulk.running) {
    setYoutubeSearchButtonsDisabled(true);
    pollYoutubeBulk();
    setSettingsStatus(youtubeSettingsStatus, youtubeBulkLabel(bulk), "running");
    return;
  }
  setYoutubeSearchButtonsDisabled(!data.root || !(data.total || playableTracks.length));
}

function startYoutubeSearch(scope) {
  if (!searchYoutubeMissingBtn && !searchYoutubeAllBtn) return;
  if (scope === "all") {
    const ok = window.confirm(
      "Això tornarà a cercar el videoclip de TOTES les cançons i substituirà els que ja tens desats. Continuar?"
    );
    if (!ok) return;
  }
  setYoutubeSearchButtonsDisabled(true);
  const enqueue =
    scope === "all"
      ? "Encuant la recerca de tots els videoclips…"
      : "Encuant la cerca de videoclips…";
  setSettingsStatus(youtubeSettingsStatus, enqueue, "running");
  api("/api/library/youtube/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scope }),
  })
    .then((res) => {
      if (!res.running && !(res.total || 0)) {
        setSettingsStatus(youtubeSettingsStatus, youtubeBulkLabel(res), "ok");
        if (lastLibraryData) {
          lastLibraryData.youtube = { ...(lastLibraryData.youtube || {}), ...res };
          applyYoutubeBulkAvailability(lastLibraryData);
        } else {
          setYoutubeSearchButtonsDisabled(false);
        }
        return;
      }
      pollYoutubeBulk();
    })
    .catch((err) => {
      setSettingsStatus(
        youtubeSettingsStatus,
        err.message || "Error en cercar videoclips",
        "error"
      );
      setYoutubeSearchButtonsDisabled(false);
    });
}

function pollYoutubeBulk() {
  if (youtubeBulkTimer) return;
  youtubeBulkTimer = setInterval(async () => {
    try {
      const state = await api("/api/library/youtube");
      if (state.running) {
        setSettingsStatus(youtubeSettingsStatus, youtubeBulkLabel(state), "running");
        if (lastLibraryData) {
          lastLibraryData.youtube = state;
          refreshLibraryMetaLabel();
        }
        return;
      }
      clearInterval(youtubeBulkTimer);
      youtubeBulkTimer = 0;
      setYoutubeSearchButtonsDisabled(false);
      const errors = state.errors || 0;
      setSettingsStatus(
        youtubeSettingsStatus,
        youtubeBulkLabel(state),
        errors ? "error" : "ok"
      );
      loadLibrary().catch(() => {});
    } catch {
      clearInterval(youtubeBulkTimer);
      youtubeBulkTimer = 0;
      setYoutubeSearchButtonsDisabled(false);
    }
  }, 1500);
}

function applyAudioMute() {
  muteOffBtn?.classList.toggle("is-active", !audioMuted);
  muteOnBtn?.classList.toggle("is-active", audioMuted);
  muteOffBtn?.setAttribute("aria-pressed", audioMuted ? "false" : "true");
  muteOnBtn?.setAttribute("aria-pressed", audioMuted ? "true" : "false");
  if (player) player.muted = false;
  previewPlayers.forEach((el) => {
    el.muted = audioMuted;
  });
  if (previewMasterGain && previewCtx) {
    const now = previewCtx.currentTime;
    previewMasterGain.gain.cancelScheduledValues(now);
    previewMasterGain.gain.setValueAtTime(audioMuted ? 0 : 1, now);
  }
}

function setAudioMuted(muted) {
  audioMuted = !!muted;
  localStorage.setItem(MUTE_KEY, audioMuted ? "1" : "0");
  applyAudioMute();
}

async function ensurePreviewGraph() {
  if (!previewGraphReady) {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    previewCtx = new Ctx();
    previewMasterGain = previewCtx.createGain();
    previewMasterGain.gain.value = audioMuted ? 0 : 1;
    previewMasterGain.connect(previewCtx.destination);
    previewPlayers.forEach((el, index) => {
      el.volume = 1; // level is controlled by Web Audio gains
      const source = previewCtx.createMediaElementSource(el);
      const gain = previewCtx.createGain();
      gain.gain.value = 0;
      source.connect(gain);
      gain.connect(previewMasterGain);
      previewGains[index] = gain;
    });
    previewGraphReady = true;
    // Probe/debug access for transition tests.
    window.__previewProbe = {
      gains: () => previewGains.map((g) => (g ? g.gain.value : 0)),
      active: () => previewActive,
      players: () =>
        previewPlayers.map((el) => ({
          paused: el.paused,
          ended: el.ended,
          t: el.currentTime,
          rs: el.readyState,
          src: (el.currentSrc || "").split("/").pop() || "",
        })),
    };
  }
  if (previewCtx.state === "suspended") {
    await previewCtx.resume();
  }
}

function setPreviewGain(index, value) {
  const gain = previewGains[index];
  if (!gain || !previewCtx) return;
  const now = previewCtx.currentTime;
  gain.gain.cancelScheduledValues(now);
  gain.gain.setValueAtTime(value, now);
}

function clearPreviewElement(el) {
  // Never call el.load() here — it can mute the shared audio device briefly.
  el.pause();
  el.removeAttribute("src");
}

function silencePreviewElement(el, index) {
  el.pause();
  if (typeof index === "number") setPreviewGain(index, 0);
}

function cancelPreviewFade() {
  if (previewFadeTimer) {
    clearTimeout(previewFadeTimer);
    previewFadeTimer = 0;
  }
  if (!previewCtx) return;
  const now = previewCtx.currentTime;
  previewGains.forEach((gain) => {
    if (!gain) return;
    gain.gain.cancelScheduledValues(now);
    gain.gain.setValueAtTime(gain.gain.value, now);
  });
}

function stopPreview() {
  previewToken += 1;
  cancelPreviewFade();
  previewPlayers.forEach((el, index) => {
    setPreviewGain(index, 0);
    clearPreviewElement(el);
  });
  previewActive = 0;
}

function settlePreviewRoles() {
  cancelPreviewFade();
  const a = previewPlayers[0];
  const b = previewPlayers[1];
  const aGain = previewGains[0] ? previewGains[0].gain.value : 0;
  const bGain = previewGains[1] ? previewGains[1].gain.value : 0;
  const aLive = !a.paused && !a.ended && aGain > 0.05;
  const bLive = !b.paused && !b.ended && bGain > 0.05;
  if (aLive && bLive) {
    previewActive = aGain >= bGain ? 0 : 1;
  } else if (bLive && !aLive) {
    previewActive = 1;
  } else if (aLive && !bLive) {
    previewActive = 0;
  }
  setPreviewGain(1 - previewActive, 0);
  silencePreviewElement(previewPlayers[1 - previewActive], 1 - previewActive);
  if (!previewPlayers[previewActive].paused && !previewPlayers[previewActive].ended) {
    setPreviewGain(previewActive, 1);
  }
}

function fadeInPreview(toIndex, token) {
  if (!previewCtx) {
    setPreviewGain(toIndex, 1);
    previewActive = toIndex;
    return;
  }
  const toGain = previewGains[toIndex];
  if (!toGain) return;
  const now = previewCtx.currentTime;
  const dur = PREVIEW_FADE_IN_MS / 1000;
  toGain.gain.cancelScheduledValues(now);
  toGain.gain.setValueAtTime(Math.max(toGain.gain.value, 0.0001), now);
  toGain.gain.exponentialRampToValueAtTime(1, now + dur);
  previewActive = toIndex;
  previewFadeTimer = setTimeout(() => {
    previewFadeTimer = 0;
    if (token !== previewToken) return;
    setPreviewGain(toIndex, 1);
    setTimeout(() => {
      if (token === previewToken) armUpcomingPreview();
    }, 400);
  }, PREVIEW_FADE_IN_MS + 40);
}

function previewUrlFor(trackId) {
  return `/api/audio/${encodeURI(trackId)}`;
}

function previewHasTrack(el, trackId) {
  if (!el?.src || !trackId) return false;
  try {
    return decodeURIComponent(new URL(el.src, location.href).pathname).endsWith(
      `/api/audio/${trackId}`
    );
  } catch {
    return el.src.includes(encodeURI(trackId));
  }
}

function preparePreviewElement(el, trackId) {
  el.pause();
  if (previewHasTrack(el, trackId) && el.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
    return false;
  }
  el.preload = "auto";
  el.src = previewUrlFor(trackId);
  return true;
}

function armUpcomingPreview() {
  const list = browseList();
  if (viewMenu.classList.contains("hidden") || list.length < 2) return;
  const upcomingItem = list[(selectedIndex + 1) % list.length];
  const upcoming =
    upcomingItem?.kind === "album" ? upcomingItem.coverTrack : upcomingItem;
  if (!upcoming?.id) return;
  const { next, nextIndex } = previewSlots();
  setPreviewGain(nextIndex, 0);
  preparePreviewElement(next, upcoming.id);
}

function cutPreviewIfNotTrack(trackId) {
  if (!previewGraphReady) return false;
  cancelPreviewFade();
  let keepIndex = -1;
  previewPlayers.forEach((el, index) => {
    if (trackId && previewHasTrack(el, trackId) && !el.paused && !el.ended) {
      keepIndex = index;
    }
  });
  previewPlayers.forEach((el, index) => {
    if (index === keepIndex) return;
    setPreviewGain(index, 0);
    el.pause();
  });
  if (keepIndex < 0) return false;
  previewActive = keepIndex;
  setPreviewGain(keepIndex, 1);
  return true;
}

async function playPreviewForSelection() {
  const track = selectedTrack();
  if (!track) {
    stopPreview();
    return;
  }
  const token = ++previewToken;
  const alreadyPlaying = cutPreviewIfNotTrack(track.id);
  await ensurePreviewGraph();
  if (token !== previewToken) return;

  if (alreadyPlaying) {
    setTimeout(() => {
      if (token === previewToken) armUpcomingPreview();
    }, 200);
    return;
  }

  settlePreviewRoles();
  const { current, next, currentIndex, nextIndex } = previewSlots();
  if (previewHasTrack(current, track.id) && !current.paused && !current.ended) {
    setPreviewGain(currentIndex, 1);
    setTimeout(() => {
      if (token === previewToken) armUpcomingPreview();
    }, 200);
    return;
  }

  setPreviewGain(currentIndex, 0);
  silencePreviewElement(current, currentIndex);
  setPreviewGain(nextIndex, 0);
  preparePreviewElement(next, track.id);

  const startIncoming = async () => {
    if (token !== previewToken) return;
    try {
      if (next.currentTime > 0.01) next.currentTime = 0;
    } catch {
      /* ignore seek before metadata */
    }
    setPreviewGain(nextIndex, 0);
    try {
      await next.play();
    } catch {
      if (token !== previewToken) silencePreviewElement(next, nextIndex);
      return;
    }
    if (token !== previewToken) {
      silencePreviewElement(next, nextIndex);
      return;
    }
    fadeInPreview(nextIndex, token);
  };

  if (next.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) {
    await startIncoming();
    return;
  }

  await new Promise((resolve) => {
    const onReady = () => {
      next.removeEventListener("canplay", onReady);
      resolve();
    };
    next.addEventListener("canplay", onReady);
    setTimeout(() => {
      next.removeEventListener("canplay", onReady);
      resolve();
    }, 1500);
  });
  if (token !== previewToken) return;
  await startIncoming();
}

function isAlbumListView() {
  return libraryBrowseMode === "album" && !openedAlbum;
}

function browseList() {
  return isAlbumListView() ? filteredAlbums : filteredTracks;
}

function selectedBrowseItem() {
  return browseList()[selectedIndex] || null;
}

function selectedTrack() {
  const item = selectedBrowseItem();
  if (!item) return null;
  if (item.kind === "album") return item.coverTrack || null;
  return item;
}

function albumKey(artist, album) {
  return `${(artist || "").toLowerCase()}::${(album || "").toLowerCase()}`;
}

function pickAlbumCoverTrack(albumTracks) {
  if (!albumTracks.length) return null;
  // Prefer the image shared by most songs; tie-break by lowest track number.
  const byHash = new Map();
  for (const track of albumTracks) {
    const hash = track.cover_hash || "";
    if (!hash) continue;
    let bucket = byHash.get(hash);
    if (!bucket) {
      bucket = [];
      byHash.set(hash, bucket);
    }
    bucket.push(track);
  }
  if (byHash.size) {
    let best = null;
    for (const group of byHash.values()) {
      if (
        !best ||
        group.length > best.length ||
        (group.length === best.length &&
          (group[0].track || 10 ** 9) < (best[0].track || 10 ** 9))
      ) {
        best = group;
      }
    }
    return (
      [...best].sort(
        (a, b) => (a.track || 10 ** 9) - (b.track || 10 ** 9) || a.title.localeCompare(b.title)
      )[0] || best[0]
    );
  }
  return (
    [...albumTracks].sort(
      (a, b) => (a.track || 10 ** 9) - (b.track || 10 ** 9) || a.title.localeCompare(b.title)
    )[0] || albumTracks[0]
  );
}

function buildAlbums(sourceTracks) {
  const map = new Map();
  for (const track of sourceTracks) {
    const artist = track.artist || "Artista desconegut";
    const album = track.album || "Sense àlbum";
    const key = albumKey(artist, album);
    let entry = map.get(key);
    if (!entry) {
      entry = {
        kind: "album",
        key,
        artist,
        album,
        year: track.year || 0,
        tracks: [],
        coverTrack: track,
      };
      map.set(key, entry);
    }
    entry.tracks.push(track);
    entry.year = Math.max(entry.year || 0, track.year || 0);
  }
  for (const entry of map.values()) {
    entry.coverTrack = pickAlbumCoverTrack(entry.tracks);
  }
  return [...map.values()].sort((a, b) => {
    const artistCmp = a.artist.localeCompare(b.artist, "ca", { sensitivity: "base" });
    if (artistCmp) return artistCmp;
    if ((b.year || 0) !== (a.year || 0)) return (b.year || 0) - (a.year || 0);
    return a.album.localeCompare(b.album, "ca", { sensitivity: "base" });
  });
}

function applyLibraryBrowseMode() {
  const albumMode = libraryBrowseMode === "album";
  libraryBrowseSongBtn?.classList.toggle("is-active", !albumMode);
  libraryBrowseAlbumBtn?.classList.toggle("is-active", albumMode);
  libraryBrowseSongBtn?.setAttribute("aria-pressed", albumMode ? "false" : "true");
  libraryBrowseAlbumBtn?.setAttribute("aria-pressed", albumMode ? "true" : "false");
  browsePanel.dataset.libraryBrowse = libraryBrowseMode;
  browsePanel.dataset.albumOpen = openedAlbum ? "1" : "0";
  if (albumBackBtn) albumBackBtn.hidden = !(libraryBrowseMode === "album" && openedAlbum);
  if (searchEl) {
    searchEl.placeholder = isAlbumListView()
      ? "Cerca àlbums, artistes…"
      : openedAlbum
        ? `Cerca a “${openedAlbum.album}”…`
        : "Cerca cançons, artistes…";
  }
}

function setLibraryBrowseMode(mode) {
  libraryBrowseMode = mode === "album" ? "album" : "song";
  localStorage.setItem(LIBRARY_BROWSE_KEY, libraryBrowseMode);
  openedAlbum = null;
  selectedIndex = 0;
  applyLibraryBrowseMode();
  renderSongs(searchEl.value, { play: false });
}

function compareTracks(a, b) {
  const artistCmp = (a.artist || "").localeCompare(b.artist || "", "ca", {
    sensitivity: "base",
  });
  if (artistCmp) return artistCmp;
  if ((b.year || 0) !== (a.year || 0)) return (b.year || 0) - (a.year || 0);
  const albumCmp = (a.album || "").localeCompare(b.album || "", "ca", {
    sensitivity: "base",
  });
  if (albumCmp) return albumCmp;
  if ((a.disc || 0) !== (b.disc || 0)) return (a.disc || 0) - (b.disc || 0);
  const at = a.track > 0 ? a.track : 10 ** 9;
  const bt = b.track > 0 ? b.track : 10 ** 9;
  if (at !== bt) return at - bt;
  return (a.title || "").localeCompare(b.title || "", "ca", { sensitivity: "base" });
}

function tracksForLyricsFilter() {
  if (lyricsFilterMode === "hidden") return hiddenTracks;
  if (lyricsFilterMode === "all") {
    return [...playableTracks, ...hiddenTracks, ...pendingTracks].sort(compareTracks);
  }
  // "Amb lletra": known lyrics + not-yet-checked (pending). Known misses stay in "Sense lletra".
  return [...playableTracks, ...pendingTracks].sort(compareTracks);
}

function applyLyricsFilterMode() {
  const mode = lyricsFilterMode;
  lyricsFilterLyricsBtn?.classList.toggle("is-active", mode === "lyrics");
  lyricsFilterHiddenBtn?.classList.toggle("is-active", mode === "hidden");
  lyricsFilterAllBtn?.classList.toggle("is-active", mode === "all");
  lyricsFilterLyricsBtn?.setAttribute("aria-pressed", mode === "lyrics" ? "true" : "false");
  lyricsFilterHiddenBtn?.setAttribute("aria-pressed", mode === "hidden" ? "true" : "false");
  lyricsFilterAllBtn?.setAttribute("aria-pressed", mode === "all" ? "true" : "false");
  browsePanel.dataset.lyricsFilter = mode;
  tracks = tracksForLyricsFilter();
}

function setLyricsFilterMode(mode) {
  lyricsFilterMode =
    mode === "hidden" || mode === "all" || mode === "lyrics" ? mode : "lyrics";
  localStorage.setItem(LYRICS_FILTER_KEY, lyricsFilterMode);
  openedAlbum = null;
  selectedIndex = 0;
  applyLyricsFilterMode();
  applyLibraryBrowseMode();
  renderSongs(searchEl.value, { play: false });
  refreshLibraryMetaLabel();
}

function openAlbum(album) {
  if (!album || album.kind !== "album") return;
  openedAlbum = album;
  selectedIndex = 0;
  if (searchEl) searchEl.value = "";
  applyLibraryBrowseMode();
  renderSongs("", { play: true });
}

function closeAlbum() {
  if (!openedAlbum) return;
  const previousKey = openedAlbum.key;
  openedAlbum = null;
  selectedIndex = 0;
  applyLibraryBrowseMode();
  renderSongs(searchEl.value, { play: true });
  const idx = filteredAlbums.findIndex((a) => a.key === previousKey);
  if (idx >= 0) setSelectedIndex(idx, { play: true, tick: false });
}

function updateCoverMeta() {
  const item = selectedBrowseItem();
  if (!item) {
    coverArtist.textContent = "";
    coverTitle.textContent = "";
    coverIndex.textContent = "";
    resyncCoverBtn.hidden = true;
    updatePrimaryAction();
    return;
  }
  const list = browseList();
  if (item.kind === "album") {
    coverArtist.textContent = item.artist || "Artista desconegut";
    coverTitle.textContent = item.album || "Sense àlbum";
    const year = item.year ? ` · ${item.year}` : "";
    coverIndex.textContent = `${selectedIndex + 1}/${list.length} · ${item.tracks.length} cançons${year}`;
    resyncCoverBtn.hidden = true;
  } else {
    coverArtist.textContent = openedAlbum
      ? openedAlbum.album || item.album || "Àlbum"
      : item.artist || "Artista desconegut";
    coverTitle.textContent = item.title || item.relpath;
    coverIndex.textContent = openedAlbum
      ? `${selectedIndex + 1}/${list.length} · ${item.artist || ""}`
      : `${selectedIndex + 1}/${list.length}`;
    resyncCoverBtn.hidden = true;
  }
  updatePrimaryAction();
}

function applyBrowseMode() {
  browsePanel.dataset.mode = browseMode;
  coverflow.hidden = browseMode !== "cover";
  songGrid.hidden = browseMode !== "grid";
  modeCoverBtn.classList.toggle("is-active", browseMode === "cover");
  modeGridBtn.classList.toggle("is-active", browseMode === "grid");
  coverPrev.hidden = browseMode !== "cover";
  coverNext.hidden = browseMode !== "cover";
  applyAlignStatusMode();
}

function setBrowseMode(mode, { rerender = true } = {}) {
  browseMode = mode === "grid" ? "grid" : "cover";
  localStorage.setItem(VIEW_MODE_KEY, browseMode);
  applyBrowseMode();
  if (rerender) renderSongs(searchEl.value, { play: false });
}

function coverImageFor(track) {
  const img = document.createElement("img");
  img.src = coverUrlFor(track.id);
  img.alt = "";
  img.draggable = false;
  img.loading = "lazy";
  img.onerror = () => {
    img.onerror = null;
    img.src = GENERIC_COVER;
  };
  return img;
}

function refreshCoverImages() {
  coverBust = Date.now();
  renderSongs(searchEl.value, { play: false });
  if (currentId) setStageCover(currentId);
}

function alignBadgeFor(track) {
  const badge = document.createElement("span");
  badge.dataset.trackId = track.id;
  paintAlignBadge(badge, track);
  return badge;
}

function coverMediaFor(track) {
  const media = document.createElement("span");
  media.className = "cover-media";
  media.append(coverImageFor(track), alignBadgeFor(track));
  return media;
}

function syncStateFor(track) {
  if (!track) return "unsynced";
  if (track.whisper_aligned) return "synced";
  if (syncActiveId === track.id) return "running";
  if (syncQueuedIds.has(track.id)) return "queued";
  return "unsynced";
}

function paintAlignBadge(badge, track) {
  const state = syncStateFor(track);
  badge.className = `align-badge is-${state}`;
  if (state === "synced") {
    badge.title = "Lletra alineada amb Whisper";
    badge.innerHTML = ICON_SYNCED;
  } else if (state === "running") {
    badge.title = "Sincronitzant ara…";
    badge.innerHTML = ICON_RUNNING;
  } else if (state === "queued") {
    badge.title = "A la cua de sincronització";
    badge.innerHTML = ICON_QUEUE;
  } else {
    badge.title = "Sense alineació Whisper";
    badge.innerHTML = ICON_CLOCK;
  }
  badge.setAttribute("aria-label", badge.title);
}

function refreshAlignBadges() {
  document.querySelectorAll(".align-badge[data-track-id]").forEach((badge) => {
    const track = tracks.find((t) => t.id === badge.dataset.trackId);
    if (track) paintAlignBadge(badge, track);
  });
}

function findBrowseIndexByTrackId(trackId) {
  if (!trackId) return -1;
  return browseList().findIndex((item) => {
    if (item?.kind === "album") {
      return item.coverTrack?.id === trackId || item.tracks?.some((t) => t.id === trackId);
    }
    return item?.id === trackId;
  });
}

function markTrackAligned(trackId) {
  const track = tracks.find((t) => t.id === trackId);
  if (track) track.whisper_aligned = true;
  if (alignMode === "synced") {
    const previousId = selectedTrack()?.id;
    renderSongs(searchEl.value, { play: false });
    if (previousId) {
      const idx = findBrowseIndexByTrackId(previousId);
      if (idx >= 0) {
        selectedIndex = idx;
        layoutCovers();
        layoutGridSelection();
        updateCoverMeta();
      }
    }
    return;
  }
  refreshAlignBadges();
  updatePrimaryAction();
}

function trackLabel(track) {
  if (!track) return "";
  return `${track.artist || "Artista"} — ${track.title || track.relpath}`;
}

function syncPhaseLabel(phase, stemPhase) {
  if (phase === "model") return "carregant model Whisper";
  if (phase === "stems") {
    if (stemPhase === "codificant") return "codificant pistes";
    if (stemPhase === "model") return "carregant model de separació";
    if (stemPhase === "fet") return "pistes aïllades";
    return "aïllant veu";
  }
  if (phase === "lyrics") return "carregant lletra";
  if (phase === "queued") return "a la cua";
  if (phase === "whisper" || phase === "running") return "alineant";
  return "";
}

function syncProgressText(track) {
  const title = trackLabel(track) || "cançó";
  const phase = syncPhaseLabel(syncPhase, syncStemPhase);
  const pct =
    typeof syncProgress === "number" && syncProgress > 0
      ? `${Math.round(syncProgress * 100)}%`
      : "";
  const detail = [phase, pct].filter(Boolean).join(" · ");
  const rest = syncQueue.length;
  const batch =
    syncTotalQueued > 1
      ? `${Math.min(syncCompleted + 1, syncTotalQueued)}/${syncTotalQueued}`
      : "";
  let text = batch ? `Whisper ${batch} · ${title}` : `Whisper · ${title}`;
  if (detail) text += ` · ${detail}`;
  if (rest) text += ` · ${rest} més a la cua`;
  return text;
}

function updateSyncQueueMeta() {
  const pending = syncQueue.length + (syncActiveId ? 1 : 0);
  if (!pending && !syncLastError) {
    if (syncQueueMeta) {
      syncQueueMeta.hidden = true;
      syncQueueMeta.textContent = "";
    }
    return;
  }
  if (syncActiveId) {
    const active =
      tracks.find((t) => t.id === syncActiveId) ||
      playableTracks.find((t) => t.id === syncActiveId);
    const text = syncProgressText(active);
    if (syncQueueMeta) {
      syncQueueMeta.hidden = false;
      syncQueueMeta.textContent = text.replace(/^Whisper/, "Sincronitzant");
    }
    setSettingsStatus(lyricsSyncSettingsStatus, text, "running");
    return;
  }
  if (syncLastError && syncQueueMeta) {
    syncQueueMeta.hidden = false;
    syncQueueMeta.textContent = syncLastError;
  }
}

function isSyncActionMode() {
  return alignMode === "status";
}

function showAlignBadges() {
  return alignMode === "status";
}

function updatePrimaryAction() {
  updatePasteLyricsButton();
  const item = selectedBrowseItem();
  const track = selectedTrack();
  const syncActions = isSyncActionMode();
  singBtn.classList.toggle("is-sync-mode", syncActions && !isAlbumListView());
  if (isAlbumListView()) {
    singBtn.disabled = !item;
    singBtn.textContent = "Obrir àlbum";
    updateSyncQueueMeta();
    return;
  }
  if (!track) {
    singBtn.disabled = true;
    singBtn.textContent = syncActions ? "Sincronitzar" : "Cantar";
    updateSyncQueueMeta();
    return;
  }
  // Known miss (LRCLIB none / probe-error): not singable. Pending = not checked yet —
  // opening fetches basic lyrics on demand; Whisper sync does the full chain.
  if (track.has_lyrics === false && !track.lyrics_pending) {
    singBtn.disabled = true;
    singBtn.textContent = "Sense lletra";
    updateSyncQueueMeta();
    return;
  }
  if (!syncActions) {
    singBtn.disabled = false;
    singBtn.textContent = "Cantar";
    updateSyncQueueMeta();
    return;
  }
  const state = syncStateFor(track);
  if (state === "synced") {
    singBtn.disabled = true;
    singBtn.textContent = "Ja sincronitzada";
  } else if (state === "running") {
    singBtn.disabled = true;
    singBtn.textContent = "Sincronitzant…";
  } else if (state === "queued") {
    singBtn.disabled = true;
    singBtn.textContent = "A la cua";
  } else {
    singBtn.disabled = false;
    singBtn.textContent = "Sincronitzar";
  }
  updateSyncQueueMeta();
}

function updatePasteLyricsButton() {
  const track = isAlbumListView() ? null : selectedTrack();
  const showBrowse = Boolean(track);
  if (pasteLyricsBtn) {
    pasteLyricsBtn.hidden = !showBrowse;
    pasteLyricsBtn.disabled = !showBrowse;
    pasteLyricsBtn.classList.toggle(
      "is-needed",
      Boolean(showBrowse && track.has_lyrics === false && !track.lyrics_pending)
    );
  }
  const onStage = Boolean(currentId && viewStage && !viewStage.classList.contains("hidden"));
  const missingOnStage = onStage && !lyricLines.length;
  if (stagePasteLyricsBtn) {
    stagePasteLyricsBtn.hidden = !missingOnStage;
  }
}

function applyAlignStatusMode() {
  browsePanel.dataset.showAlign = showAlignBadges() ? "1" : "0";
  browsePanel.dataset.alignMode = alignMode;
  syncStatusBtn.classList.toggle("is-active", alignMode === "status");
  syncStatusBtn.classList.toggle("is-filter", alignMode === "synced");
  syncStatusBtn.setAttribute("aria-pressed", alignMode === "off" ? "false" : "true");
  const titles = {
    off: "Mostrar estat de sincronització",
    status: "Només cançons sincronitzades",
    synced: "Amagar filtre de sincronització",
  };
  const labels = {
    off: "Estat de sincronització desactivat",
    status: "Mostrant estat de sincronització",
    synced: "Només cançons amb lletra sincronitzada",
  };
  syncStatusBtn.title = titles[alignMode];
  syncStatusBtn.setAttribute("aria-label", labels[alignMode]);
  updatePrimaryAction();
}

function cycleAlignMode() {
  alignMode = alignMode === "off" ? "status" : alignMode === "status" ? "synced" : "off";
  localStorage.setItem(ALIGN_MODE_KEY, alignMode);
  applyAlignStatusMode();
  selectedIndex = 0;
  renderSongs(searchEl.value, { play: false });
}

function activateSelectedTrack() {
  const item = selectedBrowseItem();
  if (!item) return;
  if (item.kind === "album") {
    openAlbum(item);
    return;
  }
  if (item.has_lyrics === false && !item.lyrics_pending) return;
  if (isSyncActionMode()) {
    enqueueSync(item);
    return;
  }
  openSong(item.id);
}

function enqueueSync(track) {
  if (!track || track.whisper_aligned) {
    updatePrimaryAction();
    return;
  }
  if (syncActiveId === track.id || syncQueuedIds.has(track.id)) {
    updatePrimaryAction();
    return;
  }
  syncLastError = "";
  syncQueue.push(track.id);
  syncQueuedIds.add(track.id);
  refreshAlignBadges();
  updatePrimaryAction();
  processSyncQueue();
}

async function waitAlignJob(jobId) {
  const started = Date.now();
  const maxMs = 30 * 60 * 1000;
  for (;;) {
    if (Date.now() - started > maxMs) {
      throw new Error("La sincronització ha trigat massa i s’ha cancel·lat l’espera");
    }
    await new Promise((resolve) => setTimeout(resolve, 1200));
    const job = await api(`/api/align/${encodeURIComponent(jobId)}`);
    let changed = false;
    if (typeof job.progress === "number" && job.progress !== syncProgress) {
      syncProgress = job.progress;
      changed = true;
    }
    if (job.phase && job.phase !== syncPhase) {
      syncPhase = job.phase;
      changed = true;
    } else if (job.status === "queued" && syncPhase !== "queued") {
      syncPhase = "queued";
      changed = true;
    }
    const nextStem = job.stem_phase || "";
    if (nextStem !== syncStemPhase) {
      syncStemPhase = nextStem;
      changed = true;
    }
    if (changed) updateSyncQueueMeta();
    if (job.status === "done") return job;
    if (job.status === "error") {
      throw new Error(job.error || "Alineació fallida");
    }
    // queued | running — keep waiting
  }
}

async function runQueuedAlign(trackId) {
  const job = await api("/api/align", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ track_id: trackId, language: "ca" }),
  });
  if (job.status === "done") return job;
  if (job.status === "unavailable") {
    throw new Error(job.error || "Alineació no disponible");
  }
  if ((job.status === "running" || job.status === "queued") && job.job_id) {
    return waitAlignJob(job.job_id);
  }
  throw new Error(job.error || "L’alineació no s’ha iniciat");
}

function whisperSyncCandidates() {
  // Whisper job always fetches basic lyrics first, then stems, then align —
  // so pending tracks (not yet probed) are valid candidates.
  const seen = new Set();
  const out = [];
  for (const track of [...playableTracks, ...pendingTracks]) {
    if (!track?.id || seen.has(track.id)) continue;
    seen.add(track.id);
    if (track.whisper_aligned) continue;
    out.push(track);
  }
  return out;
}

async function processSyncQueue() {
  if (syncRunning) return;
  syncRunning = true;
  if (syncLyricsWhisperBtn) syncLyricsWhisperBtn.disabled = true;
  if (!syncTotalQueued) {
    syncTotalQueued = syncQueue.length;
    syncCompleted = 0;
  }
  while (syncQueue.length) {
    const trackId = syncQueue.shift();
    syncQueuedIds.delete(trackId);
    const track =
      allLibraryTracks().find((t) => t.id === trackId) || tracks.find((t) => t.id === trackId);
    if (!track || track.whisper_aligned) {
      syncCompleted += 1;
      refreshAlignBadges();
      updatePrimaryAction();
      continue;
    }
    syncActiveId = trackId;
    syncLastError = "";
    syncProgress = 0;
    syncPhase = "queued";
    syncStemPhase = "";
    refreshAlignBadges();
    updatePrimaryAction();
    updateSyncQueueMeta();
    try {
      const job = await runQueuedAlign(trackId);
      markTrackAligned(trackId);
      if (currentId === trackId && job?.lines) {
        applyAlignedLyrics(job);
      }
      syncCompleted += 1;
    } catch (err) {
      syncLastError = err.message || "Error de sincronització";
      syncCompleted += 1;
    } finally {
      syncActiveId = null;
      syncProgress = 0;
      syncPhase = "";
      syncStemPhase = "";
      refreshAlignBadges();
      updatePrimaryAction();
    }
  }
  syncRunning = false;
  syncTotalQueued = 0;
  syncCompleted = 0;
  if (syncLyricsWhisperBtn) {
    syncLyricsWhisperBtn.disabled = !whisperSyncCandidates().length;
  }
  updatePrimaryAction();
  if (syncLastError) {
    setSettingsStatus(lyricsSyncSettingsStatus, syncLastError, "error");
  } else {
    setSettingsStatus(lyricsSyncSettingsStatus, "Sincronització Whisper enllestida", "ok");
  }
  loadLibrary().catch(() => {});
}

function layoutCovers() {
  if (browseMode !== "cover") return;
  const items = [...coverTrack.querySelectorAll(".cover-item")];
  items.forEach((el) => {
    const index = Number(el.dataset.index);
    const offset = index - selectedIndex;
    const abs = Math.abs(offset);
    el.classList.toggle("is-center", offset === 0);
    el.style.zIndex = String(100 - abs);
    if (abs > COVER_VISIBLE) {
      el.style.opacity = "0";
      el.style.pointerEvents = "none";
      el.style.transform = `translate(-50%, -50%) translateX(${offset * 64}%) scale(0.55)`;
      return;
    }
    const x = offset * 64;
    const scale = offset === 0 ? 1.08 : Math.max(0.58, 1 - abs * 0.15);
    const rot = offset * -26;
    const opacity = offset === 0 ? 1 : Math.max(0.28, 1 - abs * 0.18);
    el.style.opacity = String(opacity);
    el.style.pointerEvents = "auto";
    el.style.filter = offset === 0 ? "none" : "brightness(0.72)";
    el.style.transform = `translate(-50%, -50%) translateX(${x}%) rotateY(${rot}deg) scale(${scale})`;
  });
}

function layoutGridSelection() {
  if (browseMode !== "grid") return;
  songGrid.querySelectorAll(".grid-card").forEach((el) => {
    const index = Number(el.dataset.index);
    el.classList.toggle("is-selected", index === selectedIndex);
  });
  const selected = songGrid.querySelector(".grid-card.is-selected");
  if (selected) {
    selected.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
  }
}

function gridColumnCount() {
  const cards = songGrid.querySelectorAll(".grid-card");
  if (cards.length < 2) return 1;
  const firstTop = cards[0].offsetTop;
  let cols = 1;
  for (let i = 1; i < cards.length; i += 1) {
    if (cards[i].offsetTop !== firstTop) break;
    cols += 1;
  }
  return Math.max(1, cols);
}

function coverStepDirection(from, to, length) {
  if (from === to || length < 2) return 0;
  const forward = (to - from + length) % length;
  const backward = (from - to + length) % length;
  return forward <= backward ? 1 : -1;
}

function playCoverStepSoundNow(direction) {
  if (!uiSfxCtx || !direction) return;
  const nowMs = performance.now();
  if (nowMs - lastCoverTickAt < 40) return;
  lastCoverTickAt = nowMs;
  const ctx = uiSfxCtx;
  const t0 = ctx.currentTime;
  const pan = typeof ctx.createStereoPanner === "function" ? ctx.createStereoPanner() : null;
  if (pan) {
    pan.pan.setValueAtTime(direction > 0 ? 0.22 : -0.22, t0);
    pan.connect(ctx.destination);
  }
  const out = pan || ctx.destination;

  const body = ctx.createOscillator();
  const bodyGain = ctx.createGain();
  body.type = "triangle";
  body.frequency.setValueAtTime(290, t0);
  body.frequency.exponentialRampToValueAtTime(130, t0 + 0.1);
  bodyGain.gain.setValueAtTime(0.0001, t0);
  bodyGain.gain.exponentialRampToValueAtTime(0.74, t0 + 0.004);
  bodyGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.13);
  body.connect(bodyGain);
  bodyGain.connect(out);
  body.start(t0);
  body.stop(t0 + 0.14);

  const thump = ctx.createOscillator();
  const thumpGain = ctx.createGain();
  thump.type = "sine";
  thump.frequency.setValueAtTime(180, t0);
  thump.frequency.exponentialRampToValueAtTime(92, t0 + 0.11);
  thumpGain.gain.setValueAtTime(0.0001, t0);
  thumpGain.gain.exponentialRampToValueAtTime(0.54, t0 + 0.005);
  thumpGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.14);
  thump.connect(thumpGain);
  thumpGain.connect(out);
  thump.start(t0);
  thump.stop(t0 + 0.15);

  const click = ctx.createOscillator();
  const clickGain = ctx.createGain();
  click.type = "triangle";
  click.frequency.setValueAtTime(840, t0);
  click.frequency.exponentialRampToValueAtTime(360, t0 + 0.07);
  clickGain.gain.setValueAtTime(0.0001, t0);
  clickGain.gain.exponentialRampToValueAtTime(0.4, t0 + 0.003);
  clickGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.09);
  click.connect(clickGain);
  clickGain.connect(out);
  click.start(t0);
  click.stop(t0 + 0.1);

  const n = Math.max(1, Math.floor(ctx.sampleRate * 0.04));
  const buf = ctx.createBuffer(1, n, ctx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < n; i += 1) {
    const env = 1 - i / n;
    data[i] = (Math.random() * 2 - 1) * env;
  }
  const noise = ctx.createBufferSource();
  noise.buffer = buf;
  const band = ctx.createBiquadFilter();
  band.type = "bandpass";
  band.frequency.value = 620;
  band.Q.value = 0.9;
  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(0.0001, t0);
  noiseGain.gain.exponentialRampToValueAtTime(0.26, t0 + 0.002);
  noiseGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.06);
  noise.connect(band);
  band.connect(noiseGain);
  noiseGain.connect(out);
  noise.start(t0);
}

function playCoverStepSound(direction) {
  if (!direction) return;
  const Ctx = window.AudioContext || window.webkitAudioContext;
  if (!Ctx) return;
  if (!uiSfxCtx) uiSfxCtx = new Ctx();
  if (uiSfxCtx.state === "suspended") {
    uiSfxCtx.resume().then(() => playCoverStepSoundNow(direction)).catch(() => {});
    return;
  }
  playCoverStepSoundNow(direction);
}

function setSelectedIndex(index, { play = true, tick = true } = {}) {
  const list = browseList();
  if (!list.length) {
    selectedIndex = 0;
    updateCoverMeta();
    stopPreview();
    return;
  }
  const from = selectedIndex;
  const next = ((index % list.length) + list.length) % list.length;
  selectedIndex = next;
  layoutCovers();
  layoutGridSelection();
  updateCoverMeta();
  if (
    tick &&
    browseMode === "cover" &&
    from !== next &&
    !viewMenu.classList.contains("hidden")
  ) {
    playCoverStepSound(coverStepDirection(from, next, list.length));
  }
  if (play && !viewMenu.classList.contains("hidden")) {
    playPreviewForSelection();
  }
}

function coverMediaForItem(item) {
  if (item?.kind === "album") {
    const media = document.createElement("span");
    media.className = "cover-media";
    if (item.coverTrack) media.appendChild(coverImageFor(item.coverTrack));
    else {
      const img = document.createElement("img");
      img.src = GENERIC_COVER;
      img.alt = "";
      img.draggable = false;
      media.appendChild(img);
    }
    return media;
  }
  return coverMediaFor(item);
}

function itemAriaLabel(item) {
  if (item?.kind === "album") {
    return `${item.artist || "Artista"} — ${item.album || "Àlbum"}`;
  }
  return `${item?.artist || "Artista"} — ${item?.title || item?.relpath || ""}`;
}

function renderCoverflowItems() {
  coverTrack.innerHTML = "";
  browseList().forEach((item, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "cover-item";
    btn.dataset.index = String(index);
    btn.setAttribute("aria-label", itemAriaLabel(item));
    btn.appendChild(coverMediaForItem(item));
    btn.addEventListener("click", () => {
      if (index === selectedIndex) {
        activateSelectedTrack();
        return;
      }
      setSelectedIndex(index);
    });
    coverTrack.appendChild(btn);
  });
}

function renderGridItems() {
  songGrid.innerHTML = "";
  browseList().forEach((item, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "grid-card";
    btn.dataset.index = String(index);
    btn.setAttribute("aria-label", itemAriaLabel(item));
    btn.appendChild(coverMediaForItem(item));
    const artist = document.createElement("p");
    artist.className = "grid-artist";
    artist.textContent =
      item.kind === "album"
        ? item.artist || "Artista desconegut"
        : item.artist || "Artista desconegut";
    const title = document.createElement("p");
    title.className = "grid-title";
    title.textContent =
      item.kind === "album"
        ? item.album || "Sense àlbum"
        : item.title || item.relpath;
    btn.append(artist, title);
    btn.addEventListener("click", () => {
      if (index === selectedIndex) {
        activateSelectedTrack();
        return;
      }
      setSelectedIndex(index);
    });
    songGrid.appendChild(btn);
  });
}

function renderSongs(filter = "", options = { play: true }) {
  const needle = filter.trim().toLowerCase();
  const baseTracks = tracks.filter((t) => {
    if (alignMode === "synced" && !t.whisper_aligned) return false;
    return true;
  });

  if (libraryBrowseMode === "album" && openedAlbum) {
    const albumTracks = openedAlbum.tracks.filter((t) => baseTracks.some((b) => b.id === t.id));
    filteredTracks = albumTracks.filter((t) => {
      if (!needle) return true;
      return `${t.title} ${t.artist} ${t.album}`.toLowerCase().includes(needle);
    });
    filteredAlbums = [];
  } else if (isAlbumListView()) {
    filteredAlbums = buildAlbums(baseTracks).filter((album) => {
      if (!needle) return true;
      const hay = `${album.artist} ${album.album} ${album.tracks.map((t) => t.title).join(" ")}`;
      return hay.toLowerCase().includes(needle);
    });
    filteredTracks = [];
  } else {
    filteredTracks = baseTracks.filter((t) => {
      if (!needle) return true;
      return `${t.title} ${t.artist} ${t.album}`.toLowerCase().includes(needle);
    });
    filteredAlbums = [];
  }

  applyBrowseMode();
  applyLibraryBrowseMode();
  coverTrack.innerHTML = "";
  songGrid.innerHTML = "";

  const list = browseList();
  if (!list.length) {
    stopPreview();
    coverArtist.textContent = "";
    coverTitle.textContent = tracks.length
      ? alignMode === "synced"
        ? "Cap cançó sincronitzada"
        : "Cap resultat"
      : lyricsFilterMode === "hidden"
        ? "Cap cançó oculta"
        : "Sense cançons";
    coverIndex.textContent = "";
    resyncCoverBtn.hidden = true;
    updatePrimaryAction();
    const empty = document.createElement("p");
    empty.className = "cover-empty";
    empty.textContent = tracks.length
      ? alignMode === "synced"
        ? "Encara no hi ha cançons amb lletra alineada amb Whisper."
        : isAlbumListView()
          ? "Cap àlbum amb aquesta cerca."
          : "Cap resultat amb aquesta cerca."
      : lyricsFilterMode === "hidden"
        ? "No hi ha cançons amagades sense lletra."
        : "Carrega una carpeta de música per començar.";
    (browseMode === "grid" ? songGrid : coverTrack).appendChild(empty);
    return;
  }

  if (browseMode === "grid") {
    renderGridItems();
  } else {
    renderCoverflowItems();
  }

  if (selectedIndex >= list.length) selectedIndex = 0;
  setSelectedIndex(selectedIndex, {
    play: options.play !== false && !viewMenu.classList.contains("hidden"),
    tick: false,
  });
}

function applyAlignedLyrics(payload) {
  renderLyrics(payload);
  lyricsStatus.textContent = `Alineat per paraules · ${payload.source || "whisper-align"}`;
  if (currentId) markTrackAligned(currentId);
  syncKaraoke();
}

async function pollAlignJob(jobId, trackId, token) {
  try {
    const job = await api(`/api/align/${encodeURIComponent(jobId)}`);
    if (token !== alignToken || currentId !== trackId) return;
    if (job.status === "done" && job.lines) {
      stopAlignPoll();
      applyAlignedLyrics(job);
      return;
    }
    if (job.status === "error") {
      stopAlignPoll();
      lyricsStatus.textContent = `Alineació fallida · ${job.error || "error desconegut"}`;
      return;
    }
    if (job.status === "queued") {
      lyricsStatus.textContent = "Alineació a la cua del servidor…";
    } else if (job.phase === "model") {
      lyricsStatus.textContent = "Carregant el model Whisper…";
    } else if (job.phase === "stems") {
      const pct =
        typeof job.progress === "number" && job.progress > 0
          ? ` ${Math.round(job.progress * 100)}%`
          : "";
      const detail =
        job.stem_phase === "codificant"
          ? "Codificant les pistes…"
          : "Aïllant la veu abans d’alinear…";
      lyricsStatus.textContent = `${detail}${pct}`;
    } else if (typeof job.progress === "number" && job.progress > 0) {
      const pct = Math.round(job.progress * 100);
      lyricsStatus.textContent = `Alineant la lletra amb l’àudio… ${pct}%`;
    } else if (job.phase === "lyrics") {
      lyricsStatus.textContent = "Carregant la lletra…";
    }
  } catch (err) {
    if (token !== alignToken || currentId !== trackId) return;
    stopAlignPoll();
    lyricsStatus.textContent = err.message || "Error en comprovar l’alineació";
  }
}

async function startAlignment(trackId) {
  stopAlignPoll();
  const token = alignToken;
  lyricsStatus.textContent = "Alineant la lletra amb l’àudio… (la primera vegada pot trigar un minut)";
  try {
    const job = await api("/api/align", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_id: trackId, language: "ca" }),
    });
    if (token !== alignToken || currentId !== trackId) return;
    if (job.status === "done" && job.lines) {
      applyAlignedLyrics(job);
      return;
    }
    if (job.status === "unavailable") {
      lyricsStatus.textContent = job.error || "Alineació no disponible";
      return;
    }
    if ((job.status === "running" || job.status === "queued") && job.job_id) {
      alignPollTimer = setInterval(() => {
        pollAlignJob(job.job_id, trackId, token);
      }, 1200);
      return;
    }
    lyricsStatus.textContent = job.error || "L’alineació no s’ha iniciat";
  } catch (err) {
    if (token !== alignToken || currentId !== trackId) return;
    lyricsStatus.textContent = err.message || "Error d’alineació";
  }
}

function showStage() {
  clearStageOutro();
  stopPreview();
  if (player) player.muted = false;
  viewLanding?.classList.add("hidden");
  viewTitle?.classList.add("hidden");
  viewMenu.classList.add("hidden");
  viewStage.classList.remove("hidden");
  document.body.classList.remove("mode-title");
  document.body.classList.add("mode-stage");
  syncAuraEngine();
}

function buildWordNode(word) {
  const wrap = document.createElement("span");
  wrap.className = word.glue ? "k-word is-glue" : "k-word";

  const base = document.createElement("span");
  base.className = "k-word-base";
  base.textContent = word.text;

  const fill = document.createElement("span");
  fill.className = "k-word-fill";
  fill.textContent = word.text;

  wrap.append(base, fill);
  return wrap;
}

function lineWords(line) {
  if (!line) return [];
  if (line.words && line.words.length) return line.words;
  return [{ time: line.time, end: line.time + 1.5, text: line.text }];
}

function clearLineRoll() {
  if (lineSwapTimer) {
    clearTimeout(lineSwapTimer);
    lineSwapTimer = null;
  }
  if (dualRefreshTimer) {
    clearTimeout(dualRefreshTimer);
    dualRefreshTimer = null;
  }
  dualPending = null;
  kStackEl.classList.remove("is-rolling");
  kStackEl.querySelectorAll(".k-slot-ghost").forEach((node) => node.remove());
  lineCurrentEl.classList.remove("is-rising", "is-refreshing");
  lineNextEl.classList.remove("is-entering", "is-refreshing");
}

function fillSlot(slotEl, line, { trackWords = false, resetWords = true } = {}) {
  slotEl.innerHTML = "";
  slotEl.classList.remove("is-empty", "is-rising", "is-entering", "is-refreshing");
  if (!line) {
    slotEl.classList.add("is-empty");
    return;
  }
  if (trackWords && resetWords) wordNodes = [];
  let groupEl = null;
  for (const word of lineWords(line)) {
    const node = buildWordNode(word);
    if (!groupEl) {
      groupEl = document.createElement("span");
      groupEl.className = "k-word-group";
      slotEl.appendChild(groupEl);
    }
    groupEl.appendChild(node);
    if (!word.glue) groupEl = null;
    if (trackWords) {
      wordNodes.push({
        start: Number(word.time),
        end: Number(word.end),
        el: node,
        fill: node.querySelector(".k-word-fill"),
      });
    }
  }
}

function bindSlotWords(slotEl, line) {
  wordNodes = [];
  if (!line || !slotEl) return;
  const nodes = [...slotEl.querySelectorAll(".k-word")];
  lineWords(line).forEach((word, index) => {
    const el = nodes[index];
    if (!el) return;
    wordNodes.push({
      start: Number(word.time),
      end: Number(word.end),
      el,
      fill: el.querySelector(".k-word-fill"),
    });
  });
}

function setSlotRole(slotEl, role) {
  slotEl.classList.toggle("is-active", role === "active");
  slotEl.classList.toggle("is-idle", role === "idle");
  if (role === "active") slotEl.classList.remove("is-empty");
}

function markSlotSung(slotEl) {
  if (!lyricsAligned) return;
  slotEl.querySelectorAll(".k-word").forEach((el) => {
    el.classList.add("done");
    el.classList.remove("active");
    const fill = el.querySelector(".k-word-fill");
    if (fill) fill.style.width = "100%";
  });
}

function slotMatchesLine(slotEl, line) {
  if (!line || !slotEl) return false;
  const nodes = [...slotEl.querySelectorAll(".k-word")];
  const expected = lineWords(line);
  if (nodes.length !== expected.length) return false;
  return nodes.every((node, index) => {
    const text = node.querySelector(".k-word-base")?.textContent ?? node.textContent;
    return text === expected[index].text;
  });
}

function lineTimeSpan(line, index) {
  const words = lineWords(line);
  const start = words.length ? Number(words[0].time) : Number(line.time);
  let end;
  if (words.length) {
    end = Number(words[words.length - 1].end);
  } else if (lyricLines[index + 1]) {
    end = Number(lyricLines[index + 1].time);
  } else {
    end = start + 4;
  }
  return { start, end: Math.max(end, start + 0.05) };
}

function activeLineProgress(t, index) {
  const line = lyricLines[index];
  if (!line) return 0;
  const { start, end } = lineTimeSpan(line, index);
  return (t - start) / (end - start);
}

function maybeRevealDualUpcoming(t) {
  if (!dualPending || lyricsLayout !== "dual") return;
  if (activeLineIndex < 0) return;
  if (activeLineProgress(t, activeLineIndex) < 0.25) return;
  const { slotEl, line } = dualPending;
  dualPending = null;
  if (!line) {
    slotEl.classList.add("is-empty");
    setSlotRole(slotEl, "idle");
    return;
  }
  refreshSlotSoft(slotEl, line);
}

function refreshSlotSoft(slotEl, line) {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) {
    fillSlot(slotEl, line);
    setSlotRole(slotEl, "idle");
    return;
  }
  slotEl.classList.add("is-refreshing");
  if (dualRefreshTimer) clearTimeout(dualRefreshTimer);
  dualRefreshTimer = setTimeout(() => {
    slotEl.innerHTML = "";
    slotEl.classList.remove("is-empty", "is-rising", "is-entering");
    if (!line) {
      slotEl.classList.add("is-empty");
      setSlotRole(slotEl, "idle");
      dualRefreshTimer = null;
      return;
    }
    for (const word of lineWords(line)) {
      slotEl.appendChild(buildWordNode(word));
    }
    setSlotRole(slotEl, "idle");
    requestAnimationFrame(() => {
      requestAnimationFrame(() => slotEl.classList.remove("is-refreshing"));
    });
    dualRefreshTimer = null;
  }, 160);
}

function showStackLines(index, animate) {
  const current = lyricLines[index] || null;
  const next = lyricLines[index + 1] || null;
  wordNodes = [];
  lineCurrentEl.classList.remove("is-active", "is-idle");
  lineNextEl.classList.remove("is-active", "is-idle");

  if (!animate || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    clearLineRoll();
    fillSlot(lineCurrentEl, current, { trackWords: true });
    fillSlot(lineNextEl, next);
    syncWordFills(player.currentTime);
    return;
  }

  clearLineRoll();

  const stackRect = kStackEl.getBoundingClientRect();
  const currentRect = lineCurrentEl.getBoundingClientRect();

  const ghost = document.createElement("div");
  ghost.className = "k-slot k-slot-ghost";
  ghost.setAttribute("aria-hidden", "true");
  ghost.innerHTML = lineCurrentEl.innerHTML;
  ghost.style.top = `${currentRect.top - stackRect.top}px`;
  ghost.style.left = `${currentRect.left - stackRect.left}px`;
  ghost.style.width = `${currentRect.width}px`;
  kStackEl.appendChild(ghost);

  fillSlot(lineCurrentEl, current, { trackWords: true });
  lineCurrentEl.classList.add("is-rising");
  fillSlot(lineNextEl, next);
  lineNextEl.classList.add("is-entering");

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      kStackEl.classList.add("is-rolling");
      lineCurrentEl.classList.remove("is-rising");
      lineNextEl.classList.remove("is-entering");
      syncWordFills(player.currentTime);
    });
  });

  lineSwapTimer = setTimeout(() => {
    clearLineRoll();
    syncWordFills(player.currentTime);
  }, 580);
}

function showDualLines(index, sequential) {
  const current = lyricLines[index] || null;
  const upcoming = lyricLines[index + 1] || null;
  const previous = index > 0 ? lyricLines[index - 1] : null;
  const activeOnTop = index % 2 === 0;
  const activeSlot = activeOnTop ? lineCurrentEl : lineNextEl;
  const idleSlot = activeOnTop ? lineNextEl : lineCurrentEl;
  const t = player.currentTime;

  clearLineRoll();

  if (!sequential) {
    wordNodes = [];
    fillSlot(activeSlot, current, { trackWords: true });
    setSlotRole(activeSlot, "active");

    // First pair shows both lines. Later, keep the finished line until the
    // active one passes its first quarter, then reveal the next upcoming phrase.
    if (index === 0) {
      fillSlot(idleSlot, upcoming);
      setSlotRole(idleSlot, "idle");
      if (!upcoming) idleSlot.classList.add("is-empty");
    } else if (activeLineProgress(t, index) >= 0.25) {
      fillSlot(idleSlot, upcoming);
      setSlotRole(idleSlot, "idle");
      if (!upcoming) idleSlot.classList.add("is-empty");
    } else {
      fillSlot(idleSlot, previous);
      setSlotRole(idleSlot, "idle");
      if (previous) markSlotSung(idleSlot);
      else idleSlot.classList.add("is-empty");
      if (upcoming) dualPending = { slotEl: idleSlot, line: upcoming };
    }
    syncWordFills(t);
    return;
  }

  // Illumination moves to the line already on screen; finished slot waits for first quarter.
  setSlotRole(activeSlot, "active");
  setSlotRole(idleSlot, "idle");
  if (slotMatchesLine(activeSlot, current)) {
    bindSlotWords(activeSlot, current);
  } else {
    fillSlot(activeSlot, current, { trackWords: true });
  }
  markSlotSung(idleSlot);
  if (upcoming) dualPending = { slotEl: idleSlot, line: upcoming };
  maybeRevealDualUpcoming(t);
  syncWordFills(t);
}

function showLyricsLayout(index, animate) {
  if (lyricsLayout === "dual") {
    showDualLines(index, animate);
  } else {
    showStackLines(index, animate);
  }
}

function setLyricsAligned(aligned) {
  lyricsAligned = Boolean(aligned);
  lyricsEl?.classList.toggle("is-aligned", lyricsAligned);
}

function renderLyrics(payload) {
  lyricLines = payload.lines || [];
  lastLyricsPlain = payload.plain || lyricLines.map((line) => line.text).join("\n");
  activeLineIndex = -1;
  wordNodes = [];
  setLyricsAligned(payload.aligned);
  applyLyricsLayout();

  if (!lyricLines.length) {
    clearLineRoll();
    lineCurrentEl.innerHTML = "";
    lineNextEl.innerHTML = "";
    lineCurrentEl.classList.remove("is-active", "is-idle");
    lineNextEl.classList.remove("is-active", "is-idle");
    lineNextEl.classList.add("is-empty");
    const p = document.createElement("span");
    p.className = "lyrics-empty";
    p.textContent = "No s’ha trobat lletra per a aquesta cançó.";
    lineCurrentEl.appendChild(p);
    updatePasteLyricsButton();
    return;
  }

  showLyricsLayout(0, false);
  updatePasteLyricsButton();
}

function setActiveLine(index) {
  if (index === activeLineIndex) return;
  const prev = activeLineIndex;
  const sequential = prev >= 0 && index === prev + 1;
  activeLineIndex = index;
  showLyricsLayout(index, sequential);
}

function syncWordFills(t) {
  if (!lyricsAligned) return;
  for (const word of wordNodes) {
    if (t >= word.end) {
      word.el.classList.add("done");
      word.el.classList.remove("active");
      word.fill.style.width = "100%";
    } else if (t <= word.start) {
      word.el.classList.remove("done", "active");
      word.fill.style.width = "0%";
    } else {
      word.el.classList.remove("done");
      word.el.classList.add("active");
      const progress = (t - word.start) / Math.max(0.08, word.end - word.start);
      word.fill.style.width = `${Math.min(1, Math.max(0, progress)) * 100}%`;
    }
  }
}

function updatePlayButton() {
  const playing = !player.paused && !player.ended;
  playBtn.textContent = "Inicia";
  playBtn.setAttribute("aria-label", "Reproduir");
  playBtn.classList.toggle("is-playing", playing);
  playBtn.hidden = playing;
  viewStage.classList.toggle("is-live", playing);
}

async function togglePlayback() {
  if (!player.src) return;
  if (player.paused || player.ended) {
    await player.play().catch(() => {});
  } else {
    player.pause();
  }
  updatePlayButton();
}

function syncKaraoke() {
  if (!lyricLines.length) return;
  const t = player.currentTime;

  let lineIndex = 0;
  for (let i = 0; i < lyricLines.length; i += 1) {
    if (lyricLines[i].time <= t + 0.02) lineIndex = i;
    else break;
  }
  setActiveLine(lineIndex);
  syncWordFills(t);
  maybeRevealDualUpcoming(t);
}

function tick() {
  if (!player.paused && !player.ended) {
    syncKaraoke();
    const now = performance.now();
    if (now - lastYoutubeSync > 400) {
      lastYoutubeSync = now;
      syncYoutubeToAudio();
    }
  }
  rafId = requestAnimationFrame(tick);
}

function startTicker() {
  if (rafId) return;
  rafId = requestAnimationFrame(tick);
}

function stopTicker() {
  if (!rafId) return;
  cancelAnimationFrame(rafId);
  rafId = 0;
}

function setSettingsStatus(el, text, tone = "") {
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("is-running", tone === "running");
  el.classList.toggle("is-ok", tone === "ok");
  el.classList.toggle("is-error", tone === "error");
}

let lastLibraryData = null;

function refreshLibraryMetaLabel() {
  const data = lastLibraryData;
  if (!data) return;
  const pending = data.pending || 0;
  const hidden = data.hidden || 0;
  const total = data.total || 0;
  const errors = data.errors || 0;
  const coversResync = data.covers_resync || {};

  if (coversResync.running) {
    const done = coversResync.done || 0;
    const coverTotal = coversResync.total || 0;
    libraryMeta.textContent = `Resincronitzant portades… ${done}/${coverTotal}`;
    return;
  }
  const youtubeBulk = data.youtube || {};
  if (youtubeBulk.running) {
    libraryMeta.textContent = youtubeBulkLabel(youtubeBulk);
    return;
  }
  if (!data.root) {
    libraryMeta.textContent = "Carrega una carpeta de MP3s etiquetats per començar la nit";
    return;
  }
  if (lyricsFilterMode === "hidden") {
    const count = hiddenTracks.length;
    if (!count) {
      libraryMeta.textContent = `Cap cançó oculta (de ${total} al disc)`;
    } else {
      const bits = [`${count} cançons ocultes sense lletra`];
      if (errors) bits.push(`${errors} amb error de connexió`);
      if (pending) bits.push(`${pending} sense comprovar`);
      libraryMeta.textContent = bits.join(" · ");
    }
    return;
  }
  if (lyricsFilterMode === "all") {
    const count = playableTracks.length + hiddenTracks.length + pendingTracks.length;
    if (!count) {
      libraryMeta.textContent = `Cap cançó a la biblioteca (de ${total} al disc)`;
    } else {
      const bits = [`${count} cançons`];
      if (playableTracks.length) bits.push(`${playableTracks.length} amb lletra`);
      if (hiddenTracks.length) bits.push(`${hiddenTracks.length} sense lletra`);
      if (pendingTracks.length) bits.push(`${pendingTracks.length} sense comprovar`);
      libraryMeta.textContent = bits.join(" · ");
    }
    return;
  }
  if (!playableTracks.length && pending) {
    libraryMeta.textContent =
      `${pending} cançons sense lletres bàsiques · Configuració → Resincronitzar o Whisper`;
  } else if (!playableTracks.length && errors) {
    libraryMeta.textContent = `No s’ha pogut connectar a LRCLIB per ${errors} cançons · Configuració → Reintentar lletres`;
  } else if (!playableTracks.length) {
    libraryMeta.textContent = `Cap cançó amb lletra (de ${total} al disc)`;
  } else if (hidden || pending || errors) {
    const bits = [`${playableTracks.length} cançons amb lletra`];
    if (hidden - errors > 0) bits.push(`${hidden - errors} amagades sense lletra`);
    if (errors) bits.push(`${errors} amb error de connexió`);
    if (pending) bits.push(`${pending} sense comprovar`);
    libraryMeta.textContent = bits.join(" · ");
  } else {
    libraryMeta.textContent = `${playableTracks.length} cançons a punt · tria’n una per cantar`;
  }
}

function updateLibraryMeta(data) {
  const previousId = selectedTrack()?.id;
  lastLibraryData = data;
  playableTracks = data.tracks || [];
  hiddenTracks = data.hidden_tracks || [];
  pendingTracks = data.pending_tracks || [];
  applyLyricsFilterMode();
  rootInput.value = data.root || "";
  const total = data.total || 0;
  const errors = data.errors || 0;
  const probe = data.probe || {};

  retryLyricsBtn.hidden = !errors;
  const resyncBusy = !data.root || !total || !!probe.running;
  if (resyncLyricsMissingBtn) resyncLyricsMissingBtn.disabled = resyncBusy;
  if (syncLyricsWhisperBtn) {
    syncLyricsWhisperBtn.disabled =
      !data.root || !whisperSyncCandidates().length || syncRunning;
  }
  applyStemsAvailability(data);
  const cacheSectionOpen =
    isSettingsOpen() &&
    settingsModal?.querySelector(".settings-nav-btn.is-active")?.dataset?.settingsSection ===
      "cache";
  if (cacheSectionOpen) fillCacheSongSelect();

  if (probe.running && !syncRunning) {
    const done = probe.done || 0;
    const probeTotal = probe.total || 0;
    setSettingsStatus(
      lyricsSyncSettingsStatus,
      `Buscant lletres bàsiques… ${done}/${probeTotal}`,
      "running"
    );
  } else if (syncRunning) {
    updateSyncQueueMeta();
  }
  refreshLibraryMetaLabel();

  renderSongs(searchEl.value, { play: false });
  if (previousId) {
    const idx = findBrowseIndexByTrackId(previousId);
    if (idx >= 0) {
      selectedIndex = idx;
      layoutCovers();
      layoutGridSelection();
      updateCoverMeta();
    }
  } else if (browseList().length && !viewMenu.classList.contains("hidden")) {
    playPreviewForSelection();
  }
}

async function pollBasicLyricsResync() {
  setSettingsStatus(lyricsSyncSettingsStatus, "Iniciant resincronització de lletres…", "running");
  let data = await api("/api/library");
  while (data.probe && data.probe.running) {
    const done = data.probe.done || 0;
    const total = data.probe.total || 0;
    setSettingsStatus(
      lyricsSyncSettingsStatus,
      `Buscant lletres bàsiques… ${done}/${total}`,
      "running"
    );
    updateLibraryMeta(data);
    await sleep(500);
    data = await api("/api/library");
  }
  updateLibraryMeta(data);
  const found = (data.probe && data.probe.found) || 0;
  const total = (data.probe && data.probe.total) || data.total || 0;
  const msg = total
    ? `Lletres bàsiques actualitzades · ${found}/${total} amb lletra`
    : "No hi ha cançons per resincronitzar";
  libraryMeta.textContent = msg;
  setSettingsStatus(lyricsSyncSettingsStatus, msg, total ? "ok" : "error");
}

function enqueueWhisperForLibrary() {
  const pending = whisperSyncCandidates().filter(
    (track) => syncActiveId !== track.id && !syncQueuedIds.has(track.id)
  );
  if (!pending.length) {
    const known = playableTracks.length + pendingTracks.length;
    const msg = known
      ? "Totes les cançons candidates ja tenen Whisper"
      : "No hi ha cançons per sincronitzar · fes Resincronitzar lletres o canvia el filtre";
    libraryMeta.textContent = msg;
    setSettingsStatus(lyricsSyncSettingsStatus, msg, known ? "ok" : "error");
    return 0;
  }
  for (const track of pending) {
    syncQueue.push(track.id);
    syncQueuedIds.add(track.id);
  }
  syncTotalQueued = syncQueue.length + (syncActiveId ? 1 : 0);
  syncCompleted = 0;
  refreshAlignBadges();
  updatePrimaryAction();
  const msg = `Encades ${pending.length} cançons (lletres → stems → Whisper)`;
  libraryMeta.textContent = msg;
  setSettingsStatus(lyricsSyncSettingsStatus, msg, "running");
  processSyncQueue();
  return pending.length;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function loadLibrary({ onProgress } = {}) {
  libraryMeta.textContent = "Carregant la biblioteca…";
  setSettingsStatus(librarySettingsStatus, "Carregant la biblioteca…", "running");
  loadBtn.disabled = true;
  rootInput.disabled = true;
  try {
    let data = await api("/api/library");
    // Only wait when a manual basic-lyrics resync/retry is already running.
    while (data.probe && data.probe.running) {
      const total = data.probe.total || data.pending || 0;
      const done = Math.min(data.probe.done || 0, total || 0);
      const ready = (data.tracks || []).length;
      const msg = `Buscant lletres… ${done}/${total} · ${ready} a punt`;
      libraryMeta.textContent = msg;
      setSettingsStatus(librarySettingsStatus, msg, "running");
      if (typeof onProgress === "function") onProgress(msg, data);
      await sleep(500);
      data = await api("/api/library");
    }
    updateLibraryMeta(data);
    const total = data.total || 0;
    const withLyrics = (data.tracks || []).length;
    const unchecked = (data.pending_tracks || []).length;
    const bits = [`${withLyrics} amb lletra`];
    if (unchecked) bits.push(`${unchecked} sense comprovar`);
    setSettingsStatus(
      librarySettingsStatus,
      `Fet · ${bits.join(" · ")} (de ${total} al disc)`,
      "ok"
    );
    return data;
  } finally {
    loadBtn.disabled = false;
    rootInput.disabled = false;
  }
}

async function enterLibraryFromTitle() {
  const path = (titleRootInput?.value || "").trim();
  if (!path) {
    setTitleStatus("Indica una carpeta de música", "error");
    titleRootInput?.focus();
    return;
  }
  if (rootInput) rootInput.value = path;
  setTitleStatus("Carregant la biblioteca…", "running");
  if (titleStartBtn) titleStartBtn.disabled = true;
  if (titleRootInput) titleRootInput.disabled = true;
  try {
    await api("/api/library/root", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    await loadLibrary({
      onProgress: (msg) => setTitleStatus(msg, "running"),
    });
    setTitleStatus("");
    showMenu();
  } catch (err) {
    const msg = err.message || "No s’ha pogut carregar la carpeta";
    setTitleStatus(msg, "error");
  } finally {
    if (titleStartBtn) titleStartBtn.disabled = false;
    if (titleRootInput) titleRootInput.disabled = false;
  }
}

function setLandingBusy(busy) {
  if (!landingEnterBtn) return;
  landingEnterBtn.classList.toggle("is-loading", busy);
  landingEnterBtn.disabled = busy;
  landingEnterBtn.setAttribute("aria-busy", busy ? "true" : "false");
  if (busy) landingEnterBtn.setAttribute("aria-label", "Carregant");
  else landingEnterBtn.removeAttribute("aria-label");
}

async function enterFromLanding() {
  if (landingEntering) return;
  landingEntering = true;
  setLandingBusy(true);
  try {
    await bootWork;
    if (bootLibraryReady) {
      showMenu();
      return;
    }
    showTitleScreen();
  } catch (err) {
    setLandingStatus(err.message || "No s’ha pogut arrencar", "error");
  } finally {
    landingEntering = false;
    setLandingBusy(false);
  }
}

async function bootTitleScreen() {
  showLanding();
  bootLibraryReady = false;
  bootWork = (async () => {
    const health = await api("/api/health");
    if (health.music_root) {
      if (titleRootInput) titleRootInput.value = health.music_root;
      if (rootInput) rootInput.value = health.music_root;
    }
    refreshWhisperStatus({ pollWhileLoading: true }).catch(() => {});
    if (health.music_root && health.tracks > 0) {
      await loadLibrary();
      bootLibraryReady = true;
    }
  })();
  try {
    await bootWork;
  } catch (err) {
    setLandingStatus(err.message || "No s’ha pogut contactar amb l’API", "error");
  }
}

async function browseMusicFolder(initial) {
  const result = await api("/api/library/browse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ initial: initial || null }),
  });
  if (result.cancelled || !result.path) return null;
  return result.path;
}

async function pickFolderInto(inputEl, { statusEl } = {}) {
  if (!inputEl) return null;
  const buttons = [titleBrowseBtn, browseRootBtn, titleStartBtn].filter(Boolean);
  buttons.forEach((btn) => {
    btn.disabled = true;
  });
  try {
    const path = await browseMusicFolder(inputEl.value.trim());
    if (!path) {
      if (statusEl === "title") setTitleStatus("Selecció cancel·lada", "");
      return null;
    }
    inputEl.value = path;
    if (inputEl === titleRootInput && rootInput) rootInput.value = path;
    if (inputEl === rootInput && titleRootInput) titleRootInput.value = path;
    if (statusEl === "title") setTitleStatus("Carpeta seleccionada", "");
    if (statusEl === "settings") {
      setSettingsStatus(librarySettingsStatus, "Carpeta seleccionada · recarrega per aplicar", "ok");
    }
    return path;
  } catch (err) {
    const msg = err.message || "No s’ha pogut obrir el selector de carpetes";
    if (statusEl === "title") setTitleStatus(msg, "error");
    if (statusEl === "settings") setSettingsStatus(librarySettingsStatus, msg, "error");
    return null;
  } finally {
    buttons.forEach((btn) => {
      btn.disabled = false;
    });
  }
}

async function setRoot() {
  const path = rootInput.value.trim();
  if (!path) {
    setSettingsStatus(librarySettingsStatus, "Indica una carpeta de música", "error");
    return;
  }
  libraryMeta.textContent = "Carregant la biblioteca…";
  setSettingsStatus(librarySettingsStatus, "Recarregant la biblioteca…", "running");
  loadBtn.disabled = true;
  rootInput.disabled = true;
  try {
    await api("/api/library/root", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    await loadLibrary();
  } catch (err) {
    loadBtn.disabled = false;
    rootInput.disabled = false;
    throw err;
  }
}

async function openSong(trackId) {
  const track = tracks.find((t) => t.id === trackId);
  if (!track) return;
  stopAlignPoll();
  stopStemPoll();
  currentId = trackId;
  showStage();
  setStageCover(trackId);
  songTitle.textContent = track.title;
  songArtist.textContent = track.artist || "Artista desconegut";
  // Fall back to the original mix while the instrumental is still cooking.
  const wantsInstrumental = audioMode === "instrumental" && stemsAvailable;
  const useInstrumental = wantsInstrumental && !!track.has_instrumental;
  player.src = audioUrlFor(trackId, useInstrumental ? "instrumental" : "original");
  applyAudioModeButtons();
  loadYoutubeBackdrop(trackId);
  setStemStatus("");
  if (wantsInstrumental && !useInstrumental) requestInstrumental(trackId);
  lyricsStatus.textContent = "Obtenint la lletra…";
  try {
    const payload = await api(`/api/lyrics?track_id=${encodeURIComponent(trackId)}`);
    renderLyrics(payload);
    if (!payload.lines.length) {
      lyricsStatus.textContent = "No s’ha trobat lletra";
    } else if (payload.aligned) {
      lyricsStatus.textContent = `Alineat per paraules · ${payload.source}`;
      markTrackAligned(trackId);
    } else if (payload.synced) {
      lyricsStatus.textContent = `Mode karaoke · ${payload.source}`;
      startAlignment(trackId);
    } else {
      lyricsStatus.textContent = `Temps aproximat · ${payload.source}`;
      startAlignment(trackId);
    }
    await player.play().catch(() => {});
    updatePlayButton();
  } catch (err) {
    renderLyrics({ lines: [] });
    lyricsStatus.textContent = err.message || "Error en obtenir la lletra";
    updatePlayButton();
  }
}

loadBtn.addEventListener("click", () => {
  setRoot().catch((err) => {
    const msg = err.message || "Error en carregar";
    libraryMeta.textContent = msg;
    setSettingsStatus(librarySettingsStatus, msg, "error");
  });
});
retryLyricsBtn.addEventListener("click", () => {
  retryLyricsBtn.disabled = true;
  libraryMeta.textContent = "Tornant a buscar les lletres…";
  setSettingsStatus(librarySettingsStatus, "Tornant a buscar les lletres…", "running");
  api("/api/library/retry", { method: "POST" })
    .then(() => loadLibrary())
    .catch((err) => {
      const msg = err.message || "Error en reintentar";
      libraryMeta.textContent = msg;
      setSettingsStatus(librarySettingsStatus, msg, "error");
    })
    .finally(() => {
      retryLyricsBtn.disabled = false;
    });
});
function startBasicLyricsResync() {
  const label = "Resincronitzant cançons sense lletra…";
  if (resyncLyricsMissingBtn) resyncLyricsMissingBtn.disabled = true;
  libraryMeta.textContent = label;
  setSettingsStatus(lyricsSyncSettingsStatus, label, "running");
  api("/api/library/lyrics/resync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scope: "missing" }),
  })
    .then(() => pollBasicLyricsResync())
    .catch((err) => {
      const msg = err.message || "Error en resincronitzar lletres";
      libraryMeta.textContent = msg;
      setSettingsStatus(lyricsSyncSettingsStatus, msg, "error");
    })
    .finally(() => {
      if (resyncLyricsMissingBtn) resyncLyricsMissingBtn.disabled = false;
    });
}

resyncLyricsMissingBtn?.addEventListener("click", () => startBasicLyricsResync());
syncLyricsWhisperBtn?.addEventListener("click", () => {
  syncLyricsWhisperBtn.disabled = true;
  try {
    enqueueWhisperForLibrary();
  } finally {
    syncLyricsWhisperBtn.disabled = false;
  }
});
resyncCoverBtn.addEventListener("click", () => {
  const track = selectedTrack();
  if (!track) return;
  resyncCoverBtn.disabled = true;
  libraryMeta.textContent = `Buscant portada per “${track.title}”…`;
  api("/api/covers/resync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ track_id: track.id }),
  })
    .then((result) => {
      refreshCoverImages();
      libraryMeta.textContent = result.updated
        ? `Portada nova per “${track.title}”`
        : `Sense portada remota per “${track.title}” · es manté l’actual`;
    })
    .catch((err) => {
      libraryMeta.textContent = err.message || "Error en actualitzar la portada";
    })
    .finally(() => {
      resyncCoverBtn.disabled = false;
    });
});
backBtn.addEventListener("click", showMenu);
document.querySelector(".stage-dock-layer")?.addEventListener("mouseleave", () => {
  const active = document.activeElement;
  if (active instanceof HTMLElement && viewStage?.contains(active)) active.blur();
});
searchEl.addEventListener("input", () => {
  selectedIndex = 0;
  renderSongs(searchEl.value);
});
coverPrev.addEventListener("click", () => setSelectedIndex(selectedIndex - 1));
coverNext.addEventListener("click", () => setSelectedIndex(selectedIndex + 1));
modeCoverBtn.addEventListener("click", () => setBrowseMode("cover"));
modeGridBtn.addEventListener("click", () => setBrowseMode("grid"));
syncStatusBtn.addEventListener("click", () => cycleAlignMode());

function isLyricsPasteOpen() {
  return (
    lyricsPasteModal &&
    !lyricsPasteModal.classList.contains("hidden") &&
    !lyricsPasteModal.hidden
  );
}

function setLyricsPasteStatus(text, tone = "") {
  if (!lyricsPasteStatus) return;
  lyricsPasteStatus.textContent = text || "";
  lyricsPasteStatus.classList.toggle("is-running", tone === "running");
  lyricsPasteStatus.classList.toggle("is-ok", tone === "ok");
  lyricsPasteStatus.classList.toggle("is-error", tone === "error");
}

function trackForLyricsPaste() {
  if (lyricsPasteTrackId) {
    return (
      tracks.find((item) => item.id === lyricsPasteTrackId) ||
      playableTracks.find((item) => item.id === lyricsPasteTrackId) ||
      hiddenTracks.find((item) => item.id === lyricsPasteTrackId) ||
      pendingTracks.find((item) => item.id === lyricsPasteTrackId) ||
      null
    );
  }
  return selectedTrack();
}

function openLyricsPasteModal(trackId) {
  const track =
    (trackId &&
      (tracks.find((item) => item.id === trackId) ||
        playableTracks.find((item) => item.id === trackId) ||
        hiddenTracks.find((item) => item.id === trackId) ||
        pendingTracks.find((item) => item.id === trackId))) ||
    selectedTrack();
  if (!track || track.kind === "album") return;
  lyricsPasteTrackId = track.id;
  if (lyricsPasteTitle) {
    lyricsPasteTitle.textContent = "Editar lletra";
  }
  if (lyricsPasteMeta) {
    lyricsPasteMeta.textContent = `${track.artist || "Artista desconegut"} · ${track.title || track.relpath}. Es desa al fitxer d’àudio.`;
  }
  if (lyricsPasteInput) lyricsPasteInput.value = "";
  setLyricsPasteStatus("Carregant la lletra del fitxer…", "running");
  if (!lyricsPasteModal) return;
  lyricsPasteModal.hidden = false;
  lyricsPasteModal.classList.remove("hidden");
  lyricsPasteInput?.focus();
  loadLocalLyricsIntoEditor(track.id);
}

async function loadLocalLyricsIntoEditor(trackId) {
  try {
    const data = await api(`/api/lyrics/local?track_id=${encodeURIComponent(trackId)}`);
    if (lyricsPasteTrackId !== trackId || !isLyricsPasteOpen()) return;
    if (lyricsPasteInput) lyricsPasteInput.value = data.text || "";
    lastLyricsPlain = data.text || "";
    if (data.text) {
      const src = data.source ? ` · ${data.source}` : "";
      setLyricsPasteStatus(`Lletra del fitxer${src}`, "ok");
    } else {
      setLyricsPasteStatus("El fitxer encara no té lletra", "");
    }
  } catch (err) {
    if (lyricsPasteTrackId !== trackId || !isLyricsPasteOpen()) return;
    setLyricsPasteStatus(err.message || "No s’ha pogut llegir la lletra del fitxer", "error");
  }
}

function closeLyricsPasteModal() {
  if (!lyricsPasteModal || !isLyricsPasteOpen()) return;
  lyricsPasteModal.classList.add("hidden");
  lyricsPasteModal.hidden = true;
  lyricsPasteTrackId = "";
}

async function savePastedLyrics() {
  const track = trackForLyricsPaste();
  const text = (lyricsPasteInput?.value || "").trim();
  if (!track) {
    setLyricsPasteStatus("Tria una cançó", "error");
    return;
  }
  if (!text) {
    setLyricsPasteStatus("Enganxa la lletra abans de desar", "error");
    lyricsPasteInput?.focus();
    return;
  }
  if (lyricsPasteSaveBtn) lyricsPasteSaveBtn.disabled = true;
  setLyricsPasteStatus("Desant la lletra…", "running");
  try {
    const payload = await api("/api/lyrics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_id: track.id, text }),
    });
    const savedId = track.id;
    if (lyricsFilterMode === "hidden") {
      lyricsFilterMode = "lyrics";
      localStorage.setItem(LYRICS_FILTER_KEY, lyricsFilterMode);
    }
    await loadLibrary();
    closeLyricsPasteModal();
    const idx = findBrowseIndexByTrackId(savedId);
    if (idx >= 0) {
      selectedIndex = idx;
      layoutCovers();
      layoutGridSelection();
      updateCoverMeta();
    }
    if (currentId === savedId) {
      renderLyrics(payload);
      lyricsStatus.textContent = payload.synced
        ? `Mode karaoke · ${payload.source}`
        : `Temps aproximat · ${payload.source}`;
      startAlignment(savedId);
    }
    libraryMeta.textContent = `Lletra desada al fitxer per “${track.title}”`;
  } catch (err) {
    setLyricsPasteStatus(err.message || "No s’ha pogut desar la lletra", "error");
  } finally {
    if (lyricsPasteSaveBtn) lyricsPasteSaveBtn.disabled = false;
  }
}

function isSettingsOpen() {
  return settingsModal && !settingsModal.classList.contains("hidden") && !settingsModal.hidden;
}

function showSettingsSection(sectionId) {
  const id = sectionId || "general";
  settingsModal?.querySelectorAll(".settings-nav-btn").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.settingsSection === id);
  });
  settingsModal?.querySelectorAll("[data-settings-section-panel]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.settingsSectionPanel === id);
  });
  if (id === "cache") {
    fillCacheSongSelect();
    refreshSelectedCacheStatus();
  }
}

function allLibraryTracks() {
  const seen = new Set();
  const out = [];
  for (const list of [playableTracks, hiddenTracks, pendingTracks, tracks]) {
    for (const track of list || []) {
      if (!track?.id || seen.has(track.id)) continue;
      seen.add(track.id);
      out.push(track);
    }
  }
  return out.sort((a, b) =>
    `${a.artist || ""} ${a.title || ""}`.localeCompare(
      `${b.artist || ""} ${b.title || ""}`,
      "ca",
      { sensitivity: "base" }
    )
  );
}

function fillCacheSongSelect() {
  if (!cacheSongSelect) return;
  const query = (cacheSongSearch?.value || "").trim().toLowerCase();
  const previous = cacheSongSelect.value;
  const items = allLibraryTracks().filter((track) => {
    if (!query) return true;
    const hay = `${track.artist || ""} ${track.title || ""} ${track.album || ""}`.toLowerCase();
    return hay.includes(query);
  });
  cacheSongSelect.innerHTML = "";
  for (const track of items) {
    const opt = document.createElement("option");
    opt.value = track.id;
    opt.textContent = `${track.artist || "Desconegut"} — ${track.title || track.id}`;
    cacheSongSelect.appendChild(opt);
  }
  if (previous && [...cacheSongSelect.options].some((opt) => opt.value === previous)) {
    cacheSongSelect.value = previous;
  } else if (cacheSongSelect.options.length) {
    cacheSongSelect.selectedIndex = 0;
  }
  const has = !!cacheSongSelect.value;
  if (cacheClearBtn) cacheClearBtn.disabled = !has;
  if (cacheResyncBtn) cacheResyncBtn.disabled = !has;
  if (cacheExportBtn) cacheExportBtn.disabled = !has;
}

function selectedCacheScopes() {
  const scopes = [];
  if (cacheScopeLyrics?.checked) scopes.push("lyrics");
  if (cacheScopeAligned?.checked) scopes.push("aligned");
  if (cacheScopeStems?.checked) scopes.push("stems");
  if (cacheScopeCover?.checked) scopes.push("cover");
  if (cacheScopeYoutube?.checked) scopes.push("youtube");
  return scopes;
}

function renderCacheFlags(cache) {
  if (!cacheFlags) return;
  if (!cache) {
    cacheFlags.hidden = true;
    cacheFlags.innerHTML = "";
    return;
  }
  const flags = [
    ["Lletres", cache.lyrics],
    ["Whisper", cache.aligned || cache.aligned_file],
    ["Instrumental", cache.instrumental],
    ["Veu", cache.vocals],
    ["Portada", cache.cover],
    ["Videoclip", cache.youtube],
  ];
  cacheFlags.hidden = false;
  cacheFlags.innerHTML = "";
  for (const [label, on] of flags) {
    const el = document.createElement("span");
    el.className = `cache-flag${on ? " is-on" : ""}`;
    el.textContent = `${label}${on ? "" : " · no"}`;
    cacheFlags.appendChild(el);
  }
}

async function refreshSelectedCacheStatus() {
  const trackId = cacheSongSelect?.value;
  if (!trackId) {
    if (cacheSongMeta) {
      cacheSongMeta.hidden = true;
      cacheSongMeta.textContent = "";
    }
    renderCacheFlags(null);
    return;
  }
  const track =
    allLibraryTracks().find((item) => item.id === trackId) ||
    playableTracks.find((item) => item.id === trackId);
  if (cacheSongMeta) {
    cacheSongMeta.hidden = false;
    cacheSongMeta.textContent = track
      ? `${track.artist || "Desconegut"} — ${track.title || trackId}`
      : trackId;
  }
  try {
    const cache = await api(`/api/cache?track_id=${encodeURIComponent(trackId)}`);
    renderCacheFlags(cache);
  } catch (err) {
    renderCacheFlags(null);
    setSettingsStatus(cacheSettingsStatus, err.message || "No s’ha pogut llegir la cau", "error");
  }
}

async function clearAllCache() {
  const scopes = selectedCacheScopes();
  if (!scopes.length) {
    setSettingsStatus(cacheSettingsStatus, "Selecciona almenys una part de la cau", "error");
    return;
  }
  const ok = window.confirm(
    `Segur que vols esborrar la memòria cau de TOTES les cançons?\n(${scopes.join(", ")})`
  );
  if (!ok) return;
  if (cacheClearAllBtn) cacheClearAllBtn.disabled = true;
  if (cacheClearBtn) cacheClearBtn.disabled = true;
  if (cacheResyncBtn) cacheResyncBtn.disabled = true;
  if (cacheExportBtn) cacheExportBtn.disabled = true;
  setSettingsStatus(cacheSettingsStatus, "Esborrant tota la memòria cau…", "running");
  try {
    const result = await api("/api/cache/clear-all", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_id: "", scopes }),
    });
    const total = result.total || 0;
    for (const track of allLibraryTracks()) {
      if (scopes.includes("aligned")) track.whisper_aligned = false;
    }
    setSettingsStatus(
      cacheSettingsStatus,
      total ? `S’ha buidat la cau · ${total} fitxers` : "La cau ja era buida",
      total ? "ok" : ""
    );
    await refreshSelectedCacheStatus();
    loadLibrary().catch(() => {});
  } catch (err) {
    setSettingsStatus(cacheSettingsStatus, err.message || "Error esborrant la cau", "error");
  } finally {
    if (cacheClearAllBtn) cacheClearAllBtn.disabled = false;
    const has = !!cacheSongSelect?.value;
    if (cacheClearBtn) cacheClearBtn.disabled = !has;
    if (cacheResyncBtn) cacheResyncBtn.disabled = !has;
    if (cacheExportBtn) cacheExportBtn.disabled = !has;
  }
}

async function exportSelectedCache() {
  const trackId = cacheSongSelect?.value;
  if (!trackId) return;
  if (cacheExportBtn) cacheExportBtn.disabled = true;
  setSettingsStatus(cacheSettingsStatus, "Exportant la memòria cau…", "running");
  try {
    const response = await fetch(`/api/cache/export?track_id=${encodeURIComponent(trackId)}`);
    if (!response.ok) {
      let detail = "Error exportant la cau";
      try {
        const payload = await response.json();
        if (payload?.detail) detail = payload.detail;
      } catch {
        /* ignore */
      }
      throw new Error(detail);
    }
    const blob = await response.blob();
    const disposition = response.headers.get("content-disposition") || "";
    const match = /filename\*?=(?:UTF-8''|")?([^\";]+)/i.exec(disposition);
    const name = match ? decodeURIComponent(match[1].replace(/"/g, "")) : "karaoke-cache.zip";
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setSettingsStatus(cacheSettingsStatus, `Zip descarregat · ${name}`, "ok");
  } catch (err) {
    setSettingsStatus(cacheSettingsStatus, err.message || "Error exportant la cau", "error");
  } finally {
    if (cacheExportBtn) cacheExportBtn.disabled = !cacheSongSelect?.value;
  }
}

async function importCacheZip(file) {
  if (!file) return;
  if (cacheImportBtn) cacheImportBtn.disabled = true;
  setSettingsStatus(cacheSettingsStatus, "Important la memòria cau…", "running");
  try {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch("/api/cache/import", { method: "POST", body });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload?.detail || "Error important la cau");
    }
    const meta = payload.meta || {};
    const label = [meta.artist, meta.title].filter(Boolean).join(" — ") || payload.key || "cançó";
    setSettingsStatus(cacheSettingsStatus, `Importat · ${label}`, "ok");
    await refreshSelectedCacheStatus();
    loadLibrary().catch(() => {});
  } catch (err) {
    setSettingsStatus(cacheSettingsStatus, err.message || "Error important la cau", "error");
  } finally {
    if (cacheImportBtn) cacheImportBtn.disabled = false;
    if (cacheImportFile) cacheImportFile.value = "";
  }
}

async function runCacheAction(kind) {
  const trackId = cacheSongSelect?.value;
  if (!trackId) return;
  const scopes = selectedCacheScopes();
  if (!scopes.length) {
    setSettingsStatus(cacheSettingsStatus, "Selecciona almenys una part de la cau", "error");
    return;
  }
  if (cacheClearBtn) cacheClearBtn.disabled = true;
  if (cacheResyncBtn) cacheResyncBtn.disabled = true;
  if (cacheExportBtn) cacheExportBtn.disabled = true;
  const label =
    kind === "resync"
      ? "Resincronitzant la memòria cau…"
      : "Esborrant la memòria cau…";
  setSettingsStatus(cacheSettingsStatus, label, "running");
  try {
    const path = kind === "resync" ? "/api/cache/resync" : "/api/cache/clear";
    const result = await api(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_id: trackId, scopes, language: "ca" }),
    });
    renderCacheFlags(result.cache);
    const total = result.total || 0;
    if (kind === "resync") {
      const jobId = result.align?.job_id;
      const track = allLibraryTracks().find((item) => item.id === trackId);
      if (track) track.whisper_aligned = false;
      if (jobId) {
        setSettingsStatus(
          cacheSettingsStatus,
          `Cau netejada (${total}) · resincronitzant amb Whisper…`,
          "running"
        );
        syncActiveId = trackId;
        syncProgress = 0;
        syncPhase = "queued";
        updateSyncQueueMeta();
        try {
          await waitAlignJob(jobId);
          markTrackAligned(trackId);
          setSettingsStatus(cacheSettingsStatus, "Resincronització Whisper enllestida", "ok");
          await refreshSelectedCacheStatus();
        } catch (err) {
          setSettingsStatus(
            cacheSettingsStatus,
            err.message || "Resincronització Whisper fallida",
            "error"
          );
        } finally {
          syncActiveId = null;
          syncProgress = 0;
          syncPhase = "";
          updateSyncQueueMeta();
        }
      } else {
        setSettingsStatus(
          cacheSettingsStatus,
          `Cau netejada (${total}) · tornant a buscar lletres`,
          "ok"
        );
      }
    } else {
      setSettingsStatus(
        cacheSettingsStatus,
        total ? `S’han esborrat ${total} fitxers de cau` : "No hi havia res a la cau",
        total ? "ok" : ""
      );
      const track = allLibraryTracks().find((item) => item.id === trackId);
      if (track && scopes.includes("aligned")) track.whisper_aligned = false;
    }
    loadLibrary().catch(() => {});
  } catch (err) {
    setSettingsStatus(cacheSettingsStatus, err.message || "Error amb la memòria cau", "error");
  } finally {
    const has = !!cacheSongSelect?.value;
    if (cacheClearBtn) cacheClearBtn.disabled = !has;
    if (cacheResyncBtn) cacheResyncBtn.disabled = !has;
    if (cacheExportBtn) cacheExportBtn.disabled = !has;
  }
}

function formatWhisperStatus(whisper) {
  if (!whisper || typeof whisper !== "object") {
    return { text: "Model Whisper: desconegut", kind: "" };
  }
  const model = whisper.model || whisper.configured_model || "?";
  const device = whisper.device || whisper.configured_device || "?";
  const compute = whisper.compute || whisper.configured_compute || "";
  const bits = [`Model Whisper: ${model}`, device];
  if (compute) bits.push(compute);
  if (whisper.loading) {
    return { text: `${bits.join(" · ")} · baixant/carregant…`, kind: "running" };
  }
  if (whisper.error && !whisper.ready) {
    return { text: `${bits.join(" · ")} · error: ${whisper.error}`, kind: "error" };
  }
  if (whisper.ready) {
    return { text: `${bits.join(" · ")} · a punt`, kind: "ok" };
  }
  return { text: `${bits.join(" · ")} · pendent de carregar`, kind: "" };
}

function renderWhisperStatus(whisper) {
  const el = whisperModelStatus || document.getElementById("whisperModelStatus");
  if (!el) return;
  const { text, kind } = formatWhisperStatus(whisper);
  el.textContent = text;
  el.classList.toggle("is-ok", kind === "ok");
  el.classList.toggle("is-running", kind === "running");
  el.classList.toggle("is-error", kind === "error");
}

let whisperStatusTimer = null;

async function refreshWhisperStatus({ pollWhileLoading = false } = {}) {
  const el = whisperModelStatus || document.getElementById("whisperModelStatus");
  if (!el) return;
  el.textContent = "Model Whisper: consultant…";
  el.classList.remove("is-ok", "is-error");
  el.classList.add("is-running");
  try {
    // Dedicated endpoint: /api/health also runs a slow GPU diagnose and used to
    // leave the label stuck on "comprovant…" for a long time.
    const whisper = await api("/api/whisper");
    renderWhisperStatus(whisper || {});
    if (pollWhileLoading && whisper?.loading) {
      if (whisperStatusTimer) clearTimeout(whisperStatusTimer);
      whisperStatusTimer = setTimeout(() => {
        refreshWhisperStatus({ pollWhileLoading: true }).catch(() => {});
      }, 2000);
    } else if (whisperStatusTimer) {
      clearTimeout(whisperStatusTimer);
      whisperStatusTimer = null;
    }
  } catch (err) {
    renderWhisperStatus({
      ready: false,
      loading: false,
      error: err.message || "No s’ha pogut consultar l’estat",
      model: "?",
    });
  }
}

function openSettings(sectionId = "general") {
  if (!settingsModal) return;
  showSettingsSection(sectionId);
  settingsModal.hidden = false;
  settingsModal.classList.remove("hidden");
  settingsBtn?.setAttribute("aria-expanded", "true");
  (settingsCloseBtn || settingsModal).focus();
  refreshWhisperStatus({ pollWhileLoading: true }).catch(() => {});
}

function closeSettings() {
  if (!settingsModal || !isSettingsOpen()) return;
  settingsModal.classList.add("hidden");
  settingsModal.hidden = true;
  settingsBtn?.setAttribute("aria-expanded", "false");
  settingsBtn?.focus();
}

settingsBtn?.addEventListener("click", () => {
  if (isSettingsOpen()) closeSettings();
  else openSettings("general");
});
settingsModal?.addEventListener("click", (event) => {
  if (event.target?.hasAttribute?.("data-settings-close")) closeSettings();
});
settingsModal?.querySelectorAll(".settings-nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => showSettingsSection(btn.dataset.settingsSection));
});
cacheSongSearch?.addEventListener("input", () => {
  fillCacheSongSelect();
  refreshSelectedCacheStatus();
});
cacheSongSelect?.addEventListener("change", () => refreshSelectedCacheStatus());
cacheClearBtn?.addEventListener("click", () => runCacheAction("clear"));
cacheResyncBtn?.addEventListener("click", () => runCacheAction("resync"));
cacheClearAllBtn?.addEventListener("click", () => clearAllCache());
cacheExportBtn?.addEventListener("click", () => exportSelectedCache());
cacheImportBtn?.addEventListener("click", () => cacheImportFile?.click());
cacheImportFile?.addEventListener("change", () => {
  const file = cacheImportFile.files?.[0];
  if (file) importCacheZip(file);
});
libraryBrowseSongBtn?.addEventListener("click", () => setLibraryBrowseMode("song"));
libraryBrowseAlbumBtn?.addEventListener("click", () => setLibraryBrowseMode("album"));
lyricsFilterLyricsBtn?.addEventListener("click", () => setLyricsFilterMode("lyrics"));
lyricsFilterHiddenBtn?.addEventListener("click", () => setLyricsFilterMode("hidden"));
lyricsFilterAllBtn?.addEventListener("click", () => setLyricsFilterMode("all"));
muteOffBtn?.addEventListener("click", () => setAudioMuted(false));
muteOnBtn?.addEventListener("click", () => setAudioMuted(true));
lyricsLayoutStackBtn?.addEventListener("click", () => setLyricsLayout("stack"));
lyricsLayoutDualBtn?.addEventListener("click", () => setLyricsLayout("dual"));
auraParticlesOnBtn?.addEventListener("click", () => setAuraParticlesEnabled(true));
auraParticlesOffBtn?.addEventListener("click", () => setAuraParticlesEnabled(false));
audioModeOriginalBtn?.addEventListener("click", () => setAudioMode("original"));
audioModeInstrumentalBtn?.addEventListener("click", () => setAudioMode("instrumental"));
videoModeOnBtn?.addEventListener("click", () => setStageBgMode("video"));
videoModeCoverBtn?.addEventListener("click", () => setStageBgMode("cover"));
videoModeAuraBtn?.addEventListener("click", () => setStageBgMode("aura"));
videoModeOffBtn?.addEventListener("click", () => setStageBgMode("stage"));
generateStemsBtn?.addEventListener("click", () => startStemsGeneration());
searchYoutubeMissingBtn?.addEventListener("click", () => startYoutubeSearch("missing"));
searchYoutubeAllBtn?.addEventListener("click", () => startYoutubeSearch("all"));
albumBackBtn?.addEventListener("click", () => closeAlbum());
applyLyricsFilterMode();
applyLibraryBrowseMode();
applyAudioMute();
applyLyricsLayout();
applyAuraParticles();
applyAudioModeButtons();
applyVideoModeButtons();

pasteLyricsBtn?.addEventListener("click", () => openLyricsPasteModal());
stagePasteLyricsBtn?.addEventListener("click", () => openLyricsPasteModal(currentId));
lyricsPasteModal?.addEventListener("click", (event) => {
  if (event.target?.hasAttribute?.("data-lyrics-paste-close")) closeLyricsPasteModal();
});
lyricsPasteCloseBtn?.addEventListener("click", () => closeLyricsPasteModal());
lyricsPasteCancelBtn?.addEventListener("click", () => closeLyricsPasteModal());
lyricsPasteSaveBtn?.addEventListener("click", () => {
  savePastedLyrics().catch(() => {});
});
singBtn.addEventListener("click", () => {
  activateSelectedTrack();
});
coverTrack.addEventListener(
  "wheel",
  (event) => {
    if (browseMode !== "cover") return;
    if (!browseList().length || viewMenu.classList.contains("hidden")) return;
    event.preventDefault();
    if (Math.abs(event.deltaY) < 2 && Math.abs(event.deltaX) < 2) return;
    const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
    setSelectedIndex(selectedIndex + (delta > 0 ? 1 : -1));
  },
  { passive: false }
);
window.addEventListener(
  "keydown",
  (event) => {
    if (isLyricsPasteOpen()) {
      if (event.key === "Escape") {
        event.preventDefault();
        closeLyricsPasteModal();
      } else if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        savePastedLyrics().catch(() => {});
      }
      return;
    }
    if (event.key === "Escape" && isSettingsOpen()) {
      event.preventDefault();
      closeSettings();
      return;
    }
    if (event.key === "Escape" && openedAlbum && !viewMenu.classList.contains("hidden")) {
      event.preventDefault();
      closeAlbum();
      return;
    }
    if (isLandingVisible()) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        enterFromLanding();
      }
      return;
    }
    if (isLyricsPasteOpen() || isSettingsOpen()) return;
    if (viewMenu.classList.contains("hidden")) return;
    if (!browseList().length) return;

    const key = event.key;
    if (key === "ArrowLeft" || key === "Left") {
      event.preventDefault();
      setSelectedIndex(selectedIndex - 1);
      return;
    }
    if (key === "ArrowRight" || key === "Right") {
      event.preventDefault();
      setSelectedIndex(selectedIndex + 1);
      return;
    }
    if (key === "ArrowUp" || key === "Up") {
      if (browseMode !== "grid") return;
      event.preventDefault();
      setSelectedIndex(selectedIndex - gridColumnCount());
      return;
    }
    if (key === "ArrowDown" || key === "Down") {
      if (browseMode !== "grid") return;
      event.preventDefault();
      setSelectedIndex(selectedIndex + gridColumnCount());
      return;
    }

    const inField = event.target && ["INPUT", "TEXTAREA"].includes(event.target.tagName);
    if (inField) return;

    if (key === "Enter") {
      event.preventDefault();
      activateSelectedTrack();
    }
  },
  true
);
function onPreviewEnded(event) {
  if (event.target !== previewPlayers[previewActive]) return;
  if (viewMenu.classList.contains("hidden") || !browseList().length) return;
  setSelectedIndex(selectedIndex + 1);
}
previewPlayers.forEach((el) => el.addEventListener("ended", onPreviewEnded));
playBtn.addEventListener("click", () => {
  togglePlayback().catch(() => updatePlayButton());
});
player.addEventListener("play", () => {
  startTicker();
  updatePlayButton();
  syncYoutubeToAudio();
});
player.addEventListener("playing", () => {
  startTicker();
  updatePlayButton();
  syncYoutubeToAudio();
});
player.addEventListener("pause", () => {
  syncKaraoke();
  updatePlayButton();
  syncYoutubeToAudio();
});
player.addEventListener("seeked", () => {
  syncYoutubeToAudio();
});
player.addEventListener("ended", () => {
  syncWordFills(Number.POSITIVE_INFINITY);
  beginStageOutro();
});

titleStartForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  enterLibraryFromTitle();
});
landingEnterBtn?.addEventListener("click", () => {
  enterFromLanding();
});
titleBrowseBtn?.addEventListener("click", () => {
  pickFolderInto(titleRootInput, { statusEl: "title" });
});
browseRootBtn?.addEventListener("click", () => {
  pickFolderInto(rootInput, { statusEl: "settings" });
});

bootTitleScreen();
startTicker();
