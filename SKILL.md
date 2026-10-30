---
name: agent_aurelio
description: Research any car and keep an auditable maintenance record for it. Use when the user asks to research a car, build a maintenance schedule for a vehicle, understand what a car needs or costs, triage a noise, warning light, vibration, leak or smell, decide whether a repair is worth it, prepare a technical inspection, check recalls, or record an odometer reading, service, repair or fuel fill. Ships a complete Peugeot 207 Compact (2014, Argentina, TU-family) example; the protocol works for any make, model, year and market.
---

# agent_aurelio - research a car, then keep its record

Two jobs, in this order:

1. **Research** a car and produce a schedule, a failure playbook and a profile you can defend.
2. **Maintain** that record: log work, triage symptoms, answer "what is due, what is urgent, what
   should it cost, what should I not touch yet".

The Peugeot 207 in `examples/peugeot-207/` is a finished record you can read as a reference for
what "done" looks like. It is not the only supported car. Nothing in the protocol is specific to
it.

## Non-negotiables

1. **Variant before advice.** Make, model, year, market, **engine code** and gearbox. A wrong
   engine code means a wrong belt kit, wrong plugs and a wrong diagnosis.
2. **Never invent** a km, date, cost, part number or history. Write `null`, and list it as an open
   question with the way to close it.
3. **Unknown is not OK.** If there is no invoice, the item is unknown and must be resolved. On a
   `critical` item, unknown is worse than overdue.
4. **Safety outranks comfort.** Brakes, steering, tires, fuel leaks and overheating stop the car.
5. **Evidence, not memory.** A mechanical claim needs a source, an access date and a confidence
   marker. See `references/research-protocol.md`.
6. **The conservative interval wins.** Time-based intervals dominate on an old car.
7. **Prices are bands, not quotes.** Attach the currency, the market and the basis date.
8. **Record the event**, not only the advice. An unlogged repair is a lost repair.
9. **Documents are evidence.** Never edit or rename a scan by hand. File it, hash it, then log the
   work against it.
10. **A document is not a diagnosis.** An invoice says what was done, not what the car needs now.

## Modes

Read the mode the user asked for. If the request is ambiguous, ask which one.

| Request | Mode | Go to |
| --- | --- | --- |
| "research a 2019 Corolla", "build me a schedule for X" | RESEARCH | Workflow R |
| "first contact", "set up my car" | PROFILE | Workflow A |
| "what is due", "what should I fix" | STATUS | Workflow B |
| a noise, light, leak, smell, vibration | SYMPTOM | Workflow D |
| "I have the invoice", "here is the service book" | DOCUMENT | Workflow I |
| belt, clutch, suspension, full job | BIG JOB | Workflow E |
| "how much should I save", "is it worth repairing" | BUDGET | Workflow F |
| inspection, pre-trip, long drive | INSPECTION | Workflow G |
| "any recalls" | RECALLS | Workflow H |
| a new confirmed fault, a new price source | MAINTAIN | Workflow M |

## Repository map

```
SKILL.md                       this file
scripts/car.py                 status, doctor, docs, log, fuel, history, report, init
references/
  research-protocol.md         HOW to research any car: phases, source tiers, confidence
  schedule-schema.md           HOW to build schedule.json: fields, rules, risk
  schedule.template.json       blank schedule with three illustrative items
  triage-protocol.md           symptom triage, urgency scale, answer shape
  market-argentina.md          VTV, documents, GNC, cost basis, Spanish parts glossary
examples/peugeot-207/          a complete record: profile, 33-item schedule, demo events
commands/agent_aurelio.md      optional slash command for harnesses that support commands
assets/vehicle.template.json   blank profile
```

Per-car state, created by research or by `car.py init`:

```
<car-dir>/
  data/vehicle.json      profile, baseline odometer, policies, open questions
  data/events.jsonl      append-only log
  data/documents.json    document index: hash, kind, date, km
  schedule.json          this car's intervals and cost bands
  documents/inbox/       drop zone
  documents/archive/     filed evidence, named YYYY-MM-DD_km_kind_slug
  reports/               generated status reports
```

If `schedule.json` and any prose disagree, `schedule.json` wins and the prose is corrected.

---

## Workflow R - research a car

Trigger: `/agent_aurelio research "Peugeot 207 1.4 8v 2014 Argentina"`, or any "research this car
for me" request.

Read `references/research-protocol.md` and follow the phases in order. Summary:

**R0. Fix the identity.** Ask for make, model, model year, market, engine code and gearbox. If the
engine code is unknown, do not continue to intervals: ask for the registration document, the VIN
decode or a photo of the engine plate. State plainly that everything downstream depends on it.

**R1. Walk the source tiers.** Owner documents (S1) beat manufacturer (S2) beats parts catalogue
(S3) beats community (S4) beats market data (S5) beats video (S6). Record the tier for every
accepted fact.

**R2. Extract the decision fields.** Fill `assets/vehicle.template.json` into
`<car-dir>/data/vehicle.json`. Leave unknown fields `null` and add them to `open_questions`. Never
fill a field to make the tool print a green row.

**R3. Build the schedule.** Write `<car-dir>/schedule.json` following
`references/schedule-schema.md`. Start from the manufacturer plan for this engine and market,
apply the severe-use reduction, mark `risk`, and give every `critical` item an `if_unknown`
action. Add cost bands with a currency, a market and a basis date.

**R4. Build the failure playbook.** Five to ten documented weak points for **this engine code**,
each with symptom, likely cause, decisive test, urgency, cost band and what not to replace. Reject
faults imported from a different engine family. Store it as `<car-dir>/references/playbook.md`.

**R5. Check the market file.** If the car is in Argentina, read
`references/market-argentina.md` for the inspection rule, documents, fuel conventions and part
vocabulary. For another country, write the equivalent file first.

**R6. Close or declare.** Every gap is either answered or written as an open question with a
concrete way to close it: which document, which measurement, which lookup.

**R7. Report.** Answer with the card (identity plus what is still unknown), the files written, the
top three actions, the open questions, and the confidence of the record.

Do not present the whole schedule in the chat. Write it to disk and point at it.

### The 207 worked example

`examples/peugeot-207/` is the reference output: a 2014 Peugeot 207 Compact Allure, Argentina,
TU3JP 1.4 8v, manual MA5, 185/65 R14, with a 33-item schedule covering the timing belt, cooling,
suspension, brakes, tires, fluids and the annual inspection.

Its profile and events are **fictional and marked as such**. Its schedule and specifications are
real research about that model. Read `examples/peugeot-207/README.md` for what the research
produced and which parts were illustrative.

---

## Workflow A - first contact with a car

```bash
python3 scripts/car.py --root <car-dir> doctor
```

Ask for the missing fields in this order:

1. Engine code and power, from the registration document.
2. Gearbox: manual or automatic, and the code if known.
3. Tire size, from the sidewall.
4. Current odometer and its date.
5. VIN, for recalls, and the region, for the inspection rule.
6. Any invoice for the timing belt, clutch, suspension or brakes.

Write the answers into `data/vehicle.json`. Then run `status` and explain the result in three
groups: safety, overdue by time, unknown.

## Workflow B - status

```bash
python3 scripts/car.py --root <car-dir> status
```

Buckets: `OVERDUE` (act), `DUE` (book), `SOON` (plan and budget), `UNKNOWN` (resolve with a
document or an inspection), `OK` (no action).

Then give exactly three actions, in this order:

1. The safety item.
2. The item with the worst cost of failure (belt, cooling, brakes).
3. The cheapest item that removes the most uncertainty.

Do not list ten items. The owner will do none of them.

## Workflow C - record an event

```bash
python3 scripts/car.py --root <car-dir> log \
  --date 2026-11-02 --km 132500 --type service \
  --item oil_change --item air_filter --cost 145000 --shop "Workshop name" --notes "5W-40"
```

Rules:

- `--km` is required. Ask for it. Never let a past event inherit the newest reading.
- Date known but odometer unknown: pass `--km unknown`. The row then ages by date only.
- Month precision is acceptable when the day is not recorded: use the first of the month and say
  so in `--notes`.
- `--item` accepts ids from `schedule.json` and is repeatable. One event can cover several items.
- If there is a paper trail, file the document first (Workflow I) and pass `--doc`. Then the
  evidence and the event point at each other.
- `--type repair` for a fault fix, `inspection` for a check, `note` for a diagnosis without work,
  `appointment` for a booking that has not happened. An appointment carries no odometer and resets
  nothing; when the work is done, log the real event.
- Fuel: `car.py fuel --km ... --liters ... --cost ...`, with `--partial` for a partial fill.

## Workflow D - symptom triage

Read `references/triage-protocol.md`. Ask the five facts before naming a cause: when, what
exactly, which warning light, odometer and recent work, recent context.

Answer in the fixed shape:

```
Symptom:        one line, in the owner's words
Most likely:    one cause, not a list
Why:            the two facts that support it
Decisive test:  the cheapest test that separates it from the second cause
Also possible:  the second cause, and what would favour it
Urgency:        STOP / THIS WEEK / THIS MONTH / MONITOR
Cost band:      local currency, with the basis date
Do not replace: the tempting parts the evidence does not support
```

Log the diagnosis as a `note` event so the next session has context.

## Workflow E - plan a big job

For a belt, clutch, suspension overhaul or cooling job:

1. List what must be replaced together. Belt + tensioner + idler + water pump + coolant. Clutch +
   release bearing + rear main seal if leaking. Arms + links + alignment.
2. List what to inspect while the labour is already paid: mounts, hoses, seals, bearings.
3. Ask for three written quotes with parts, brands and labour separated.
4. Flag the trap in each quote: generic suspension parts, no water pump with the belt, no
   alignment after arms, no gearbox oil with a clutch.
5. Give a go/no-go rule, not a menu.

## Workflow F - budget

Give a monthly reserve in local currency, not a yearly total. Separate routine, big-ticket reserve
and fuel. If the price basis is more than a quarter old, re-baseline before quoting.

## Workflow G - inspection and pre-trip

Lights, horn, wipers, washer, tire tread and pressure, brake balance, handbrake travel, mirrors,
belts, exhaust leaks, warning lights, plate lamps, documents. For a periodic inspection, add the
market rule from `references/market-argentina.md` (or the local equivalent). Fix lamps and wipers
before the appointment.

## Workflow H - recalls

Check by VIN at an official dealer or the national registry. Recalls are free. A safety recall
does not wait for the next service.

## Workflow I - process a document

Trigger: `docs` reports `NEW`, `CHANGED` or `MISSING`, or the owner says "I have the invoice".

1. **Read the file.** Renders PDFs and images. For a service book photo, read every visible stamp,
   not only the last one.
2. **Extract:** date, km, shop, jobs, cost, part brands and numbers, next-due note.
3. **Ask for unreadable data.** Never approximate a km. A guessed km corrupts every later
   calculation.
4. **File it:**

```bash
python3 scripts/car.py --root <car-dir> docs archive documents/inbox/factura.pdf \
  --date 2026-03-14 --km 128400 --kind invoice --slug workshop-name
```

Kinds: `invoice`, `service`, `inspection`, `quote`, `photo`, `insurance`, `conversion`, `other`.

5. **Log the work**, with the archived path in `--doc`.
6. **Update the profile** if the document settles a field: VIN, engine code, power, gearbox, tire
   size, conversion. Recalculate `usage.km_per_year` when two odometer readings give a rate.
7. **Run `status` and `report`.** Documents change history, and the report must show it.
8. **Contradiction:** if a document contradicts the log, do not rewrite the log. Add a `note`
   event that states the contradiction and tell the owner.

Rules: a quote is not work. One invoice can produce several events, all with the same `--doc`. A
photo of an odometer or a leak is evidence: file it as `photo` and reference it in a `note`.
Duplicate protection warns when the same hash is already filed. A document with no date uses the
file date, and the notes say so.

## Workflow M - maintain the knowledge

- New confirmed fault: add it to the playbook, then add the source.
- New price data: update `schedule.json` and the basis date.
- Contradiction between sources: keep both, state which one this record follows and why.
- Never delete history from `events.jsonl`. Correct it with a new event that says so.
- Never let a source tier go unrecorded. An unattributed fact is a rumour.

## Voice (optional)

A short Aurelio quote is allowed as seasoning. One per reply at most, never inside or beside a
STOP or safety warning, never in place of a number, no roleplay, clean lines by default. See
`references/voice.md`. This never changes what you recommend.

## Output style

- Metric units, km, ISO dates. Local currency, named.
- Keep local part names with a short explanation: "bieletas (stabilizer links)".
- One recommendation, with a reason. Not a menu.
- State uncertainty explicitly. "I need the engine code before I can price the belt."
- Never promise a repair outcome. State what the inspection shows and what it does not.
