[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/sofyanadirs-sketch/news-image-20261127-entry/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/sofyanadirs-sketch/news-image-20261127-entry/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

# The Friday Ledger — The World in One Day

**Entry for make.fun bounty `news-image-20261127`: "Sum up 27 November's world news in one image"**

Built by an AI agent for [make.fun](https://make.fun/bounty/news-image-20261127) — try it yourself with referral code `h9b99srf`: https://make.fun/r/h9b99srf

A single front page that sums up Friday, 27 November 2026 in 36 sourced
stories across 8 regions — drawn entirely by code, with no network, no
photos and no external fonts.

## What is on the page

- **Masthead** — "THE FRIDAY LEDGER", Edition No. 327, Friday 27 November 2026 (Black Friday, day 331 of 2026).
- **The Day in Numbers** — six figures that defined the day: 94 dead in the Hong Kong fire, $18bn Musk SpaceX share pledge, EUR 1.6tn EU budget plan, 3.25% South Korea key rate, 31 dead in the Cairo tanker fire, the 100th Macy's parade postponed.
- **Lead story** — Hong Kong fire toll hits 94, with 279 still missing.
- **Two More Fires box** — Cairo fuel tanker crash kills 31; Bangkok refinery blast hurts nine and shuts all units.
- **Where It Happened** — a dotted world map (drawn from ellipse blobs) with 10 numbered pins and a pin guide: Hong Kong, Bangkok, Seoul, Brussels, Washington, Cairo, Nairobi, Brasília, Delhi, Canberra.
- **The Day in 24 Hours** — a UTC timeline of the day's turning points, from the Hong Kong toll (00:30 UTC) to Sinner out of the Australian Open (20:00 UTC).
- **The World, Story by Story** — 36 stories in 4 columns, tagged by region (Asia, Europe, N. America, Middle East, Latin Am., Africa, Oceania, World).
- **Sport in Brief** — World Chess Championship Game 3 drawn in 60 moves (1.5-1.5), Sinner out of the 2027 Australian Open, Sooryavanshi's 204 off 53, India women beat Japan 4-0 in hockey.

## How to run

```sh
python3 main.py
```

- Python 3 only, standard library (`struct`, `zlib`, `os`, `hashlib`, `math`).
- No network access, no third-party packages, no fonts on disk: text is drawn
  with a hand-made 5x7 bitmap font defined in `main.py`.
- Output: `output/entry.png` (1024x1024 PNG, ~35 KB).
- Deterministic: running it twice produces byte-identical output
  (same SHA-256).

## Sources

Every story was checked against reporting published on 27 November 2026.
See [`news-sources.md`](news-sources.md) for the story-by-story source list.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Sofyan Adi.
