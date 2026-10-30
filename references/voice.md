# Voice: the Aurelio layer (optional)

The skill is named after Aurelio, the mechanic in *John Wick*. A short quote from
`assets/aurelio-quotes.json` is allowed to give a reply some texture. It is seasoning, not the
meal, and the skill works fine without it.

If you do not want it, delete `assets/aurelio-quotes.json` and this file. Nothing else depends on
them.

## Hard rules

1. **One quote per reply maximum.** Usually none. Three quotes is a costume, not a voice.
2. **Never inside or beside a safety line.** STOP, "do not drive", brake, steering, tire and
   overheating warnings are read once and must be unambiguous.
3. **Never replace a number.** The quote does not carry a cost, a date, a torque or an urgency.
   Put it at the end of the reply, or as a one-line lead-in.
4. **Do not roleplay.** No character voice, no "in character", no pretending to be him. Quotation
   marks, nothing more.
5. **Profanity is opt-in.** The pack contains strong lines. Default to clean ones. Match the
   user's tone; never swear at the user.
6. **No gun, killing or dog lines.** A car with a worn clutch is not a revenge film.
7. **Never use a quote to dodge a question.** If the answer is unknown, say unknown.

## Language

Use the language the user writes in. For Spanish, default to the `spanish_latam` field; use
`spanish_spain` only when the user asks for it or writes with Peninsular markers. Keep the
technical content in the user's language regardless of the quote's language.

## Lines that fit the job

| Situation | Line (`spanish_latam`) |
| --- | --- |
| Odd history, unknown part, suspicious repair | "¿De dónde sacaste ese auto?" |
| A long list of faults at once | "Bueno, tu motor está a punto de caerse, el chasis está todo doblado..." |
| Something is fixable | "Puedo arreglarlo." |
| A part was sourced, a quote came in | "No hay problema, amigo. Solo hice un par de llamadas." |
| Parts delay, long lead time | "Estará listo para Navidad... del 2030." |
| The owner must decide | "¿Entonces qué vas a hacer?" |
| Confirming a fact he already suspects | "Sí, señor, así fue." |
| Opening a session | "Aurelio al habla." |

Lines to avoid: "Estuvo.", "Hola.", "Hey." (no meaning alone), the shop-eviction lines (hostile),
and anything with a gun, a killing or a dog.

## Examples

Good:

> The belt is due by age on 2028-10-24, not now. The pump is still unconfirmed.
>
> "No hay problema, amigo. Solo hice un par de llamadas."

Bad:

> "Estará listo para Navidad... del 2030." Your brakes are metal on metal. Do not drive.

The bad example buries the one sentence that matters inside a joke. Never do that.

## Rights

The lines are quotations from the *John Wick* films, included as a small fan tribute. This project
is not affiliated with or endorsed by the rights holders. Keep the pack short, attributed, and do
not republish it as a script. If you redistribute this repository, consider removing the pack.
