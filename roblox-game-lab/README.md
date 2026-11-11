# Roblox Game Lab

A repeatable way to pick the next Roblox game: read what is trending from live chart data,
mix proven mechanics that nobody has paired yet, score the idea before building, and plan
the money from day one.

## The loop (about an hour a week)

| Step | What you do | Output |
|---|---|---|
| 1. Scan | `python3 lab.py scan` | `data/snapshots/<date>.json`: every game on Roblox's 23 public charts |
| 2. Read | `python3 lab.py report` | `reports/<date>.md`: breakouts, open lanes, what earns, mix candidates |
| 3. Play | 20 minutes each in the top 5 breakouts. Note the first 5 minutes, the return reason, the shop. | Notes |
| 4. Mix | Pick a loop pair from report section 8, a theme from section 6, a hook from section 7 | A one-line pitch |
| 5. Score | Copy `concepts/example.json`, rate it honestly, `python3 lab.py score concepts/<idea>.json` | Build / rework / pass |
| 6. Build | 2-4 week MVP, then judge it on real numbers (see [PLAYBOOK.md](PLAYBOOK.md)) | Keep, fix or kill |

Python 3.9+, no installs. The scan needs network access to `apis.roblox.com` and
`games.roblox.com`.

Scan at roughly the same time of day each time: player counts swing with time zones. From
the second snapshot on, the report adds a "Movers" section showing who gained and lost
players and which games are new to the charts.

## Files

- `lab.py`: the scanner, report and scorecard.
- `PLAYBOOK.md`: what decides success, how the money works, and the current read of the market.
- `reports/`: one trend report per scan.
- `data/snapshots/`: raw chart data, kept so later scans can show movement.
- `concepts/`: one JSON card per game idea.

## Limits worth knowing

- Mechanic tags come from keyword matching on each game's title and the opening of its
  description. They are a net, not a classifier. Check the example games before trusting a
  row, and add patterns to the tables at the top of `lab.py` as new crazes appear.
- Roblox does not publish revenue. "Top Earning" rank is the only public money signal, so
  the report compares earning rank against player rank rather than quoting dollar figures.
- The chart endpoints are public but undocumented, so Roblox can change them without notice.
