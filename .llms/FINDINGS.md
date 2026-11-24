# Findings

## Upstream (marcovdss/FF12IvaliceLegacy @ 48c2158; research source only, no code imported (it has no LICENSE))
- Native job labels are patched by `ivalice_legacy/job_labels.py`: `encode_label` only supports space, A–Z, a–z and
  digits 1–9 — no hyphens or apostrophes. Patches are source-hash pinned against the game's ST2E text files.
- `patches/hybrid_names.json` holds upstream's 66 pair names keyed by *their* renamed job indices (0 = White Mage,
  4 = Knight, …), not vanilla names. Their jobs are renamed (Hunter, Samurai, Gunner…); ours stay vanilla.
- Hybrid display in-game upstream is tied to a native C++ board-fusion core (`native/hybrid_boards`), only piloted for
  Paladin. We only want the label, so expect to need a lighter hook or text patch than theirs.
- Upstream has no LICENSE file.

## Hybrid label hook (how ours works)
- Native job IDs: 0 White Mage, 1 Uhlan, 2 Machinist, 3 Red Battlemage, 4 Knight, 5 Monk, 6 Time Battlemage,
  7 Foebreaker, 8 Archer, 9 Black Mage, 10 Bushi, 11 Shikari. Job-name strings are IDs 10100+id in
  `ps2data/image/ff12/test_battle/us/binaryfile/menu_command.bin` (sha 7c8002…).
- The shared "Job/Job" formatter (party menu, board header, job screen) calls the label lookup 0x2F9860 at
  VA 0x556419 (continuation 0x55641E; Steam 1.0.4.0, base 0x120000) with R13D/R15D = the two jobs. Returning a
  string in RAX and setting R15D = -1 makes it print that string alone. Source: upstream adapter.cpp `PairLabel`
  site / sites.py site 18. Not yet observed in game by us or (as far as their docs say) upstream.
- Lua loader API used: memory.readArray/writeArray (writeArray works on code pages), memory.alloc/allocExe,
  event.registerEventAsync('onInitDone'). Scripts are Lua 5.4 (`&`, `math.type`).
- The game lives in Flatpak Steam: ~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/FINAL FANTASY XII THE ZODIAC AGE. Its FFXII_TZA.exe sha256 matches upstream (73461d08…), and the bytes at 0x556419 are the expected CALL. The loaders are symlinked from ~/Games/Amethyst (Flatpak has access). The file loader reads loose files from mods\deploy\ff12data.
