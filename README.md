<p align="center">
  <img src="assets/aurelio.jpg" alt="Aurelio, a mechanic in worn blue overalls, holding a wrench" width="200">
</p>

# agent_aurelio

An agent skill that researches a car and then keeps an auditable maintenance record for it.
Point it at any car, get a profile, a maintenance schedule, a failure playbook and a cost basis
you can defend. Then log what actually happens and ask it what is due.

Ships a complete **Peugeot 207 Compact (2014, Argentina, 1.4 8v)** record as the worked example.
The protocol is not specific to that car.

```
/agent_aurelio research "Peugeot 207 1.4 8v 2014 Argentina"
/agent_aurelio research "Toyota Corolla 2019 2.0 CVT Brazil"
/agent_aurelio research "VW Golf 7 1.4 TSI 2016 Spain"
```

No API keys. No account. No telemetry. Python 3.9+ standard library only, and the knowledge lives
in plain JSON and Markdown that you own.

## Why it exists

A used car comes with a folder of invoices, a service book with three stamps, and no reliable
answer to "what is about to break and what does it cost". Forums give you symptoms, the manual
gives you intervals for a different market, and the workshop gives you a number with no basis.

This skill separates three things that are usually mixed:

- **What the car is** — one engine code, one gearbox, one tire size, proven or `null`.
- **What is due** — intervals derived from the manufacturer plan, shortened for real conditions,
  with the time half never ignored.
- **What is known** — every fact carries a source tier and a confidence marker, so a proof and a
  rumour never look the same.

## Install

Clone it into your agent's skills directory:

```bash
git clone https://github.com/gbenselum/agent_aurelio.git ~/.agents/skills/agent_aurelio
```

For Claude Code style layouts:

```bash
git clone https://github.com/gbenselum/agent_aurelio.git ~/.claude/skills/agent_aurelio
```

Optional slash command, for harnesses that read command files from `.opencode/command/`:

```bash
mkdir -p .opencode/command
cp ~/.agents/skills/agent_aurelio/commands/agent_aurelio.md .opencode/command/
```

## Use

### Research a car

```bash
/agent_aurelio research "Peugeot 207 1.4 8v 2014 Argentina"
```

The agent asks for the engine code first, because the belt kit, the plugs and the oil all depend on
it. Then it works through the source tiers in
[`references/research-protocol.md`](references/research-protocol.md) and writes a car directory:

```text
peugeot-207-2014/
├── data/vehicle.json
├── data/events.jsonl
├── schedule.json
├── references/playbook.md
├── documents/inbox/
└── reports/
```

Anything it cannot prove becomes an open question with a named way to close it. It does not fill
gaps with plausible numbers.

### Keep the record

```bash
cd peugeot-207-2014
python3 ~/.agents/skills/agent_aurelio/scripts/car.py doctor
python3 ~/.agents/skills/agent_aurelio/scripts/car.py status
python3 ~/.agents/skills/agent_aurelio/scripts/car.py report
```

Log a service, with the odometer it happened at:

```bash
python3 .../car.py log --date 2026-11-02 --km 132500 --type service \
  --item oil_change --item air_filter --cost 145000 --shop "Taller X" --notes "5W-40"
```

File an invoice, then log the work against it:

```bash
python3 .../car.py docs archive documents/inbox/factura.pdf \
  --date 2026-03-14 --km 128400 --kind invoice --slug taller-x
```

Ask it about a noise, a warning light, or whether a quote is reasonable. It answers with one
likely cause, one decisive test, an urgency level and a cost band — not a list of guesses.

## CLI

| Command | Purpose |
| --- | --- |
| `init` | Scaffold a car workspace from the blank template |
| `doctor` | Check profile completeness, field by field |
| `status` | Print `OVERDUE` / `DUE` / `SOON` / `UNKNOWN` / `OK` per item |
| `log` | Append a service, repair, inspection, note or appointment |
| `fuel` | Append a fuel fill and print consumption |
| `history` | List recorded events |
| `docs` | List filed documents, or archive one with a hash |
| `report` | Write `reports/status-YYYY-MM-DD.md` |

Every command takes `--root <car-dir>`. Without it, the script walks up from the current directory
looking for `data/vehicle.json`.

`status` also accepts `--json` for scripting.

## What is in the box

| Path | What it is |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The skill: modes, non-negotiables, workflows |
| [`references/research-protocol.md`](references/research-protocol.md) | How to research any car: phases, source tiers, confidence markers, anti-patterns |
| [`references/schedule-schema.md`](references/schedule-schema.md) | How to build `schedule.json`: fields, risk levels, bucket rules |
| [`references/triage-protocol.md`](references/triage-protocol.md) | Symptom triage, urgency scale, the fixed answer shape |
| [`references/market-argentina.md`](references/market-argentina.md) | Inspection rule, documents, fuel conventions, Spanish parts glossary |
| [`references/voice.md`](references/voice.md) | Optional voice layer: when a quote helps and when it does not |
| [`examples/peugeot-207/`](examples/peugeot-207/) | A complete record, with a 33-item schedule |
| [`scripts/car.py`](scripts/car.py) | The maintenance calculator, standard library only |

## The 207 example

`examples/peugeot-207/` is what a finished research run looks like: engine code `TU3JP / KFV`,
75 cv, manual `MA5`, 185/65 R14, and 33 schedule items from the timing belt and the water pump to
the annual inspection.

- The **schedule and specifications are real research** about that model in that market.
- The **profile and events are fictional** and marked as such. No VIN, no plate, no real history.
  The odometer and the two demo events exist to show the tool working.

Read [`examples/peugeot-207/README.md`](examples/peugeot-207/README.md) for the reasoning behind
the example, including the engine-family trap that makes the 207 a good teaching case.

## Voice (optional)

The skill is named after Aurelio, so it may answer with a short line from the films. It is
governed: one quote per reply at most, never near a safety warning, never in place of a number,
no roleplay, and clean lines by default. Rules and the accepted lines are in
[`references/voice.md`](references/voice.md). Delete `assets/aurelio-quotes.json` and the voice
file to turn it off.

## Design rules

1. **The variant, not the model.** Two engine codes means two records.
2. **`null` beats a guess.** An unknown safety item is a warning, not a gap to fill.
3. **Time beats distance on an old car.** Rubber, seals, belts and fluids expire in the driveway.
4. **One recommendation, with a reason.** A menu of options is not advice.
5. **Every number has a date.** A price without a basis date is a rumour.
6. **`schedule.json` is authoritative.** Prose that disagrees gets corrected.

## Scope and safety

This is a record-keeping and research tool. It is not a workshop manual, it does not replace a
qualified mechanic, and it cannot inspect your car. Cost bands are order-of-magnitude estimates
with a stated basis, not quotes. Safety-critical work — brakes, steering, timing belts, airbags —
belongs to someone who can measure the parts.

## License

MIT. See [LICENSE](LICENSE).
