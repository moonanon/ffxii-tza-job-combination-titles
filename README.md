# FFXII: The Zodiac Age — Hybrid Job Titles

A **text-only** mod for FINAL FANTASY XII THE ZODIAC AGE (PC). When a character has two jobs, the game shows one title
for the pair (Knight + White Mage → **Paladin**). The 12 vanilla jobs, license boards, abilities, stats and saves are
untouched.

**Scope:** hybrid job labels and job renames (Uhlan → **Lancer**). Nothing deeper.

## Installing

Requires the Steam version of the game (1.0.4.0, the current build) with:
- [FF12 External File Loader](https://www.nexusmods.com/finalfantasy12/mods/170)
- [FF12 LUA Loader](https://www.nexusmods.com/finalfantasy12/mods/171)

1. Download `HybridJobTitles-<version>.zip` from [Releases](../../releases).
2. Extract it into the game folder (the one with `FFXII_TZA.vbf`), so the script lands at
   `x64/scripts/HybridJobTitles.lua`. With a mod manager (Vortex, Amethyst), add the zip as a mod instead.
3. Start the game. A character with two jobs shows its hybrid title in the party menu, license board header and job
   screen. If your game build differs, the script changes nothing and logs why.

Uninstall by deleting `x64/scripts/HybridJobTitles.lua`. Saves are never touched.

### Optional: Uhlan → Lancer

The rename patches one of the game's own text files, so it is built from your copy instead of shipped:

```sh
cd src
python -m hybrid_job_titles --game "<FINAL FANTASY XII THE ZODIAC AGE folder>" --out ../dist
```

Copy `dist/HybridJobTitles/mods` into the game folder. Python 3.10+, no other packages.

## Naming philosophy

1. **Classic Final Fantasy names when they fit both jobs.** Paladin is Knight + White Mage (holy knight), not
   Knight + Archer. Sage is White + Black Mage, Dark Knight is Knight + Black Mage.
2. **Hand-picked titles** for pairs with an obvious identity: Lancer + White Mage = **Holy Lancer** (Kain's Holy
   Dragoon, renamed to suit FFXII's military naming: Uhlan/Lancer instead of Dragoon, since there's no Jump).
   Archer + White Mage = **Druid**, Archer + Lancer = **Hunter**, Knight + Shikari = **Duelist**.
3. **Main characters' canon pairs get evocative titles, not other characters' iconic ones.** Vaan
   (Shikari + Black Mage) = **Saboteur**; Penelo (White Mage + Monk) = **Dervish**, a dancer-mystic nod to her
   later Dancer class. Iconic names like Dragoon are avoided so they don't read as a specific character.
4. **Affixes when a name would stretch.** Each job has stems (prefixes) and/or suffixes, sometimes several. When both
   jobs have a suffix, the more distinctive one wins (‑blade, ‑fist).
5. **Bushi uses Japanese titles only with physical jobs** (Shikari, Archer, Foebreaker, Knight, Monk, Machinist,
   Lancer). With mage jobs it gets plain titles.
6. **No duplicates**, and only letters and spaces (upstream's label encoder in `job_labels.py` supports just those).

In `data/job-titles.json`, pairs use **vanilla** job names (`Uhlan`); `renames` holds the displayed labels.

### Job affixes

| Job | Stem (prefix) | Suffix | Examples |
|---|---|---|---|
| Shikari | Shadow | ‑blade | Whiteblade, Arcaneblade, Chronoblade, Dragonblade, Gunblade |
| Monk | — | ‑fist | Blackfist, Arcanefist, Chronofist, Dragonfist, Gunfist, Shadowfist, Hawkfist |
| Machinist | Gun / Magitek | ‑gunner | Gunblade, Gunfist, Gunmage, Gunner, Magitek Adept, Chrono Gunner |
| Archer | Hawk | ‑arrow / ‑shot | Spellarrow, Chronoshot, Hawkfist |
| Lancer (Uhlan) | Dragon | … Lancer | Holy Lancer, Dark Lancer, Rune Lancer, Chrono Lancer, Dragonblade, Dragonfist |
| Black Mage | Spell / Black / Dark | — | Spellarrow, Spellbreaker, Blackfist, Dark Knight, Dark Lancer, Dark Samurai |
| Red Battlemage | Arcane | — | Arcane Ranger, Arcaneblade, Arcanefist |
| White Mage | White / Holy | — | Whiteblade, Holy Lancer, Holy Samurai |
| Time Battlemage | Chrono | — | Chronoblade, Chronofist, Chronoshot, Chronobreaker, Chrono Gunner, Chrono Lancer, Chronodraw |
| Foebreaker | — | ‑breaker | Spellbreaker, Chronobreaker |
| Knight | — | … Knight | Dark Knight, Mystic Knight, Rune Knight |
| Bushi | Japanese title (physical pairs) | — | Shinobi, Sohei, Ryukishi (竜騎士, "Dragoon"), Hatamoto, Ashigaru, Kyudoka, Ronin |

## Development

- `data/job-titles.json`: the 66 titles (pairs use vanilla job names) and renames.
- `src/lua/HybridJobTitles.lua.in`: the in-game hook. At startup it redirects one call in the game's shared
  "Job/Job" label formatter so a two-job character shows its title.
- `src/hybrid_job_titles/`: the build (`python -m hybrid_job_titles` from `src/`) the game archive reader (`archive.py`) and text patcher (`labels.py`).
- Tests: `python -m unittest discover -s tests`. Pushing a `v*` tag builds and publishes a release.

**Status: not yet confirmed in game.**

## Credits

The location of the game's "Job/Job" label formatter, the native job IDs and the game's text and archive formats were
worked out by [**Ivalice Legacy** by marcovdss](https://github.com/marcovdss/FF12IvaliceLegacy); this mod builds on that
research. Thanks also to ffgriever for the FF12 External File Loader and LUA Loader.

## Combinations

Every job lists all 11 partners, so each pair appears twice.

### Archer

| Pair | Title |
|---|---|
| Archer + Black Mage | Spellarrow |
| Archer + Bushi | Kyudoka |
| Archer + Foebreaker | Arbalist |
| Archer + Knight | Warden |
| Archer + Lancer | Hunter |
| Archer + Machinist | Sniper |
| Archer + Monk | Hawkfist |
| Archer + Red Battlemage | Arcane Ranger |
| Archer + Shikari | Ranger |
| Archer + Time Battlemage | Chronoshot |
| Archer + White Mage | Druid |

### Black Mage

| Pair | Title |
|---|---|
| Black Mage + Archer | Spellarrow |
| Black Mage + Bushi | Dark Samurai |
| Black Mage + Foebreaker | Spellbreaker |
| Black Mage + Knight | Dark Knight |
| Black Mage + Lancer | Dark Lancer |
| Black Mage + Machinist | Magitek Adept |
| Black Mage + Monk | Blackfist |
| Black Mage + Red Battlemage | Magus |
| Black Mage + Shikari | Saboteur |
| Black Mage + Time Battlemage | Warlock |
| Black Mage + White Mage | Sage |

### Bushi

| Pair | Title |
|---|---|
| Bushi + Archer | Kyudoka |
| Bushi + Black Mage | Dark Samurai |
| Bushi + Foebreaker | Ronin |
| Bushi + Knight | Hatamoto |
| Bushi + Lancer | Ryukishi |
| Bushi + Machinist | Ashigaru |
| Bushi + Monk | Sohei |
| Bushi + Red Battlemage | Swordmage |
| Bushi + Shikari | Shinobi |
| Bushi + Time Battlemage | Chronodraw |
| Bushi + White Mage | Holy Samurai |

### Foebreaker

| Pair | Title |
|---|---|
| Foebreaker + Archer | Arbalist |
| Foebreaker + Black Mage | Spellbreaker |
| Foebreaker + Bushi | Ronin |
| Foebreaker + Knight | Barbarian |
| Foebreaker + Lancer | Ravager |
| Foebreaker + Machinist | Artillerist |
| Foebreaker + Monk | Brawler |
| Foebreaker + Red Battlemage | Warmage |
| Foebreaker + Shikari | Reaver |
| Foebreaker + Time Battlemage | Chronobreaker |
| Foebreaker + White Mage | Crusader |

### Knight

| Pair | Title |
|---|---|
| Knight + Archer | Warden |
| Knight + Black Mage | Dark Knight |
| Knight + Bushi | Hatamoto |
| Knight + Foebreaker | Barbarian |
| Knight + Lancer | Cavalier |
| Knight + Machinist | Musketeer |
| Knight + Monk | Templar |
| Knight + Red Battlemage | Mystic Knight |
| Knight + Shikari | Duelist |
| Knight + Time Battlemage | Rune Knight |
| Knight + White Mage | Paladin |

### Lancer

| Pair | Title |
|---|---|
| Lancer + Archer | Hunter |
| Lancer + Black Mage | Dark Lancer |
| Lancer + Bushi | Ryukishi |
| Lancer + Foebreaker | Ravager |
| Lancer + Knight | Cavalier |
| Lancer + Machinist | Gunner |
| Lancer + Monk | Dragonfist |
| Lancer + Red Battlemage | Rune Lancer |
| Lancer + Shikari | Dragonblade |
| Lancer + Time Battlemage | Chrono Lancer |
| Lancer + White Mage | Holy Lancer |

### Machinist

| Pair | Title |
|---|---|
| Machinist + Archer | Sniper |
| Machinist + Black Mage | Magitek Adept |
| Machinist + Bushi | Ashigaru |
| Machinist + Foebreaker | Artillerist |
| Machinist + Knight | Musketeer |
| Machinist + Lancer | Gunner |
| Machinist + Monk | Gunfist |
| Machinist + Red Battlemage | Gunmage |
| Machinist + Shikari | Gunblade |
| Machinist + Time Battlemage | Chrono Gunner |
| Machinist + White Mage | Medic |

### Monk

| Pair | Title |
|---|---|
| Monk + Archer | Hawkfist |
| Monk + Black Mage | Blackfist |
| Monk + Bushi | Sohei |
| Monk + Foebreaker | Brawler |
| Monk + Knight | Templar |
| Monk + Lancer | Dragonfist |
| Monk + Machinist | Gunfist |
| Monk + Red Battlemage | Arcanefist |
| Monk + Shikari | Shadowfist |
| Monk + Time Battlemage | Chronofist |
| Monk + White Mage | Dervish |

### Red Battlemage

| Pair | Title |
|---|---|
| Red Battlemage + Archer | Arcane Ranger |
| Red Battlemage + Black Mage | Magus |
| Red Battlemage + Bushi | Swordmage |
| Red Battlemage + Foebreaker | Warmage |
| Red Battlemage + Knight | Mystic Knight |
| Red Battlemage + Lancer | Rune Lancer |
| Red Battlemage + Machinist | Gunmage |
| Red Battlemage + Monk | Arcanefist |
| Red Battlemage + Shikari | Arcaneblade |
| Red Battlemage + Time Battlemage | Oracle |
| Red Battlemage + White Mage | Devout |

### Shikari

| Pair | Title |
|---|---|
| Shikari + Archer | Ranger |
| Shikari + Black Mage | Saboteur |
| Shikari + Bushi | Shinobi |
| Shikari + Foebreaker | Reaver |
| Shikari + Knight | Duelist |
| Shikari + Lancer | Dragonblade |
| Shikari + Machinist | Gunblade |
| Shikari + Monk | Shadowfist |
| Shikari + Red Battlemage | Arcaneblade |
| Shikari + Time Battlemage | Chronoblade |
| Shikari + White Mage | Whiteblade |

### Time Battlemage

| Pair | Title |
|---|---|
| Time Battlemage + Archer | Chronoshot |
| Time Battlemage + Black Mage | Warlock |
| Time Battlemage + Bushi | Chronodraw |
| Time Battlemage + Foebreaker | Chronobreaker |
| Time Battlemage + Knight | Rune Knight |
| Time Battlemage + Lancer | Chrono Lancer |
| Time Battlemage + Machinist | Chrono Gunner |
| Time Battlemage + Monk | Chronofist |
| Time Battlemage + Red Battlemage | Oracle |
| Time Battlemage + Shikari | Chronoblade |
| Time Battlemage + White Mage | Astrologian |

### White Mage

| Pair | Title |
|---|---|
| White Mage + Archer | Druid |
| White Mage + Black Mage | Sage |
| White Mage + Bushi | Holy Samurai |
| White Mage + Foebreaker | Crusader |
| White Mage + Knight | Paladin |
| White Mage + Lancer | Holy Lancer |
| White Mage + Machinist | Medic |
| White Mage + Monk | Dervish |
| White Mage + Red Battlemage | Devout |
| White Mage + Shikari | Whiteblade |
| White Mage + Time Battlemage | Astrologian |
