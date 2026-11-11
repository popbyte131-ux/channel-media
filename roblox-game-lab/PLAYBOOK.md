# Playbook: what to build, why games win, where the money is

Two kinds of facts are in here. Market readings come from our own scan of Roblox's public
charts on 2026-11-11 ([report](reports/2026-11-11.md)). Platform rules (the feed's ranking
signals, payout rates) come from Roblox's Creator docs and DevForum announcements as
summarised by web search in November 2026; the pages themselves were not opened, so confirm
the numbers in Creator Hub before planning around them. Sources are at the bottom.

## 1. What decides success

Almost all traffic comes from the Home feed ("Recommended For You"), and that feed ranks
games on how players behave *after* seeing them. Roblox lists these signals, measured as
averages per user over a 28-day window:

| Tier | Signal | What it means | What you control |
|---|---|---|---|
| Most important | Play-through rate | Of people shown your tile, how many click play | Icon, title, thumbnail |
| Most important | First-play bounce rate | How many leave after a very short first session | The first 5 minutes |
| Most important | Play days per user | How many separate days a player comes back | The reason to return tomorrow |
| Most important | Playtime per user | Total time played | Depth of the loop |
| Next | Intentional co-play days | Days played together with friends on purpose | Co-op and social features |
| Next | Qualified play sessions | Sessions long enough to count | Session pacing |
| Next | Spend days, Robux spent per user | How often and how much players pay | The shop |

Because the signals are per-user averages, a small game with strong numbers outranks a big
game with weak ones. That is the opening for a new game: the feed gives every game a trickle
of test impressions, and good numbers on that trickle earn more.

In practice that makes four gates, in order. A game that fails an early gate never gets to
show its strength at a later one.

1. **The tile.** Title and icon must explain the fantasy in under three seconds. Look at
   the names charting right now: *Steal An Egg*, *Throw Food For Animals*, *Net a Fish!*,
   *Sweep The Moon*, *Build a Bridge*. Each is a verb, an object, and the whole game.
2. **The first five minutes.** No menus, no tutorial text walls. The player should do the
   core action within 30 seconds, win something within 2 minutes, see something they want
   but cannot yet afford, and know their next goal.
3. **The reason to come back.** Offline income waiting to be collected, a hatch timer, a
   daily reward streak, a restock or weekly event. Without one, play days stay at 1.
4. **The reason to pay.** Covered in section 3.

For scale: across all Roblox games the median is roughly 10% of players back on day 1 and
under 2% on day 7. The top 1% reach about 22% on day 1 and 9% on day 7 (third-party
GameAnalytics figures). Roblox says these benchmarks do not feed the algorithm directly;
use the "similar games" benchmarks in Creator Analytics for your own genre.

Things that also matter:

- **Speed.** Trends turn over in weeks. Most of the 25 breakouts in the report are under
  35 days old. A decent game in the right month beats a great one two months late.
- **Updates.** Top games ship weekly, with a visible event or content drop. Each one is a
  fresh reason to return and to spend.
- **Kill fast.** If the MVP's first-play bounce and day-1 return are well under the genre
  benchmark after a few thousand plays and one round of fixes, move to the next idea.

## 2. What the market looks like (scan of 2026-11-11)

**Where new games are winning.** "Young share" is the share of a lane's players who are in
games under 180 days old. "Leader share" is how much one game owns.

| Lane | Playing | Young share | Leader share | Read |
|---|---|---|---|---|
| Simulation / Tycoon | 1.3M | 92% | 54% (Steal An Egg) | Hottest lane, but half of it is one game |
| Simulation / Incremental Simulator | 471K | 54% | 13% | Biggest open lane: large, fresh, no single owner |
| Survival / Escape | 148K | 60% | 28% | Open |
| Simulation / Vehicle Sim | 133K | 65% | 11% | Open and fragmented |
| Simulation / Physics Sim | 100K | 78% | 21% | Easy traffic, see the money warning below |

**Where they are not.** Pet Care (Adopt Me! holds 97%), Life roleplay (Brookhaven 70%),
1 vs All (Murder Mystery 2 80%), Action RPG (2% young share), Deathmatch Shooter (5%).
These are owned by old giants with years of content. Do not enter head-on.

**What earns.** Comparing each game's rank on Top Earning to its rank on players:

- RPG, Shooter and Action games sit about 40 places higher on earnings than on players.
  Deep progression and competition make people pay.
- Simulation is positive but lower (+20). Survival earns *less* than its audience suggests.
- Physics and sandbox games had zero entries in the top 50 earners despite 145K players.
  They get clicks and have nothing to sell.
- Rarity and mutation systems appear in 10 of the top 50 earners. Trading appears in few
  games but those games are huge and old (Murder Mystery 2, Adopt Me!): it is what turns a
  hit into a decade-long one.

**Themes.** Animals (75% young share) and food (90%) are what new hits are wearing.
Brainrot is down to 4% young share: its audience is still there but new entrants are no
longer winning with it.

**The takeaway.** The easy lanes to enter (incremental, physics, tycoon) are not the ones
that pay best (RPG, fighting, collection with rarity). The strongest play is to enter
through an open lane's simple, instantly readable loop and bolt on the spending depth of
the lanes that pay: rarity tiers, mutations, upgrades without a ceiling, and eventually
trading.

## 3. How the money works

**The conversion.** Players pay in Robux. You keep 70% of game pass and developer product
sales. Earned Robux cash out through DevEx at $0.0038 each ($0.0054 for qualifying spend
from verified US players aged 18+, since June 2026). Minimum cash-out is 30,000 earned
Robux, about $114.

So a 100 Robux purchase is 70 Robux to you, which is about $0.27.

**Rough revenue formula:**

    daily $ = daily players x share who pay x Robux per payer per day x 0.70 x 0.0038

As an illustration with made-up inputs, 20,000 daily players with 2% paying 150 Robux each
gives 20,000 x 0.02 x 150 x 0.70 x 0.0038 = about $160 a day. Replace the inputs with your
real numbers from Creator Analytics; conversion and spend vary enormously by genre.

**Revenue streams, in the order to build them:**

1. **Developer products (repeatable purchases).** The main earner in every top simulator:
   currency packs, luck boosts, skip-the-wait, extra rolls, revives. They can be bought
   again and again, so they scale with how long someone plays. Price a ladder from about
   25 to 5,000+ Robux so there is always a next step up.
2. **Game passes (one-off).** Permanent perks: 2x income, auto-collect, extra slots, VIP.
   Sell 3-5 that a committed player obviously wants. Show them at the moment of need, for
   example offer auto-collect while the player is collecting by hand.
3. **Starter pack and limited offers.** A cheap, generous first purchase, shown after the
   first real win. A player who has paid once is far more likely to pay again.
4. **Creator Rewards (no shop needed).** Roblox pays 5 Robux each day for every
   active-spender who makes your game one of their first three of the day and stays 10
   minutes, plus a 35% share of the first $100 spent by players your game brings to
   Roblox or brings back after 60+ days away. This pays for retention directly.
5. **Subscriptions.** A monthly VIP tier once you have a returning audience.
6. **Rewarded video ads.** Players choose to watch an ad for a boost. Income from players
   who will never buy Robux.
7. **Private servers and avatar items.** Minor, but nearly free to add.

**Design rules that raise spend without hurting retention:**

- Sell *time and luck*, not the win itself. Boosts and skips monetise impatience; selling
  outright victory in a competitive game drives away the non-payers everyone plays against.
- Tie the best purchases to the weekly event. Limited-time rarity is what makes people act.
- Spending depth has to grow with progress. If the most a veteran can spend is 500 Robux,
  that is the ceiling on your best customers.
- Follow Roblox's rules for paid random items (odds must be shown; they are restricted in
  some countries) and remember much of the audience is children. Dark patterns get games
  moderated and get refunds issued.

## 4. Three mixes worth testing now

Each pairs two proven loops that no charting game combined on 2026-11-11, uses a rising
theme, and carries a spend system from the lanes that pay. These are starting hypotheses:
play the reference games and score each with `lab.py score` before committing.

1. **Fling For Eggs** (ragdoll physics x collect-and-hatch). Launch yourself across a
   canyon to grab eggs from cliff nests; farther nests hold rarer eggs; hatched pets earn
   while you are offline. It takes the click appeal of physics games, which currently earn
   nothing, and gives them a shop: launch power, luck, egg slots. Reference games:
   DONT SPLASH, Steal An Egg. Scored in `concepts/example.json`: 74/100 on first-guess
   ratings, one point short of "build", held back by social pull and build speed.
2. **Build a Vault** (sandbox building x steal). Build trap-filled defences around your
   loot from blocks, then raid other players' builds. Other players make the levels, so
   content never runs out. Sells block packs, trap types, raid shields. Larger scope than
   the others. Reference games: Steal An Egg, Build a Bridge.
3. **Feed the Thief** (incremental x social deduction). A server grows a shared food stall
   together; each round one hidden player is secretly skimming the till, and everyone
   votes. The riskiest of the three, because round-based games need full servers to be
   fun, but the pairing is untouched and Murder Mystery 2 shows how long the format lasts.

## Sources

Market data: our own scan of Roblox's public chart API, in `data/snapshots/`.

Platform rules and benchmarks (via web search summaries, November 2026):

- [Roblox Creator Docs: Discovery](https://create.roblox.com/docs/discovery) and [Discovery FAQ](https://create.roblox.com/docs/discovery-faq)
- [Roblox newsroom: Optimizing discovery (June 2026)](https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox)
- [DevForum: Improved Recommended For You algorithm](https://devforum.roblox.com/t/boost-your-discovery-with-the-improved-recommended-for-you-algorithm-and-analytics-for-creators/3587441)
- [Roblox Creator Docs: Creator Rewards](https://create.roblox.com/docs/creator-rewards)
- [DevForum: US 18+ DevEx rate](https://devforum.roblox.com/t/introducing-the-us-18-devex-rate-earn-42-more-on-spend-from-18-us-players/4607091)
- [devex.gg: DevEx rates in 2026](https://devex.gg/devex-rates)
- [GameAnalytics 2025 Roblox report](https://www.gameanalytics.com/reports/2025-roblox-report) (retention medians, via a secondary summary)
