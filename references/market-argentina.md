# Market profile: Argentina

Market-specific facts that do not belong in the portable core. Copy this file when you research a
car in another country, and replace the rules with the local ones.

## Documents and identifiers

| Document | What it gives you | Use it for |
| --- | --- | --- |
| Cédula verde / cédula azul | VIN, engine code, model year, power, plate, owner | The profile source of truth |
| Título del automotor | Ownership, liens | Only when buying or selling |
| Póliza de seguro | Coverage, and often the VIN and the engine code | Confirms the VIN without opening the bonnet |
| Comprobante de VTV | Last inspection date and result | Fills the inspection item with evidence |
| Factura / presupuesto | What was done, at which odometer, at what price | Highest-value evidence for the log |

The VIN is on the cédula and stamped on the car. Decode it before you trust the model year: the
tenth character is the model year, and Argentine registration years can lag the build year.

## VTV (technical inspection)

The rule is provincial, not national. For Buenos Aires province:

- Annual for cars older than 2 years.
- The month is fixed by the **last digit of the plate** and does not move if you verify early or
  late.
- Bring the cédula, the insurance and the plate. Fix lamps, wipers, horn and the exhaust before
  the appointment.
- The fee is re-set periodically. Read the current value at the provincial site instead of
  reusing an old number.

For CABA the rule differs. Ask for the province before you write the item.

## Fuel, conversions and hardware

- Petrol is `nafta`. Diesel is `diesel` or `gasoil`. Do not translate the fuel field loosely.
- **GNC** (compressed natural gas) is common and changes the record: plug interval, valve seat
  wear, the spare-wheel well, the annual cylinder inspection, and the insurance premium.
- Cars sold without ABS exist in this market well into the 2010s. Check, do not assume.
- Aftermarket alarm and audio wiring is a common source of parasitic drain. Ask before you
  diagnose a battery.

## Severe-use factors that are always true here

Apply the severe schedule, not the European one, unless the owner proves otherwise:

- Dust and unpaved roads: air filter, cabin filter, and every rubber bush.
- Traffic and short trips: oil, battery, brake pads, clutch.
- Heat and sun: tires by age, coolant, plastics, battery life.
- Speed humps and potholes: strut mounts, links, lower arm bushes, wheel bearings.
- Fuel quality variability: plugs, injector cleaning, knock sensor codes on modern engines.

## Cost basis

- Parts prices move weekly. A band older than a quarter is history, not a price.
- Name the basis: official dealer, independent workshop, or parts only. The spread is often 3x.
- Labour in a dealership and labour in a neighbourhood workshop are different products.
- Financing changes the real price: a 12-instalment plan carries a surcharge. Record the total,
  not the instalment.

## Spanish part vocabulary

Keep the local term and put the English in brackets, so the owner can talk to a workshop and the
next session can search the catalogue.

| Local term | English |
| --- | --- |
| Bieletas | Stabilizer links |
| Extremos de dirección | Tie rod ends |
| Bujes de barra | Sway bar bushes |
| Amortiguadores | Shock absorbers / struts |
| Fuelles | Rubber boots (CV, steering rack) |
| Triceta | Tripod CV joint (inner) |
| Homocinética | Constant-velocity joint (outer) |
| Cintas y cilindros de freno | Brake shoes and wheel cylinders |
| Pastillas / discos | Pads / discs |
| Correa de distribución | Timing belt |
| Tensor / polea | Tensioner / idler |
| Bomba de agua | Water pump |
| Radiador / electroventilador | Radiator / cooling fan |
| Empaquetadura de tapa de válvulas | Valve cover gasket |
| Rulemán | Bearing |
| Retén | Oil seal |
| Batería | Battery |
| Burro de arranque | Starter motor |
| Alternador | Alternator |

## Recalls

Recalls are handled by the official importer or dealer, free of charge, and are checked by VIN.
Check the national vehicle safety registry and the importer's site. Never charge the owner for a
recall, and never let a safety recall wait for the next service.

## Inspection habits that pay off here

- Photograph the odometer at every service. It is the cheapest evidence you will ever collect.
- Keep the invoice PDF. A handwritten note is not a document.
- Note the shop name and the town. Two shops with the same surname are common.
- Ask for the replaced parts back on any suspension or brake job. It settles later arguments.
