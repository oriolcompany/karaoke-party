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
const approachEl = document.getElementById("kApproach");
const songTitle = document.getElementById("songTitle");
const songArtist = document.getElementById("songArtist");
const lyricsStatus = document.getElementById("lyricsStatus");
const libraryMeta = document.getElementById("libraryMeta");
const playBtn = document.getElementById("playBtn");
const coverArtist = document.getElementById("coverArtist");
const coverTitle = document.getElementById("coverTitle");
const coverIndex = document.getElementById("coverIndex");
const songRating = document.getElementById("songRating");
const coverPrev = document.getElementById("coverPrev");
const coverNext = document.getElementById("coverNext");
const singBtn = document.getElementById("singBtn");
const exportVideoBtn = document.getElementById("exportVideoBtn");
const exportVideoStatus = document.getElementById("exportVideoStatus");
// const exportCaptureBadge = document.getElementById("exportCaptureBadge");
// const exportOverlay = document.getElementById("exportOverlay");
// const exportOverlayDetail = document.getElementById("exportOverlayDetail");
// const exportCancelBtn = document.getElementById("exportCancelBtn");
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
const ratingFilterToggle = document.getElementById("ratingFilterToggle");
const muteOffBtn = document.getElementById("muteOffBtn");
const muteOnBtn = document.getElementById("muteOnBtn");
const lyricsLayoutStackBtn = document.getElementById("lyricsLayoutStackBtn");
const lyricsLayoutDualBtn = document.getElementById("lyricsLayoutDualBtn");
const lyricsSizeToggle = document.getElementById("lyricsSizeToggle");
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
const RATING_FILTER_KEY = "karaoke-rating-filter";
const LYRICS_LAYOUT_KEY = "karaoke-lyrics-layout";
const LYRICS_SIZE_KEY = "karaoke-lyrics-size";
const LYRICS_SIZE_BUMPS = { small: "-2pt", normal: "0pt", large: "2pt", xlarge: "4pt" };
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

function loadLyricsSize() {
  const stored = localStorage.getItem(LYRICS_SIZE_KEY);
  return stored && stored in LYRICS_SIZE_BUMPS ? stored : "normal";
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

function loadRatingFilterMode() {
  const stored = localStorage.getItem(RATING_FILTER_KEY);
  if (stored === "all" || stored === "none") return stored;
  const n = Number(stored);
  if (n >= 1 && n <= 5) return n;
  return "all";
}

const ICON_SYNCED =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.2 16.6 5.4 12.8l1.4-1.4 2.4 2.4 7-7 1.4 1.4z"/></svg>`;
const ICON_CLOCK =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zm0 2a6 6 0 1 1 0 12 6 6 0 0 1 0-12zm-.8 2.5h1.6v4.2l3.2 1.9-.8 1.3-4-2.4V8.5z"/></svg>`;
const ICON_QUEUE =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 6h16v2H4zm0 5h16v2H4zm0 5h10v2H4z"/></svg>`;
const ICON_RUNNING =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 14h2v4H4zm3.5-4h2v8h-2zm3.5-5h2v13h-2zm3.5 3h2v10h-2zm3.5 2h2v8h-2z"/></svg>`;
const ICON_STAR =
  `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.8 14.8 9l6.7.6-5.1 4.4 1.6 6.6L12 17.2 6 20.6l1.6-6.6L2.5 9.6 9.2 9z"/></svg>`;

function clampRating(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(5, Math.round(n)));
}

function ratingLabel(rating) {
  const value = clampRating(rating);
  if (!value) return "Sense puntuació";
  return `${value} de 5 estrelles`;
}

function findTrackById(trackId) {
  if (!trackId) return null;
  return (
    tracks.find((item) => item.id === trackId) ||
    playableTracks.find((item) => item.id === trackId) ||
    hiddenTracks.find((item) => item.id === trackId) ||
    pendingTracks.find((item) => item.id === trackId) ||
    null
  );
}

function paintRatingWidget(root, rating) {
  if (!root) return;
  const value = clampRating(rating);
  root.dataset.rating = String(value);
  root.querySelectorAll(".rating-star").forEach((btn) => {
    const n = Number(btn.dataset.value);
    const on = n <= value;
    btn.classList.toggle("is-on", on);
    btn.setAttribute("aria-pressed", n === value && value > 0 ? "true" : "false");
    btn.title = n === value && value ? "Treure puntuació" : `${n} estrella${n === 1 ? "" : "es"}`;
  });
  root.setAttribute("aria-label", `Puntuació: ${ratingLabel(value)}`);
}

function previewRatingWidget(root, hover) {
  if (!root) return;
  root.querySelectorAll(".rating-star").forEach((btn) => {
    btn.classList.toggle("is-on", Number(btn.dataset.value) <= hover);
  });
}

function fillRatingWidget(root, { compact = false, asButtons = true } = {}) {
  if (!root || root.dataset.ready === "1") return root;
  root.dataset.ready = "1";
  root.classList.toggle("is-compact", compact);
  root.replaceChildren();
  for (let n = 1; n <= 5; n += 1) {
    const btn = document.createElement(asButtons ? "button" : "span");
    if (asButtons) btn.type = "button";
    else {
      btn.setAttribute("role", "button");
      btn.tabIndex = 0;
    }
    btn.className = "rating-star";
    btn.dataset.value = String(n);
    btn.innerHTML = ICON_STAR;
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const trackId = root.dataset.trackId;
      if (!trackId) return;
      const current = clampRating(root.dataset.rating);
      setTrackRating(trackId, current === n ? 0 : n);
    });
    btn.addEventListener("mouseenter", () => previewRatingWidget(root, n));
    btn.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      event.stopPropagation();
      btn.click();
    });
    root.appendChild(btn);
  }
  root.addEventListener("mouseleave", () => {
    paintRatingWidget(root, root.dataset.rating);
  });
  return root;
}

function bindRatingWidget(root, track, { compact = false, asButtons = true } = {}) {
  if (!root) return;
  fillRatingWidget(root, { compact, asButtons });
  if (!track?.id) {
    root.hidden = true;
    root.dataset.trackId = "";
    paintRatingWidget(root, 0);
    return;
  }
  root.hidden = false;
  root.dataset.trackId = track.id;
  paintRatingWidget(root, track.rating);
}

function applyTrackRating(trackId, rating) {
  const value = clampRating(rating);
  for (const list of [playableTracks, hiddenTracks, pendingTracks, tracks]) {
    const track = list.find((item) => item.id === trackId);
    if (track) track.rating = value;
  }
  document.querySelectorAll(".song-rating[data-track-id]").forEach((el) => {
    if (el.dataset.trackId === trackId) paintRatingWidget(el, value);
  });
  if (ratingFilterMode === "all") return;
  const previousId = selectedTrack()?.id;
  applyLyricsFilterMode();
  renderSongs(searchEl?.value || "", { play: false });
  if (previousId) {
    const idx = findBrowseIndexByTrackId(previousId);
    if (idx >= 0) {
      selectedIndex = idx;
      layoutCovers();
      layoutGridSelection();
      updateCoverMeta();
    }
  }
  refreshLibraryMetaLabel();
}

async function setTrackRating(trackId, rating) {
  const previous = clampRating(findTrackById(trackId)?.rating);
  const value = clampRating(rating);
  applyTrackRating(trackId, value);
  try {
    const result = await api("/api/rating", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track_id: trackId, rating: value }),
    });
    applyTrackRating(trackId, result.rating);
  } catch {
    applyTrackRating(trackId, previous);
  }
}

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
let ratingFilterMode = loadRatingFilterMode();
let audioMuted = localStorage.getItem(MUTE_KEY) === "1";
let lyricsLayout = loadLyricsLayout();
let lyricsSize = loadLyricsSize();
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
/** Stack view: next phrase is held back until shortly before it is sung. */
let stackPending = false;
let restHoldActive = false;
let restLeadInActive = false;
let restFadeTimer = null;
/** False until the new audio element reports a real playhead (avoids stale time from the previous song). */
let audioClockReady = false;
/** Hold the next phrase when the rest after this line is longer than a breath. */
const UPCOMING_REST_GAP = 5;
/** Seconds before the next phrase starts to bring it on screen. */
const UPCOMING_LEAD_IN = 3;
const REST_FADE_MS = 750;
let rafId = 0;
let alignPollTimer = 0;
let alignToken = 0;
let exportVideoBusy = false;
let exportVideoTrackId = "";
let stageCapture = null;
const EXPORT_VIDEO_W = 1920;
const EXPORT_VIDEO_H = 1080;
const EXPORT_VIDEO_FPS = 30;
// Keep in sync with INTRO_SECONDS / OUTRO_SECONDS in video.py.
const EXPORT_INTRO_SECONDS = 5;
const EXPORT_OUTRO_SECONDS = 8;
// 1:1 with the output frame: supersampling the aura cost four times the fill
// work and bought nothing once the video was scaled back down to 1080p.
const EXPORT_AURA_DPR = 1;
const EXPORT_VIDEO_BITRATE = 24_000_000;
const EXPORT_QUEUE_LIMIT = 48;
const EXPORT_ENCODER_STALLED = "El codificador de vídeo s’ha encallat";
const EXPORT_CODECS = [
  "avc1.640029",
  "avc1.64002a",
  "avc1.640028",
  "avc1.4d0029",
  "avc1.42002a",
];
/** Virtual export clock in seconds; null while the stage runs in real time. */
let exportClock = null;
let exportAborted = false;
const exportTimers = [];
const exportAnimationStarts = new WeakMap();
/** @type {object[]} */
const videoQueue = [];
const videoQueuedIds = new Set();
let videoQueueDone = 0;
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
  if (exportClock !== null) return;
  if (stageCapture && !stageCapture.aborted) {
    abortStageCapture("S’ha cancel·lat la gravació");
  }
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

function applyLyricsSize() {
  lyricsEl?.style.setProperty("--k-lyrics-bump", LYRICS_SIZE_BUMPS[lyricsSize] || "0pt");
  lyricsSizeToggle?.querySelectorAll("[data-lyrics-size]").forEach((btn) => {
    const on = btn.getAttribute("data-lyrics-size") === lyricsSize;
    btn.classList.toggle("is-active", on);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
  });
  approachInkCache = null;
}

function setLyricsSize(size) {
  lyricsSize = size in LYRICS_SIZE_BUMPS ? size : "normal";
  localStorage.setItem(LYRICS_SIZE_KEY, lyricsSize);
  applyLyricsSize();
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
let auraLastTs = 0;

function auraReduceMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function auraLive() {
  // The offline export never plays the audio, so the stage is always "singing".
  if (exportClock !== null) return true;
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
  if (document.body.classList.contains("is-exporting-video")) {
    auraDpr = EXPORT_AURA_DPR;
    auraW = EXPORT_VIDEO_W;
    auraH = EXPORT_VIDEO_H;
  } else {
    const rect = stageAuraEl.getBoundingClientRect();
    auraDpr = Math.min(window.devicePixelRatio || 1, 1.5);
    auraW = Math.max(1, Math.floor(rect.width));
    auraH = Math.max(1, Math.floor(rect.height));
  }
  stageAuraCanvas.width = Math.floor(auraW * auraDpr);
  stageAuraCanvas.height = Math.floor(auraH * auraDpr);
  auraCtx = stageAuraCanvas.getContext("2d", { alpha: false });
  if (auraCtx) auraCtx.setTransform(auraDpr, 0, 0, auraDpr, 0, 0);
}

function drawAuraRibbon(t, spec, live, glow) {
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
  auraCtx.strokeStyle = `rgba(${r},${g},${b},${(live ? 0.28 : 0.18) * glow})`;
  auraCtx.lineWidth = spec.width * (live ? 1.25 : 1);
  auraCtx.lineCap = "round";
  auraCtx.stroke();
}

function drawAuraFrame(ts) {
  if (!auraCtx || !auraW) return;
  const t = (ts - auraT0) / 1000;
  // Live, drift and trails advance once per animation frame, as they always have.
  // The export walks a virtual clock in 30 fps steps, so only there we scale by
  // elapsed time to keep the aura moving at the speed of a 60 Hz stage.
  const frameMs = 1000 / 60;
  const elapsed = auraLastTs ? Math.min(Math.max(ts - auraLastTs, 1), 100) : frameMs;
  auraLastTs = ts;
  const step = exportClock === null ? 1 : elapsed / frameMs;
  const live = auraLive();
  // Trails fade a fixed fraction per tick; brightness settles at stroke/fade.
  // Export ticks at 30 fps with a stronger fade so motion stays at 60 Hz, which
  // would leave the glow at ~56% of the live stage. Boost the additive stroke
  // by the same ratio instead of ticking twice (that path flickered).
  const trailKeep = 0.78;
  const fade = 1 - trailKeep ** step;
  const glow = fade / (1 - trailKeep);
  auraCtx.globalCompositeOperation = "source-over";
  auraCtx.fillStyle = `rgba(3, 2, 8, ${fade.toFixed(4)})`;
  auraCtx.fillRect(0, 0, auraW, auraH);

  auraCtx.globalCompositeOperation = "lighter";
  for (const spec of AURA_RIBBONS) drawAuraRibbon(t, spec, live, glow);

  if (!auraParticlesEnabled) return;

  const palette = [
    [255, 45, 106],
    [255, 225, 74],
    [61, 231, 255],
  ];
  for (const p of auraParticles) {
    p.x += (p.vx * (live ? 1.8 : 1) + Math.sin(t * 0.6 + p.y * 12) * 0.00012) * step;
    p.y += p.vy * (live ? 1.6 : 1) * step;
    if (p.y < -0.04) p.y = 1.04;
    if (p.x < -0.04) p.x = 1.04;
    if (p.x > 1.04) p.x = -0.04;
    const [r, g, b] = palette[p.hue];
    const s = (live ? 2.0 : 1.4) * p.z;
    auraCtx.fillStyle = `rgba(${r},${g},${b},${(0.12 + p.z * 0.32) * glow})`;
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
  auraLastTs = 0;
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
  if (document.body.classList.contains("is-exporting-video")) {
    resizeAuraCanvas();
    return;
  }
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

function setStageBgMode(mode, { persist = true } = {}) {
  if (mode === "video" && !youtubeVideoReady()) return;
  stageBgMode = STAGE_BG_MODES.has(mode) ? mode : "stage";
  if (persist) localStorage.setItem(STAGE_BG_KEY, stageBgMode);
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

function trackMatchesRatingFilter(track) {
  const rating = clampRating(track?.rating);
  if (ratingFilterMode === "all") return true;
  if (ratingFilterMode === "none") return rating === 0;
  return rating >= ratingFilterMode;
}

function tracksForLibraryFilters() {
  return tracksForLyricsFilter().filter(trackMatchesRatingFilter);
}

function ratingFilterLabel() {
  if (ratingFilterMode === "none") return "sense puntuació";
  if (typeof ratingFilterMode === "number") {
    return ratingFilterMode === 5 ? "5 estrelles" : `${ratingFilterMode}+ estrelles`;
  }
  return "";
}

function applyRatingFilterMode() {
  const mode = String(ratingFilterMode);
  ratingFilterToggle?.querySelectorAll("[data-rating-filter]").forEach((btn) => {
    const active = btn.dataset.ratingFilter === mode;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });
  if (browsePanel) browsePanel.dataset.ratingFilter = mode;
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
  applyRatingFilterMode();
  tracks = tracksForLibraryFilters();
}

function setRatingFilterMode(mode) {
  if (mode === "all" || mode === "none") {
    ratingFilterMode = mode;
  } else {
    const n = Number(mode);
    ratingFilterMode = n >= 1 && n <= 5 ? n : "all";
  }
  localStorage.setItem(RATING_FILTER_KEY, String(ratingFilterMode));
  openedAlbum = null;
  selectedIndex = 0;
  applyLyricsFilterMode();
  applyLibraryBrowseMode();
  renderSongs(searchEl.value, { play: false });
  refreshLibraryMetaLabel();
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
    bindRatingWidget(songRating, null);
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
    bindRatingWidget(songRating, null);
    resyncCoverBtn.hidden = true;
  } else {
    coverArtist.textContent = openedAlbum
      ? openedAlbum.album || item.album || "Àlbum"
      : item.artist || "Artista desconegut";
    coverTitle.textContent = item.title || item.relpath;
    coverIndex.textContent = openedAlbum
      ? `${selectedIndex + 1}/${list.length} · ${item.artist || ""}`
      : `${selectedIndex + 1}/${list.length}`;
    bindRatingWidget(songRating, item);
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
  updateExportVideoButton();
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

function setExportVideoStatus(text, kind) {
  if (!exportVideoStatus) return;
  if (!text) {
    exportVideoStatus.hidden = true;
    exportVideoStatus.textContent = "";
    exportVideoStatus.removeAttribute("data-kind");
    return;
  }
  exportVideoStatus.hidden = false;
  exportVideoStatus.textContent = text;
  if (kind) exportVideoStatus.dataset.kind = kind;
  else exportVideoStatus.removeAttribute("data-kind");
}

function updateExportVideoButton() {
  if (!exportVideoBtn) return;
  const album = isAlbumListView();
  const track = album ? null : selectedTrack();
  exportVideoBtn.hidden = album || !track;
  exportVideoBtn.classList.toggle("is-busy", exportVideoBusy);
  if (!track) {
    exportVideoBtn.disabled = true;
    exportVideoBtn.textContent = "Desar vídeo";
    return;
  }
  if (track.has_lyrics === false && !track.lyrics_pending) {
    exportVideoBtn.disabled = true;
    exportVideoBtn.textContent = "Desar vídeo";
    exportVideoBtn.title = "Cal lletra per crear el vídeo karaoke";
    return;
  }
  const pending = videoQueue.length + (exportVideoTrackId ? 1 : 0);
  exportVideoBtn.disabled = false;
  if (exportVideoTrackId === track.id) {
    exportVideoBtn.textContent = "Aturar vídeo";
    exportVideoBtn.title = "Atura la creació d’aquest vídeo i la resta de la cua";
    return;
  }
  if (videoQueuedIds.has(track.id)) {
    exportVideoBtn.textContent = "Treure de la cua";
    exportVideoBtn.title = "Aquesta cançó ja espera torn";
    return;
  }
  exportVideoBtn.textContent = pending ? `Desar vídeo (+${pending})` : "Desar vídeo";
  exportVideoBtn.title = exportVideoBusy
    ? "Els vídeos es creen un darrere l’altre en segon pla"
    : "Sincronitza la lletra si cal i desa un MP4 de l’escenari karaoke";
}

function videoPhaseLabel(phase, progress, stemPhase) {
  if (phase === "render") {
    const pct =
      typeof progress === "number" && progress > 0 ? ` ${Math.round(progress * 100)}%` : "";
    return `Creant el vídeo${pct}`;
  }
  if (phase === "capture") return "Gravant l’escenari";
  const sync = syncPhaseLabel(phase, stemPhase);
  if (sync) return `Sincronitzant · ${sync}`;
  if (phase === "done") return "Vídeo a punt";
  if (phase === "ready") return "Escenari a punt";
  return "Preparant el vídeo…";
}

async function downloadVideoFile(job) {
  const jobId = job.job_id;
  const response = await fetch(`/api/video/${encodeURIComponent(jobId)}/file`);
  if (!response.ok) {
    let detail = "No s’ha pogut descarregar el vídeo";
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
  const name = match
    ? decodeURIComponent(match[1].replace(/"/g, ""))
    : job.filename || "karaoke.mp4";
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  return name;
}

async function waitVideoJob(jobId) {
  const started = Date.now();
  const maxMs = 40 * 60 * 1000;
  let marked = false;
  for (;;) {
    if (Date.now() - started > maxMs) {
      throw new Error("La creació del vídeo ha trigat massa");
    }
    const job = await api(`/api/video/${encodeURIComponent(jobId)}`);
    const track =
      allLibraryTracks().find((t) => t.id === exportVideoTrackId) ||
      tracks.find((t) => t.id === exportVideoTrackId);
    if (!marked && (job.status === "ready" || job.status === "done")) {
      marked = true;
      if (exportVideoTrackId) markTrackAligned(exportVideoTrackId);
    }
    setExportVideoStatus(
      `${trackLabel(track) || "Cançó"} · ${videoPhaseLabel(job.phase, job.progress, job.stem_phase)}`,
      "running"
    );
    if (job.status === "done" || job.status === "ready") return job;
    if (job.status === "error" || job.status === "unavailable") {
      throw new Error(job.error || "No s’ha pogut crear el vídeo");
    }
    await new Promise((resolve) => setTimeout(resolve, 1200));
  }
}

function setExportCaptureBadge(_text, _detail = "") {
  // Overlay paused: progress stays on #exportVideoStatus under the cover buttons.
  // if (exportOverlay) exportOverlay.hidden = !_text;
  // if (exportCaptureBadge) exportCaptureBadge.textContent = _text || "Preparant…";
  // if (exportOverlayDetail) exportOverlayDetail.textContent = _text ? _detail : "";
}

function waitAnimationFrames(count) {
  return new Promise((resolve) => {
    const step = () => {
      if (count <= 1) {
        resolve();
        return;
      }
      count -= 1;
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
}

async function waitForLyricsAligned(timeoutMs = 180000) {
  const started = Date.now();
  while (!lyricsAligned) {
    if (!currentId) throw new Error("S’ha sortit de l’escenari");
    if (Date.now() - started > timeoutMs) {
      throw new Error("La sincronització no ha acabat");
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
}

async function waitForPlayerReady(timeoutMs = 20000) {
  if (player.readyState >= 2) return;
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("L’àudio no s’ha carregat")), timeoutMs);
    const done = () => {
      clearTimeout(timer);
      player.removeEventListener("canplay", done);
      resolve();
    };
    player.addEventListener("canplay", done);
  });
}

function exportRecorderMime() {
  const types = [
    "video/webm;codecs=h264",
    "video/mp4;codecs=avc1",
    "video/mp4",
    "video/webm;codecs=vp9",
    "video/webm;codecs=vp8",
    "video/webm",
  ];
  return types.find((type) => window.MediaRecorder?.isTypeSupported?.(type)) || "";
}

function makeExportGrainTile() {
  const tile = document.createElement("canvas");
  tile.width = 140;
  tile.height = 140;
  const grain = tile.getContext("2d");
  const pixels = grain.createImageData(140, 140);
  for (let i = 0; i < pixels.data.length; i += 4) {
    const on = Math.random() < 0.22;
    const n = 234 + Math.random() * 21;
    pixels.data[i] = n;
    pixels.data[i + 1] = n * 0.96;
    pixels.data[i + 2] = n * 0.9;
    pixels.data[i + 3] = on ? 40 : 0;
  }
  grain.putImageData(pixels, 0, 0);
  return tile;
}

function canvasFontFrom(style) {
  return `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
}

function applyCanvasLetterSpacing(ctx, style) {
  if (typeof ctx.letterSpacing === "string") {
    ctx.letterSpacing = style.letterSpacing || "0px";
  }
}

function transformedElementText(el, style) {
  let text = el.textContent || "";
  if (style.textTransform === "uppercase") return text.toLocaleUpperCase("ca");
  if (style.textTransform === "lowercase") return text.toLocaleLowerCase("ca");
  return text;
}

function elementOpacity(el) {
  let opacity = 1;
  let node = el;
  while (node && node !== document.body) {
    const style = getComputedStyle(node);
    if (style.display === "none" || style.visibility === "hidden") return 0;
    opacity *= Number(style.opacity);
    if (node === viewStage) break;
    node = node.parentElement;
  }
  return opacity;
}

const EXPORT_TEXT_SHADOWS = [
  { x: 0, y: 1, blur: 0, color: "rgba(0,0,0,0.7)" },
  { x: 0, y: 2, blur: 8, color: "rgba(0,0,0,0.85)" },
  { x: 0, y: 0, blur: 18, color: "rgba(0,0,0,0.8)" },
  { x: 0, y: 0, blur: 36, color: "rgba(0,0,0,0.55)" },
];

function drawShadowedText(ctx, text, x, y, fill, withAuraShadow) {
  if (withAuraShadow) {
    for (const layer of EXPORT_TEXT_SHADOWS) {
      ctx.shadowOffsetX = layer.x;
      ctx.shadowOffsetY = layer.y;
      ctx.shadowBlur = layer.blur;
      ctx.shadowColor = layer.color;
      ctx.fillStyle = fill;
      ctx.fillText(text, x, y);
    }
  }
  ctx.shadowColor = "transparent";
  ctx.shadowBlur = 0;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;
  ctx.fillStyle = fill;
  ctx.fillText(text, x, y);
}

function textClientRect(el) {
  if (!el) return { left: 0, top: 0, width: 0, height: 0 };
  if (!el.firstChild) return el.getBoundingClientRect();
  const range = document.createRange();
  range.selectNodeContents(el);
  const rects = range.getClientRects();
  if (rects.length) return rects[0];
  return range.getBoundingClientRect();
}

function glyphBaseline(ctx, text, glyph) {
  const metrics = ctx.measureText(text);
  return (
    glyph.top +
    (metrics.fontBoundingBoxAscent || metrics.actualBoundingBoxAscent || glyph.height * 0.8)
  );
}

function measuredTextItem(ctx, { text, style, glyph, color, opacity, shadow, clip, fill }) {
  const font = canvasFontFrom(style);
  ctx.font = font;
  applyCanvasLetterSpacing(ctx, style);
  return {
    text,
    font,
    spacing: style.letterSpacing || "0px",
    color,
    opacity,
    shadow,
    clip,
    fill,
    x: glyph.left,
    y: glyphBaseline(ctx, text, glyph),
  };
}

function collectExportElementText(ctx, items, el, { shadow, clip = null }) {
  if (!el) return;
  const opacity = elementOpacity(el);
  if (opacity < 0.02) return;
  const style = getComputedStyle(el);
  const text = transformedElementText(el, style).trim();
  if (!text) return;
  const glyph = textClientRect(el);
  if (glyph.width < 0.5 || glyph.height < 0.5) return;
  items.push(
    measuredTextItem(ctx, {
      text,
      style,
      glyph,
      color: style.color,
      opacity,
      shadow,
      clip,
      fill: null,
    })
  );
}

function collectExportWord(ctx, items, wordEl, { shadow, clip }) {
  const opacity = elementOpacity(wordEl);
  if (opacity < 0.02) return;
  const base = wordEl.querySelector(".k-word-base") || wordEl;
  const style = getComputedStyle(wordEl);
  const baseStyle = getComputedStyle(base);
  const text = (base.textContent || "").trim();
  if (!text) return;
  const glyph = textClientRect(base);
  if (glyph.width < 0.5 || glyph.height < 0.5) return;
  let fill = null;
  const fillEl = wordEl.querySelector(".k-word-fill");
  if (fillEl) {
    const fillStyle = getComputedStyle(fillEl);
    if (fillStyle.display !== "none" && fillStyle.visibility !== "hidden") {
      const rect = fillEl.getBoundingClientRect();
      if (rect.width > 0.5) fill = { rect, color: fillStyle.color };
    }
  }
  items.push(
    measuredTextItem(ctx, {
      text,
      style,
      glyph,
      color: baseStyle.color || style.color,
      opacity,
      shadow,
      clip,
      fill,
    })
  );
}

function collectExportText(ctx) {
  const items = [];
  const shadow = viewStage.classList.contains("has-aura");
  if (lyricsEl) {
    const clip = lyricsEl.getBoundingClientRect();
    lyricsEl
      .querySelectorAll(".k-word")
      .forEach((node) => collectExportWord(ctx, items, node, { shadow, clip }));
    const empty = lyricsEl.querySelector(".lyrics-empty");
    if (empty) collectExportElementText(ctx, items, empty, { shadow: false, clip });
  }
  return items;
}

function clipTextItem(ctx, item) {
  if (!item.clip) return;
  ctx.beginPath();
  ctx.rect(item.clip.left, item.clip.top, item.clip.width, item.clip.height);
  ctx.clip();
}

function prepareTextItem(ctx, item) {
  ctx.globalAlpha = item.opacity;
  ctx.font = item.font;
  if (typeof ctx.letterSpacing === "string") ctx.letterSpacing = item.spacing;
  ctx.textBaseline = "alphabetic";
  ctx.textAlign = "left";
}

/** Everything but the gold fill: the part that only changes when the line does. */
function exportTextSignature(items) {
  let signature = "";
  for (const item of items) {
    signature += `${item.text}|${item.font}|${item.spacing}|${item.color}|${item.shadow ? 1 : 0}`;
    signature += `|${item.opacity.toFixed(3)}|${item.x.toFixed(2)}|${item.y.toFixed(2)}`;
    if (item.clip) {
      signature += `|${item.clip.left.toFixed(1)},${item.clip.top.toFixed(1)}`;
      signature += `,${item.clip.width.toFixed(1)},${item.clip.height.toFixed(1)}`;
    }
    signature += "\n";
  }
  return signature;
}

function drawExportTextLayer(ctx, items) {
  for (const item of items) {
    ctx.save();
    clipTextItem(ctx, item);
    prepareTextItem(ctx, item);
    drawShadowedText(ctx, item.text, item.x, item.y, item.color, item.shadow);
    ctx.restore();
  }
}

function drawExportTextFills(ctx, items) {
  for (const item of items) {
    if (!item.fill) continue;
    ctx.save();
    clipTextItem(ctx, item);
    prepareTextItem(ctx, item);
    ctx.beginPath();
    ctx.rect(item.fill.rect.left, item.fill.rect.top, item.fill.rect.width, item.fill.rect.height);
    ctx.clip();
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
    ctx.fillStyle = item.fill.color;
    ctx.fillText(item.text, item.x, item.y);
    ctx.restore();
  }
}

/**
 * The four blurred shadow passes per word dominate the frame cost, and they only
 * change when the line changes. Keep them in a full resolution layer and blit it
 * back 1:1, so the cached pixels are identical to drawing them again.
 */
function paintExportText(ctx, view) {
  const items = collectExportText(ctx);
  const layer = stageCapture?.textLayer;
  if (!layer) {
    drawExportTextLayer(ctx, items);
    drawExportTextFills(ctx, items);
    return;
  }
  const signature = exportTextSignature(items);
  if (signature !== layer.signature) {
    exportProfile.rebuilds += 1;
    layer.signature = signature;
    layer.ctx.setTransform(1, 0, 0, 1, 0, 0);
    layer.ctx.clearRect(0, 0, EXPORT_VIDEO_W, EXPORT_VIDEO_H);
    layer.ctx.setTransform(view.scale, 0, 0, view.scale, view.tx, view.ty);
    layer.ctx.imageSmoothingEnabled = true;
    if (layer.ctx.imageSmoothingQuality) layer.ctx.imageSmoothingQuality = "high";
    drawExportTextLayer(layer.ctx, items);
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.drawImage(layer.canvas, 0, 0);
  ctx.setTransform(view.scale, 0, 0, view.scale, view.tx, view.ty);
  drawExportTextFills(ctx, items);
}

// Map the stage layout onto the 1920x1080 frame. Text is drawn through the same
// transform, so glyphs are rasterised at output resolution instead of upscaled.
function applyStageExportTransform(ctx) {
  const stage = viewStage.getBoundingClientRect();
  const scale = Math.min(
    EXPORT_VIDEO_W / Math.max(1, stage.width),
    EXPORT_VIDEO_H / Math.max(1, stage.height)
  );
  const tx = (EXPORT_VIDEO_W - stage.width * scale) / 2 - stage.left * scale;
  const ty = (EXPORT_VIDEO_H - stage.height * scale) / 2 - stage.top * scale;
  ctx.setTransform(scale, 0, 0, scale, tx, ty);
  return { stage, scale, tx, ty };
}

const exportProfile = {
  frames: 0,
  rebuilds: 0,
  karaoke: 0,
  anim: 0,
  aura: 0,
  bg: 0,
  text: 0,
  encode: 0,
  wait: 0,
  queue: 0,
  outputs: 0,
};

function resetExportProfile() {
  for (const key of Object.keys(exportProfile)) exportProfile[key] = 0;
}

function exportProfileDetail() {
  const frames = Math.max(1, exportProfile.frames);
  const per = (value) => (value / frames).toFixed(1);
  return [
    `lletra ${per(exportProfile.karaoke)}`,
    `anim ${per(exportProfile.anim)}`,
    `aura ${per(exportProfile.aura)}`,
    `fons ${per(exportProfile.bg)}`,
    `text ${per(exportProfile.text)}`,
    `codif ${per(exportProfile.encode)}`,
    `espera ${per(exportProfile.wait)} ms/f`,
    `${exportProfile.rebuilds} refets`,
    `cua ${exportProfile.queue}`,
    `sortides ${exportProfile.outputs}`,
  ].join(" · ");
}

function clamp01(value) {
  return value < 0 ? 0 : value > 1 ? 1 : value;
}

function smoothstep(value) {
  const t = clamp01(value);
  return t * t * (3 - 2 * t);
}

let exportBrandLogo = null;
let exportBrandLogoWait = null;

function ensureExportBrandLogo() {
  if (exportBrandLogo?.complete && exportBrandLogo.naturalWidth) return Promise.resolve();
  if (exportBrandLogoWait) return exportBrandLogoWait;
  exportBrandLogoWait = new Promise((resolve) => {
    const img = new Image();
    img.decoding = "async";
    img.onload = () => {
      exportBrandLogo = img;
      resolve();
    };
    img.onerror = () => resolve();
    img.src = "/intro-logo.png?v=1";
  });
  return exportBrandLogoWait;
}

function setExportLetterSpacing(ctx, px) {
  if (typeof ctx.letterSpacing === "string") ctx.letterSpacing = `${px}px`;
}

function fitExportFont(ctx, text, family, maxPx, minPx, maxWidth) {
  let size = maxPx;
  while (size > minPx) {
    ctx.font = `${size}px ${family}`;
    if (ctx.measureText(text || "").width <= maxWidth) return size;
    size -= 2;
  }
  ctx.font = `${minPx}px ${family}`;
  return minPx;
}

function fillExportHeadline(ctx, text, x, y) {
  ctx.save();
  ctx.shadowColor = "rgba(0,0,0,0.85)";
  ctx.shadowBlur = 18;
  ctx.shadowOffsetY = 2;
  ctx.fillText(text, x, y);
  ctx.restore();
  ctx.fillText(text, x, y);
}

function drawExportBrandMark(ctx, x, y, size) {
  if (!exportBrandLogo?.naturalWidth) return;
  ctx.save();
  ctx.imageSmoothingEnabled = true;
  if (ctx.imageSmoothingQuality) ctx.imageSmoothingQuality = "high";
  ctx.drawImage(exportBrandLogo, x, y, size, size);
  ctx.restore();
}

function paintExportIntro(ctx, t, track) {
  const fadeIn = smoothstep(t / 0.7);
  const card = smoothstep((t - 0.65) / 0.55);
  const fadeOut = smoothstep((t - 4.2) / 0.8);
  const alpha = fadeIn * (1 - fadeOut);
  if (alpha < 0.01) return;
  const artist = (track?.artist || "").toLocaleUpperCase("ca");
  const title = track?.title || "";
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.fillStyle = `rgba(3, 2, 8, ${0.52 * alpha})`;
  ctx.fillRect(0, 0, EXPORT_VIDEO_W, EXPORT_VIDEO_H);
  const cx = EXPORT_VIDEO_W / 2;
  const logoSize = 220 + (1 - card) * 160;
  const artistSize = 28;
  const titleSize = fitExportFont(ctx, title, "Bebas Neue, sans-serif", 88, 44, 1600);
  const subSize = 22;
  const gap = 36;
  const textH = artistSize + 16 + titleSize + 44 + subSize;
  const stackH = logoSize + card * (gap + textH);
  const logoY = (EXPORT_VIDEO_H - stackH) / 2;
  ctx.globalAlpha = alpha;
  drawExportBrandMark(ctx, cx - logoSize / 2, logoY, logoSize);
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.globalAlpha = alpha * card;
  const artistY = logoY + logoSize + gap + artistSize;
  setExportLetterSpacing(ctx, 7);
  ctx.font = `700 ${artistSize}px Outfit, sans-serif`;
  ctx.fillStyle = "#ffe14a";
  fillExportHeadline(ctx, artist, cx, artistY);
  setExportLetterSpacing(ctx, 2);
  ctx.font = `${titleSize}px Bebas Neue, sans-serif`;
  ctx.fillStyle = "#fff6ea";
  fillExportHeadline(ctx, title, cx, artistY + 16 + titleSize);
  setExportLetterSpacing(ctx, 4);
  ctx.font = `500 ${subSize}px Outfit, sans-serif`;
  ctx.fillStyle = "#3de7ff";
  fillExportHeadline(ctx, "KARAOKE", cx, artistY + titleSize + 60);
  ctx.restore();
}

function paintExportOutro(ctx, t) {
  const fade = smoothstep(t / 1.1);
  if (fade < 0.01) return;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = fade;
  ctx.fillStyle = `rgba(3, 2, 8, ${0.28 * fade})`;
  ctx.fillRect(0, 0, EXPORT_VIDEO_W, EXPORT_VIDEO_H);
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  setExportLetterSpacing(ctx, 2);
  const text = "Gràcies per cantar!";
  const size = fitExportFont(ctx, text, "Bebas Neue, sans-serif", 120, 64, 1680);
  ctx.font = `${size}px Bebas Neue, sans-serif`;
  ctx.fillStyle = "#fff6ea";
  fillExportHeadline(ctx, text, EXPORT_VIDEO_W / 2, EXPORT_VIDEO_H / 2);
  ctx.restore();
}

function paintExportFrame(options = {}) {
  if (!stageCapture?.ctx || !viewStage) return;
  const ctx = stageCapture.ctx;
  const startedAt = performance.now();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = "source-over";
  ctx.fillStyle = "#030208";
  ctx.fillRect(0, 0, EXPORT_VIDEO_W, EXPORT_VIDEO_H);

  const view = applyStageExportTransform(ctx);
  const stage = view.stage;
  ctx.imageSmoothingEnabled = true;
  if (ctx.imageSmoothingQuality) ctx.imageSmoothingQuality = "high";

  if (stageAuraEl && viewStage.classList.contains("has-aura")) {
    const aura = stageAuraEl.getBoundingClientRect();
    if (stageAuraCanvas && stageAuraCanvas.width && stageAuraCanvas.height) {
      ctx.drawImage(stageAuraCanvas, aura.left, aura.top, aura.width, aura.height);
    }
    if (auraParticlesEnabled && stageCapture.grainPattern) {
      ctx.save();
      ctx.globalAlpha = 0.18;
      ctx.globalCompositeOperation = "overlay";
      ctx.fillStyle = stageCapture.grainPattern;
      ctx.fillRect(aura.left, aura.top, aura.width, aura.height);
      ctx.restore();
    }
    const vignette = ctx.createLinearGradient(0, aura.top, 0, aura.top + aura.height);
    vignette.addColorStop(0, "rgba(0,0,0,0.38)");
    vignette.addColorStop(0.16, "rgba(0,0,0,0)");
    vignette.addColorStop(0.84, "rgba(0,0,0,0)");
    vignette.addColorStop(1, "rgba(0,0,0,0.5)");
    ctx.fillStyle = vignette;
    ctx.fillRect(aura.left, aura.top, aura.width, aura.height);
  } else {
    ctx.fillStyle = "#07060b";
    ctx.fillRect(stage.left, stage.top, stage.width, stage.height);
  }

  const afterBackground = performance.now();
  exportProfile.bg += afterBackground - startedAt;
  if (!options.skipText) {
    paintExportText(ctx, view);
    exportProfile.text += performance.now() - afterBackground;
  }
}

function stopExportPaintLoop() {
  if (stageCapture?.raf) {
    cancelAnimationFrame(stageCapture.raf);
    stageCapture.raf = 0;
  }
}

function startExportPaintLoop() {
  const capture = stageCapture;
  if (!capture) return;
  const track = capture.videoTrack;
  const frameMs = 1000 / EXPORT_VIDEO_FPS;
  capture.nextFrameAt = performance.now();
  const tickPaint = (now) => {
    if (!stageCapture) return;
    if (now >= capture.nextFrameAt) {
      paintExportFrame();
      if (typeof track?.requestFrame === "function") track.requestFrame();
      capture.nextFrameAt += frameMs;
      if (now - capture.nextFrameAt > frameMs * 3) {
        capture.nextFrameAt = now + frameMs;
      }
    }
    capture.raf = requestAnimationFrame(tickPaint);
  };
  paintExportFrame();
  if (typeof track?.requestFrame === "function") track.requestFrame();
  capture.raf = requestAnimationFrame(tickPaint);
}

function detachStageCapture() {
  stopExportPaintLoop();
  if (stageCapture?.canvas) stageCapture.canvas.remove();
  stageCapture = null;
  document.body.classList.remove("is-exporting-video");
  viewStage?.classList.remove("is-exporting");
  setExportCaptureBadge("");
}

function abortStageCapture(message) {
  if (!stageCapture || stageCapture.aborted) return;
  stageCapture.aborted = true;
  stageCapture.abortError = new Error(message || "S’ha cancel·lat la gravació");
  try {
    if (stageCapture.recorder && stageCapture.recorder.state === "recording") {
      stageCapture.recorder.stop();
    } else {
      stageCapture.reject?.(stageCapture.abortError);
    }
  } catch {
    stageCapture.reject?.(stageCapture.abortError);
  }
}

function finishStageCapture() {
  if (!stageCapture || stageCapture.aborted) return;
  try {
    if (stageCapture.recorder && stageCapture.recorder.state === "recording") {
      stageCapture.recorder.stop();
    }
  } catch {
    /* ignore */
  }
}

function createExportCanvas() {
  document.querySelectorAll(".export-capture-canvas").forEach((node) => node.remove());
  const canvas = document.createElement("canvas");
  canvas.width = EXPORT_VIDEO_W;
  canvas.height = EXPORT_VIDEO_H;
  canvas.className = "export-capture-canvas";
  canvas.setAttribute("aria-hidden", "true");
  document.body.appendChild(canvas);
  return canvas;
}

function makeExportTextLayer() {
  const canvas = document.createElement("canvas");
  canvas.width = EXPORT_VIDEO_W;
  canvas.height = EXPORT_VIDEO_H;
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  return { canvas, ctx, signature: "" };
}

function attachStageCanvas(canvas, ctx, extra = {}) {
  ctx.imageSmoothingEnabled = true;
  if (ctx.imageSmoothingQuality) ctx.imageSmoothingQuality = "high";
  const grain = auraParticlesEnabled ? makeExportGrainTile() : null;
  stageCapture = {
    canvas,
    ctx,
    grain,
    grainPattern: grain ? ctx.createPattern(grain, "repeat") : null,
    textLayer: makeExportTextLayer(),
    raf: 0,
    nextFrameAt: 0,
    aborted: false,
    abortError: null,
    resolve: null,
    reject: null,
    ...extra,
  };
  return stageCapture;
}

function prepareStageCapture() {
  const mime = exportRecorderMime();
  if (!window.MediaRecorder || !mime) {
    throw new Error("Aquest navegador no pot gravar l’escenari");
  }
  const canvas = createExportCanvas();
  const ctx = canvas.getContext("2d", { alpha: false, desynchronized: false });
  if (!ctx || typeof canvas.captureStream !== "function") {
    canvas.remove();
    throw new Error("Aquest navegador no pot gravar l’escenari");
  }
  ctx.imageSmoothingEnabled = true;
  if (ctx.imageSmoothingQuality) ctx.imageSmoothingQuality = "high";
  let stream;
  try {
    stream = canvas.captureStream(0);
    const probe = stream.getVideoTracks?.()?.[0];
    if (typeof probe?.requestFrame !== "function") {
      stream.getTracks().forEach((track) => track.stop());
      stream = canvas.captureStream(EXPORT_VIDEO_FPS);
    }
  } catch {
    stream = canvas.captureStream(EXPORT_VIDEO_FPS);
  }
  const videoTrack = stream.getVideoTracks()[0] || null;
  if (videoTrack && "contentHint" in videoTrack) videoTrack.contentHint = "detail";
  let recorder;
  try {
    recorder = new MediaRecorder(stream, {
      mimeType: mime,
      videoBitsPerSecond: 12_000_000,
    });
  } catch {
    recorder = new MediaRecorder(stream, { mimeType: mime });
  }
  attachStageCanvas(canvas, ctx, { recorder, videoTrack, mime, chunks: [] });
  paintExportFrame();
}

function recordStageUntilEnded() {
  return new Promise((resolve, reject) => {
    const capture = stageCapture;
    if (!capture?.recorder) {
      reject(new Error("No s’ha pogut gravar l’escenari"));
      return;
    }
    capture.resolve = resolve;
    capture.reject = reject;
    const recorder = capture.recorder;
    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size) capture.chunks.push(event.data);
    };
    recorder.onerror = () => {
      capture.aborted = true;
      capture.abortError = new Error("No s’ha pogut gravar l’escenari");
    };
    recorder.onstop = () => {
      stopExportPaintLoop();
      if (capture.aborted) {
        reject(capture.abortError || new Error("S’ha cancel·lat la gravació"));
        return;
      }
      const blob = new Blob(capture.chunks, { type: capture.mime || "video/webm" });
      if (!blob.size) {
        reject(new Error("La gravació de l’escenari és buida"));
        return;
      }
      resolve(blob);
    };
    startExportPaintLoop();
    try {
      recorder.start(250);
    } catch (err) {
      reject(err instanceof Error ? err : new Error("No s’ha pogut gravar l’escenari"));
    }
  });
}

async function uploadStageRecording(track, blob, filename) {
  const form = new FormData();
  form.append("file", blob, filename);
  return api(`/api/video/upload?track_id=${encodeURIComponent(track.id)}`, {
    method: "POST",
    body: form,
  });
}

function yieldToBrowser() {
  if (typeof scheduler !== "undefined" && typeof scheduler.yield === "function") {
    return scheduler.yield();
  }
  // A message task is not throttled the way timers are in a hidden tab.
  return new Promise((resolve) => {
    const channel = new MessageChannel();
    channel.port1.onmessage = () => resolve();
    channel.port2.postMessage(0);
  });
}

async function pickExportEncoderConfig(preferences = ["prefer-hardware", "no-preference"]) {
  if (typeof window.VideoEncoder !== "function") return null;
  // Ask for the GPU encoder first; only fall back to the software one if the
  // machine has no usable hardware H.264 encoder.
  for (const hardwareAcceleration of preferences) {
    for (const codec of EXPORT_CODECS) {
      const config = {
        codec,
        width: EXPORT_VIDEO_W,
        height: EXPORT_VIDEO_H,
        bitrate: EXPORT_VIDEO_BITRATE,
        framerate: EXPORT_VIDEO_FPS,
        hardwareAcceleration,
        latencyMode: "quality",
        avc: { format: "annexb" },
      };
      try {
        const support = await VideoEncoder.isConfigSupported(config);
        if (support?.supported) return config;
      } catch {
        /* try the next codec */
      }
    }
  }
  return null;
}

/** The muxer trims to the shortest stream, so never render less than the audio. */
function probeAudioSeconds(trackId) {
  return new Promise((resolve) => {
    const probe = new Audio();
    probe.preload = "metadata";
    let settled = false;
    const done = () => {
      if (settled) return;
      settled = true;
      resolve(Number(probe.duration) || 0);
    };
    probe.addEventListener("loadedmetadata", done, { once: true });
    probe.addEventListener("error", done, { once: true });
    probe.src = audioUrlFor(trackId, "original");
    setTimeout(done, 5000);
  });
}

function exportSongSeconds(track, probedSeconds) {
  let lyricsEnd = 0;
  for (const line of lyricLines) {
    for (const word of lineWords(line)) {
      lyricsEnd = Math.max(lyricsEnd, Number(word.end) || 0);
    }
  }
  return Math.max(Number(track?.duration) || 0, probedSeconds || 0, lyricsEnd + 1.5, 1);
}

/** Lay the stage out offscreen: no audio, no playback, nothing for the user to watch. */
async function openStageForExport(track) {
  stopAlignPoll();
  stopStemPoll();
  clearStageOutro();
  stopPreview();
  setStageBgMode("aura", { persist: false });
  // Keep the library on screen so more videos can be queued. The stage is
  // parked offscreen via body.is-exporting-video.
  // viewMenu.classList.add("hidden");
  viewStage.classList.add("is-exporting");
  document.body.classList.add("is-exporting-video");
  viewStage.classList.remove("hidden");
  songArtist.textContent = track.artist || "Artista desconegut";
  songTitle.textContent = track.title;

  const payload = await api(`/api/lyrics?track_id=${encodeURIComponent(track.id)}`);
  if (!payload.lines?.length) throw new Error("No hi ha lletra per al vídeo");
  if (!payload.aligned) throw new Error("La lletra encara no està sincronitzada");

  exportClock = 0;
  exportTimers.length = 0;
  renderLyrics(payload);

  // Same seeding as the live stage, then take over the clock ourselves.
  startAuraEngine();
  stopAuraEngine();
  await document.fonts.ready.catch(() => {});
  await ensureExportBrandLogo();
  return payload;
}

function closeStageForExport(previousBgMode) {
  exportClock = null;
  exportTimers.length = 0;
  clearLineRoll();
  resumeStageAnimations();
  if (!currentId) viewStage.classList.add("hidden");
  detachStageCapture();
  // if (!currentId) viewMenu.classList.remove("hidden");
  if (previousBgMode) setStageBgMode(previousBgMode, { persist: false });
  syncAuraEngine();
}

function flushEncoder(encoder, timeoutMs = 12000) {
  let timer = 0;
  const guard = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(EXPORT_ENCODER_STALLED)), timeoutMs);
  });
  return Promise.race([encoder.flush(), guard]).finally(() => clearTimeout(timer));
}

/**
 * Keep a bounded number of frames in flight without ever waiting forever.
 * Hardware encoders buffer a pipeline and some only emit once they receive more
 * input, so a strict queue limit deadlocks: we stop feeding waiting for output
 * that will not come until we feed. When the queue stops moving, flush it.
 */
async function relieveEncoder(encoder, state, frame) {
  const primed = state.outputs > 0 || frame < EXPORT_QUEUE_LIMIT;
  if (encoder.encodeQueueSize < EXPORT_QUEUE_LIMIT && primed) return;
  const deadline = performance.now() + 400;
  while (encoder.encodeQueueSize >= EXPORT_QUEUE_LIMIT && !state.error) {
    if (performance.now() > deadline) break;
    await yieldToBrowser();
  }
  if (state.error) return;
  if (encoder.encodeQueueSize >= EXPORT_QUEUE_LIMIT || state.outputs === 0) {
    await flushEncoder(encoder);
    if (state.outputs === 0) throw new Error(EXPORT_ENCODER_STALLED);
  }
}

/**
 * Render the stage frame by frame on a virtual clock and encode it directly.
 * Faster than the song, and the browser encode is the only compression step.
 */
async function renderStageOffline(track, config, onProgress) {
  const canvas = createExportCanvas();
  const ctx = canvas.getContext("2d", { alpha: false });
  if (!ctx) {
    canvas.remove();
    throw new Error("Aquest navegador no pot preparar el vídeo");
  }
  attachStageCanvas(canvas, ctx);

  const parts = [];
  const state = { error: null, outputs: 0 };
  const encoder = new VideoEncoder({
    output: (chunk) => {
      const bytes = new Uint8Array(chunk.byteLength);
      chunk.copyTo(bytes);
      parts.push(bytes);
      state.outputs += 1;
    },
    error: (err) => {
      state.error = err;
    },
  });
  encoder.configure(config);

  const songSeconds = exportSongSeconds(track, await probeAudioSeconds(track.id));
  const introFrames = Math.round(EXPORT_INTRO_SECONDS * EXPORT_VIDEO_FPS);
  const songFrames = Math.max(1, Math.round(songSeconds * EXPORT_VIDEO_FPS));
  const outroFrames = Math.round(EXPORT_OUTRO_SECONDS * EXPORT_VIDEO_FPS);
  const totalFrames = introFrames + songFrames + outroFrames;
  const songEnd = songFrames / EXPORT_VIDEO_FPS;
  // A keyframe every two seconds instead of every half second: fewer bits spent
  // on repeated keyframes leaves more for the picture at the same bitrate.
  const gop = EXPORT_VIDEO_FPS * 2;
  const frameDuration = Math.round(1e6 / EXPORT_VIDEO_FPS);
  const staticAura = auraReduceMotion();
  let windowStartedAt = performance.now();
  let windowStartFrame = 0;
  resetExportProfile();

  try {
    for (let frame = 0; frame < totalFrames; frame += 1) {
      if (state.error) throw state.error;
      if (exportAborted) throw new Error("S’ha cancel·lat el vídeo");

      const fileTime = frame / EXPORT_VIDEO_FPS;
      const markStart = performance.now();
      let skipText = false;
      if (frame < introFrames) {
        exportClock = 0;
        skipText = true;
      } else if (frame < introFrames + songFrames) {
        exportClock = (frame - introFrames) / EXPORT_VIDEO_FPS;
        runDueStageSteps(exportClock);
        syncKaraoke();
      } else {
        exportClock = songEnd;
        skipText = true;
      }
      const markKaraoke = performance.now();
      if (!skipText) stepStageAnimations(exportClock * 1000);
      const markAnim = performance.now();
      drawAuraFrame(auraT0 + (staticAura ? 0 : fileTime * 1000));
      const markAura = performance.now();
      paintExportFrame({ skipText });
      if (frame < introFrames) {
        paintExportIntro(stageCapture.ctx, fileTime, track);
      } else if (frame >= introFrames + songFrames) {
        paintExportOutro(stageCapture.ctx, fileTime - EXPORT_INTRO_SECONDS - songEnd);
      }
      const markPaint = performance.now();

      const videoFrame = new VideoFrame(canvas, {
        timestamp: Math.round(fileTime * 1e6),
        duration: frameDuration,
      });
      encoder.encode(videoFrame, { keyFrame: frame % gop === 0 });
      videoFrame.close();

      exportProfile.frames += 1;
      exportProfile.karaoke += markKaraoke - markStart;
      exportProfile.anim += markAnim - markKaraoke;
      exportProfile.aura += markAura - markAnim;
      exportProfile.encode += performance.now() - markPaint;
      exportProfile.queue = encoder.encodeQueueSize;
      exportProfile.outputs = state.outputs;

      if (frame % 10 === 0) {
        const windowSeconds = (performance.now() - windowStartedAt) / 1000;
        const rendered = (frame - windowStartFrame) / EXPORT_VIDEO_FPS;
        onProgress(frame / totalFrames, windowSeconds > 0.4 ? rendered / windowSeconds : 0);
        await yieldToBrowser();
      }
      const markWait = performance.now();
      await relieveEncoder(encoder, state, frame);
      exportProfile.wait += performance.now() - markWait;

      // Report on a recent window so a slow start does not hide the real pace.
      if (frame - windowStartFrame >= EXPORT_VIDEO_FPS * 3) {
        windowStartFrame = frame;
        windowStartedAt = performance.now();
        resetExportProfile();
      }
    }
    await flushEncoder(encoder);
    if (state.error) throw state.error;
  } finally {
    try {
      encoder.close();
    } catch {
      /* already closed */
    }
  }

  const blob = new Blob(parts, { type: "video/h264" });
  if (!blob.size) throw new Error("No s’ha generat cap fotograma");
  return blob;
}

async function buildKaraokeVideo(track, label) {
  let config = await pickExportEncoderConfig();
  if (!config) {
    // No WebCodecs: fall back to recording the stage in real time.
    return captureAndMuxStage(track);
  }
  const previousBgMode = stageBgMode;
  setExportCaptureBadge(`${trackLabel(track)} · preparant…`);
  const onProgress = (ratio, speed) => {
    const pct = Math.round(ratio * 100);
    const rate = speed > 0 ? ` · ×${speed.toFixed(1)}` : "";
    setExportVideoStatus(`${label} · creant el vídeo ${pct}%${rate}`, "running");
    setExportCaptureBadge(`${trackLabel(track)} · ${pct}%${rate}`, exportProfileDetail());
  };
  try {
    let blob = null;
    for (let attempt = 0; attempt < 2 && !blob; attempt += 1) {
      await openStageForExport(track);
      try {
        blob = await renderStageOffline(track, config, onProgress);
      } catch (err) {
        // Some drivers accept the config and then never emit a frame. Retry once
        // on the software encoder rather than leaving the user stuck.
        const stalled = err?.message === EXPORT_ENCODER_STALLED;
        const software = stalled ? await pickExportEncoderConfig(["prefer-software"]) : null;
        if (!software || attempt > 0) throw err;
        setExportVideoStatus(`${label} · el codificador de la GPU falla, reintentant…`, "running");
        config = software;
      }
    }
    setExportVideoStatus(`${label} · muntant l’àudio original…`, "running");
    setExportCaptureBadge("Muntant l’àudio…");
    return await uploadStageRecording(track, blob, "stage.h264");
  } finally {
    closeStageForExport(previousBgMode);
  }
}

async function captureAndMuxStage(track) {
  const prevAudio = audioMode;
  const prevBg = stageBgMode;
  try {
    await setAudioMode("original", { persist: false });
    setStageBgMode("aura", { persist: false });
    await openSong(track.id, { autoplay: false });
    if (currentId !== track.id) throw new Error("S’ha sortit de l’escenari");
    if (!lyricLines.length) throw new Error("No hi ha lletra per al vídeo");
    setExportVideoStatus(`${trackLabel(track)} · esperant la sincronització…`, "running");
    await waitForLyricsAligned();
    await waitForPlayerReady();
    player.pause();
    player.currentTime = 0;
    viewStage.classList.add("is-exporting");
    document.body.classList.add("is-exporting-video");
    resizeAuraCanvas();
    syncAuraEngine();
    await document.fonts.ready.catch(() => {});
    await waitAnimationFrames(3);
    syncKaraoke();
    setExportCaptureBadge("Gravant l’escenari…");
    setExportVideoStatus(`${trackLabel(track)} · gravant l’escenari…`, "running");
    prepareStageCapture();
    const mime = stageCapture.mime;
    const blobPromise = recordStageUntilEnded();
    try {
      await player.play();
    } catch {
      abortStageCapture("No s’ha pogut reproduir la cançó");
      await blobPromise.catch(() => {});
      throw new Error("No s’ha pogut reproduir la cançó");
    }
    updatePlayButton();
    const blob = await blobPromise;
    setExportCaptureBadge("Muntant l’àudio…");
    setExportVideoStatus(`${trackLabel(track)} · muntant l’àudio original…`, "running");
    const ext = (mime || blob.type || "").includes("mp4") ? "mp4" : "webm";
    return await uploadStageRecording(track, blob, `stage.${ext}`);
  } finally {
    const stillOnStage = Boolean(viewStage && !viewStage.classList.contains("hidden"));
    detachStageCapture();
    try {
      await setAudioMode(prevAudio, { persist: false });
    } catch {
      /* keep going */
    }
    setStageBgMode(prevBg, { persist: false });
    if (stillOnStage) showMenu();
  }
}

function exportQueuePrefix() {
  const total = videoQueueDone + videoQueue.length + 1;
  if (total < 2) return "";
  return `Vídeo ${videoQueueDone + 1}/${total} · `;
}

async function exportKaraokeVideo(track) {
  const label = `${exportQueuePrefix()}${trackLabel(track)}`;
  setExportVideoStatus(`${label} · comprovant la sincronització…`, "running");
  const job = await api("/api/video", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      track_id: track.id,
      language: "ca",
      lyrics_layout: lyricsLayout === "dual" ? "dual" : "stack",
    }),
  });
  if (job.status === "unavailable") {
    throw new Error(job.error || "No s’ha pogut crear el vídeo");
  }
  let ready = job;
  if (job.status !== "done" && job.status !== "ready") {
    if (!job.job_id) throw new Error(job.error || "El vídeo no s’ha iniciat");
    setExportVideoStatus(
      `${label} · ${videoPhaseLabel(job.phase, job.progress, job.stem_phase)}`,
      "running"
    );
    ready = await waitVideoJob(job.job_id);
  }
  markTrackAligned(track.id);
  if (ready.status === "ready") {
    ready = await buildKaraokeVideo(track, label);
  }
  const name = await downloadVideoFile(ready);
  setExportVideoStatus(`Vídeo desat · ${name}`, "ok");
  loadLibrary().catch(() => {});
}

async function runVideoQueue() {
  if (exportVideoBusy) return;
  exportVideoBusy = true;
  videoQueueDone = 0;
  while (videoQueue.length) {
    const track = videoQueue.shift();
    videoQueuedIds.delete(track.id);
    exportAborted = false;
    exportVideoTrackId = track.id;
    updateExportVideoButton();
    try {
      await exportKaraokeVideo(track);
    } catch (err) {
      setExportVideoStatus(
        `${trackLabel(track)} · ${err.message || "error creant el vídeo"}`,
        "error"
      );
      await new Promise((resolve) => setTimeout(resolve, 1600));
    }
    videoQueueDone += 1;
  }
  videoQueueDone = 0;
  exportVideoBusy = false;
  exportVideoTrackId = "";
  updateExportVideoButton();
}

function cancelVideoQueue() {
  exportAborted = true;
  videoQueue.length = 0;
  videoQueuedIds.clear();
  if (stageCapture && !stageCapture.aborted) {
    abortStageCapture("S’ha aturat el vídeo");
  }
  setExportVideoStatus("S’ha aturat la creació de vídeos", "error");
  updateExportVideoButton();
}

function exportSelectedKaraokeVideo() {
  const track = selectedTrack();
  if (!track || isAlbumListView()) return;
  if (track.has_lyrics === false && !track.lyrics_pending) return;
  if (exportVideoTrackId === track.id) {
    cancelVideoQueue();
    return;
  }
  if (videoQueuedIds.has(track.id)) {
    videoQueuedIds.delete(track.id);
    const index = videoQueue.findIndex((item) => item.id === track.id);
    if (index >= 0) videoQueue.splice(index, 1);
    setExportVideoStatus(`${trackLabel(track)} · fora de la cua`, "running");
    updateExportVideoButton();
    return;
  }
  videoQueue.push(track);
  videoQueuedIds.add(track.id);
  updateExportVideoButton();
  if (exportVideoBusy) {
    setExportVideoStatus(
      `${trackLabel(track)} · a la cua (${videoQueue.length} pendents)`,
      "running"
    );
    return;
  }
  runVideoQueue();
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
  if (exportVideoBusy) {
    setExportVideoStatus("Espera que acabi el vídeo per cantar", "error");
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
  const rating = clampRating(item?.rating);
  const score = rating ? ` · ${rating} de 5` : "";
  return `${item?.artist || "Artista"} — ${item?.title || item?.relpath || ""}${score}`;
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
    if (item.kind !== "album") {
      const rating = document.createElement("div");
      rating.className = "song-rating";
      bindRatingWidget(rating, item, { compact: true, asButtons: false });
      btn.append(artist, title, rating);
    } else {
      btn.append(artist, title);
    }
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
      : tracksForLyricsFilter().length && ratingFilterMode !== "all"
        ? ratingFilterMode === "none"
          ? "Cap cançó sense nota"
          : `Cap cançó amb ${ratingFilterLabel()}`
      : lyricsFilterMode === "hidden"
        ? "Cap cançó oculta"
        : "Sense cançons";
    coverIndex.textContent = "";
    bindRatingWidget(songRating, null);
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
      : tracksForLyricsFilter().length && ratingFilterMode !== "all"
        ? ratingFilterMode === "none"
          ? "No hi ha cançons sense puntuació."
          : `No hi ha cançons amb ${ratingFilterLabel()}.`
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

function karaokeNow() {
  if (exportClock !== null) return exportClock;
  if (!audioClockReady) return 0;
  const t = Number(player.currentTime);
  return Number.isFinite(t) && t >= 0 ? t : 0;
}

function markAudioClockReady() {
  audioClockReady = true;
}

function resetAudioClock() {
  audioClockReady = player.readyState >= HTMLMediaElement.HAVE_METADATA;
  if (audioClockReady) return;
  player.addEventListener("loadedmetadata", markAudioClockReady, { once: true });
}

/** setTimeout on the live stage, virtual-clock step while exporting. */
function scheduleStageStep(delayMs, fn) {
  if (exportClock === null) return setTimeout(fn, delayMs);
  const token = { at: exportClock + delayMs / 1000, fn };
  exportTimers.push(token);
  return token;
}

function cancelStageStep(handle) {
  if (!handle) return;
  if (typeof handle === "number") {
    clearTimeout(handle);
    return;
  }
  const index = exportTimers.indexOf(handle);
  if (index >= 0) exportTimers.splice(index, 1);
}

function runDueStageSteps(seconds) {
  for (let guard = 0; guard < 8 && exportTimers.length; guard += 1) {
    const due = exportTimers.filter((item) => item.at <= seconds);
    if (!due.length) return;
    for (const item of due) cancelStageStep(item);
    for (const item of due) item.fn();
  }
}

// The live stage waits two frames so the browser keeps the "from" style and the
// transition runs. Offline there is no next frame, so force the recalc instead.
function afterStyleFlush(fn) {
  if (exportClock !== null) {
    void document.body.offsetHeight;
    fn();
    return;
  }
  requestAnimationFrame(() => requestAnimationFrame(fn));
}

/** Only the subtrees the compositor actually draws; the rest never reaches the video. */
function drawnStageAnimations() {
  const roots = [songArtist, songTitle, lyricsEl];
  const animations = [];
  for (const root of roots) {
    if (!root?.getAnimations) continue;
    for (const animation of root.getAnimations({ subtree: true })) animations.push(animation);
  }
  if (viewStage?.getAnimations) {
    for (const animation of viewStage.getAnimations()) animations.push(animation);
  }
  return animations;
}

/** Drive CSS transitions from the virtual clock so frames are reproducible. */
function stepStageAnimations(virtualMs) {
  let animations = [];
  try {
    animations = drawnStageAnimations();
  } catch {
    return;
  }
  for (const animation of animations) {
    let startedAt = exportAnimationStarts.get(animation);
    if (startedAt === undefined) {
      startedAt = virtualMs;
      exportAnimationStarts.set(animation, startedAt);
      try {
        animation.pause();
      } catch {
        /* ignore */
      }
    }
    try {
      animation.currentTime = Math.max(0, virtualMs - startedAt);
    } catch {
      /* ignore */
    }
  }
}

function resumeStageAnimations() {
  try {
    for (const animation of drawnStageAnimations()) {
      if (animation.playState === "paused") animation.play();
    }
  } catch {
    /* ignore */
  }
}

function clearLineRoll() {
  if (lineSwapTimer) {
    cancelStageStep(lineSwapTimer);
    lineSwapTimer = null;
  }
  if (dualRefreshTimer) {
    cancelStageStep(dualRefreshTimer);
    dualRefreshTimer = null;
  }
  if (!restHoldActive && restFadeTimer) {
    cancelStageStep(restFadeTimer);
    restFadeTimer = null;
  }
  if (!restHoldActive) dualPending = null;
  kStackEl.classList.remove("is-rolling");
  kStackEl.querySelectorAll(".k-slot-ghost").forEach((node) => node.remove());
  lineCurrentEl.classList.remove("is-rising");
  lineNextEl.classList.remove("is-entering");
  if (!restHoldActive) {
    lineCurrentEl.classList.remove("is-refreshing", "is-rest-fade", "is-rest-hidden");
    lineNextEl.classList.remove("is-refreshing", "is-rest-fade", "is-rest-hidden");
  }
}

function fillSlot(slotEl, line, { trackWords = false, resetWords = true } = {}) {
  slotEl.innerHTML = "";
  slotEl.classList.remove(
    "is-empty",
    "is-rising",
    "is-entering",
    "is-refreshing",
    "is-rest-fade",
    "is-rest-hidden",
  );
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

function restBeforeUpcoming(index) {
  const current = lyricLines[index];
  const next = lyricLines[index + 1];
  if (!current || !next) return false;
  const gap = lineTimeSpan(next, index + 1).start - lineTimeSpan(current, index).end;
  return gap >= UPCOMING_REST_GAP;
}

function upcomingReady(index, t) {
  const next = lyricLines[index + 1];
  if (!next) return false;
  if (!restBeforeUpcoming(index)) return true;
  return t >= lineTimeSpan(next, index + 1).start - UPCOMING_LEAD_IN;
}

function upcomingLineIfReady(index, t) {
  return upcomingReady(index, t) ? lyricLines[index + 1] || null : null;
}

function lineHasEnded(index, t) {
  const line = lyricLines[index];
  if (!line) return true;
  return t >= lineTimeSpan(line, index).end;
}

function firstLineStart() {
  if (!lyricLines[0]) return 0;
  return lineTimeSpan(lyricLines[0], 0).start;
}

function hasIntroRest() {
  return firstLineStart() > UPCOMING_LEAD_IN;
}

function isIntroHold(t) {
  if (!hasIntroRest()) return false;
  return t < firstLineStart() - UPCOMING_LEAD_IN;
}

function isIntroLeadIn(t) {
  if (!hasIntroRest()) return false;
  const start = firstLineStart();
  return t >= start - UPCOMING_LEAD_IN && t < start;
}

function isOutroHold(index, t) {
  if (index < 0 || index !== lyricLines.length - 1) return false;
  return lineHasEnded(index, t);
}

function isRestHold(index, t) {
  return restBeforeUpcoming(index) && lineHasEnded(index, t) && !upcomingReady(index, t);
}

function isRestLeadIn(index, t) {
  return restBeforeUpcoming(index) && lineHasEnded(index, t) && upcomingReady(index, t);
}

function isLyricHold(index, t) {
  return isIntroHold(t) || isRestHold(index, t) || isOutroHold(index, t);
}

function isLyricLeadIn(index, t) {
  return isIntroLeadIn(t) || isRestLeadIn(index, t);
}

function leadInLineIndex(index, t) {
  if (isIntroLeadIn(t)) return 0;
  if (isRestLeadIn(index, t)) return index + 1;
  return -1;
}

function dualPairOriginFor(index) {
  let i = Math.max(0, index);
  while (i > 0 && !restBeforeUpcoming(i - 1)) i -= 1;
  return i;
}

function dualActiveOnTop(index) {
  return (index - dualPairOriginFor(index)) % 2 === 0;
}

function approachLineIndex(index, t) {
  if (hasIntroRest()) {
    const start = firstLineStart();
    if (t >= start - UPCOMING_LEAD_IN && t <= start) return 0;
  }
  if (restBeforeUpcoming(index) && lineHasEnded(index, t)) {
    const next = lyricLines[index + 1];
    if (next) {
      const start = lineTimeSpan(next, index + 1).start;
      if (t >= start - UPCOMING_LEAD_IN && t <= start) return index + 1;
    }
  }
  return -1;
}

function stackLinesFor(index, t) {
  if (isLyricHold(index, t)) return { current: null, next: null };
  const leadIndex = leadInLineIndex(index, t);
  if (leadIndex >= 0) {
    return {
      current: lyricLines[leadIndex] || null,
      next: upcomingLineIfReady(leadIndex, t),
    };
  }
  return {
    current: lyricLines[index] || null,
    next: upcomingLineIfReady(index, t),
  };
}

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function fadeSlotsOut(slots) {
  const live = slots.filter((el) => el && !el.classList.contains("is-empty"));
  if (!live.length) {
    wordNodes = [];
    return;
  }
  const empty = () => {
    for (const el of live) fillSlot(el, null);
    wordNodes = [];
  };
  if (prefersReducedMotion()) {
    empty();
    return;
  }
  if (restFadeTimer) cancelStageStep(restFadeTimer);
  for (const el of live) el.classList.add("is-rest-fade");
  afterStyleFlush(() => {
    for (const el of live) el.classList.add("is-rest-hidden");
  });
  restFadeTimer = scheduleStageStep(REST_FADE_MS, () => {
    empty();
    restFadeTimer = null;
  });
}

function fadeSlotsIn(updates) {
  if (prefersReducedMotion()) {
    for (const { slotEl, line, trackWords, role } of updates) {
      fillSlot(slotEl, line, { trackWords: Boolean(trackWords) });
      if (role) setSlotRole(slotEl, role);
    }
    syncWordFills(karaokeNow());
    return;
  }
  for (const { slotEl, line, trackWords, role } of updates) {
    fillSlot(slotEl, line, { trackWords: Boolean(trackWords) });
    if (role) setSlotRole(slotEl, role);
    slotEl.classList.add("is-rest-fade", "is-rest-hidden");
  }
  afterStyleFlush(() => {
    for (const { slotEl } of updates) slotEl.classList.remove("is-rest-hidden");
    syncWordFills(karaokeNow());
    if (restFadeTimer) cancelStageStep(restFadeTimer);
    restFadeTimer = scheduleStageStep(REST_FADE_MS, () => {
      for (const { slotEl } of updates) slotEl.classList.remove("is-rest-fade");
      restFadeTimer = null;
    });
  });
}

function showLeadInPair(currentIndex, t) {
  const nextLine = lyricLines[currentIndex] || null;
  const after = upcomingLineIfReady(currentIndex, t);
  stackPending = false;
  dualPending = null;
  wordNodes = [];

  const currentSlot = lineCurrentEl;
  const nextSlot = lineNextEl;

  const updates = [{ slotEl: currentSlot, line: nextLine, trackWords: true }];
  if (lyricsLayout === "dual") updates[0].role = "active";
  updates.push({
    slotEl: nextSlot,
    line: after,
    role: lyricsLayout === "dual" ? "idle" : undefined,
  });
  fadeSlotsIn(updates);
}

function slotsAreClear() {
  return lineCurrentEl.classList.contains("is-empty") && lineNextEl.classList.contains("is-empty");
}

function leadInSlotEl(_targetIndex) {
  return lineCurrentEl;
}

function hideApproachBar() {
  if (!approachEl) return;
  approachEl.classList.remove("is-on");
  approachEl.style.transform = "";
  approachEl.style.height = "";
  approachInkCache = null;
}

let approachMetricsCtx = null;
/** @type {{ wordEl: HTMLElement, topOffset: number, leftOffset: number, height: number } | null} */
let approachInkCache = null;

function glyphMetricsFor(el) {
  const style = getComputedStyle(el);
  if (!approachMetricsCtx) {
    approachMetricsCtx = document.createElement("canvas").getContext("2d");
  }
  approachMetricsCtx.font = style.font;
  const text = (el.textContent || "H").trim() || "H";
  const metrics = approachMetricsCtx.measureText(text);
  const ascent = metrics.actualBoundingBoxAscent;
  const descent = metrics.actualBoundingBoxDescent;
  const left = Number.isFinite(metrics.actualBoundingBoxLeft) ? metrics.actualBoundingBoxLeft : 0;
  if (ascent > 0) return { ascent, descent: Math.max(0, descent), left };
  const fontSize = parseFloat(style.fontSize) || 48;
  return { ascent: fontSize * 0.7, descent: 0, left };
}

function textInkRect(el) {
  const box = el.getBoundingClientRect();
  if (approachInkCache?.wordEl === el) {
    return {
      top: box.top + approachInkCache.topOffset,
      left: box.left + approachInkCache.leftOffset,
      height: approachInkCache.height,
    };
  }
  const base = el.querySelector(".k-word-base") || el;
  const { ascent, descent, left } = glyphMetricsFor(base);
  const probe = document.createElement("span");
  probe.setAttribute("aria-hidden", "true");
  probe.style.cssText =
    "display:inline-block;width:0;height:1px;padding:0;border:0;margin:0;vertical-align:baseline;overflow:hidden;";
  base.appendChild(probe);
  const baseline = probe.getBoundingClientRect().bottom;
  probe.remove();
  const height = ascent + descent;
  const topOffset = baseline - ascent - box.top;
  const leftOffset = left;
  approachInkCache = { wordEl: el, topOffset, leftOffset, height };
  return { top: box.top + topOffset, left: box.left + leftOffset, height };
}

function syncApproachBar(t) {
  if (!approachEl || activeLineIndex < 0) {
    hideApproachBar();
    return;
  }
  const targetIndex = approachLineIndex(activeLineIndex, t);
  const line = targetIndex >= 0 ? lyricLines[targetIndex] : null;
  const slotEl = targetIndex >= 0 ? leadInSlotEl(targetIndex) : null;
  const firstWord = slotEl?.querySelector(".k-word");
  if (!line || !firstWord || slotEl.classList.contains("is-empty")) {
    hideApproachBar();
    return;
  }

  const start = lineTimeSpan(line, targetIndex).start;
  const begin = start - UPCOMING_LEAD_IN;
  const progress = Math.min(1, Math.max(0, (t - begin) / Math.max(0.001, start - begin)));

  const stackRect = kStackEl.getBoundingClientRect();
  const ink = textInkRect(firstWord);
  const barWidth = approachEl.offsetWidth || 5;
  const travel = Math.min(240, Math.max(120, stackRect.width * 0.22));
  const x = ink.left - stackRect.left - barWidth - travel * (1 - progress);
  const y = ink.top - stackRect.top;

  approachEl.style.height = `${ink.height}px`;
  approachEl.style.transform = `translate(${x}px, ${y}px)`;
  approachEl.classList.add("is-on");
}

function syncVerseRest(t) {
  const index = activeLineIndex;
  if (index < 0) return;

  if (isLyricHold(index, t)) {
    restLeadInActive = false;
    const fading =
      lineCurrentEl.classList.contains("is-refreshing") ||
      lineNextEl.classList.contains("is-refreshing");
    if (restHoldActive && (slotsAreClear() || fading)) return;
    restHoldActive = true;
    fadeSlotsOut([lineCurrentEl, lineNextEl]);
    if (lyricsLayout === "dual" && isRestHold(index, t)) {
      const upcoming = lyricLines[index + 1];
      if (upcoming) dualPending = { slotEl: lineCurrentEl, line: upcoming };
    } else {
      stackPending = true;
    }
    return;
  }

  const leadIndex = leadInLineIndex(index, t);
  if (leadIndex >= 0) {
    if (restLeadInActive) return;
    restHoldActive = false;
    restLeadInActive = true;
    if (restFadeTimer) {
      cancelStageStep(restFadeTimer);
      restFadeTimer = null;
    }
    showLeadInPair(leadIndex, t);
    return;
  }

  restHoldActive = false;
  restLeadInActive = false;
}

function maybeRevealDualUpcoming(t) {
  if (!dualPending || lyricsLayout !== "dual") return;
  if (activeLineIndex < 0) return;
  if (isLyricHold(activeLineIndex, t) || isLyricLeadIn(activeLineIndex, t)) return;
  if (!upcomingReady(activeLineIndex, t)) return;
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

function maybeRevealStackUpcoming(t) {
  if (!stackPending || lyricsLayout !== "stack") return;
  if (activeLineIndex < 0) return;
  if (isLyricHold(activeLineIndex, t) || isLyricLeadIn(activeLineIndex, t)) return;
  if (!upcomingReady(activeLineIndex, t)) return;
  stackPending = false;
  const next = lyricLines[activeLineIndex + 1] || null;
  refreshSlotSoft(lineNextEl, next);
}

function refreshSlotSoft(slotEl, line) {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) {
    fillSlot(slotEl, line);
    setSlotRole(slotEl, "idle");
    return;
  }
  if (slotEl.classList.contains("is-empty") && line) {
    fillSlot(slotEl, line);
    setSlotRole(slotEl, "idle");
    slotEl.classList.add("is-refreshing");
    afterStyleFlush(() => slotEl.classList.remove("is-refreshing"));
    return;
  }
  slotEl.classList.add("is-refreshing");
  if (dualRefreshTimer) cancelStageStep(dualRefreshTimer);
  dualRefreshTimer = scheduleStageStep(160, () => {
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
    afterStyleFlush(() => slotEl.classList.remove("is-refreshing"));
    dualRefreshTimer = null;
  });
}

function showStackLines(index, animate) {
  const t = karaokeNow();
  const { current, next } = stackLinesFor(index, t);
  restHoldActive = isLyricHold(index, t);
  restLeadInActive = isLyricLeadIn(index, t);
  stackPending = Boolean(
    !isLyricHold(index, t) && !isLyricLeadIn(index, t) && lyricLines[index + 1] && !next,
  );
  wordNodes = [];
  lineCurrentEl.classList.remove("is-active", "is-idle");
  lineNextEl.classList.remove("is-active", "is-idle");

  const currentMatch = current
    ? slotMatchesLine(lineCurrentEl, current)
    : lineCurrentEl.classList.contains("is-empty");
  const nextMatch = next ? slotMatchesLine(lineNextEl, next) : lineNextEl.classList.contains("is-empty");
  if (currentMatch && nextMatch) {
    if (current) bindSlotWords(lineCurrentEl, current);
    syncWordFills(t);
    return;
  }

  const fromEmpty = lineCurrentEl.classList.contains("is-empty") && lineNextEl.classList.contains("is-empty");
  if (current && (fromEmpty || isLyricLeadIn(index, t))) {
    fadeSlotsIn([
      { slotEl: lineCurrentEl, line: current, trackWords: true },
      { slotEl: lineNextEl, line: next },
    ]);
    return;
  }

  if (!animate || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    clearLineRoll();
    fillSlot(lineCurrentEl, current, { trackWords: true });
    fillSlot(lineNextEl, next);
    syncWordFills(karaokeNow());
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

  afterStyleFlush(() => {
    kStackEl.classList.add("is-rolling");
    lineCurrentEl.classList.remove("is-rising");
    lineNextEl.classList.remove("is-entering");
    syncWordFills(karaokeNow());
  });

  lineSwapTimer = scheduleStageStep(580, () => {
    clearLineRoll();
    syncWordFills(karaokeNow());
  });
}

function showDualLines(index, sequential) {
  const current = lyricLines[index] || null;
  const upcoming = lyricLines[index + 1] || null;
  const previous = index > 0 ? lyricLines[index - 1] : null;
  const activeOnTop = dualActiveOnTop(index);
  const activeSlot = activeOnTop ? lineCurrentEl : lineNextEl;
  const idleSlot = activeOnTop ? lineNextEl : lineCurrentEl;
  const t = karaokeNow();
  restHoldActive = isLyricHold(index, t);
  restLeadInActive = isLyricLeadIn(index, t);

  if (isLyricHold(index, t)) {
    clearLineRoll();
    wordNodes = [];
    fillSlot(lineCurrentEl, null);
    fillSlot(lineNextEl, null);
    setSlotRole(lineCurrentEl, "idle");
    setSlotRole(lineNextEl, "idle");
    if (upcoming && isRestHold(index, t)) dualPending = { slotEl: idleSlot, line: upcoming };
    return;
  }

  const leadIndex = leadInLineIndex(index, t);
  if (leadIndex >= 0) {
    clearLineRoll();
    showLeadInPair(leadIndex, t);
    return;
  }

  if (
    sequential &&
    slotMatchesLine(activeSlot, current) &&
    (upcoming ? slotMatchesLine(idleSlot, upcoming) : idleSlot.classList.contains("is-empty"))
  ) {
    setSlotRole(activeSlot, "active");
    setSlotRole(idleSlot, "idle");
    bindSlotWords(activeSlot, current);
    syncWordFills(t);
    return;
  }

  clearLineRoll();

  if (!sequential) {
    wordNodes = [];
    fillSlot(activeSlot, current, { trackWords: true });
    setSlotRole(activeSlot, "active");

    // First pair shows both lines. Later, keep the finished line until the
    // active one passes its first quarter, then reveal the next upcoming phrase.
    const ready = upcomingReady(index, t);
    const pairStart = index === dualPairOriginFor(index);
    const showUpcoming = ready && (pairStart || activeLineProgress(t, index) >= 0.25);
    if (showUpcoming) {
      fillSlot(idleSlot, upcoming);
      setSlotRole(idleSlot, "idle");
      if (!upcoming) idleSlot.classList.add("is-empty");
    } else {
      fillSlot(idleSlot, pairStart ? null : previous);
      setSlotRole(idleSlot, "idle");
      if (!pairStart && previous) markSlotSung(idleSlot);
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
  stackPending = false;
  dualPending = null;
  restHoldActive = false;
  restLeadInActive = false;
  hideApproachBar();
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
  if (stageCapture) return;
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
  const t = karaokeNow();

  let lineIndex = 0;
  for (let i = 0; i < lyricLines.length; i += 1) {
    if (lyricLines[i].time <= t + 0.02) lineIndex = i;
    else break;
  }
  setActiveLine(lineIndex);
  syncWordFills(t);
  maybeRevealDualUpcoming(t);
  maybeRevealStackUpcoming(t);
  syncVerseRest(t);
  syncApproachBar(t);
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
  const ratingBit = ratingFilterLabel();
  const visibleCount = tracks.length;
  if (lyricsFilterMode === "hidden") {
    const count = hiddenTracks.length;
    if (!count) {
      libraryMeta.textContent = `Cap cançó oculta (de ${total} al disc)`;
    } else if (ratingBit && !visibleCount) {
      libraryMeta.textContent = `Cap cançó oculta amb ${ratingBit} (de ${count})`;
    } else {
      const bits = [
        ratingBit
          ? `${visibleCount} ocultes · ${ratingBit}`
          : `${count} cançons ocultes sense lletra`,
      ];
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
    } else if (ratingBit && !visibleCount) {
      libraryMeta.textContent = `Cap cançó amb ${ratingBit} (de ${count})`;
    } else {
      const bits = [ratingBit ? `${visibleCount} cançons · ${ratingBit}` : `${count} cançons`];
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
  } else if (ratingBit && !visibleCount) {
    libraryMeta.textContent = `Cap cançó amb ${ratingBit} (de ${playableTracks.length} amb lletra)`;
  } else if (hidden || pending || errors) {
    const bits = [
      ratingBit
        ? `${visibleCount} cançons · ${ratingBit}`
        : `${playableTracks.length} cançons amb lletra`,
    ];
    if (hidden - errors > 0) bits.push(`${hidden - errors} amagades sense lletra`);
    if (errors) bits.push(`${errors} amb error de connexió`);
    if (pending) bits.push(`${pending} sense comprovar`);
    libraryMeta.textContent = bits.join(" · ");
  } else {
    libraryMeta.textContent = ratingBit
      ? `${visibleCount} cançons · ${ratingBit}`
      : `${playableTracks.length} cançons a punt · tria’n una per cantar`;
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

async function openSong(trackId, { autoplay = true } = {}) {
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
  audioClockReady = false;
  player.src = audioUrlFor(trackId, useInstrumental ? "instrumental" : "original");
  resetAudioClock();
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
    if (autoplay) await player.play().catch(() => {});
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
ratingFilterToggle?.addEventListener("click", (event) => {
  const btn = event.target?.closest?.("[data-rating-filter]");
  if (!btn || !ratingFilterToggle.contains(btn)) return;
  setRatingFilterMode(btn.dataset.ratingFilter);
});
muteOffBtn?.addEventListener("click", () => setAudioMuted(false));
muteOnBtn?.addEventListener("click", () => setAudioMuted(true));
lyricsLayoutStackBtn?.addEventListener("click", () => setLyricsLayout("stack"));
lyricsLayoutDualBtn?.addEventListener("click", () => setLyricsLayout("dual"));
lyricsSizeToggle?.addEventListener("click", (event) => {
  const btn = event.target.closest("[data-lyrics-size]");
  if (btn) setLyricsSize(btn.getAttribute("data-lyrics-size"));
});
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
fillRatingWidget(songRating);
applyLyricsFilterMode();
applyRatingFilterMode();
applyLibraryBrowseMode();
applyAudioMute();
applyLyricsLayout();
applyLyricsSize();
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
exportVideoBtn?.addEventListener("click", () => {
  exportSelectedKaraokeVideo();
});
// exportCancelBtn?.addEventListener("click", () => {
//   cancelVideoQueue();
// });
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
  markAudioClockReady();
  startTicker();
  updatePlayButton();
  syncYoutubeToAudio();
});
player.addEventListener("playing", () => {
  markAudioClockReady();
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
  if (stageCapture && !stageCapture.aborted) {
    finishStageCapture();
    return;
  }
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
