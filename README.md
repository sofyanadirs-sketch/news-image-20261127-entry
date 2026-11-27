# The Friday Ledger — The World in One Day

An entry for the [make.fun](https://make.fun/c/news-image-20261127)
bounty `news-image-20261127`: sum up 27 November 2026's world news in a
single image. Prize $100 (~Rp1,65 jt) across 50 paid places. Entries close
29 November 2026, 07:00 WIB.

Built for make.fun by **@sofyan-adi** (GitHub: sofyanadirs-sketch).
Referral code: `h9b99srf`.

## The image

`main.py` draws a one-page newspaper front page, 1024x1024, using only the
Python standard library. No network calls, no outside files, no downloaded
fonts — every letter comes from a small 5x7 bitmap font defined in the
script, and the PNG bytes are assembled by hand, so the output is identical
on every run.

What's on the page:

- **Masthead** — "THE FRIDAY LEDGER" over "THE WORLD IN ONE DAY", with a
  crimson date strip: FRIDAY 27 NOVEMBER 2026.
- **The Day in Numbers** — six figures that set the day: 94 dead in the
  Hong Kong fire, $18bn of SpaceX shares pledged for US children, a EUR
  1.6tn EU budget, a 3.25% Bank of Korea rate, 31 dead in the Cairo tanker
  fire, and the 100th Macy's parade postponed.
- **Lead story** — the Hong Kong tower fire: 94 dead, 279 missing, 70+
  hurt, after flames spread through bamboo scaffolding at Wang Fuk Court.
- **Two More Fires** — the Cairo fuel tanker fire (31 dead) and the
  explosion at Bangkok's Bangchak refinery (9 hurt).
- **World map** — ten pins: Hong Kong, Bangkok, Seoul, Brussels,
  Washington, Cairo, Nairobi, Brasilia, Delhi and Canberra.
- **The Day in UTC** — an eight-event timeline from midnight to midnight,
  from the first Hong Kong toll reports to the Gukesh–Sindarov draw.
- **Around the World** — 36 short stories from 8 regions, each in the
  entry's own wording.
- **Sport footer** — Gukesh–Sindarov Game 3 drawn after 60 moves (1.5–1.5),
  Sinner out of Australian Open 2027, Sooryavanshi's 204 off 53, and
  India's 4–0 hockey win over Japan.

## Run it

```sh
python3 main.py
# wrote output/entry.png (34297 bytes) sha256=754136d26d596c56309a17f53930b11528612a3c841ce63ab175504b6f5ac8d0
```

Run it twice and the SHA-256 matches: the render is fully deterministic.

## Files

| File | What it is |
| --- | --- |
| `main.py` | The renderer (stdlib only: `struct`, `zlib`, `os`, `hashlib`, `math`) |
| `output/entry.png` | The rendered front page, 1024x1024 RGB, under 1 MiB |
| `news-sources.md` | Every story checked against reporting from 27 November 2026 |
| `LICENSE` | MIT |
| `.makefun/owner.json` | Payout wallet for the entry |

## Sources

Headlines are the entry's own wording of facts reported on 27 November
2026 by AP, Reuters, Chess.com, NBC Sports and the day's roundups — the
full list, story by story, is in `news-sources.md`.
