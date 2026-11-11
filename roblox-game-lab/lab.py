#!/usr/bin/env python3
"""Roblox Game Lab: find what is trending, see what mixes are untried, score a concept.

    python3 lab.py scan              pull today's charts into data/snapshots/<date>.json
    python3 lab.py report            write reports/<date>.md from the newest snapshot
    python3 lab.py score FILE.json   score a concept card (see concepts/example.json)

Standard library only. Uses Roblox's public, unauthenticated chart endpoints.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOTS = ROOT / "data" / "snapshots"
REPORTS = ROOT / "reports"

EXPLORE = "https://apis.roblox.com/explore-api/v1"
GAMES = "https://games.roblox.com/v1/games"

# Charts that describe the whole platform. Genre charts ("trending-in-*") are added at scan time.
CORE_SORTS = [
    "top-trending", "up-and-coming", "top-playing-now", "top-earning",
    "top-revisited", "most-popular", "top-rated", "fun-with-friends", "top-paid-access",
]

PITCH_CHARS = 350  # only the opening of a description is matched: later lines are update logs and credits
YOUNG_DAYS = 180  # a game younger than this that charts is evidence a lane is still open

# --------------------------------------------------------------------------------------
# Mechanic taxonomy. Matched against title + description, so it is a rough net: read the
# exemplar games in the report before trusting a tag. Add rows as new crazes appear.
# --------------------------------------------------------------------------------------
LOOPS = {
    "steal": r"\bsteal",
    "tycoon/base-builder": r"\btycoon|build (your|a) (base|factory|empire)|\bfactory\b",
    "incremental/training": r"\+\s?\d|\bsimulator\b|\bclicker\b|\bincremental\b|\btrain(ing)?\b|every (second|click|step)",
    "collect-and-hatch": r"\bhatch|\beggs?\b|\bcollect (all|pets|them|rare)",
    "grow/farm": r"\bgrow (a|an|your|the)\b|\bgarden|\bfarm(ing)?\b|\bplant (seeds|crops|a)\b|\bharvest",
    "tower-defense": r"tower defen[sc]e|\btd\b|\bdefend your\b",
    "obby/parkour": r"\bobby\b|\bparkour\b|\btower of\b|\bclimb",
    "survival": r"\bsurvival\b|\bsurvive (the|a|in|your)\b|\bnights? (in|at)\b|\bdisaster",
    "horror/chase": r"\bhorror\b|\bscary\b|\bkillers?\b|\bescape (the|from)\b|\bjumpscare|\bmonsters?\b",
    "fighting/pvp": r"battlegrounds?|\bfight|\bpvp\b|\bcombat\b|\bduel|\bbrawl",
    "shooter": r"\bshooter\b|\bfps\b|\bguns?\b|\bgunfight",
    "rng/roll": r"\brng\b|\broll(s|ing)?\b|\bluck\b|\bgacha\b|\bspin\b",
    "fishing": r"\bfish",
    "dig/mine": r"\bdig\b|\bdigging\b|\bmine\b|\bmining\b|\bdrill",
    "cook/serve": r"\bcook|\brestaurant|\bbakery|\bpizza|\bcafe\b|\bchef\b",
    "racing/driving": r"\brac(e|ing)\b|\bdriving\b|\bdrift|\bcar (game|sim|dealership)|\boffroad\b|\bdrag rac",
    "sports": r"\bsoccer\b|\bfootball\b|\bbasketball\b|\bvolleyball\b|\bhoops\b|\bbaseball\b",
    "roleplay/life-sim": r"\broleplay\b|\brp\b|\badopt\b|\bfamily\b|\bcity life\b|\bhigh ?school\b",
    "dress-up/avatar": r"dress|\boutfit|\bfashion\b|\bmakeover\b|\bavatar\b",
    "merge": r"\bmerge",
    "social-deduction": r"\bmurder\b|\bimpost[eo]r|hide and seek|\bsheriff\b|\binnocent",
    "sandbox/build": r"\bsandbox\b|\bbuild a\b|build (and|to)\b|\bcraft",
    "party/minigames": r"\bminigames?\b|\bparty\b|\bquiz\b|\btrivia\b|\bspeed draw",
    "rpg/quest": r"\brpg\b|\bquests?\b|\bdungeon|\braid\b|\bbosses?\b",
    "ragdoll/physics": r"\bragdoll|\bphysics\b|\bfling\b|\bsplash",
}
THEMES = {
    "brainrot/meme": r"brainrot|\bmeme|\bsigma\b|\bskibidi|\bitalian\b",
    "anime": r"\banime\b|\bblox fruits\b|\bshinobi\b|\bjujutsu\b|\bslayer\b|\bone piece\b|\bnaruto\b",
    "animals": r"\bcats?\b|\bdogs?\b|\banimals?\b|\bdinos?\b|\bdinosaurs?\b|\bhorses?\b|\bspider|\bsharks?\b|\bpets?\b|\bcreatures?\b",
    "food": r"\bfood\b|\bpizza\b|\bcandy\b|\bburger|\bsushi\b|\bcake\b|\bcookie|\bfries\b",
    "zombies/undead": r"\bzombie|\bundead\b|\binfect",
    "military/war": r"\bwar\b|\barmy\b|\bmilitary\b|\btanks?\b|\bsoldier",
    "school/everyday": r"\bschool\b|\bneighbou?rhood\b|\bmall\b|\bhospital\b",
    "fantasy/magic": r"\bmagic|\bwizard|\bsword|\bknight|\bcastle\b|\belemental",
    "space/sci-fi": r"\bspace\b|\balien|\brocket|\bplanet",
    "ocean": r"\bocean\b|\bsea\b|\bisland|\bpirate|\bboat",
}
HOOKS = {
    "trading": r"\btrad(e|ing)\b",
    "rebirth/prestige": r"\brebirth|\bprestige\b|\bascend",
    "offline/idle income": r"\boffline\b|\bidle\b|\bafk\b|\bpassive\b",
    "rarity/mutations": r"\bmutation|\brare\b|\blegendary\b|\bmythic|\bsecret\b|\bdivine\b|\bshiny\b",
    "co-op/friends": r"\bfriends?\b|\bco-?op\b|\bteam ?up\b|\btogether\b|\bparty up\b",
    "live events": r"\bevent\b|\badmin abuse\b|\blimited\b|\bseason\b|\bweekly\b",
    "codes/free rewards": r"\bcodes?\b|\bfree\b|\bdaily reward|\blike the game\b|\bjoin the group\b",
    "leaderboards/ranked": r"\bleaderboard|\branked\b|\bcompetitive\b|\btournament",
}
TAXONOMY = {"loop": LOOPS, "theme": THEMES, "hook": HOOKS}


# ------------------------------------------------------------------------------- fetch --
def get_json(url: str, tries: int = 5) -> dict:
    """GET JSON, backing off on rate limits and transient failures."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "roblox-game-lab/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError("unreachable")


def list_sorts(session: str) -> dict[str, str]:
    """Every game chart Roblox currently publishes: {sortId: display name}."""
    found, token = {}, None
    for _ in range(12):
        url = f"{EXPLORE}/get-sorts?sessionId={session}"
        if token:
            url += "&sortsPageToken=" + urllib.parse.quote(token)
        page = get_json(url)
        for sort in page.get("sorts", []):
            if sort.get("contentType") == "Games" and sort.get("games"):
                found[sort["sortId"]] = sort.get("sortDisplayName") or sort["sortId"]
        token = page.get("nextSortsPageToken")
        if not token:
            break
    return found


def scan(_args) -> Path:
    session = str(uuid.uuid4())
    available = list_sorts(session)
    wanted = [s for s in CORE_SORTS if s in available] + sorted(s for s in available if s.startswith("trending-in-"))
    missing = [s for s in CORE_SORTS if s not in available]
    if missing:
        print(f"note: Roblox no longer publishes {missing}; carrying on without them", file=sys.stderr)

    games: dict[int, dict] = {}
    charts: dict[str, list[int]] = {}
    for sort_id in wanted:
        content = get_json(f"{EXPLORE}/get-sort-content?sessionId={session}&sortId={sort_id}")
        ids = []
        for g in content.get("games", []):
            if g.get("isSponsored"):
                continue  # paid placement says nothing about organic demand
            uid = g["universeId"]
            ids.append(uid)
            games.setdefault(uid, {
                "universeId": uid, "placeId": g.get("rootPlaceId"), "name": g.get("name", ""),
                "playing": g.get("playerCount", 0), "up": g.get("totalUpVotes", 0),
                "down": g.get("totalDownVotes", 0), "genre": g.get("genreL1") or "",
                "maturity": g.get("contentMaturity") or "",
            })
        charts[sort_id] = ids
        print(f"  {sort_id:<40} {len(ids):>3} games", file=sys.stderr)

    ids = list(games)
    for i in range(0, len(ids), 50):
        batch = ",".join(map(str, ids[i:i + 50]))
        for d in get_json(f"{GAMES}?universeIds={batch}").get("data", []):
            g = games[d["id"]]
            g.update({
                "description": (d.get("description") or "")[:800], "visits": d.get("visits", 0),
                "favorites": d.get("favoritedCount", 0), "maxPlayers": d.get("maxPlayers"),
                "created": d.get("created"), "updated": d.get("updated"),
                "genre": d.get("genre_l1") or g["genre"], "subgenre": d.get("genre_l2") or "",
                "creator": (d.get("creator") or {}).get("name", ""), "price": d.get("price"),
            })

    today = dt.datetime.now(dt.timezone.utc)
    snapshot = {"taken": today.isoformat(timespec="seconds"), "sortNames": {s: available[s] for s in wanted},
                "charts": charts, "games": list(games.values())}
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    out = SNAPSHOTS / f"{today:%Y-%m-%d}.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")))
    print(f"saved {len(games)} games across {len(charts)} charts -> {out.relative_to(ROOT)}")
    return out


# ----------------------------------------------------------------------------- analyse --
def parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", value)
    return dt.datetime.fromisoformat(m.group(1)).replace(tzinfo=dt.timezone.utc) if m else None


def load(path: Path | None = None) -> dict:
    if path is None:
        files = sorted(SNAPSHOTS.glob("*.json"))
        if not files:
            sys.exit("no snapshot yet: run `python3 lab.py scan` first")
        path = files[-1]
    snap = json.loads(path.read_text())
    taken = dt.datetime.fromisoformat(snap["taken"])
    ranks = {sort: {uid: i + 1 for i, uid in enumerate(ids)} for sort, ids in snap["charts"].items()}
    for g in snap["games"]:
        created = parse_time(g.get("created"))
        g["ageDays"] = max((taken - created).days, 1) if created else None
        votes = g["up"] + g["down"]
        g["likePct"] = round(100 * g["up"] / votes, 1) if votes else None
        g["visitsPerDay"] = g.get("visits", 0) / g["ageDays"] if g["ageDays"] else 0
        g["ranks"] = {sort: r[g["universeId"]] for sort, r in ranks.items() if g["universeId"] in r}
        text = f"{g['name']}\n{g.get('description', '')[:PITCH_CHARS]}".lower()
        g["tags"] = {kind: [t for t, rx in table.items() if re.search(rx, text)] for kind, table in TAXONOMY.items()}
    snap["path"] = path
    return snap


def previous_snapshot(current: Path) -> dict | None:
    older = [f for f in sorted(SNAPSHOTS.glob("*.json")) if f.name < current.name]
    if not older:
        return None
    raw = json.loads(older[-1].read_text())
    return {"taken": raw["taken"], "playing": {g["universeId"]: g["playing"] for g in raw["games"]},
            "date": older[-1].stem}


def num(n: float) -> str:
    n = float(n)
    for unit, size in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= size:
            return f"{n / size:.1f}{unit}"
    return f"{n:.0f}"


def clean(name: str, width: int = 44) -> str:
    name = re.sub(r"[\[\(【].*?[\]\)】]", "", name)          # strip "[UPD]" style prefixes
    name = re.sub(r"[|\n\r]", " ", name)
    name = re.sub(r"\s+", " ", name).strip() or "(untitled)"
    return name if len(name) <= width else name[: width - 1] + "…"


def link(g: dict) -> str:
    return f"[{clean(g['name'])}](https://www.roblox.com/games/{g['placeId']})"


def breakout_score(g: dict) -> float:
    """Young games earning chart positions on their own. Higher = hotter proof of an open lane."""
    if not g["ageDays"] or g["ageDays"] > YOUNG_DAYS:
        return 0.0
    youth = 1 + (YOUNG_DAYS - g["ageDays"]) / YOUNG_DAYS            # 1..2, newer is better
    charts = sum(1 for s in ("top-trending", "up-and-coming", "top-earning", "top-revisited", "top-playing-now") if s in g["ranks"])
    quality = (g["likePct"] or 60) / 100
    return math.log10(g["playing"] + 10) * youth * (1 + 0.35 * charts) * quality


def tag_stats(games: list[dict], kind: str) -> dict[str, dict]:
    stats = defaultdict(lambda: {"games": [], "players": 0, "youngPlayers": 0, "earners": 0})
    for g in games:
        young = bool(g["ageDays"] and g["ageDays"] <= YOUNG_DAYS)
        for tag in g["tags"][kind]:
            s = stats[tag]
            s["games"].append(g)
            s["players"] += g["playing"]
            s["youngPlayers"] += g["playing"] if young else 0
            s["earners"] += 1 if g["ranks"].get("top-earning", 999) <= 50 else 0
    for s in stats.values():
        s["games"].sort(key=lambda g: -g["playing"])
        s["momentum"] = s["youngPlayers"] / s["players"] if s["players"] else 0
        s["leaderShare"] = s["games"][0]["playing"] / s["players"] if s["players"] else 1
    return stats


def money_gap(games: list[dict]) -> list[tuple[str, float, int]]:
    """Per genre: how much better games rank on earnings than on players (positive = monetises well)."""
    gaps = defaultdict(list)
    for g in games:
        earn, play = g["ranks"].get("top-earning"), g["ranks"].get("top-playing-now")
        if earn and g["genre"]:
            gaps[g["genre"]].append((play or 110) - earn)
    return sorted(((k, sum(v) / len(v), len(v)) for k, v in gaps.items() if len(v) >= 3), key=lambda r: -r[1])


def mixes(games: list[dict], loops: dict[str, dict], limit: int = 15) -> list[dict]:
    """Pairs of proven loops that few charting games combine yet."""
    together = defaultdict(int)
    for g in games:
        for a, b in itertools.combinations(sorted(g["tags"]["loop"]), 2):
            together[(a, b)] += 1
    out = []
    for a, b in itertools.combinations(sorted(loops), 2):
        sa, sb = loops[a], loops[b]
        if min(len(sa["games"]), len(sb["games"])) < 4:
            continue  # too thin to call the tag proven
        overlap = together[(a, b)] / min(len(sa["games"]), len(sb["games"]))
        heat = math.sqrt(sa["players"] * sb["players"])
        momentum = (sa["momentum"] + sb["momentum"]) / 2
        out.append({"a": a, "b": b, "overlap": overlap, "heat": heat, "momentum": momentum,
                    "existing": together[(a, b)], "score": heat * (0.4 + momentum) * (1 - overlap) ** 2})
    return sorted(out, key=lambda m: -m["score"])[:limit]


def exemplars(loops: dict[str, dict], a: str, b: str) -> list[dict]:
    """Biggest game of each loop, skipping one game that would stand for both."""
    first = loops[a]["games"][0]
    second = next((g for g in loops[b]["games"] if g is not first), first)
    return [first, second]


def report(args) -> Path:
    snap = load(Path(args.snapshot) if args.snapshot else None)
    games, date = snap["games"], snap["path"].stem
    prev = previous_snapshot(snap["path"])
    L = [f"# Roblox trend report: {date}", "",
         f"{len(games)} games from {len(snap['charts'])} public charts, taken {snap['taken']} UTC. "
         "Player counts are a single moment; rerun `scan` at the same time of day to compare like with like.", ""]

    def table(head: list[str], rows: list[list]) -> None:
        L.append("| " + " | ".join(head) + " |")
        L.append("|" + "|".join("---" for _ in head) + "|")
        L.extend("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
        L.append("")

    def age(g):
        return f"{g['ageDays']}d" if g["ageDays"] else "?"

    L += ["## 1. Breakouts: young games already on the charts", "",
          f"Games under {YOUNG_DAYS} days old. These are the strongest evidence of what players want *now* "
          "and that a newcomer can still take the lane.", ""]
    hot = sorted((g for g in games if breakout_score(g) > 0), key=breakout_score, reverse=True)[:25]
    table(["Game", "Age", "Playing", "Visits/day", "Like %", "Genre", "Loop tags", "Earning rank"],
          [[link(g), age(g), num(g["playing"]), num(g["visitsPerDay"]), g["likePct"] or "?",
            " / ".join(x for x in (g["genre"], g.get("subgenre")) if x), ", ".join(g["tags"]["loop"]) or "-",
            g["ranks"].get("top-earning", "-")] for g in hot])

    if prev:
        L += [f"## 2. Movers since {prev['date']}", ""]
        moved = [(g, g["playing"] - prev["playing"][g["universeId"]]) for g in games if g["universeId"] in prev["playing"]]
        new = [g for g in games if g["universeId"] not in prev["playing"]]
        table(["Game", "Playing", "Change", "Loop tags"],
              [[link(g), num(g["playing"]), f"{d:+,}", ", ".join(g["tags"]["loop"]) or "-"]
               for g, d in sorted(moved, key=lambda x: -x[1])[:12]])
        L += ["New to the charts: " + (", ".join(link(g) for g in sorted(new, key=lambda g: -g["playing"])[:15]) or "none"), ""]
    else:
        L += ["## 2. Movers", "", "Only one snapshot so far. Scan again on another day and this section fills in "
              "with the games gaining and losing players.", ""]

    L += ["## 3. Sub-genres: where the players are and how open the lane is", "",
          "*Young share* = players in games under 180 days old (high = new entrants are winning). "
          "*Leader share* = how much one game owns (high = a monopoly you will not dislodge by cloning).", ""]
    subs = defaultdict(list)
    for g in games:
        if g.get("subgenre"):
            subs[(g["genre"], g["subgenre"])].append(g)
    rows = []
    for (genre, sub), gs in subs.items():
        if len(gs) < 3:
            continue
        gs.sort(key=lambda g: -g["playing"])
        total = sum(g["playing"] for g in gs) or 1
        young = sum(g["playing"] for g in gs if g["ageDays"] and g["ageDays"] <= YOUNG_DAYS)
        rows.append((total, [f"{genre} / {sub}", len(gs), num(total), f"{100 * young / total:.0f}%",
                             f"{100 * gs[0]['playing'] / total:.0f}%",
                             sum(1 for g in gs if g["ranks"].get("top-earning", 999) <= 50), clean(gs[0]["name"], 30)]))
    table(["Sub-genre", "Games", "Playing", "Young share", "Leader share", "In top-50 earning", "Leader"],
          [r for _, r in sorted(rows, key=lambda x: -x[0])[:25]])

    L += ["## 4. Which genres earn more than their player count suggests", "",
          "Average of (player rank minus earning rank) for games on the Top Earning chart. "
          "Positive means the genre punches above its audience on revenue.", ""]
    table(["Genre", "Rank advantage", "Games on Top Earning"], [[g, f"{gap:+.0f}", n] for g, gap, n in money_gap(games)])

    for kind, title, blurb in (
        ("loop", "5. Core loops", "What the player actually does minute to minute."),
        ("theme", "6. Themes", "The skin. Cheap to swap, and the main thing the icon and title sell."),
        ("hook", "7. Retention and social hooks", "Reasons to come back tomorrow or bring a friend."),
    ):
        stats = tag_stats(games, kind)
        L += [f"## {title}", "", blurb + " Tags come from keyword matching on titles and descriptions, so check the examples.", ""]
        table(["Tag", "Games", "Playing", "Young share", "In top-50 earning", "Examples"],
              [[t, len(s["games"]), num(s["players"]), f"{100 * s['momentum']:.0f}%", s["earners"],
                ", ".join(clean(g["name"], 26) for g in s["games"][:3])]
               for t, s in sorted(stats.items(), key=lambda kv: -kv[1]["players"])])

    loops = tag_stats(games, "loop")
    L += ["## 8. Mix candidates: proven loops rarely combined", "",
          "Ranked by combined audience, weighted toward loops where young games are winning and penalised when "
          "charting games already pair them. This is raw material, not a verdict: take a pair, add a theme from "
          "section 6 and a hook from section 7, then run it through the scorecard.", ""]
    table(["Loop A", "Loop B", "Charting games combining both", "Combined heat", "Young share", "Study these"],
          [[m["a"], m["b"], m["existing"], num(m["heat"]), f"{100 * m['momentum']:.0f}%",
            " + ".join(clean(g["name"], 24) for g in exemplars(loops, m["a"], m["b"]))]
           for m in mixes(games, loops)])

    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"{date}.md"
    out.write_text("\n".join(L))
    print(f"wrote {out.relative_to(ROOT)}")
    return out


# ------------------------------------------------------------------------------- score --
# Weights sum to 100. The first four map directly onto the signals Roblox's home feed ranks on.
CRITERIA = [
    ("trend_fit", 15, "Sits in a lane where young games are charting right now"),
    ("instant_read", 15, "Icon + title explain the fantasy in under 3 seconds (drives play-through rate)"),
    ("first_five_minutes", 15, "A win, a reveal and a next goal inside 5 minutes (drives first-play bounce)"),
    ("return_reason", 15, "Something is waiting tomorrow: offline income, timers, events (drives play days)"),
    ("social_pull", 10, "Better with friends, or other players are the content (drives co-play)"),
    ("spend_depth", 10, "Repeatable purchases that scale with progress, not just one-off passes"),
    ("twist", 10, "One clear thing the exemplars do not have"),
    ("build_speed", 10, "Playable MVP in 2-4 weeks with the team you actually have"),
]
MUST_HAVES = ("instant_read", "first_five_minutes", "return_reason")


def score(args) -> None:
    card = json.loads(Path(args.file).read_text())
    ratings = card.get("ratings", {})
    unknown = set(ratings) - {k for k, _, _ in CRITERIA}
    if unknown:
        sys.exit(f"unknown criteria in {args.file}: {sorted(unknown)}")
    total, weak = 0.0, []
    print(f"\n{card.get('name', 'Untitled concept')}\n{card.get('pitch', '')}\n")
    for key, weight, meaning in CRITERIA:
        r = ratings.get(key)
        if not isinstance(r, (int, float)) or not 1 <= r <= 5:
            sys.exit(f"'{key}' needs a rating from 1 to 5 ({meaning})")
        total += weight * (r - 1) / 4
        if key in MUST_HAVES and r <= 2:
            weak.append(key)
        print(f"  {r} /5  x{weight:<3} {key:<20} {meaning}")
    print(f"\n  SCORE {total:.0f}/100")
    if weak:
        print(f"  VERDICT: rework. Rated 2 or lower on {', '.join(weak)}, and no other strength makes up for those.")
    elif total >= 75:
        print("  VERDICT: build the 2-4 week MVP and test it with real traffic.")
    elif total >= 60:
        print("  VERDICT: promising. Fix the lowest-rated line before building.")
    else:
        print("  VERDICT: pass. Go back to the mix table.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan", help="pull today's charts").set_defaults(fn=scan)
    r = sub.add_parser("report", help="write the trend report")
    r.add_argument("--snapshot", help="snapshot file (default: newest)")
    r.set_defaults(fn=report)
    s = sub.add_parser("score", help="score a concept card")
    s.add_argument("file")
    s.set_defaults(fn=score)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
