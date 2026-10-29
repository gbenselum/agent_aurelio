# Research protocol: from a car name to a usable record

This is the heart of the skill. It turns a phrase like `"Peugeot 207 1.4 2014 Argentina"`
into the same artifact set that `examples/peugeot-207/` ships with, without inventing a single
number.

The protocol is car-independent. Market-specific detail lives in `market-<country>.md`
(for Argentina, see `market-argentina.md`).

---

## Phase 0 - Fix the identity of the car before you search

"A 207" is not a car. It is a family of cars with different engines, brakes, gearboxes and
belt systems. Research the variant, not the model.

A record is only valid for one combination of:

| Dimension | Why it changes the answer |
| --- | --- |
| Make + model + generation | Parts, faults and intervals differ between generations |
| Model year | Mid-cycle changes add or remove ABS, a chain, a different gearbox |
| Market | Emissions hardware, fuel, inspection rules, available engines |
| Engine code | Belt vs chain, plug type, oil capacity, known failures |
| Gearbox | Clutch items versus ATF and a different failure profile |

**Ask for these, in this order, before any advice:**

1. Registration document: VIN, engine code, model year, power.
2. VIN decode (17 characters): confirms plant, year and often the engine.
3. Engine plate: the code stamped on the block, not only on paper.
4. Tire sidewall: width, profile, rim, load and speed rating.
5. Gearbox: feel it on a drive, or read the code.

**Hard rule:** if the engine code is unknown, stop. Everything downstream - belt kit, plugs, oil,
intervals, cost - depends on it. A record with a guessed engine code is worse than no record.

**Two engine codes means two records.** Do not average intervals between an 8-valve and a
16-valve. Split the file, or add a `variants` list and mark which one the car has.

---

## Phase 1 - Know which source wins

Every fact enters the record with a source tier and a confidence marker. When two tiers
disagree, the higher tier wins and the disagreement is recorded, not deleted.

| Tier | Source | Use it for | Trust |
| --- | --- | --- | --- |
| S1 | Owner documents: invoices, service book, inspection certificate, registration | What was actually done, at which odometer | Highest |
| S2 | Manufacturer: owner's manual, official service plan, technical bulletins, recall lookup by VIN | Intervals, capacities, fluids, safety campaigns | High |
| S3 | Parts catalogue keyed by VIN or engine code | Exact part numbers, belt tooth count, plug type | High |
| S4 | Independent workshop data and model-specific community threads with photos and follow-ups | Known failure modes, real labour times | Medium |
| S5 | Market data: parts prices, labour rates, insurer valuations | Cost bands | Medium, expires fast |
| S6 | Video, social posts, answer farms | A lead to test, never a fact | Lowest |

Rules:

- One post is not evidence. Read at least three independent threads, and prefer threads where
  the author reports the outcome.
- A part number without a source is a guess. Get it from a catalogue keyed by engine code.
- A price without a date is not a price. Record currency, date and market.
- If only S6 supports a claim, the claim stays out of the schedule and goes into
  `open_questions` as "unverified".

---

## Phase 2 - Extract the fields that drive decisions

Fill this table for the car. Anything you cannot fill stays `null`.

| Field | Where it comes from | What breaks if it is wrong |
| --- | --- | --- |
| `engine_code` | Registration document, engine plate, VIN decode | Belt kit, plugs, oil, every interval |
| `displacement_cc`, `power_cv` | Registration document | Insurance, parts lookup, expectations |
| `gearbox`, `gearbox_code` | Drive test, catalogue | Clutch versus ATF, service items |
| `fuel`, `conversion` | Registration document, visual check | Plug interval, valve care, inspection items |
| `abs` | Visual check of the engine bay and a hard stop on gravel | Brake parts and diagnostic path |
| `tire_size` | Sidewall | Pressure, rotation, cost, speedometer error |
| Oil capacity and grade | Manual, then confirm on the dipstick | Overfill, wrong viscosity, sludge |
| Coolant type and capacity | Manual | Mixed chemistries clog the radiator |
| Gearbox oil spec | Manual or catalogue | Wrong fluid destroys synchronisers or the valve body |
| Brake fluid spec | Manual | DOT4 versus DOT5.1 is not a preference |
| Belt or chain | Engine code, visual, manual | A chain service that does not exist, or a missed belt |
| Inspection regime | Market rules | A car that cannot legally circulate |
| Known failures | Phase 4 | Money spent on the wrong part |

Record the *source* of each important field next to the value, in a `verification` block or in
`open_questions`. The next session must be able to tell a proven value from a plausible one.

---

## Phase 3 - Build the interval table

Intervals are not copied. They are derived.

1. **Start from the manufacturer plan for this engine and market.** Not from a forum, not from
   a different market.
2. **Take the shorter of km and time.** A 12-year-old car fails by age before kilometres.
3. **Apply the severe-use reduction** if any of these are true: short trips, heavy traffic, dust,
   heat, cold starts, poor fuel, towing, mountainous terrain. Most manuals already publish a
   severe schedule - use it rather than inventing a factor.
4. **Mark risk**: `critical` (belt, brakes, brake fluid, tires, cooling, fuel leaks),
   `high`, `medium`, `low`.
5. **Write the `if_unknown` action for every critical item.** If there is no invoice, the answer
   is usually "replace now", because the cost of failure is an engine or a crash.
6. **Attach a cost band, not a price**, with currency, market and basis date.

Trap: a European 150,000 km belt interval is not valid in a hot, dusty market with traffic.
Use the local plan, or the conservative one. Document which you chose and why.

---

## Phase 4 - Build the failure playbook for this car

A generic "check the brakes" list is worthless. You want the faults that this platform, with
this engine, actually develops.

**Where to look:**

1. Search in the local language: `"<model> <engine> fallas comunes"`, `"problemas"`,
   `"ruido"`. Local threads describe local fuel, roads and workshops.
2. Search in the source language of the brand: `"<model> <engine> common problems"`.
3. Check model-specific forums and clubs, sorted by replies, not by date.
4. Check technical bulletins if you can find them, and the recall database by VIN.
5. Check parts-catalogue "frequently replaced" lists; they leak real failure rates.

**How to accept a fault into the playbook:**

- It appears in at least two independent sources.
- At least one source states the engine code or the model year range.
- It has a cheap decisive test (a noise test, a resistance reading, a visual check).
- If it is expensive to fix, note the cost of ignoring it.

**Reject these:**

- Faults from a different engine family. The turbocharged chain engine and the 8-valve belt
  engine share a body, not a failure list.
- Faults from a different market's hardware (different emissions parts, different gearbox).
- "Known issue" posts with no model year range and no follow-up.

Store each entry as: symptom, likely cause, why it fits, decisive test, urgency, cost band,
what not to replace.

---

## Phase 5 - Cost bands

- Always a range: low and high, in one currency, with the market and a basis date.
- Name the basis: dealer price, independent workshop, parts only, parts plus labour.
- Re-baseline when the basis is older than a quarter in a high-inflation market.
- Never present a band as a quote. A band answers "is this worth doing", not "what will I pay".

---

## Phase 6 - Write the artifacts and stop

Produce exactly these files for a researched car:

```text
<car-slug>/
├── data/vehicle.json       profile, baseline odometer, policies, open questions
├── data/events.jsonl       append-only log, starts empty
├── schedule.json           intervals, risk, specs, cost bands
├── documents/inbox/        empty drop zone
├── documents/archive/      empty
└── reports/                empty
```

Plus two notes in the record:

- **`sources.md`**: every source with tier, URL or document name, access date, and what it
  supports.
- **`open_questions.md`** (or the `open_questions` array): everything you could not prove.
  An empty list is allowed only when the profile is genuinely complete.

**Stop condition.** The research is done when either the profile is complete, or every gap is
written down as a question with a named way to answer it. It is never done by filling a gap
with a plausible guess.

---

## Confidence markers

Use the same words every time, so the next session can read the record quickly.

| Marker | Meaning |
| --- | --- |
| `documented` | An owner document proves it |
| `manufacturer` | Manual, official plan or bulletin |
| `catalogue` | Parts data keyed by VIN or engine code |
| `community` | Two or more independent reports agree |
| `single-source` | One report only. A lead, not a fact |
| `inferred` | Reasoned from other facts. Say so in the text |

Downgrade a marker when the supporting source disappears or a contradiction appears. Never
silently upgrade one.

---

## Anti-patterns that invalidate the whole record

1. Researching a model instead of a variant.
2. Copying intervals from another market.
3. Treating a forum post as a measurement.
4. Quoting a price with no date and no currency.
5. Assuming ABS, an automatic gearbox, or a fuel conversion because "most cars have it".
6. Filling a `null` to make the tool print a green row.
7. Deleting the previous owner's history because it looks incomplete.

---

## Output contract

At the end of a research run, answer the user with:

1. **The card**: make, model, year, engine code, gearbox, tire size, and the three fields still
   unknown.
2. **The files written**, by path.
3. **The top three actions**, in this order: the safety item, the item with the worst cost of
   failure, the cheapest item that removes the most uncertainty.
4. **The open questions**, each with the concrete way to close it (which document, which
   measurement, which lookup).
5. **The confidence level of the record** overall, and what would raise it.

Do not present the full schedule table in the chat. Point at the artifacts.
