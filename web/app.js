const viewMenu = document.getElementById("view-menu");
const viewStage = document.getElementById("view-stage");
const coverTrack = document.getElementById("coverTrack");
const songGrid = document.getElementById("songGrid");
const coverflow = document.getElementById("coverflow");
const browsePanel = document.getElementById("browsePanel");
const searchEl = document.getElementById("search");
const rootInput = document.getElementById("rootInput");
const loadBtn = document.getElementById("loadBtn");
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

const GENERIC_COVER = "/album-generic.png";
const COVER_VISIBLE = 4;
const VIEW_MODE_KEY = "karaoke-browse-mode";

let tracks = [];
let filteredTracks = [];
let selectedIndex = 0;
let previewToken = 0;
let browseMode = localStorage.getItem(VIEW_MODE_KEY) === "grid" ? "grid" : "cover";
let currentId = null;
let lyricLines = [];
let activeLineIndex = -1;
let wordNodes = [];
let lineSwapTimer = null;
let rafId = 0;
let alignPollTimer = 0;
let alignToken = 0;
let libraryPollTimer = 0;

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

function showMenu() {
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
    singBtn.disabled = true;
    return;
  }
  coverArtist.textContent = track.artist || "Artista desconegut";
  coverTitle.textContent = track.title || track.relpath;
  coverIndex.textContent = `${selectedIndex + 1}/${filteredTracks.length}`;
  singBtn.disabled = false;
}

function applyBrowseMode() {
  browsePanel.dataset.mode = browseMode;
  coverflow.hidden = browseMode !== "cover";
  songGrid.hidden = browseMode !== "grid";
  modeCoverBtn.classList.toggle("is-active", browseMode === "cover");
  modeGridBtn.classList.toggle("is-active", browseMode === "grid");
  coverPrev.hidden = browseMode !== "cover";
  coverNext.hidden = browseMode !== "cover";
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
    btn.appendChild(coverImageFor(track));
    btn.addEventListener("click", () => {
      if (index === selectedIndex) {
        openSong(track.id);
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
    btn.appendChild(coverImageFor(track));
    const artist = document.createElement("p");
    artist.className = "grid-artist";
    artist.textContent = track.artist || "Artista desconegut";
    const title = document.createElement("p");
    title.className = "grid-title";
    title.textContent = track.title || track.relpath;
    btn.append(artist, title);
    btn.addEventListener("click", () => {
      if (index === selectedIndex) {
        openSong(track.id);
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
    if (!needle) return true;
    return `${t.title} ${t.artist} ${t.album}`.toLowerCase().includes(needle);
  });

  applyBrowseMode();
  coverTrack.innerHTML = "";
  songGrid.innerHTML = "";

  if (!filteredTracks.length) {
    stopPreview();
    coverArtist.textContent = "";
    coverTitle.textContent = tracks.length ? "Cap resultat" : "Sense cançons";
    coverIndex.textContent = "";
    singBtn.disabled = true;
    const empty = document.createElement("p");
    empty.className = "cover-empty";
    empty.textContent = tracks.length
      ? "Cap resultat amb aquesta cerca."
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
    if (job.status === "running" && job.job_id) {
      alignPollTimer = setInterval(() => {
        pollAlignJob(job.job_id, trackId, token);
      }, 1500);
      return;
    }
    lyricsStatus.textContent = job.error || "L’alineació no s’ha iniciat";
  } catch (err) {
    if (token !== alignToken || currentId !== trackId) return;
    lyricsStatus.textContent = err.message || "Error d’alineació";
  }
}

function showStage() {
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
  const probe = data.probe || {};

  if (!data.root) {
    libraryMeta.textContent = "Carrega una carpeta de MP3s etiquetats per començar la nit";
  } else if (probe.running) {
    libraryMeta.textContent = `Buscant lletres… ${probe.done || 0}/${probe.total || pending} · ${tracks.length} a punt`;
  } else if (!tracks.length && pending) {
    libraryMeta.textContent = `Comprovant lletres de ${pending} cançons…`;
  } else if (!tracks.length) {
    libraryMeta.textContent = `Cap cançó amb lletra (de ${total} al disc)`;
  } else if (hidden || pending) {
    const bits = [`${tracks.length} cançons amb lletra`];
    if (hidden) bits.push(`${hidden} amagades sense lletra`);
    if (pending) bits.push(`${pending} pendents`);
    libraryMeta.textContent = bits.join(" · ");
  } else {
    libraryMeta.textContent = `${tracks.length} cançons a punt · tria’n una per cantar`;
  }

  const keepPlaying = Boolean(previousId);
  renderSongs(searchEl.value, { play: false });
  if (previousId) {
    const idx = filteredTracks.findIndex((t) => t.id === previousId);
    if (idx >= 0) {
      selectedIndex = idx;
      layoutCovers();
      layoutGridSelection();
      updateCoverMeta();
    }
  } else if (!keepPlaying && filteredTracks.length && !viewMenu.classList.contains("hidden")) {
    playPreviewForSelection();
  }
}

function stopLibraryPoll() {
  if (libraryPollTimer) {
    clearInterval(libraryPollTimer);
    libraryPollTimer = 0;
  }
}

function startLibraryPoll() {
  stopLibraryPoll();
  libraryPollTimer = setInterval(() => {
    api("/api/library")
      .then((data) => {
        updateLibraryMeta(data);
        const pending = data.pending || 0;
        const running = data.probe && data.probe.running;
        if (!pending && !running) stopLibraryPoll();
      })
      .catch(() => {});
  }, 2000);
}

async function loadLibrary() {
  libraryMeta.textContent = "Carregant la biblioteca…";
  const data = await api("/api/library");
  updateLibraryMeta(data);
  if ((data.pending || 0) > 0 || (data.probe && data.probe.running)) {
    startLibraryPoll();
  }
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
backBtn.addEventListener("click", showMenu);
searchEl.addEventListener("input", () => {
  selectedIndex = 0;
  renderSongs(searchEl.value);
});
coverPrev.addEventListener("click", () => setSelectedIndex(selectedIndex - 1));
coverNext.addEventListener("click", () => setSelectedIndex(selectedIndex + 1));
modeCoverBtn.addEventListener("click", () => setBrowseMode("cover"));
modeGridBtn.addEventListener("click", () => setBrowseMode("grid"));
singBtn.addEventListener("click", () => {
  const track = selectedTrack();
  if (track) openSong(track.id);
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
      const track = selectedTrack();
      if (track) openSong(track.id);
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
  stopTicker();
  updatePlayButton();
});

loadLibrary().catch((err) => {
  libraryMeta.textContent = "Arrenca el servidor i carrega una carpeta";
  lyricsStatus.textContent = err.message || "No s’ha pogut contactar amb l’API";
});
startTicker();
