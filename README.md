# til

Catatan kecil yang kepake: satu hal baru per hari, disimpan sebagai file pendek
biar nggak lupa dan gampang dicari lagi.

```
notes/YYYY-MM-DD-slug.md   # satu catatan
tags.json                  # hitungan per tag
```

Satu catatan nggak harus panjang. Kalau butuh lebih dari 10 baris,
kemungkinan itu artikel, bukan TIL.

## Isi repo

| File | Fungsi |
|---|---|
| `notes/*.md` | catatan harian (judul, tag, ringkasan) |
| `tags.json` | rekap jumlah catatan per tag |
| `generate.py` | backfill hari kosong |
| `daily-til.sh` | catatan hari ini + commit, cocok buat cron |

## Pakai

```bash
python3 generate.py --days 115 --span 160   # backfill
./daily-til.sh                              # catatan hari ini
```

Cron:

```bash
crontab -e
30 22 * * * /path/ke/til/daily-til.sh
```
