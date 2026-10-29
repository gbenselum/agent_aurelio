# Failure playbook: Peugeot 207 Compact (PF1), 1.4 8v TU3, Argentina

A condensed playbook for the worked example. It shows the shape the research protocol asks for:
symptom, likely cause, decisive test, urgency, cost band, and what not to replace.

**Scope.** This is for the **1.4 8v `TU3JP`** on the PF1 platform (206 / 207 Compact), manual
`MA5`, no turbo. It does **not** apply to the `EP6` turbo, the European 1.6 VTi chain engine, or
the 207 CC. Those share a body, not a failure list.

**Confidence markers:** `[C]` two or more independent reports, `[S]` single source, `[V]` verify
on the car before acting. Cost bands are ARS, order of magnitude, basis 2026.

## 0. Stop driving

- Brake pedal soft or sinking.
- Fuel smell with the engine running.
- Temperature climbing with a cold radiator.
- A tire with a bulge or exposed cords.
- Steering with play, or a clunk that changes with direction.
- Grinding under braking.

## 1. Front end and steering - the documented weak point `[C]`

The front end is a consumable on this platform, not a terminal disease. Parts are cheap and
available. Diagnose corner by corner.

| Symptom | Likely cause | Decisive test | Urgency | Cost band |
| --- | --- | --- | --- | --- |
| Clunk over speed bumps at low speed | Stabilizer links (bieletas) | Shake each link by hand. Torn boot or play means replace | This week | 80,000-160,000 per pair |
| Clunk plus vague steering plus inner tire wear | Lower arm bush or ball joint | Pry bar between arm and subframe, look for cracked rubber | This week | 200,000-450,000 per side |
| Creak when turning the wheel while parked | Strut top mount bearing (cazoleta) | Listen with the hood open while an assistant turns the wheel | This month | 150,000-300,000 per pair |
| Hum that changes when swerving left or right | Wheel bearing | 3-9 o'clock shake with the wheel off the ground, then a road test | This week | 100,000-220,000 per side |
| Vibration at 100-120 km/h | Balance, deformed tire, tie rod end, bearing | Rotate and balance first, then check play | This week | 29,000-45,000 alignment |
| Steering play, wander | Tie rod ends, then the rack | Assistant rocks the wheel while you watch the joint | This week | 100,000-250,000 |
| Nose dive, more than two rebounds | Dampers | Push each corner, count the rebounds, look for oil | This month | 200,000-400,000 per pair |
| Hum from the rear, worse with load | Rear trailing-arm bearings | Lift, spin, listen. Known 206/207 failure | This week | 180,000-350,000 |
| Scalloped front tires | Dampers plus alignment | Read the tread depth pattern | This month | - |

Rules:

1. Do not accept "change the whole front end" without a per-part reason and a written list.
2. Use known brands for rubber and joints. Generic links last 10,000-20,000 km and you pay the
   labour twice.
3. Always align after arms, tie rods, struts or rack work. Alignment is not optional.
4. A clunk that survives new links is usually the arm bush or the top mount, not a second set of
   links.
5. Front struts are **side-specific**. A shop that says "they are the same" is wrong.
6. The rear is a torsion-beam axle, not coil springs. Rear shocks are eye-to-eye and are not
   interchangeable with coil-spring parts.

## 2. Timing belt - the one job never to defer `[C]`

The TU engines use a **belt, not a chain**. A broken belt bends valves; the repair cost multiplies
by five to ten.

- Argentine aftermarket guidance for the 207 Compact: **80,000 km or 5 years**.
- European manuals list 150,000 km or 10 years. That assumes a mild climate, clean fuel and steady
  highway use. It does not apply here.
- With no invoice, the belt is due **by age**, whatever the odometer says.
- Replace as a kit: belt, tensioner, idler, water pump, coolant. Skipping the water pump means
  paying the same labour again.
- A chirp at cold start is the **accessory** belt. It is not evidence that the timing belt is fine.

## 3. Ignition and oil leaks `[C]`

| Symptom | Likely cause | Decisive test | Urgency |
| --- | --- | --- | --- |
| Misfire, rough idle, poor cold start | Plugs, coil pack, plug wells full of oil | Pull the coils, look for oil in the wells | This week |
| Oil smell after a run, oil on the exhaust | Valve cover gasket, plug well seals | Clean, run 20 minutes, watch for fresh tracks | This month |
| Oil at the head-to-block joint, alternator side | Head gasket external seep `[S]` | Clean with brake cleaner, watch for tracks, check for emulsion under the cap | Monitor for a seep; this week for coolant loss |

Do not rebuild a top end on a rumour. An external seep is far more common than oil-to-coolant
mixing. Prove it before spending.

## 4. Cooling `[C]`

- Plastic thermostat housings and ageing hoses fail by age.
- Never mix coolant chemistries, and never top up with plain water except as an emergency.
- Overheating with a cold radiator points at a thermostat or a blocked radiator, not a sensor.
- Replace the water pump with the belt, every time.

## 5. Brakes

| Symptom | Cause | Action |
| --- | --- | --- |
| Pedal soft or sinking | Air, hose, master cylinder | Stop. Inspect and bleed |
| Pulls to one side | Slide pins, collapsed hose, stuck piston | This week |
| Grinding | Pads worn to metal | This week |
| Rear drag or lockup | Wheel cylinder leak, seized adjuster | This week |
| Handbrake needs many clicks | Rear adjustment or a stretched cable | This month |
| Pedal fades on a long descent | Old fluid with absorbed water | Replace fluid every 2 years |

Front: ventilated discs. Rear: drums on most units. `[V]` Confirm rear discs if the unit is a late
or special version.

**Check for ABS before ordering parts.** This market sold cars without it into the 2010s. A brake
warning lamp on a car without ABS means fluid, handbrake or pressure - not a wheel speed sensor.

## 6. Transmission

**Manual `MA5`** `[C]`: input shaft bearing and second-gear synchro wear are the known items. A
whine in neutral that disappears when the clutch is pressed points at the bearing. A crunch into
second when cold points at the synchro. Check the oil level before anything else.

**Automatic `AL4`** `[C]`: harsh shifts, a slipping torque converter and a solenoid valve body are
the common failures. Never use Dexron III; use the specified fluid only. A healthy automatic
changes the economics of a repair; a slipping one does not justify engine work.

## 7. Electrical `[S]`

- The BSI (body computer) is sensitive to a weak battery. Odd faults across unrelated systems often
  start with a battery test, not a scan tool.
- Aftermarket alarm or audio wiring is a common parasitic drain. Ask before you test.
- The COM2000 column unit carries the stalks and the airbag connectors. A failing unit shows as
  wipers, indicators or horn misbehaving together.

## 8. Tires and geometry `[C]`

- Read the DOT week and year on all four. Rubber older than 6 years is a safety item whatever the
  tread depth says.
- Scalloped or feathered front tread means dampers plus alignment, not a tire defect.
- After any front-end work: alignment. After a hard kerb strike: check the arm and the strut.

## 9. Do not do this

- Do not replace five parts because one code appeared.
- Do not fit generic suspension links or bushes.
- Do not lower or stiffen the car. The front end is already the weak point.
- Do not extend oil changes because the oil "looks clean".
- Do not mix coolant chemistries.
- Do not put Dexron III in an AL4.
- Do not recharge the A/C without a leak test.
- Do not apply `EP6` turbo or 1.6 VTi chain faults to this engine.

## 10. Diagnostic order: cheap to expensive

1. Battery and charging test.
2. Fluid levels and condition: oil, coolant, brake fluid, gearbox oil.
3. Visual: leaks, boots, pads, tire dates, exhaust.
4. Play tests: links, tie rods, bearings, mounts.
5. Scan tool, codes read before parts.
6. Only then, the expensive hypothesis.

Most wasted money is spent at step 6 first.

## Sources

Owner documents, the manufacturer plan for the TU engine, parts catalogues keyed by engine code,
and two or more independent model-specific reports per accepted fault. Bands are 2026, Argentina,
independent workshop. Re-baseline before quoting.

Full method: [`../../../references/research-protocol.md`](../../../references/research-protocol.md).
