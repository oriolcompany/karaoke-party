const viewMenu = document.getElementById("view-menu");
const viewStage = document.getElementById("view-stage");
const coverTrack = document.getElementById("coverTrack");
const songGrid = document.getElementById("songGrid");
const coverflow = document.getElementById("coverflow");
const browsePanel = document.getElementById("browsePanel");
const searchEl = document.getElementById("search");
const rootInput = document.getElementById("rootInput");
const loadBtn = document.getElementById("loadBtn");
const retryLyricsBtn = document.getElementById("retryLyricsBtn");
const backBtn = document.getElementById("backBtn");
const player = document.getElementById("player");
const previewPlayer = document.getElementById("previewPlayer");
const lyricsEl = document.getElementById("lyrics");
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

const GENERIC_COVER = "/album-generic.png";
const COVER_VISIBLE = 4;
const VIEW_MODE_KEY = "karaoke-browse-mode";
const ALIGN_MODE_KEY = "karaoke-align-mode";

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

let tracks = [];
let filteredTracks = [];
let selectedIndex = 0;
let previewToken = 0;
let browseMode = localStorage.getItem(VIEW_MODE_KEY) === "grid" ? "grid" : "cover";
let alignMode = loadAlignMode();
let currentId = null;
let lyricLines = [];
let activeLineIndex = -1;
let wordNodes = [];
let lineSwapTimer = null;
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

function showMenu() {
  clearStageOutro();
  viewMenu.classList.remove("hidden");
  viewStage.classList.add("hidden");
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

function stopPreview() {
  previewToken += 1;
  previewPlayer.pause();
  previewPlayer.removeAttribute("src");
  previewPlayer.load();
}

function playPreviewForSelection() {
  const track = filteredTracks[selectedIndex];
  if (!track) {
    stopPreview();
    return;
  }
  const token = ++previewToken;
  previewPlayer.src = `/api/audio/${encodeURI(track.id)}`;
  previewPlayer.currentTime = 0;
  previewPlayer.play().catch(() => {
    if (token !== previewToken) return;
  });
}

function selectedTrack() {
  return filteredTracks[selectedIndex] || null;
}

function updateCoverMeta() {
  const track = selectedTrack();
  if (!track) {
    coverArtist.textContent = "";
    coverTitle.textContent = "";
    coverIndex.textContent = "";
    updatePrimaryAction();
    return;
  }
  coverArtist.textContent = track.artist || "Artista desconegut";
  coverTitle.textContent = track.title || track.relpath;
  coverIndex.textContent = `${selectedIndex + 1}/${filteredTracks.length}`;
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
  img.src = `/api/cover/${encodeURI(track.id)}`;
  img.alt = "";
  img.draggable = false;
  img.loading = "lazy";
  img.onerror = () => {
    img.onerror = null;
    img.src = GENERIC_COVER;
  };
  return img;
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

function markTrackAligned(trackId) {
  const track = tracks.find((t) => t.id === trackId);
  if (track) track.whisper_aligned = true;
  if (alignMode === "synced") {
    const previousId = selectedTrack()?.id;
    renderSongs(searchEl.value, { play: false });
    if (previousId) {
      const idx = filteredTracks.findIndex((t) => t.id === previousId);
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

function updateSyncQueueMeta() {
  const pending = syncQueue.length + (syncActiveId ? 1 : 0);
  if (!pending && !syncLastError) {
    syncQueueMeta.hidden = true;
    syncQueueMeta.textContent = "";
    return;
  }
  syncQueueMeta.hidden = false;
  if (syncActiveId) {
    const active = tracks.find((t) => t.id === syncActiveId);
    const rest = syncQueue.length;
    const pct =
      syncProgress > 0 ? ` · ${Math.round(syncProgress * 100)}%` : "";
    syncQueueMeta.textContent = rest
      ? `Sincronitzant: ${trackLabel(active)}${pct} · ${rest} més a la cua`
      : `Sincronitzant: ${trackLabel(active)}${pct}`;
    return;
  }
  if (syncLastError) {
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
  const track = selectedTrack();
  const syncActions = isSyncActionMode();
  singBtn.classList.toggle("is-sync-mode", syncActions);
  if (!track) {
    singBtn.disabled = true;
    singBtn.textContent = syncActions ? "Sincronitzar" : "Cantar";
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
  const track = selectedTrack();
  if (!track) return;
  if (isSyncActionMode()) {
    enqueueSync(track);
    return;
  }
  openSong(track.id);
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
    if (typeof job.progress === "number") {
      syncProgress = job.progress;
      updateSyncQueueMeta();
    }
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

async function processSyncQueue() {
  if (syncRunning) return;
  syncRunning = true;
  while (syncQueue.length) {
    const trackId = syncQueue.shift();
    syncQueuedIds.delete(trackId);
    const track = tracks.find((t) => t.id === trackId);
    if (!track || track.whisper_aligned) {
      refreshAlignBadges();
      updatePrimaryAction();
      continue;
    }
    syncActiveId = trackId;
    syncLastError = "";
    syncProgress = 0;
    refreshAlignBadges();
    updatePrimaryAction();
    try {
      await runQueuedAlign(trackId);
      markTrackAligned(trackId);
    } catch (err) {
      syncLastError = err.message || "Error de sincronització";
    } finally {
      syncActiveId = null;
      syncProgress = 0;
      refreshAlignBadges();
      updatePrimaryAction();
    }
  }
  syncRunning = false;
  updatePrimaryAction();
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

function setSelectedIndex(index, { play = true } = {}) {
  if (!filteredTracks.length) {
    selectedIndex = 0;
    updateCoverMeta();
    stopPreview();
    return;
  }
  const next = ((index % filteredTracks.length) + filteredTracks.length) % filteredTracks.length;
  selectedIndex = next;
  layoutCovers();
  layoutGridSelection();
  updateCoverMeta();
  if (play && !viewMenu.classList.contains("hidden")) {
    playPreviewForSelection();
  }
}

function renderCoverflowItems() {
  coverTrack.innerHTML = "";
  filteredTracks.forEach((track, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "cover-item";
    btn.dataset.index = String(index);
    btn.setAttribute("aria-label", `${track.artist || "Artista"} — ${track.title || track.relpath}`);
    btn.appendChild(coverMediaFor(track));
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
  filteredTracks.forEach((track, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "grid-card";
    btn.dataset.index = String(index);
    btn.setAttribute("aria-label", `${track.artist || "Artista"} — ${track.title || track.relpath}`);
    btn.appendChild(coverMediaFor(track));
    const artist = document.createElement("p");
    artist.className = "grid-artist";
    artist.textContent = track.artist || "Artista desconegut";
    const title = document.createElement("p");
    title.className = "grid-title";
    title.textContent = track.title || track.relpath;
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
  filteredTracks = tracks.filter((t) => {
    if (alignMode === "synced" && !t.whisper_aligned) return false;
    if (!needle) return true;
    return `${t.title} ${t.artist} ${t.album}`.toLowerCase().includes(needle);
  });

  applyBrowseMode();
  coverTrack.innerHTML = "";
  songGrid.innerHTML = "";

  if (!filteredTracks.length) {
    stopPreview();
    coverArtist.textContent = "";
    coverTitle.textContent = tracks.length
      ? alignMode === "synced"
        ? "Cap cançó sincronitzada"
        : "Cap resultat"
      : "Sense cançons";
    coverIndex.textContent = "";
    updatePrimaryAction();
    const empty = document.createElement("p");
    empty.className = "cover-empty";
    empty.textContent = tracks.length
      ? alignMode === "synced"
        ? "Encara no hi ha cançons amb lletra alineada amb Whisper."
        : "Cap resultat amb aquesta cerca."
      : "Carrega una carpeta de música per començar.";
    (browseMode === "grid" ? songGrid : coverTrack).appendChild(empty);
    return;
  }

  if (browseMode === "grid") {
    renderGridItems();
  } else {
    renderCoverflowItems();
  }

  if (selectedIndex >= filteredTracks.length) selectedIndex = 0;
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
    if (typeof job.progress === "number" && job.progress > 0) {
      const pct = Math.round(job.progress * 100);
      const phase = job.status === "queued" ? "A la cua" : "Alineant";
      lyricsStatus.textContent = `${phase} la lletra amb l’àudio… ${pct}%`;
    } else if (job.status === "queued") {
      lyricsStatus.textContent = "Alineació a la cua del servidor…";
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
  viewMenu.classList.add("hidden");
  viewStage.classList.remove("hidden");
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

function fillSlot(slotEl, line, { trackWords = false } = {}) {
  slotEl.innerHTML = "";
  slotEl.classList.remove("is-empty", "swap-out", "swap-in");
  if (!line) {
    slotEl.classList.add("is-empty");
    return;
  }
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

function showTwoLines(index, animate) {
  const current = lyricLines[index] || null;
  const next = lyricLines[index + 1] || null;
  wordNodes = [];

  if (!animate) {
    fillSlot(lineCurrentEl, current, { trackWords: true });
    fillSlot(lineNextEl, next);
    syncWordFills(player.currentTime);
    return;
  }

  lineCurrentEl.classList.add("swap-out");
  if (lineSwapTimer) clearTimeout(lineSwapTimer);
  lineSwapTimer = setTimeout(() => {
    fillSlot(lineCurrentEl, current, { trackWords: true });
    fillSlot(lineNextEl, next);
    lineCurrentEl.classList.add("swap-in");
    syncWordFills(player.currentTime);
    requestAnimationFrame(() => lineCurrentEl.classList.remove("swap-in"));
  }, 160);
}

function renderLyrics(payload) {
  lyricLines = payload.lines || [];
  activeLineIndex = -1;
  wordNodes = [];

  if (!lyricLines.length) {
    lineCurrentEl.innerHTML = "";
    lineNextEl.innerHTML = "";
    lineNextEl.classList.add("is-empty");
    const p = document.createElement("span");
    p.className = "lyrics-empty";
    p.textContent = "No s’ha trobat lletra per a aquesta cançó.";
    lineCurrentEl.appendChild(p);
    return;
  }

  showTwoLines(0, false);
}

function setActiveLine(index) {
  if (index === activeLineIndex) return;
  const animate = activeLineIndex >= 0;
  activeLineIndex = index;
  showTwoLines(index, animate);
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

function updateLibraryMeta(data) {
  const previousId = selectedTrack()?.id;
  tracks = data.tracks || [];
  rootInput.value = data.root || "";
  const pending = data.pending || 0;
  const hidden = data.hidden || 0;
  const total = data.total || 0;
  const errors = data.errors || 0;

  retryLyricsBtn.hidden = !errors;

  if (!data.root) {
    libraryMeta.textContent = "Carrega una carpeta de MP3s etiquetats per començar la nit";
  } else if (!tracks.length && pending) {
    libraryMeta.textContent = `Comprovant lletres de ${pending} cançons…`;
  } else if (!tracks.length && errors) {
    libraryMeta.textContent = `No s’ha pogut connectar a LRCLIB per ${errors} cançons · prova “Reintentar lletres”`;
  } else if (!tracks.length) {
    libraryMeta.textContent = `Cap cançó amb lletra (de ${total} al disc)`;
  } else if (hidden || pending || errors) {
    const bits = [`${tracks.length} cançons amb lletra`];
    if (hidden - errors > 0) bits.push(`${hidden - errors} amagades sense lletra`);
    if (errors) bits.push(`${errors} amb error de connexió`);
    if (pending) bits.push(`${pending} pendents`);
    libraryMeta.textContent = bits.join(" · ");
  } else {
    libraryMeta.textContent = `${tracks.length} cançons a punt · tria’n una per cantar`;
  }

  renderSongs(searchEl.value, { play: false });
  if (previousId) {
    const idx = filteredTracks.findIndex((t) => t.id === previousId);
    if (idx >= 0) {
      selectedIndex = idx;
      layoutCovers();
      layoutGridSelection();
      updateCoverMeta();
    }
  } else if (filteredTracks.length && !viewMenu.classList.contains("hidden")) {
    playPreviewForSelection();
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function loadLibrary() {
  libraryMeta.textContent = "Carregant la biblioteca…";
  let data = await api("/api/library");
  // Wait for the single in-flight probe pass (no perpetual 2s refresh after it ends).
  while (data.probe && data.probe.running) {
    const total = data.probe.total || data.pending || 0;
    const done = Math.min(data.probe.done || 0, total || 0);
    libraryMeta.textContent = `Buscant lletres… ${done}/${total} · ${(data.tracks || []).length} a punt`;
    await sleep(500);
    data = await api("/api/library");
  }
  updateLibraryMeta(data);
}

async function setRoot() {
  const path = rootInput.value.trim();
  if (!path) return;
  libraryMeta.textContent = "Carregant la biblioteca…";
  await api("/api/library/root", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  await loadLibrary();
}

async function openSong(trackId) {
  const track = tracks.find((t) => t.id === trackId);
  if (!track) return;
  stopAlignPoll();
  currentId = trackId;
  showStage();
  songTitle.textContent = track.title;
  songArtist.textContent = track.artist || "Artista desconegut";
  player.src = `/api/audio/${encodeURI(trackId)}`;
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
    libraryMeta.textContent = err.message || "Error en carregar";
  });
});
retryLyricsBtn.addEventListener("click", () => {
  retryLyricsBtn.disabled = true;
  libraryMeta.textContent = "Tornant a buscar les lletres…";
  api("/api/library/retry", { method: "POST" })
    .then(() => loadLibrary())
    .catch((err) => {
      libraryMeta.textContent = err.message || "Error en reintentar";
    })
    .finally(() => {
      retryLyricsBtn.disabled = false;
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
singBtn.addEventListener("click", () => {
  activateSelectedTrack();
});
coverTrack.addEventListener(
  "wheel",
  (event) => {
    if (browseMode !== "cover") return;
    if (!filteredTracks.length || viewMenu.classList.contains("hidden")) return;
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
    if (viewMenu.classList.contains("hidden")) return;
    if (!filteredTracks.length) return;

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
      const cols = Math.max(1, Math.floor(songGrid.clientWidth / 180));
      setSelectedIndex(selectedIndex - cols);
      return;
    }
    if (key === "ArrowDown" || key === "Down") {
      if (browseMode !== "grid") return;
      event.preventDefault();
      const cols = Math.max(1, Math.floor(songGrid.clientWidth / 180));
      setSelectedIndex(selectedIndex + cols);
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
previewPlayer.addEventListener("ended", () => {
  // Loop preview lightly so the selected song keeps playing.
  if (!viewMenu.classList.contains("hidden") && selectedTrack()) {
    previewPlayer.currentTime = 0;
    previewPlayer.play().catch(() => {});
  }
});
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

loadLibrary().catch((err) => {
  libraryMeta.textContent = "Arrenca el servidor i carrega una carpeta";
  lyricsStatus.textContent = err.message || "No s’ha pogut contactar amb l’API";
});
startTicker();
