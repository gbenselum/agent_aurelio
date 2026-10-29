# Symptom triage protocol

Use this when the owner reports something the car does or fails to do. It is car-independent.
The car-specific part is `failure-playbook.md` in the car record.

## Step 1 - Collect five facts before naming a cause

Never name a cause first and ask questions to confirm it. That is how a cheap job becomes an
expensive one.

1. **When**: cold or hot, at what speed, which gear, turning, braking, over bumps, at start-up.
2. **What exactly**: clunk, hum, squeal, rattle, misfire, vibration, leak, smell, smoke, warning
   light, change in pedal or steering feel.
3. **Warning lights**: which one, steady or flashing, and did it appear after a specific event.
4. **Odometer and recent work**: what was done, at which odometer, by whom.
5. **Recent context**: rain, deep puddle, fuel fill, part replacement, a conversion, a long trip,
   a kerb strike.

If the owner cannot answer 1 to 3, ask for a short recording or a photo. A 10-second video of a
noise is worth more than three descriptions.

## Step 2 - Classify urgency before diagnosis

| Urgency | Signals | Action |
| --- | --- | --- |
| **STOP** | Brake pedal to the floor, smoke, fuel smell, overheating, a wheel with play, steering that pulls hard, a flashing engine light | Do not drive. Tow or park it |
| **THIS WEEK** | Grinding brakes, a new vibration above 80 km/h, a coolant leak, a slipping clutch, a belt noise at start | Book it, limit use |
| **THIS MONTH** | A steady warning light, a slow leak, a noise that only appears cold | Inspect at the next opportunity |
| **MONITOR** | Cosmetic, a rattle with no effect on control, a slow change in behaviour | Record it, watch for a trigger |

A flashing check-engine light is a STOP: it means a misfire that is dumping unburnt fuel into the
catalyst. A steady one is THIS MONTH.

## Step 3 - Answer in a fixed shape

```text
Symptom:        one line, in the owner's own words
Most likely:    one cause, not a list
Why:            the two facts that support it
Decisive test:  the cheapest test that separates it from the second cause
Also possible:  the second cause, and what would make it more likely
Urgency:        STOP / THIS WEEK / THIS MONTH / MONITOR
Cost band:      local currency, with the basis date
Do not replace: the tempting parts the evidence does not support
```

Three rules for this shape:

- **One likely cause.** A list of five possibilities is not a diagnosis, it is a menu.
- **A decisive test.** If a test cannot separate the first cause from the second, the diagnosis is
  not finished.
- **Name the trap.** Most wasted money is spent on the part that "usually" fails, not on the part
  the evidence points at.

## Step 4 - Separate noise from failure

| Symptom class | Usually | Confirm by |
| --- | --- | --- |
| Noise over bumps | Worn links, bushes, top mounts, sway bar | Rock the car by hand, then a lever test on each joint |
| Hum that rises with speed | Wheel bearing, tire wear, driveline | Swap the wheel side to side; sound follows the bearing, not the road |
| Vibration at one speed band | Wheel balance, tire flat spot, CV joint under load | Rebalance first, then load the joint in a tight turn |
| Squeal on braking | Pads at the wear indicator, glazed pads, a sticking caliper | Measure lining thickness; check for uneven wheel temperature |
| Clunk on take-up | Engine mount, dog bone, CV joint, subframe | Load the engine in first gear with the brake on, watch for movement |
| Smell of fuel | Leaking line or injector seal, a rich mixture | Visual check with the engine cold, then a pressure test. No smoking |
| Sweet smell, fogging glass | Coolant leak in the heater core or a hose | Pressure test, look for residue at the bulkhead |

## Step 5 - Record it

Log the diagnosis as an event of type `note`, even when no work was done:

```bash
python3 scripts/car.py --root <car-dir> log \
  --date 2026-11-02 --km 121500 --type note \
  --notes "Clunk front left over bumps. Links have play, strut top mount dry. Links booked."
```

A diagnosis that is not recorded is repeated at the next visit. The record is the product.

## Red flags that override the whole protocol

- Brake fluid on a wheel or a wet booster: STOP.
- Fuel smell with the engine running: STOP, cut the ignition, no sparks.
- Temperature gauge climbing with a cold radiator: STOP, do not open the cap.
- A tire with a bulge or exposed cords: STOP, do not drive on it.
- Steering with play or a clunk that changes with direction: STOP.

Safety items are not deferred because the owner is busy or the budget is short. Say so once,
plainly, then give the cheapest safe option: park it, use one tire, use a mobile mechanic.
