#!/usr/bin/env python3
"""Fix and hash an ex-situ clip list. GT_PROTOCOL.md section 8.2.

The point of this script is that it runs BEFORE the pipeline, and that its
output is hashed. Once `CLIPLIST_<corpus>.csv` exists and its SHA256 is written
into `CLIPLIST_<corpus>.sha256`, the set of clips that will be scored is fixed.
Dropping a clip afterwards because it scored badly changes the hash and is
visible; that visibility is the entire mechanism.

The clip list joins two things that must both be pinned:
  * the video files actually on disk, each with its own SHA256, so that "the
    clip we scored" is a specific sequence of bytes and not a file name; and
  * the source corpus's published annotation, used unmodified (section 8.1).

Usage:
    python build_clip_list.py gmdcsa24
"""
import csv, collections, hashlib, io, json, os, sys, datetime

ROOT = r"D:\AAP_exsitu_data"
HERE = os.path.dirname(os.path.abspath(__file__))

LABEL2ID = {}
ID2LABEL = {}


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(buf), b""):
            h.update(chunk)
    return h.hexdigest()


def load_label_map():
    p = os.path.join(ROOT, "omnifall_ann", "labels_label2id.csv")
    with open(p, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            LABEL2ID[r["label"]] = int(r["id"])
            ID2LABEL[int(r["id"])] = r["label"]


# --------------------------------------------------------------- corpora
def gmdcsa24():
    """OmniFall path 'Subject_1/ADL/01' -> disk 'Subject 1/ADL/01.mp4'."""
    base = os.path.join(ROOT, "gmdcsa24", "extracted")
    top = [d for d in os.listdir(base) if d.startswith("ekramalam")]
    base = os.path.join(base, top[0]) if top else base

    ann = collections.defaultdict(list)
    with open(os.path.join(ROOT, "omnifall_ann", "labels_GMDCSA24.csv"),
              encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            ann[r["path"]].append(r)

    rows = []
    missing = []
    for apath in sorted(ann):
        rel = apath.replace("Subject_", "Subject ") + ".mp4"
        full = os.path.join(base, *rel.split("/"))
        if not os.path.exists(full):
            missing.append(apath)
            continue
        segs = ann[apath]
        rows.append({
            "corpus": "GMDCSA24",
            "clip_id": apath,
            "file_relpath": rel,
            "size_bytes": os.path.getsize(full),
            "sha256": sha256(full),
            "n_segments": len(segs),
            "labels": ";".join(sorted({ID2LABEL[int(s["label"])] for s in segs})),
            "has_fall": int(any(int(s["label"]) == LABEL2ID["fall"] for s in segs)),
            "subject": segs[0]["subject"],
            "cam": segs[0]["cam"],
        })
    return rows, missing, base


CORPORA = {"gmdcsa24": gmdcsa24}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CORPORA:
        sys.exit("usage: build_clip_list.py {%s}" % "|".join(CORPORA))
    name = sys.argv[1]
    load_label_map()
    rows, missing, base = CORPORA[name]()

    out = os.path.join(HERE, "CLIPLIST_%s.csv" % name)
    cols = ["corpus", "clip_id", "file_relpath", "size_bytes", "sha256",
            "n_segments", "labels", "has_fall", "subject", "cam"]
    with io.open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    listhash = sha256(out)
    meta = {
        "corpus": name,
        "fixed_at": datetime.datetime.now().astimezone().isoformat(),
        "video_root": base,
        "clips": len(rows),
        "clips_with_fall_segment": sum(r["has_fall"] for r in rows),
        "total_segments": sum(r["n_segments"] for r in rows),
        "annotation_source": "OmniFall simplexsigil2/omnifall labels/GMDCSA24.csv (unmodified)",
        "annotation_licence": "CC BY-NC-SA 4.0 (annotations); video CC BY 4.0 (Zenodo 12921216)",
        "missing_from_disk": missing,
        "cliplist_sha256": listhash,
    }
    with io.open(os.path.join(HERE, "CLIPLIST_%s.sha256" % name), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write("%s  CLIPLIST_%s.csv\n" % (listhash, name))
    with io.open(os.path.join(HERE, "CLIPLIST_%s.meta.json" % name), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2)

    print("clips              :", len(rows))
    print("with a fall segment:", meta["clips_with_fall_segment"])
    print("total segments     :", meta["total_segments"])
    print("missing from disk  :", len(missing), missing[:5])
    print("CLIPLIST SHA256    :", listhash)
    labs = collections.Counter()
    for r in rows:
        for l in r["labels"].split(";"):
            labs[l] += 1
    print("label coverage     :", dict(labs.most_common()))


if __name__ == "__main__":
    main()
