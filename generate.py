#!/usr/bin/env python3
"""
TIL generator — satu catatan per hari aktif, backdated.

Tiap commit nambah notes/YYYY-MM-DD-slug.md dan update tags.json.

Syarat biar kehitung di contribution graph:
  - email author verified di akun GitHub
  - commit di default branch repo sendiri (bukan fork)
  - 1 hari = 1 kotak, jadi butuh banyak HARI, bukan banyak commit

Pakai:
  python3 generate.py                # 115 hari dalam 160 hari terakhir
  python3 generate.py --days 140 --span 200 --seed 9
"""

import argparse
import json
import os
import random
import re
import subprocess
from datetime import datetime, timedelta

AUTHOR_NAME = "sug212"
AUTHOR_EMAIL = "sugiartopuji2@gmail.com"

TIPS = [
    ("git switch -c", "bikin branch baru tanpa pindah dari detached HEAD", ["git"]),
    ("curl -w timing", "ukur latency request tanpa tooling tambahan", ["cli", "perf"]),
    ("JSON.stringify replacer", "filter field sensitif sebelum log objek", ["js"]),
    ("Array.at(-1)", "ambil elemen terakhir tanpa length-1", ["js"]),
    ("Intl.NumberFormat", "format angka rupiah tanpa library", ["js", "i18n"]),
    ("CSS :has()", "styling parent berdasarkan isi child", ["css"]),
    ("SQLite WAL mode", "write concurrent tanpa lock panjang", ["db"]),
    ("SSH ControlMaster", "reuse koneksi, login berulang jadi instan", ["ssh"]),
    ("tar --exclude", "backup folder tanpa node_modules", ["cli"]),
    ("systemd timer", "pengganti cron yang ada log-nya", ["linux"]),
    ("git log -S", "cari commit yang menambah/menghapus string", ["git"]),
    ("Promise.allSettled", "jalanin banyak request tanpa gagal semua", ["js"]),
    ("clamp()", "font responsif satu baris", ["css"]),
    ("du -sh * | sort -h", "temukan folder paling makan disk", ["cli"]),
    ("git worktree", "kerja dua branch tanpa stash", ["git"]),
    ("crypto.randomUUID", "id unik tanpa dependency", ["js"]),
    ("EXPLAIN QUERY PLAN", "lihat query mana yang diam-diam full scan", ["db", "perf"]),
    ("safe-area-inset", "UI nggak ketutup notch", ["css", "mobile"]),
    ("trap 'echo bye' EXIT", "cleanup otomatis di shell script", ["bash"]),
    ("git stash push -m", "simpan WIP dengan label yang jelas", ["git"]),
]

BODIES = [
    "Simpel tapi sering kepake. Nggak perlu install apa-apa.",
    "Baru sadar selama ini nulis manual. Sekarang satu baris.",
    "Cocok buat script sekali pakai maupun automation harian.",
    "Catatan kecil biar nggak lupa. Detail lengkap ada di docs resmi.",
    "Nemu waktu debugging, langsung masuk catatan.",
]


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "note"


def sh(cmd, env):
    subprocess.run(cmd, check=True, shell=True, env=env, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=115)
    ap.add_argument("--span", type=int, default=160)
    ap.add_argument("--seed", type=int, default=31)
    args = ap.parse_args()

    random.seed(args.seed)
    root = os.path.dirname(os.path.abspath(__file__))
    notes = os.path.join(root, "notes")
    os.makedirs(notes, exist_ok=True)
    tags_path = os.path.join(root, "tags.json")

    tags = {}
    if os.path.exists(tags_path):
        with open(tags_path) as f:
            tags = json.load(f)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    window = [today - timedelta(days=d) for d in range(1, args.span + 1)]
    days = sorted(random.sample(window, min(args.days, len(window))))

    for day in days:
        ts = day + timedelta(hours=random.randint(8, 23), minutes=random.randint(0, 59))
        stamp = ts.strftime("%Y-%m-%d %H:%M:%S +0700")
        env = dict(os.environ,
                   GIT_AUTHOR_NAME=AUTHOR_NAME, GIT_AUTHOR_EMAIL=AUTHOR_EMAIL,
                   GIT_COMMITTER_NAME=AUTHOR_NAME, GIT_COMMITTER_EMAIL=AUTHOR_EMAIL,
                   GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)

        title, desc, note_tags = random.choice(TIPS)
        path = os.path.join(notes, f"{day:%Y-%m-%d}-{slug(title)}.md")
        if os.path.exists(path):
            continue

        with open(path, "w") as f:
            f.write(
                f"# {title}\n\n"
                f"**Tanggal:** {day:%Y-%m-%d}  \n"
                f"**Tag:** {' '.join('`#' + t + '`' for t in note_tags)}\n\n"
                f"{desc}.\n\n"
                f"> {random.choice(BODIES)}\n"
            )

        for t in note_tags:
            tags[t] = tags.get(t, 0) + 1
        with open(tags_path, "w") as f:
            json.dump(dict(sorted(tags.items())), f, indent=2)
            f.write("\n")

        sh(f'git add "{path}" tags.json', env)
        sh(f'git commit -m "til: {title} ({day:%Y-%m-%d})"', env)

    print(f"done: {len(days)} catatan, {len(tags)} tag")


if __name__ == "__main__":
    main()
