import time

import httpx

base = "http://127.0.0.1:8765"
client = httpx.Client(timeout=60.0)
print("health", client.get(f"{base}/api/health").json())
tracks = client.get(f"{base}/api/library").json()["tracks"]
chosen = None
for t in sorted(tracks, key=lambda x: x.get("duration") or 9999):
    r = client.get(f"{base}/api/lyrics", params={"track_id": t["id"]})
    if r.status_code != 200:
        print("lyrics fail", r.status_code, t["title"][:40])
        continue
    data = r.json()
    n = len(data.get("lines") or [])
    if n:
        print(
            f"FOUND {n} lines | {t['artist']} - {t['title']} | "
            f"{t['duration']:.0f}s | aligned={data.get('aligned')}"
        )
        chosen = t
        if data.get("aligned"):
            print("already aligned")
            print("first words", (data["lines"][0].get("words") or [])[:4])
            raise SystemExit(0)
        break
    print(f"no lyrics | {t['artist']} - {t['title']}")

if not chosen:
    raise SystemExit("no track with lyrics")

print("POST align", chosen["id"])
job = client.post(
    f"{base}/api/align",
    json={"track_id": chosen["id"], "language": "ca"},
).json()
print("start", {k: job.get(k) for k in ("job_id", "status", "error", "source")})
if job.get("status") == "done":
    print("done from cache, words", (job["lines"][0].get("words") or [])[:4])
    raise SystemExit(0)

jid = job["job_id"]
for i in range(180):
    time.sleep(5)
    st = client.get(f"{base}/api/align/{jid}").json()
    print(
        f"[{i}] status={st.get('status')} err={st.get('error')} "
        f"lines={len(st.get('lines') or [])}"
    )
    if st.get("status") in ("done", "error"):
        if st.get("status") == "done":
            line0 = st["lines"][0]
            print("line0", line0["text"], "t=", round(line0["time"], 2))
            print("words", line0.get("words")[:5])
            mid = st["lines"][len(st["lines"]) // 2]
            print("mid", mid["text"], "t=", round(mid["time"], 2), mid.get("words")[:4])
        break
else:
    raise SystemExit("timeout")
