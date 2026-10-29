# Worked example: Peugeot 207 Compact Allure 2014 (Argentina)

A complete record, produced by the protocol in
[`../../references/research-protocol.md`](../../references/research-protocol.md). Read it to see
what "researched" means before you run the skill on your own car.

## What is in this directory

| File | Real or illustrative |
| --- | --- |
| `schedule.json` | **Real research.** 33 items with intervals, specifications and Argentine cost bands for this model |
| `data/vehicle.json` | **Illustrative.** The vehicle specification is real for the variant; the VIN and plate are `null`, and the baseline odometer is invented |
| `data/events.jsonl` | **Illustrative.** Two demo events, labelled `DEMO EVENT, not a real car` |
| `references/playbook.md` | **Real research, condensed.** Ten fault groups for the 1.4 8v, each with a decisive test and a cost band |
| `documents/` | Empty, as a fresh record should be |
| `reports/` | Empty. Generate one with `car.py report` |

No personal data is present: no VIN, no plate, no owner, no shop that can be traced to a person,
no real invoice. `Example Garage` is not a real workshop.

## Why this car is a good teaching case

The 2014 Argentine Allure was sold mainly with the **1.4 8v** (`TU3JP`) and the **1.4 HDi**, while
earlier Allures had the **1.6 16v** (`TU5JP4`). Three different engines, three different belt or
chain situations, three different plug sets, all under one model name and one body.

That is the trap the protocol exists to prevent. Research the model name and you will price the
wrong belt kit. The example therefore fixes the engine code first, records it in `verification`,
and keeps "confirm on the engine plate" as an open question.

It is also a case where **age beats kilometres**: a 12-year-old car with 120,000 km needs a belt
by time, not by distance.

## What the research produced

- **Identity:** `TU3JP / KFV`, 1.4 8v petrol, 75 cv, 1,360 cc, manual `MA5`, 185/65 R14.
- **Critical items:** timing belt with tensioner, idler and water pump; brake fluid; front and
  rear brakes; tires by DOT age; cooling system; steering play; the annual inspection; the recall
  check by VIN.
- **The expensive-to-defer item:** the timing belt. An interference engine with a broken belt bends
  valves, so the cheap job deferred becomes an engine rebuild.
- **The cheap-to-verify items:** fluid condition, pad thickness, DOT week on the tires, play in the
  links. Each one turns an `UNKNOWN` into a decision for very little money.
- **The market layer:** the inspection rule is provincial and the month follows the last plate
  digit, so the item is time-only (`interval_km: 0`) with the rule in `spec`.

## Try it

```bash
# from the repository root
python3 scripts/car.py --root examples/peugeot-207 doctor
python3 scripts/car.py --root examples/peugeot-207 status
python3 scripts/car.py --root examples/peugeot-207 report
```

`doctor` reports three missing fields. That is the intended output of an honest record: the
example refuses to invent a VIN, a region or a conversion status.

Then copy the directory and make it yours:

```bash
cp -r examples/peugeot-207 ~/cars/my-207
# edit ~/cars/my-207/data/vehicle.json with your real values
python3 scripts/car.py --root ~/cars/my-207 doctor
```

## Reusing it for another car

Do not edit this directory. Run the research workflow for the new car instead: it writes a fresh
`vehicle.json` and a fresh `schedule.json`. The structure of this example is the output contract;
the contents do not transfer between models, and they certainly do not transfer between engine
codes.
