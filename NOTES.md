# NOTES — the-poster-for-a-place-that-i-2-20261121-0539-entry-v2

## Submit title

Velmara

## One-line summary (repo About description)

Velmara — a golden-hour travel poster for a floating-island village above the clouds, rendered in pure-stdlib Python.

## The 3 variants

All three are complete, self-contained `main.py` programs (pure Python standard
library: `zlib` + `struct` PNG writer, gradient skies, vector shapes, a
built-in 5x7 bitmap font — no PIL, no network). Each renders a 768x1024 PNG
to `/output/entry.png`. Sources live in `variants/v1|v2|v3/main.py`.

- **V1 — VELMARA, "Isles Above the Clouds"**: a village with lit windows on a
  floating island at golden hour; sun setting behind the island rim,
  waterfalls spilling into a sea of clouds below. Warm indigo-to-amber palette.
- **V2 — THALORIN, "Lights Over the Quiet Fjord"**: aurora bands over a dark
  fjord at night; moon, stars, snow-capped mountains, lantern-lit cabins on
  the shore with reflections. Cold teal/violet palette.
- **V3 — SOLMERE, "The Oasis of Two Suns"**: a desert of rose dunes with two
  suns, a stone ring-gate monument on the horizon, and a teal oasis lagoon
  framed by palms. Warm peach/rose palette.

## Scoring against the 5 judge criteria (1 = best, 5 = worst, per variant)

| Criterion | V1 Velmara | V2 Thalorin | V3 Solmere |
|---|---|---|---|
| 1. Poster for a place that isn't there, name set in the picture | 1 — name large, legible, top of poster | 1 — same | 1 — same |
| 2. Makes you want to go (weather, light, landmark = promise of a stay) | 1 — lit village windows promise a stay; golden-hour warmth | 2 — cabins promise a stay but the scene is cold, dark, remote | 3 — lagoon + gate invite a visit, but no dwelling, no "stay" |
| 3. Distinct invented identity | 1 — floating-island village is unmistakably invented | 3 — aurora + fjord reads close to real Norway/Iceland | 2 — twin suns + ring gate are distinct |
| 4. Type with intent (legible, well placed, carries the mood) | 1 — cream on deep violet, clean after fix | 1 — crisp white on dark night sky | 2 — legible, but subtitle rules first struck through the text |
| 5. Colour & composition (eye: name -> landmark -> horizon) | 1 — warm gradient leads name -> island -> cloud sea | 2 — aurora leads the eye, but the bottom half is empty dark water | 3 — strong gate/lagoon, but dune polygons left black slivers at the edges and the palms read as stick arrows |

## Why the winner won

**V1 Velmara** is the only variant that scores top marks on the two criteria the
judge weights most: it is unmistakably a poster for a place that doesn't exist,
and it sells a stay — a lived-in village with glowing windows on an island in
the sky at golden hour, waterfalls falling into clouds. Its warm palette and
clear name -> island -> cloud-sea composition beat Thalorin's beautiful but
cold and half-empty fjord, and Solmere's twin-sun desert, which had visible
rendering defects (black gaps at the dune edges, stick-figure palms).

## Fixes applied to the winner after judging

- The sun was hidden behind the island; moved to set just behind the island's
  rim (glow + disc now visible above the village).
- The subtitle rule lines struck through the subtitle text; shortened and moved
  to flank the text cleanly.
- Added faint rock strata lines so the island's underside is not one flat
  dark triangle.

## Winner verification (final root main.py, run twice)

- PNG: **768x1024**, 8-bit RGB
- Size: **47,207 bytes** (limit 1,048,576)
- SHA-256: `4631f160aa4ac197617c146e7b64fbf3bc2e3171c966c4cb00d59b3e43c609c1`
- Determinism: **byte-identical across two runs** (same SHA-256 both times)
- Pre-fix verification (for the record): V1 41,937 bytes
  (`110cdd172b37c2b8e6decffbe42bf02d24c3a21ae6d13fed3e5a3679b1adf978`),
  V2 43,854 bytes
  (`b31162ae19c0b22e03390d56d71d155596fe9a96d535aeb50b377a29be59616c`),
  V3 36,316 bytes
  (`3f91d8fd4d41b4b2f976d04d66fca6e82142fb82865d3d6e5be169961977d7ce`) —
  all 768x1024, all deterministic across two runs.

`preview-entry.png` in this directory is the winner's rendered poster
(inspection only — do not push).
