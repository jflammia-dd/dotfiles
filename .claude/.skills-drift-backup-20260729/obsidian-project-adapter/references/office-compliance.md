# Office Compliance Calculation

Canonical algorithm for office attendance compliance. All office tracking commands and the obsidian skill defer to this file. Do not duplicate this logic elsewhere.

## Lookup Table

60% of available days, rounded:

| Available Days | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|
| Expected Days  | 3 | 2 | 2 | 1 | 1 | 0 |

## Per-Week Calculation

For a given week:

1. Count `ooo_days`: entries starting with `- OOO`. A combined line like `OOO - Public Holiday, ...; PTO, ...` counts as 2.
2. `available_days = 5 − ooo_days`
3. Look up `expected_days` from the table above using `available_days`.
4. Count `actual_days`: entries starting with `- DayOfWeek,` (plain in-office days only — do NOT count WFH or OOO entries).

WFH days do not reduce available days and do not count as in-office days. Only OOO/PTO/holidays reduce available days.

### Weekly Status Line Format

Place immediately after the `#### Week N` header, before any entries. `X` = `actual_days`, `Y` = `expected_days`.

A week is "completed" if its Friday has passed.

- Week in progress or future, on track (`actual >= expected`): `✅ X/Y days`
- Week in progress or future, behind: `⚠️ Need Z more day(s) by Friday (X/Y so far)`
- Week completed, on track: `✅ X/Y days`
- Week completed, behind: `❌ X/Y days`

Where `Z = expected_days − actual_days`.

Future weeks with no entries: no status line.

## Monthly Calculation

Sum across **all weeks in the month**, including weeks with only a bare `-` placeholder. A bare `-` week contributes `actual_days = 0` and its full `expected_days` (looked up from the table using `available_days = 5 − ooo_days`, where `ooo_days = 0` for a bare week).

- `monthly_actual = sum of actual_days across all weeks`
- `monthly_expected = sum of expected_days across all weeks`
- `deficit = monthly_expected − monthly_actual`

### Monthly Status Line Format

Place at the top of the `## Month` section. Format: `Target: Y | In-office: X`

Where `Y` = `monthly_expected` (sum of expected days across all weeks in the month) and `X` = `monthly_actual` (running count of in-office days logged so far).

- Month complete and compliant (`X >= Y`): `Target: Y | In-office: X ✅`
- All other states (in progress, behind, or complete but non-compliant): `Target: Y | In-office: X`

Recompute `Target:` only when OOO entries in a week change (adding or removing OOO changes available days, which may shift expected days via the lookup table). Increment `In-office:` by 1 for each new in-office day. `In-office:` does not change when adding WFH or OOO entries.

## YTD Summary Badge Format

The YTD badge is auto-computed by a Dataview JS block at the top of `docs/2026 - In-Office Tracking.md`. It reads the `Target: Y | In-office: X` line from each month section and renders the badge dynamically on save.

Do not update the badge manually. Keeping `Target:` and `In-office:` accurate in each monthly section is sufficient.
