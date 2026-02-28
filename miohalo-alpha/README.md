# miohalo-alpha

`miohalo-alpha` is the first technical prototype for the Miohalo project.

Its current focus is building a symbol pipeline that can later support ASO-style multi-agent collaboration.

## Goals in alpha

- Collect candidate characters/glyphs.
- Group them into stable families.
- Rank/select representative symbols.
- Audit whether common fonts can render them.
- Produce previews for fast human review.

## Scripts (current)

- `scripts/collect_latin.py`
  - Collects Latin/extended symbol candidates.
- `scripts/e8_family_grouper.py`
  - Groups symbols into structural families.
- `scripts/e8_family_rank_sample.py`
  - Scores/ranks samples from grouped families.
- `scripts/preview_miohalo_selection.py`
  - Renders preview sheets for selected symbols.
- `scripts/audit_font_coverage.py`
  - Checks missing glyphs/combining marks against available fonts.
- `scripts/render_stub.py`
  - Rendering/testing scaffold.

## Intended alpha flow

1. Generate or refresh candidate sets.
2. Group + rank.
3. Preview selected symbols.
4. Run font coverage audit.
5. Iterate with reject/allow lists.

## Relationship to ASO

The alpha is the **symbol substrate**.  
The next layer (to be added) is the **spell packet schema** and inter-agent handoff runtime.

In other words:

- alpha now = visual/symbolic infrastructure,
- next = protocol and orchestration.
