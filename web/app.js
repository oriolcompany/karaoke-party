const viewTitle = document.getElementById("view-title");
const viewMenu = document.getElementById("view-menu");
const viewStage = document.getElementById("view-stage");
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
const audioModeToggle = document.getElementById("audioModeToggle");
const audioModeOriginalBtn = document.getElementById("audioModeOriginalBtn");
const audioModeInstrumentalBtn = document.getElementById("audioModeInstrumentalBtn");
const audioModeStatus = document.getElementById("audioModeStatus");
const generateStemsBtn = document.getElementById("generateStemsBtn");
const stemsSettingsStatus = document.getElementById("stemsSettingsStatus");
const cacheSongSearch = document.getElementById("cacheSongSearch");
const cacheSongSelect = document.getElementById("cacheSongSelect");
const cacheSongMeta = document.getElementById("cacheSongMeta");
const cacheFlags = document.getElementById("cacheFlags");
const cacheScopeLyrics = document.getElementById("cacheScopeLyrics");
const cacheScopeAligned = document.getElementById("cacheScopeAligned");
const cacheScopeStems = document.getElementById("cacheScopeStems");
const cacheScopeCover = document.getElementById("cacheScopeCover");
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
const AUDIO_MODE_KEY = "karaoke-audio-mode";
const MUTE_KEY = "karaoke-muted";
let coverBust = 0;

function loadLyricsLayout() {
  const stored = localStorage.getItem(LYRICS_LAYOUT_KEY);
  return stored === "dual" ? "dual" : "stack";
}

function loadAudioMode() {
  return localStorage.getItem(AUDIO_MODE_KEY) === "instrumental" ? "instrumental" : "original";
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
const PREVIEW_FADE_MS = 320;
let previewCtx = null;
let previewGains = [null, null];
let previewMasterGain = null;
let previewGraphReady = false;
let browseMode = localStorage.getItem(VIEW_MODE_KEY) === "grid" ? "grid" : "cover";
let libraryBrowseMode =
  localStorage.getItem(LIBRARY_BROWSE_KEY) === "album" ? "album" : "song";
let lyricsFilterMode = loadLyricsFilterMode();
let audioMuted = localStorage.getItem(MUTE_KEY) === "1";
let lyricsLayout = loadLyricsLayout();
let audioMode = loadAudioMode();
let stemsAvailable = false;
let stemsJobTimer = 0;
let stemsBulkTimer = 0;
let openedAlbum = null;
let alignMode = loadAlignMode();
let currentId = null;
let lyricLines = [];
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

function showTitleScreen() {
  clearStageOutro();
  viewTitle?.classList.remove("hidden");
  viewMenu.classList.add("hidden");
  viewStage.classList.add("hidden");
  document.body.classList.add("mode-title");
  document.body.classList.remove("mode-stage");
  viewStage.classList.remove("is-live");
  player.pause();
  stopTicker();
  stopAlignPoll();
  currentId = null;
  updatePlayButton();
  titleRootInput?.focus();
}

function showMenu() {
  clearStageOutro();
  viewTitle?.classList.add("hidden");
  viewMenu.classList.remove("hidden");
  viewStage.classList.add("hidden");
  document.body.classList.remove("mode-title");
  document.body.classList.remove("mode-stage");
  viewStage.classList.remove("is-live");
  player.pause();
  stopTicker();
  stopAlignPoll();
  currentId = null;
  updatePlayButton();
  renderSongs(searchEl.value);
}

function beginStageOutro() {
  clearStageOutro();
  viewStage.classList.remove("is-live");
  viewStage.classList.add("is-outro");
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

function audioUrlFor(trackId, mode) {
  const base = `/api/audio/${encodeURI(trackId)}`;
  return mode === "instrumental" ? `${base}?mode=instrumental` : base;
}

function setStemStatus(text) {
  if (audioModeStatus) audioModeStatus.textContent = text || "";
}

function applyAudioModeButtons() {
  const instrumental = audioMode === "instrumental";
  audioModeOriginalBtn?.classList.toggle("is-active", !instrumental);
  audioModeInstrumentalBtn?.classList.toggle("is-active", instrumental);
  audioModeOriginalBtn?.setAttribute("aria-pressed", instrumental ? "false" : "true");
  audioModeInstrumentalBtn?.setAttribute("aria-pressed", instrumental ? "true" : "false");
  if (audioModeToggle) audioModeToggle.hidden = !stemsAvailable;
}

function applyStemsAvailability(data) {
  stemsAvailable = !!data.stems_available;
  applyAudioModeButtons();
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

function applyAudioMute() {
  muteOffBtn?.classList.toggle("is-active", !audioMuted);
  muteOnBtn?.classList.toggle("is-active", audioMuted);
  muteOffBtn?.setAttribute("aria-pressed", audioMuted ? "false" : "true");
  muteOnBtn?.setAttribute("aria-pressed", audioMuted ? "true" : "false");
  if (player) player.muted = audioMuted;
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

function crossfadePreview(fromIndex, toIndex, token) {
  if (!previewCtx) return;
  const fromGain = previewGains[fromIndex];
  const toGain = previewGains[toIndex];
  const fromEl = previewPlayers[fromIndex];
  const fromAlive = fromEl && !fromEl.paused && !fromEl.ended && fromGain.gain.value > 0.01;
  const now = previewCtx.currentTime;
  const dur = PREVIEW_FADE_MS / 1000;
  const steps = 32;
  const fadeOut = new Float32Array(steps);
  const fadeIn = new Float32Array(steps);
  for (let i = 0; i < steps; i += 1) {
    const t = i / (steps - 1);
    const angle = t * (Math.PI / 2);
    fadeOut[i] = fromAlive ? Math.cos(angle) : 0;
    fadeIn[i] = Math.sin(angle);
  }
  fromGain.gain.cancelScheduledValues(now);
  toGain.gain.cancelScheduledValues(now);
  fromGain.gain.setValueAtTime(fromAlive ? Math.max(fromGain.gain.value, 0.001) : 0, now);
  toGain.gain.setValueAtTime(Math.max(toGain.gain.value, 0.0001), now);
  if (fromAlive) fromGain.gain.setValueCurveAtTime(fadeOut, now, dur);
  else fromGain.gain.setValueAtTime(0, now);
  toGain.gain.setValueCurveAtTime(fadeIn, now, dur);

  previewFadeTimer = setTimeout(() => {
    previewFadeTimer = 0;
    if (token !== previewToken) return;
    setPreviewGain(fromIndex, 0);
    clearPreviewElement(fromEl);
    setPreviewGain(toIndex, 1);
    previewActive = toIndex;
    setTimeout(() => {
      if (token === previewToken) armUpcomingPreview();
    }, 400);
  }, PREVIEW_FADE_MS + 40);
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

function sleepPreview(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForPreviewPrimed(el, token, minTime = 0.15) {
  const deadline = performance.now() + 1800;
  while (performance.now() < deadline) {
    if (token !== previewToken) return false;
    if (
      !el.paused &&
      !el.ended &&
      el.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA &&
      el.currentTime >= minTime
    ) {
      return true;
    }
    await sleepPreview(16);
  }
  return !el.paused && !el.ended && token === previewToken;
}

async function playPreviewForSelection() {
  const track = selectedTrack();
  if (!track) {
    stopPreview();
    return;
  }
  await ensurePreviewGraph();
  settlePreviewRoles();
  const token = ++previewToken;
  const { current, next, currentIndex, nextIndex } = previewSlots();

  // Already playing this track — keep it, and arm the following one.
  if (previewHasTrack(current, track.id) && !current.paused && !current.ended) {
    setPreviewGain(currentIndex, 1);
    setTimeout(() => {
      if (token === previewToken) armUpcomingPreview();
    }, 200);
    return;
  }

  // Keep the current song audible until the next one is really producing audio.
  if (!current.paused && !current.ended) setPreviewGain(currentIndex, 1);
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
    const primed = await waitForPreviewPrimed(next, token, 0.15);
    if (token !== previewToken) {
      silencePreviewElement(next, nextIndex);
      return;
    }
    if (!primed && (current.paused || current.ended)) {
      setPreviewGain(nextIndex, 1);
      previewActive = nextIndex;
      return;
    }
    crossfadePreview(currentIndex, nextIndex, token);
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
  if (idx >= 0) setSelectedIndex(idx, { play: true });
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
    resyncCoverBtn.hidden = false;
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
  const bust = coverBust ? `?t=${coverBust}` : "";
  img.src = `/api/cover/${encodeURI(track.id)}${bust}`;
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
      await runQueuedAlign(trackId);
      markTrackAligned(trackId);
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

function setSelectedIndex(index, { play = true } = {}) {
  const list = browseList();
  if (!list.length) {
    selectedIndex = 0;
    updateCoverMeta();
    stopPreview();
    return;
  }
  const next = ((index % list.length) + list.length) % list.length;
  selectedIndex = next;
  layoutCovers();
  layoutGridSelection();
  updateCoverMeta();
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
  });
}

function applyAlignedLyrics(payload) {
  renderLyrics(payload);
  lyricsStatus.textContent = `Alineat per paraules · ${payload.source || "whisper-align"}`;
  if (currentId) markTrackAligned(currentId);
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
  viewTitle?.classList.add("hidden");
  viewMenu.classList.add("hidden");
  viewStage.classList.remove("hidden");
  document.body.classList.remove("mode-title");
  document.body.classList.add("mode-stage");
}

function buildWordNode(word) {
  const wrap = document.createElement("span");
  wrap.className = "k-word";

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
  for (const word of lineWords(line)) {
    const node = buildWordNode(word);
    slotEl.appendChild(node);
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

function renderLyrics(payload) {
  lyricLines = payload.lines || [];
  activeLineIndex = -1;
  wordNodes = [];
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
    return;
  }

  showLyricsLayout(0, false);
}

function setActiveLine(index) {
  if (index === activeLineIndex) return;
  const prev = activeLineIndex;
  const sequential = prev >= 0 && index === prev + 1;
  activeLineIndex = index;
  showLyricsLayout(index, sequential);
}

function syncWordFills(t) {
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

async function bootTitleScreen() {
  showTitleScreen();
  setTitleStatus("Connectant…", "running");
  try {
    const health = await api("/api/health");
    if (health.music_root && titleRootInput && !titleRootInput.value) {
      titleRootInput.value = health.music_root;
    }
    if (health.music_root && rootInput && !rootInput.value) {
      rootInput.value = health.music_root;
    }
    setTitleStatus("");
    refreshWhisperStatus({ pollWhileLoading: true }).catch(() => {});
  } catch (err) {
    setTitleStatus(err.message || "No s’ha pogut contactar amb l’API", "error");
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
  songTitle.textContent = track.title;
  songArtist.textContent = track.artist || "Artista desconegut";
  // Fall back to the original mix while the instrumental is still cooking.
  const wantsInstrumental = audioMode === "instrumental" && stemsAvailable;
  const useInstrumental = wantsInstrumental && !!track.has_instrumental;
  player.src = audioUrlFor(trackId, useInstrumental ? "instrumental" : "original");
  applyAudioModeButtons();
  setStemStatus("");
  if (wantsInstrumental && !useInstrumental) requestInstrumental(trackId);
  lyricsStatus.textContent = "Obtenint la lletra…";
  try {
    const payload = await api(`/api/lyrics?track_id=${encodeURIComponent(trackId)}`);
    renderLyrics(payload);
    if (!payload.lines.length) {
      lyricsStatus.textContent = "No hi ha lletra a LRCLIB";
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
searchEl.addEventListener("input", () => {
  selectedIndex = 0;
  renderSongs(searchEl.value);
});
coverPrev.addEventListener("click", () => setSelectedIndex(selectedIndex - 1));
coverNext.addEventListener("click", () => setSelectedIndex(selectedIndex + 1));
modeCoverBtn.addEventListener("click", () => setBrowseMode("cover"));
modeGridBtn.addEventListener("click", () => setBrowseMode("grid"));
syncStatusBtn.addEventListener("click", () => cycleAlignMode());

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
audioModeOriginalBtn?.addEventListener("click", () => setAudioMode("original"));
audioModeInstrumentalBtn?.addEventListener("click", () => setAudioMode("instrumental"));
generateStemsBtn?.addEventListener("click", () => startStemsGeneration());
albumBackBtn?.addEventListener("click", () => closeAlbum());
applyLyricsFilterMode();
applyLibraryBrowseMode();
applyAudioMute();
applyLyricsLayout();
applyAudioModeButtons();

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
    if (isSettingsOpen()) return;
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
});
player.addEventListener("playing", () => {
  startTicker();
  updatePlayButton();
});
player.addEventListener("pause", () => {
  syncKaraoke();
  updatePlayButton();
});
player.addEventListener("ended", () => {
  syncWordFills(Number.POSITIVE_INFINITY);
  beginStageOutro();
});

titleStartForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  enterLibraryFromTitle();
});
titleBrowseBtn?.addEventListener("click", () => {
  pickFolderInto(titleRootInput, { statusEl: "title" });
});
browseRootBtn?.addEventListener("click", () => {
  pickFolderInto(rootInput, { statusEl: "settings" });
});

bootTitleScreen();
startTicker();
