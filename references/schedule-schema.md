# The schedule file

`schedule.json` is the machine-readable authority for what is due, how risky it is, and what it
costs. `scripts/car.py` reads it and nothing else. Prose that disagrees with it is wrong.

One schedule per car, stored next to that car's `data/` directory. Resolution order:

1. `<car-dir>/schedule.json`
2. `<car-dir>/references/schedule.json`
3. the bundled `references/schedule.json` (the 207 example, used as a shape reference)

## Shape

```json
{
  "version": 1,
  "currency": "ARS",
  "market": "Argentina",
  "price_basis": {
    "source": "who published the numbers",
    "date": "2026-06",
    "note": "Bands are order-of-magnitude. Re-quote before deciding."
  },
  "items": [ ... ]
}
```

`currency` is the label printed in reports. `market` and `price_basis` are for the reader: they
are how a future session knows when a band has gone stale.

## Item fields

| Field | Type | Rules |
| --- | --- | --- |
| `id` | string | Stable, lowercase, snake_case. Used by `log --item`, so never rename it without a migration |
| `name` | string | Short, human. The unit is included: "front struts (pair)" |
| `interval_km` | int | `0` means time-only. Never guess a number to fill it |
| `interval_months` | int | `0` means distance-only. Most old-car items have both |
| `risk` | enum | `critical`, `high`, `medium`, `low` |
| `applies` | object | Filter on the profile, for example `{"gearbox": ["manual"]}`. `{}` means always |
| `spec` | string | The concrete specification: grade, capacity, part constraint |
| `if_unknown` | string | The action when there is no history. Required for `critical` |
| `cost_band` | `[low, high]` | Same currency as the file. `[0, 0]` for free work such as a recall |
| `notes` | string | The trap, the source, the exception |

The script derives `OVERDUE`, `DUE`, `SOON`, `UNKNOWN` and `OK` from these fields plus
`data/events.jsonl`. It does not hold its own copy of any interval, so editing this file is always
safe and always takes effect.

## Rules for adding items

1. **One item is one decision.** "Brakes" is not an item. Discs, pads, fluid and a rear cylinder
   are four items with four different triggers.
2. **`critical` is reserved for safety and for the cost of a sudden failure.** Belt, brake
   fluid, brakes, tires, cooling, steering. If everything is critical, nothing is.
3. **A `critical` item needs `if_unknown`.** The default answer is "replace now", because an
   unknown safety item cannot be driven on trust.
4. **Intervals come from the manufacturer plan for this engine and market**, shortened for severe
   use. Record the deviation in `notes` and say why.
5. **`interval_km: 0` is legitimate.** Inspections, the annual technical inspection, recall
   checks and fluid-by-age items are time-based.
6. **Every item must be resolvable.** If it has no interval and no `if_unknown`, delete it. It
   will only produce noise in the status table.

## Risk and the status buckets

The bucket is computed from the remaining distance and the remaining days, whichever expires
first. `risk` decides the ordering and whether the item appears in the critical shortlist.

| Bucket | Meaning |
| --- | --- |
| `OVERDUE` | Past the km limit or past the date. Act |
| `DUE` | Within 1,000 km or 30 days. Book it |
| `UNKNOWN` | No recorded history. Resolve with a document or an inspection |
| `SOON` | Within 3,000 km or 90 days. Plan and budget |
| `OK` | No action |

`UNKNOWN` is not a neutral state. On a `critical` item it is a stronger warning than `OVERDUE`,
because it hides a possible failure rather than a known one.

## Example

A minimal item, complete enough for the script to use:

```json
{
  "id": "timing_belt",
  "name": "Timing belt + tensioner + water pump",
  "interval_km": 80000,
  "interval_months": 60,
  "risk": "critical",
  "applies": {},
  "spec": "Kit ordered by engine code. Replace the tensioner, the idler and the water pump together.",
  "if_unknown": "Replace now if there is no invoice. At this age the belt is due by time even with low km.",
  "cost_band": [300000, 600000],
  "notes": "A broken belt on an interference engine bends valves. This is the most expensive item to defer."
}
```

For a complete, real example with 33 items, read
[`examples/peugeot-207/schedule.json`](../examples/peugeot-207/schedule.json).

## When the car is unknown

`references/schedule.template.json` ships an empty schedule with three illustrative items. The
research workflow fills it, item by item, from the source tiers in
[`research-protocol.md`](research-protocol.md). An empty `items` list is valid: the tool then
reports every profile gap and nothing else, which is the correct answer for a car nobody has
researched yet.
