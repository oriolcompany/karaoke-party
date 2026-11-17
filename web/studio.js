const PAGE_SIZE = 40;

const catalogState = {
  tracks: [],
  page: 0,
  selected: new Set(),
  runTimer: 0,
};

const dlState = {
  queue: [],
  running: false,
  nextId: 1,
};

function jsonRequest(path, body, method = "POST") {
  return api(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function setText(id, text, kind) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text || "";
  el.classList.toggle("is-error", kind === "error");
}

function catalogTracksFiltered() {
  const query = (document.getElementById("catFilter")?.value || "").trim().toLowerCase();
  const incompleteOnly = Boolean(document.getElementById("catOnlyIncomplete")?.checked);
  return catalogState.tracks.filter((track) => {
    if (incompleteOnly && !track.incomplete) return false;
    if (!query) return true;
    return [track.title, track.artist, track.album, track.albumartist, track.file, track.folder]
      .join(" ")
      .toLowerCase()
      .includes(query);
  });
}

function trackDirty(track) {
  const original = track.original || {};
  const fields = ["title", "artist", "album", "date", "track", "albumartist", "file"];
  if (fields.some((key) => (track[key] || "") !== (original[key] || ""))) return true;
  return Boolean(track.coverAction);
}

function syncRunLabel() {
  const write = document.getElementById("catWrite")?.checked;
  const button = document.getElementById("catRunBtn");
  if (button) button.textContent = write ? "Escriure etiquetes" : "Passada de prova";
}

async function loadCatalogSettings() {
  try {
    const settings = await api("/api/studio/catalog/settings");
    const folder = document.getElementById("catalogFolder");
    if (folder) {
      folder.textContent = settings.root
        ? `Mateixa carpeta que el karaoke: ${settings.root}`
        : "Encara no hi ha carpeta de karaoke.";
    }
    const key = document.getElementById("catAcoustidKey");
    if (key && settings.acoustid_key_hint) key.placeholder = `Desada (${settings.acoustid_key_hint})`;
    const fp = document.getElementById("catFpcalc");
    if (fp) {
      fp.textContent = settings.fpcalc_ready
        ? "AcoustID pot llegir l’empremta d’àudio."
        : "Falta fpcalc: l’empremta d’àudio no es podrà calcular.";
    }
  } catch (error) {
    setText("catRunStatus", error.message, "error");
  }
}

function renderCatalogPage() {
  const body = document.getElementById("catTable");
  if (!body) return;
  const filtered = catalogTracksFiltered();
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  if (catalogState.page >= pages) catalogState.page = pages - 1;
  if (catalogState.page < 0) catalogState.page = 0;
  const slice = filtered.slice(catalogState.page * PAGE_SIZE, (catalogState.page + 1) * PAGE_SIZE);
  body.replaceChildren();
  for (const track of slice) {
    const tr = document.createElement("tr");
    tr.classList.toggle("is-dirty", trackDirty(track));
    tr.classList.toggle("is-incomplete", track.incomplete);
    const checkCell = document.createElement("td");
    const check = document.createElement("input");
    check.type = "checkbox";
    check.checked = catalogState.selected.has(track.rel);
    check.addEventListener("change", () => {
      if (check.checked) catalogState.selected.add(track.rel);
      else catalogState.selected.delete(track.rel);
      refreshCoverPanel();
    });
    checkCell.appendChild(check);
    tr.appendChild(checkCell);
    for (const field of ["track", "title", "artist", "album", "date", "file"]) {
      const td = document.createElement("td");
      const input = document.createElement("input");
      input.type = "text";
      input.value = track[field] || "";
      input.addEventListener("input", () => {
        track[field] = field === "date" ? input.value.trim().slice(0, 4) : input.value;
        track.incomplete = !track.title || !track.artist || !track.album || !track.date;
        tr.classList.toggle("is-dirty", trackDirty(track));
        tr.classList.toggle("is-incomplete", track.incomplete);
        updateEditStatus();
        if (catalogState.selected.has(track.rel)) refreshCoverPanel();
      });
      td.appendChild(input);
      tr.appendChild(td);
    }
    tr.addEventListener("click", (event) => {
      if (event.target instanceof HTMLInputElement) return;
      catalogState.selected.clear();
      catalogState.selected.add(track.rel);
      renderCatalogPage();
    });
    body.appendChild(tr);
  }
  const label = document.getElementById("catPageLabel");
  if (label) {
    label.textContent = filtered.length
      ? `${catalogState.page + 1} / ${pages} · ${filtered.length} cançons`
      : "Cap cançó";
  }
  updateEditStatus();
  refreshCoverPanel();
}

function updateEditStatus() {
  const dirty = catalogState.tracks.filter(trackDirty).length;
  const incomplete = catalogState.tracks.filter((track) => track.incomplete).length;
  setText(
    "catEditStatus",
    catalogState.tracks.length
      ? `${dirty} sense desar · ${incomplete} incompletes · ${catalogState.tracks.length} carregades`
      : "Carrega la carpeta per editar les etiquetes."
  );
}

function selectedTracks() {
  return catalogState.tracks.filter((track) => catalogState.selected.has(track.rel));
}

function refreshCoverPanel() {
  const img = document.getElementById("catCoverImg");
  const status = document.getElementById("catCoverStatus");
  const rows = selectedTracks();
  if (!img || !status) return;
  if (!rows.length) {
    img.hidden = true;
    img.removeAttribute("src");
    status.textContent = "Selecciona una cançó";
    return;
  }
  const track = rows[0];
  const extra = rows.length > 1 ? `${rows.length} seleccionades · ` : "";
  if (track.coverAction === "remove") {
    img.hidden = true;
    img.removeAttribute("src");
    status.textContent = `${extra}Es traurà en desar`;
    return;
  }
  if (track.coverB64) {
    img.hidden = false;
    img.src = `data:${track.coverMime || "image/jpeg"};base64,${track.coverB64}`;
    status.textContent = `${extra}Portada nova, sense desar`;
    return;
  }
  if (track.has_cover) {
    const rel = encodeURIComponent(track.rel);
    img.hidden = false;
    img.src = `/api/studio/catalog/cover?rel=${rel}`;
    status.textContent = `${extra}Portada incrustada`;
    return;
  }
  img.hidden = true;
  img.removeAttribute("src");
  status.textContent = `${extra}Sense portada`;
}

async function loadCatalogTracks() {
  setText("catEditStatus", "Carregant…");
  const data = await api("/api/studio/catalog/tracks");
  const folder = document.getElementById("catalogFolder");
  if (folder) {
    folder.textContent = `Mateixa carpeta que el karaoke: ${data.root} · ${data.count} cançons`;
  }
  catalogState.tracks = data.tracks.map((track) => ({
    ...track,
    coverAction: "",
    coverB64: "",
    coverMime: "",
    original: {
      title: track.title,
      artist: track.artist,
      album: track.album,
      date: track.date,
      track: track.track,
      albumartist: track.albumartist,
      file: track.file,
    },
  }));
  catalogState.selected = new Set();
  catalogState.page = 0;
  const note = data.truncated ? " S’han mostrat les primeres 5000." : "";
  renderCatalogPage();
  setText("catEditStatus", `${data.count} cançons, ${data.incomplete} incompletes.${note}`);
}

function applyToSelected(mutator) {
  const rows = selectedTracks();
  if (!rows.length) {
    setText("catEditStatus", "Selecciona una o més cançons.", "error");
    return;
  }
  rows.forEach(mutator);
  renderCatalogPage();
}

async function runCatalog() {
  const button = document.getElementById("catRunBtn");
  if (button) button.disabled = true;
  setText("catRunStatus", "Preparant la passada…");
  document.getElementById("catResults")?.replaceChildren();
  try {
    const started = await jsonRequest("/api/studio/catalog/run", {
      write: Boolean(document.getElementById("catWrite")?.checked),
      rename_files: Boolean(document.getElementById("catRename")?.checked),
      use_musicbrainz: Boolean(document.getElementById("catMusicBrainz")?.checked),
      use_acoustid: Boolean(document.getElementById("catAcoustid")?.checked),
      only_incomplete: Boolean(document.getElementById("catIncomplete")?.checked),
      ignore_existing_tags: Boolean(document.getElementById("catIgnoreTags")?.checked),
      artist: document.getElementById("catArtist")?.value.trim() || "",
      limit: Number(document.getElementById("catLimit")?.value || 0),
    });
    if (catalogState.runTimer) clearInterval(catalogState.runTimer);
    catalogState.runTimer = setInterval(() => pollCatalog(started.job_id), 700);
    await pollCatalog(started.job_id);
  } catch (error) {
    setText("catRunStatus", error.message, "error");
    if (button) button.disabled = false;
  }
}

async function pollCatalog(jobId) {
  const bar = document.getElementById("catProgress");
  const fill = document.getElementById("catProgressFill");
  try {
    const job = await api(`/api/studio/catalog/run/${jobId}`);
    if (bar) bar.hidden = false;
    const pct = job.total ? Math.round((job.done / job.total) * 100) : 0;
    if (fill) fill.style.width = `${pct}%`;
    const current = job.current ? ` · ${job.current}` : "";
    setText(
      "catRunStatus",
      job.status === "error"
        ? job.error || "La passada ha fallat"
        : `${job.done}/${job.total || "…"} · ${job.changed} canvis · ${job.errors} errors${current}`,
      job.status === "error" ? "error" : ""
    );
    const list = document.getElementById("catResults");
    if (list) {
      list.replaceChildren();
      for (const row of (job.results || []).slice(-40).reverse()) {
        const li = document.createElement("li");
        const name = [row.artist, row.title].filter(Boolean).join(" — ") || row.path;
        li.textContent = row.error ? `${name}: ${row.error}` : `${name}${row.changed ? " · canviat" : ""}`;
        if (row.error) li.classList.add("is-error");
        list.appendChild(li);
      }
    }
    if (job.status === "done" || job.status === "error") {
      clearInterval(catalogState.runTimer);
      catalogState.runTimer = 0;
      const button = document.getElementById("catRunBtn");
      if (button) button.disabled = false;
      if (job.write && catalogState.tracks.length) loadCatalogTracks().catch(() => {});
    }
  } catch (error) {
    clearInterval(catalogState.runTimer);
    catalogState.runTimer = 0;
    setText("catRunStatus", error.message, "error");
    const button = document.getElementById("catRunBtn");
    if (button) button.disabled = false;
  }
}

async function saveCatalog() {
  const dirty = catalogState.tracks.filter(trackDirty);
  if (!dirty.length) {
    setText("catEditStatus", "No hi ha canvis per desar.");
    return;
  }
  const ok = window.confirm(`Desar ${dirty.length} cançó${dirty.length === 1 ? "" : "ns"}?`);
  if (!ok) return;
  setText("catEditStatus", "Desant…");
  try {
    const result = await jsonRequest("/api/studio/catalog/save", {
      rename: Boolean(document.getElementById("catRenameOnSave")?.checked),
      rows: dirty.map((track) => ({
        rel: track.rel,
        title: track.title || "",
        artist: track.artist || "",
        album: track.album || "",
        date: track.date || "",
        track: track.track || "",
        albumartist: track.albumartist || "",
        file: track.file || "",
        cover_action: track.coverAction || "",
        cover_b64: track.coverAction === "set" ? track.coverB64 || "" : "",
        cover_mime: track.coverMime || "",
      })),
    });
    const byRel = new Map((result.updated || []).map((item) => [item.rel, item]));
    for (const track of dirty) {
      const next = byRel.get(track.rel);
      if (!next) continue;
      if (catalogState.selected.has(track.rel)) {
        catalogState.selected.delete(track.rel);
        catalogState.selected.add(next.new_rel);
      }
      const removedCover = track.coverAction === "remove";
      const addedCover = track.coverAction === "set";
      track.rel = next.new_rel;
      track.file = next.file;
      track.coverAction = "";
      track.coverB64 = "";
      if (removedCover) track.has_cover = false;
      else if (addedCover) track.has_cover = true;
      track.original = {
        title: track.title,
        artist: track.artist,
        album: track.album,
        date: track.date,
        track: track.track,
        albumartist: track.albumartist,
        file: track.file,
      };
    }
    const errorNote = result.errors?.length ? ` ${result.errors.length} errors.` : "";
    if (result.errors?.length) {
      setText("catEditStatus", result.errors.map((item) => item.error).join(" · "), "error");
    } else {
      setText("catEditStatus", `Desades ${result.saved}, renombrades ${result.renamed}, portades ${result.covers}.${errorNote}`);
    }
    renderCatalogPage();
  } catch (error) {
    setText("catEditStatus", error.message, "error");
  }
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result || "");
      const comma = text.indexOf(",");
      resolve({ mime: file.type || "image/jpeg", data: comma >= 0 ? text.slice(comma + 1) : text });
    };
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function setCover(track, mime, data) {
  track.coverAction = "set";
  track.coverMime = mime;
  track.coverB64 = data;
  track.has_cover = true;
}

function showCatalogTab(name) {
  document.querySelectorAll("[data-cat-tab]").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.catTab === name);
  });
  document.getElementById("catalogAuto")?.toggleAttribute("hidden", name !== "auto");
  document.getElementById("catalogEdit")?.toggleAttribute("hidden", name !== "edit");
}

function selectedRadio(name, fallback) {
  const el = document.querySelector(`input[name="${name}"]:checked`);
  return el ? el.value : fallback;
}

function syncQuality() {
  const select = document.getElementById("dlQuality");
  if (!select) return;
  const video = selectedRadio("dlMode", "audio") === "video";
  const options = video
    ? [
        ["best", "Millor"],
        ["720p", "720p"],
        ["1080p", "1080p"],
      ]
    : [
        ["best", "Millor"],
        ["192k", "192 kbps"],
      ];
  const previous = select.value;
  select.replaceChildren();
  for (const [value, label] of options) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    select.appendChild(option);
  }
  if (options.some(([value]) => value === previous)) select.value = previous;
}

function formatBytes(size) {
  if (!size && size !== 0) return "";
  const units = ["B", "KB", "MB", "GB"];
  let value = size;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${value.toFixed(index ? 1 : 0)} ${units[index]}`;
}

function renderDownloadQueue() {
  const panel = document.getElementById("dlQueuePanel");
  const list = document.getElementById("dlQueue");
  const pending = dlState.queue.filter((item) => item.state === "queued" || item.state === "running");
  if (!panel || !list) return;
  panel.hidden = !pending.length;
  list.replaceChildren();
  for (const item of pending) {
    const li = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = item.state === "running" ? `En curs · ${item.url}` : item.url;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "title-browse-btn";
    remove.textContent = "Treure";
    remove.disabled = item.state === "running";
    remove.addEventListener("click", () => {
      dlState.queue = dlState.queue.filter((entry) => entry.id !== item.id);
      renderDownloadQueue();
    });
    li.append(label, remove);
    list.appendChild(li);
  }
  const submit = document.getElementById("dlSubmit");
  if (submit) submit.textContent = dlState.running ? "Afegeix a la cua" : "Descarrega";
}

function showDownloadStatus(kind, label, detail, percent) {
  const card = document.getElementById("dlStatus");
  const fill = document.getElementById("dlBarFill");
  if (card) card.hidden = false;
  setText("dlStatusLabel", label, kind);
  setText("dlStatusDetail", detail || "");
  const pct = document.getElementById("dlStatusPct");
  if (pct) pct.textContent = percent == null ? "" : `${Math.round(percent)}%`;
  if (fill) fill.style.width = percent == null ? "35%" : `${Math.max(0, Math.min(100, percent))}%`;
}

function enqueueDownload(item) {
  dlState.queue.push({ id: dlState.nextId++, state: "queued", ...item });
  renderDownloadQueue();
  runDownloadQueue();
}

async function pollDownload(jobId) {
  while (true) {
    const job = await api(`/api/studio/yt/progress/${jobId}`);
    const detail = [
      job.item_title || job.filename || "",
      job.total_items ? `${job.index || 0}/${job.total_items}` : "",
      job.failed_items ? `${job.failed_items} errors` : "",
    ]
      .filter(Boolean)
      .join(" · ");
    const labels = {
      queued: "En cua…",
      downloading: "Descarregant…",
      processing: "Processant…",
      done: "Fet",
      error: "Error",
    };
    showDownloadStatus(job.status === "error" ? "error" : job.status === "done" ? "" : "", labels[job.status] || job.status, job.error || detail, job.percent);
    if (job.status === "done" || job.status === "error") return job;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

async function runDownloadQueue() {
  if (dlState.running) return;
  const next = dlState.queue.find((item) => item.state === "queued");
  if (!next) return;
  dlState.running = true;
  next.state = "running";
  renderDownloadQueue();
  try {
    const started = await jsonRequest("/api/studio/yt/download", {
      url: next.url,
      mode: next.mode,
      quality: next.quality,
      kind: next.kind,
      destination: next.destination,
    });
    const job = await pollDownload(started.job_id);
    next.state = job.status === "error" ? "error" : "done";
  } catch (error) {
    next.state = "error";
    showDownloadStatus("error", "Error", error.message, null);
  }
  dlState.running = false;
  renderDownloadQueue();
  refreshDownloadFiles();
  refreshFailures();
  runDownloadQueue();
}

async function refreshDownloadConfig() {
  try {
    const config = await api("/api/studio/yt/config");
    const hint = document.getElementById("dlDestHint");
    const destination = selectedRadio("dlDest", "library");
    if (hint) {
      hint.textContent =
        destination === "library"
          ? config.library_root
            ? `Es desarà a ${config.library_root}`
            : "Encara no hi ha carpeta de karaoke. Tria-la a la portada o canvia la destinació."
          : `Es desarà a ${config.downloads_dir}`;
    }
    const cookies = document.getElementById("dlCookies");
    if (cookies && config.settings?.cookies_browser) cookies.value = config.settings.cookies_browser;
    const status = document.getElementById("dlCookiesStatus");
    if (status && config.settings?.cookies_txt_path) {
      status.textContent = config.settings.cookies_txt_exists
        ? `cookies.txt trobat: ${config.settings.cookies_txt_path}`
        : "Chrome i Edge sovint no comparteixen cookies. Exporta un cookies.txt.";
    }
  } catch (error) {
    setText("dlDestHint", error.message, "error");
  }
}

async function refreshDownloadFiles() {
  const destination = selectedRadio("dlDest", "library");
  const list = document.getElementById("dlFiles");
  const empty = document.getElementById("dlEmptyFiles");
  if (!list) return;
  try {
    const data = await api(`/api/studio/yt/files?destination=${destination}`);
    list.replaceChildren();
    for (const file of data.files || []) {
      const li = document.createElement("li");
      li.className = "studio-file";
      const link = document.createElement("a");
      link.href = `/api/studio/yt/file?destination=${destination}&rel=${encodeURIComponent(file.rel)}`;
      link.textContent = file.rel;
      const size = document.createElement("span");
      size.textContent = formatBytes(file.size);
      li.append(link, size);
      list.appendChild(li);
    }
    if (empty) empty.hidden = Boolean(data.files?.length);
  } catch (error) {
    if (empty) {
      empty.hidden = false;
      empty.textContent = error.message;
    }
  }
}

async function refreshFailures() {
  const list = document.getElementById("dlFailed");
  const empty = document.getElementById("dlEmptyFailed");
  const count = document.getElementById("dlFailedCount");
  if (!list) return;
  try {
    const failures = await api("/api/studio/yt/failures");
    if (count) {
      count.hidden = !failures.length;
      count.textContent = String(failures.length);
    }
    list.replaceChildren();
    for (const failure of failures) {
      const li = document.createElement("li");
      const text = document.createElement("span");
      text.textContent = `${failure.title || failure.url}: ${failure.reason || failure.error || ""}`;
      const retry = document.createElement("button");
      retry.type = "button";
      retry.className = "title-browse-btn";
      retry.textContent = "Reintentar";
      retry.addEventListener("click", async () => {
        const again = await jsonRequest(`/api/studio/yt/failures/${failure.id}/retry`, {});
        enqueueDownload({
          url: again.url,
          mode: again.mode,
          quality: again.quality,
          kind: again.kind || "single",
          destination: selectedRadio("dlDest", "library"),
        });
        refreshFailures();
      });
      li.append(text, retry);
      list.appendChild(li);
    }
    if (empty) empty.hidden = Boolean(failures.length);
  } catch (error) {
    if (empty) {
      empty.hidden = false;
      empty.textContent = error.message;
    }
  }
}

function showDownloadTab(name) {
  document.querySelectorAll("[data-dl-tab]").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.dlTab === name);
  });
  document.getElementById("dlTabFiles")?.toggleAttribute("hidden", name !== "files");
  document.getElementById("dlTabFailed")?.toggleAttribute("hidden", name !== "failed");
}

function parseUrlFile(text) {
  const seen = new Set();
  const urls = [];
  for (const rawLine of String(text || "").split(/\r?\n/)) {
    let line = rawLine.trim();
    if (!line || line.startsWith("#") || line.startsWith("//")) continue;
    const comment = line.indexOf(" #");
    if (comment >= 0) line = line.slice(0, comment).trim();
    if (!/^https?:\/\//i.test(line)) line = `https://${line}`;
    if (seen.has(line)) continue;
    seen.add(line);
    urls.push(line);
  }
  return urls;
}

function currentDownloadOptions() {
  return {
    mode: selectedRadio("dlMode", "audio"),
    quality: document.getElementById("dlQuality")?.value || "best",
    kind: selectedRadio("dlKind", "auto"),
    destination: selectedRadio("dlDest", "library"),
  };
}

function bindStudio() {
  document.querySelectorAll("[data-app-section]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const section = btn.dataset.appSection;
      if (section === "karaoke") showMenu();
      else showStudio(section);
    });
  });
  document.getElementById("titleCatalogBtn")?.addEventListener("click", () => showStudio("catalog"));
  document.getElementById("titleDownloadBtn")?.addEventListener("click", () => showStudio("downloads"));

  document.querySelectorAll("[data-cat-tab]").forEach((btn) => {
    btn.addEventListener("click", () => showCatalogTab(btn.dataset.catTab));
  });
  document.getElementById("catWrite")?.addEventListener("change", syncRunLabel);
  document.getElementById("catRunBtn")?.addEventListener("click", () => runCatalog());
  document.getElementById("catSaveKeyBtn")?.addEventListener("click", async () => {
    const value = document.getElementById("catAcoustidKey")?.value.trim();
    if (!value) {
      setText("catRunStatus", "Escriu la clau abans de desar-la.", "error");
      return;
    }
    try {
      await jsonRequest("/api/studio/catalog/settings", { acoustid_api_key: value }, "PUT");
      document.getElementById("catAcoustidKey").value = "";
      setText("catRunStatus", "Clau d’AcoustID desada.");
      loadCatalogSettings();
    } catch (error) {
      setText("catRunStatus", error.message, "error");
    }
  });
  document.getElementById("catLoadBtn")?.addEventListener("click", () => {
    loadCatalogTracks().catch((error) => setText("catEditStatus", error.message, "error"));
  });
  document.getElementById("catFilter")?.addEventListener("input", () => {
    catalogState.page = 0;
    renderCatalogPage();
  });
  document.getElementById("catOnlyIncomplete")?.addEventListener("change", () => {
    catalogState.page = 0;
    renderCatalogPage();
  });
  document.getElementById("catPrevPage")?.addEventListener("click", () => {
    catalogState.page -= 1;
    renderCatalogPage();
  });
  document.getElementById("catNextPage")?.addEventListener("click", () => {
    catalogState.page += 1;
    renderCatalogPage();
  });
  document.getElementById("catSelectAllBtn")?.addEventListener("click", () => {
    catalogState.selected = new Set(catalogTracksFiltered().map((track) => track.rel));
    renderCatalogPage();
  });
  document.getElementById("catFillBtn")?.addEventListener("click", () => {
    const field = document.getElementById("catFillField")?.value || "artist";
    const value = document.getElementById("catFillValue")?.value ?? "";
    applyToSelected((track) => {
      track[field] = field === "date" ? value.trim().slice(0, 4) : value.trim();
      track.incomplete = !track.title || !track.artist || !track.album || !track.date;
    });
  });
  document.getElementById("catNumberBtn")?.addEventListener("click", () => {
    const start = Number(document.getElementById("catNumberStart")?.value || 1);
    let index = 0;
    applyToSelected((track) => {
      track.track = String(start + index);
      index += 1;
    });
  });
  document.getElementById("catSaveBtn")?.addEventListener("click", () => saveCatalog());
  document.getElementById("catCoverFileBtn")?.addEventListener("click", () => {
    document.getElementById("catCoverFile")?.click();
  });
  document.getElementById("catCoverFile")?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const rows = selectedTracks();
    if (!rows.length) {
      setText("catCoverStatus", "Selecciona una cançó", "error");
      return;
    }
    const encoded = await readFileAsBase64(file);
    setCover(rows[0], encoded.mime, encoded.data);
    renderCatalogPage();
  });
  document.getElementById("catCoverSearchBtn")?.addEventListener("click", async () => {
    const track = selectedTracks()[0];
    if (!track) {
      setText("catCoverStatus", "Selecciona una cançó", "error");
      return;
    }
    setText("catCoverStatus", "Cercant portada…");
    try {
      const found = await jsonRequest("/api/studio/catalog/cover/search", {
        artist: track.artist,
        title: track.title,
        album: track.album,
      });
      setCover(track, found.mime, found.data_b64);
      renderCatalogPage();
    } catch (error) {
      setText("catCoverStatus", error.message, "error");
    }
  });
  document.getElementById("catCoverRemoveBtn")?.addEventListener("click", () => {
    applyToSelected((track) => {
      track.coverAction = "remove";
      track.coverB64 = "";
      track.has_cover = false;
    });
  });
  document.getElementById("catCoverApplyBtn")?.addEventListener("click", async () => {
    const source = selectedTracks()[0];
    if (!source || source.coverAction === "remove" || (!source.coverB64 && !source.has_cover)) {
      setText("catCoverStatus", "La primera cançó seleccionada no té portada.", "error");
      return;
    }
    let mime = source.coverMime || "image/jpeg";
    let data = source.coverB64;
    if (!data) {
      const response = await fetch(
        `/api/studio/catalog/cover?rel=${encodeURIComponent(source.rel)}`
      );
      if (!response.ok) {
        setText("catCoverStatus", "No s’ha pogut llegir la portada.", "error");
        return;
      }
      const blob = await response.blob();
      const encoded = await readFileAsBase64(new File([blob], "cover", { type: blob.type || mime }));
      mime = encoded.mime;
      data = encoded.data;
    }
    applyToSelected((track) => setCover(track, mime, data));
  });

  document.getElementById("dlForm")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const url = document.getElementById("dlUrl")?.value.trim();
    if (!url) return;
    enqueueDownload({ url, ...currentDownloadOptions() });
    document.getElementById("dlUrl").value = "";
  });
  document.getElementById("dlClearBtn")?.addEventListener("click", () => {
    document.getElementById("dlUrl").value = "";
  });
  document.getElementById("dlClearQueueBtn")?.addEventListener("click", () => {
    dlState.queue = dlState.queue.filter((item) => item.state === "running");
    renderDownloadQueue();
  });
  document.querySelectorAll('input[name="dlMode"]').forEach((input) => input.addEventListener("change", syncQuality));
  document.querySelectorAll('input[name="dlDest"]').forEach((input) => {
    input.addEventListener("change", () => {
      refreshDownloadConfig();
      refreshDownloadFiles();
    });
  });
  document.getElementById("dlLoadUrlsBtn")?.addEventListener("click", () => document.getElementById("dlUrlsFile")?.click());
  document.getElementById("dlUrlsFile")?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const urls = parseUrlFile(await file.text());
    const options = currentDownloadOptions();
    urls.forEach((url) => enqueueDownload({ url, ...options }));
    showDownloadStatus("", `${urls.length} URLs a la cua`, file.name, null);
  });
  document.getElementById("dlCookies")?.addEventListener("change", async (event) => {
    try {
      await jsonRequest("/api/studio/yt/settings", { cookies_browser: event.target.value }, "PUT");
      refreshDownloadConfig();
    } catch (error) {
      setText("dlCookiesStatus", error.message, "error");
    }
  });
  document.getElementById("dlCookiesUploadBtn")?.addEventListener("click", () => {
    document.getElementById("dlCookiesFile")?.click();
  });
  document.getElementById("dlCookiesFile")?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    try {
      await api("/api/studio/yt/cookies", { method: "POST", body });
      const select = document.getElementById("dlCookies");
      if (select) select.value = "file";
      refreshDownloadConfig();
    } catch (error) {
      setText("dlCookiesStatus", error.message, "error");
    }
  });
  document.querySelectorAll("[data-dl-tab]").forEach((btn) => {
    btn.addEventListener("click", () => showDownloadTab(btn.dataset.dlTab));
  });
  document.getElementById("dlRefreshBtn")?.addEventListener("click", () => refreshDownloadFiles());
  document.getElementById("dlRefreshFailedBtn")?.addEventListener("click", () => refreshFailures());
  document.getElementById("dlClearFailedBtn")?.addEventListener("click", async () => {
    await api("/api/studio/yt/failures", { method: "DELETE" });
    refreshFailures();
  });
  syncRunLabel();
  syncQuality();
}

window.karaokeStudio = {
  open(section) {
    if (section === "catalog") {
      loadCatalogSettings();
      loadCatalogTracks().catch((error) => setText("catEditStatus", error.message, "error"));
    }
    if (section === "downloads") {
      refreshDownloadConfig();
      refreshDownloadFiles();
      refreshFailures();
    }
  },
};

bindStudio();
