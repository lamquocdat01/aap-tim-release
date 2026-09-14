#!/usr/bin/env python3
"""Fix and hash the FURG fire clip list. GT_PROTOCOL.md section 8.2.

FURG annotates FIRE with per-frame rectangles. Two things it does not give us,
both declared here rather than discovered later:

  * NO SMOKE. `SmokeFireChecker` fires on smoke or fire; FURG labels flame only.
    Every recall number from this corpus is therefore conditional on the fire
    sub-class, and the `gt_class` column says so on every row.
  * The corpus was built, in its own README's words, "to compare the performance
    of different non-stationary video based fire detectors". Most clips are from
    a moving platform; the deployment is a fixed indoor camera. Clips are
    stratified into static and moving and reported separately, never pooled.

The static/moving assignment is by platform name, which FURG encodes explicitly
(hand_held_*, rover, patrolbot, car*, cleaner, coolerbot are moving platforms;
house*, barbecue are fixed). It is a DECLARED assignment, listed row by row
below so a reader can disagree with any single call, not an inferred one.

GT events: contiguous runs of annotated frames, converted to seconds with the
XML's own frameRate, then merged with SmokeFireChecker's 60 s gap
(max(operational 60, production cooldown none) -- see GT_PROTOCOL 4.3).
"""
import csv, hashlib, io, json, os, re, datetime

ROOT = r"D:\AAP_exsitu_data\furg"
HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_GAP = 60.0   # SmokeFireChecker, GT_PROTOCOL 4.3

# Declared platform assignment. FURG names its platform in the file name.
MOVING = {
    "Car1": "car", "car2": "car", "car3": "car", "case2_car": "car",
    "cleaner": "cleaning robot", "coolerbot": "robot", "rover": "robot",
    "non_fire_patrolbot_onboard": "patrol robot", "icra": "robot (ICRA demo)",
    "hand_held_batteries_night": "hand-held",
    "hand_held_camera_wildfire": "hand-held",
    "hand_held_nasa_training": "hand-held",
    "hand_held_nasa_training2": "hand-held",
    "hand_held_winnebago": "hand-held",
}
STATIC = {
    "barbecue": "fixed", "house1": "fixed", "house2": "fixed", "house3": "fixed",
    "house4": "fixed", "house5": "fixed", "house6": "fixed",
    "case2_house": "fixed (house scene)", "case2_outside": "fixed (outdoor scene)",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def parse_xml(path):
    """The 'weird OpenCV 2.4.9 XML'. Pull frameRate, size, and the frame numbers
    that carry at least one rectangle."""
    txt = io.open(path, encoding="utf-8", errors="replace").read()

    def one(tag, cast=str):
        m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), txt, re.S)
        return cast(m.group(1).strip()) if m else None

    fr = one("frameRate", lambda s: float(s))
    w, h = one("frameWidth", int), one("frameHeight", int)

    fire_frames = []
    for blk in re.finditer(r"<frameNumber>(\d+)</frameNumber>\s*<annotations>(.*?)</annotations>",
                           txt, re.S):
        n = int(blk.group(1))
        body = blk.group(2)
        rects = re.findall(r"<_>\s*([-\d]+)\s+([-\d]+)\s+([-\d]+)\s+([-\d]+)\s*</_>", body)
        if any(int(r[2]) > 0 and int(r[3]) > 0 for r in rects):
            fire_frames.append(n)
    return fr, w, h, sorted(set(fire_frames)), len(re.findall(r"<frameNumber>", txt))


def runs_to_events(frames, fps):
    if not frames:
        return []
    ev, s, p = [], frames[0], frames[0]
    for f in frames[1:]:
        if f == p + 1:
            p = f
            continue
        ev.append((s / fps, (p + 1) / fps))
        s = p = f
    ev.append((s / fps, (p + 1) / fps))
    merged = [list(ev[0])]
    for a, b in ev[1:]:
        if a - merged[-1][1] <= MERGE_GAP:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [tuple(x) for x in merged]


def main():
    vids = sorted(f for f in os.listdir(ROOT) if f.endswith(".mp4"))
    xmls = {f[:-4].lower(): f for f in os.listdir(ROOT) if f.endswith(".xml")}

    rows, problems = [], []
    for v in vids:
        stem = v[:-4]
        xml = xmls.get(stem.lower())
        if not xml:
            problems.append("no XML for %s" % v)
            continue
        vp, xp = os.path.join(ROOT, v), os.path.join(ROOT, xml)
        fps, w, h, fire, nframes = parse_xml(xp)
        if not fps:
            problems.append("no frameRate in %s" % xml)
            continue
        ev = runs_to_events(fire, fps)
        if stem in MOVING:
            stratum, platform = "moving", MOVING[stem]
        elif stem in STATIC:
            stratum, platform = "static", STATIC[stem]
        else:
            stratum, platform = "UNASSIGNED", "?"
            problems.append("unassigned stratum: %s" % stem)
        rows.append({
            "corpus": "FURG", "clip_id": stem, "video_file": v, "xml_file": xml,
            "size_bytes": os.path.getsize(vp), "sha256": sha256(vp),
            "xml_sha256": sha256(xp),
            "frame_rate": fps, "width": w, "height": h,
            "frames_annotated": nframes, "frames_with_fire": len(fire),
            "gt_events": len(ev),
            "gt_seconds": round(sum(b - a for a, b in ev), 3),
            "gt_class": "fire_only_no_smoke",
            "camera_stratum": stratum, "platform": platform,
        })

    cols = list(rows[0].keys())
    out = os.path.join(HERE, "CLIPLIST_furg.csv")
    with io.open(out, "w", encoding="utf-8", newline="") as fh:
        wtr = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        wtr.writeheader()
        for r in rows:
            wtr.writerow(r)
    lh = sha256(out)
    with io.open(os.path.join(HERE, "CLIPLIST_furg.sha256"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write("%s  CLIPLIST_furg.csv\n" % lh)

    by = {}
    for r in rows:
        s = r["camera_stratum"]
        d = by.setdefault(s, {"clips": 0, "events": 0, "seconds": 0.0})
        d["clips"] += 1; d["events"] += r["gt_events"]; d["seconds"] += r["gt_seconds"]

    meta = {"corpus": "FURG", "fixed_at": datetime.datetime.now().astimezone().isoformat(),
            "video_root": ROOT, "clips": len(rows),
            "licence": "CC0-1.0 (GitHub API license.spdx_id, steffensbola/furg-fire-dataset)",
            "gt_class": "fire only; corpus contains NO smoke annotation",
            "merge_gap_s": MERGE_GAP, "by_stratum": by,
            "problems": problems, "cliplist_sha256": lh}
    with io.open(os.path.join(HERE, "CLIPLIST_furg.meta.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2)

    print("clips:", len(rows))
    for s in sorted(by):
        d = by[s]
        print("  %-11s clips %2d  GT events %3d  fire seconds %8.1f"
              % (s, d["clips"], d["events"], d["seconds"]))
    res = collections_counter = {}
    for r in rows:
        res.setdefault("%dx%d @ %.0f fps" % (r["width"], r["height"], r["frame_rate"]), 0)
        res["%dx%d @ %.0f fps" % (r["width"], r["height"], r["frame_rate"])] += 1
    print("formats:", res)
    print("problems:", problems if problems else "none")
    print("CLIPLIST SHA256:", lh)


if __name__ == "__main__":
    main()
