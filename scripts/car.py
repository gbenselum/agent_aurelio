#!/usr/bin/env python3
"""car.py - maintenance state calculator for one car.

Standard library only. Python 3.9+. No network, no accounts.

Commands:
  doctor    Check profile completeness. Run this first.
  status    Show overdue, due, unknown and upcoming items.
  log       Append a service, repair, inspection or note event.
  fuel      Append a fuel fill and print consumption.
  history   List recorded events.
  docs      List filed documents, or file one.
  report    Write reports/status-YYYY-MM-DD.md.
  init      Scaffold a new car workspace.

State, per car (the directory that holds data/vehicle.json):
  data/vehicle.json         profile, baseline odometer, policies
  data/events.jsonl         append-only event log
  data/documents.json       index of filed documents
  schedule.json             intervals and cost bands for this car
  documents/inbox           drop zone for new invoices and photos
  documents/archive         filed evidence
  reports/                  generated status reports

The schedule is resolved per car: ./schedule.json first, then
./references/schedule.json, then the bundled references/schedule.json.
"""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

# Currency label, taken from the schedule the run resolves to.
CURRENCY = ""

RISK_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
STATUS_ORDER = {"OVERDUE": 0, "DUE": 1, "UNKNOWN": 2, "SOON": 3, "OK": 4}
EVENT_TYPES_SERVICE = ("service", "repair", "inspection")


# ---------------------------------------------------------------- utilities


def project_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).expanduser().resolve()
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "data" / "vehicle.json").exists():
            return candidate
    return cwd


def data_dir(root: Path) -> Path:
    return root / "data"


def schedule_path(root: Path) -> Path:
    """Per-car schedule wins, then data/references, then the bundled example."""
    for candidate in (
        root / "schedule.json",
        root / "references" / "schedule.json",
        SKILL_DIR / "references" / "schedule.json",
    ):
        if candidate.exists():
            return candidate
    return SKILL_DIR / "references" / "schedule.json"


def load_schedule(root: Path) -> dict:
    global CURRENCY
    schedule = read_json(schedule_path(root)) or {}
    CURRENCY = schedule.get("currency") or ""
    return schedule


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def load_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSON in {path} line {number}: {exc}") from exc
    return events


def append_event(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def add_months(day: date, months: int) -> date:
    year = day.year + (day.month - 1 + months) // 12
    month = (day.month - 1 + months) % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last))


def fmt_int(value) -> str:
    return "?" if value is None else f"{value:,}".replace(",", ".")


def fmt_date(value: date | str | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, str):
        return value
    return value.isoformat()


def remaining_text(rem_km, rem_days) -> str:
    if rem_km is not None and rem_km < 0 and rem_days is not None and rem_days < 0:
        return f"OVERDUE {fmt_int(-rem_km)} km / {-rem_days} d"
    if rem_km is not None and rem_km < 0:
        return f"OVERDUE by {fmt_int(-rem_km)} km"
    if rem_days is not None and rem_days < 0:
        return f"OVERDUE by {-rem_days} d"
    parts = []
    if rem_km is not None:
        parts.append(f"{fmt_int(rem_km)} km")
    if rem_days is not None:
        parts.append(f"{rem_days} d")
    return " / ".join(parts) if parts else "-"


def money(band) -> str:
    if not band:
        return "-"
    low, high = band
    if not low and not high:
        return "no cost / variable"
    if low == high:
        return f"{fmt_int(low)} {CURRENCY}".strip()
    return f"{fmt_int(low)}-{fmt_int(high)} {CURRENCY}".strip()


# ---------------------------------------------------------------- model


def current_odometer(vehicle: dict, events: list[dict]):
    values = [(e["km"], e.get("date")) for e in events if isinstance(e.get("km"), int)]
    baseline = vehicle.get("baseline") or {}
    if isinstance(baseline.get("km"), int):
        values.append((baseline["km"], baseline.get("date")))
    if not values:
        return None, None
    km, when = max(values, key=lambda pair: pair[0])
    return km, when


def applies(item: dict, vehicle: dict) -> bool:
    for key, allowed in (item.get("applies") or {}).items():
        value = vehicle.get(key)
        if value is None:
            continue  # unknown profile: keep the item and warn in the header
        if value not in allowed:
            return False
    return True


def latest_event(events: list[dict], item_id: str):
    candidates = [
        event
        for event in events
        if item_id in (event.get("items") or [])
        and event.get("type") in EVENT_TYPES_SERVICE
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda e: (e.get("date", ""), e.get("km") or 0))


def compute_rows(vehicle: dict, events: list[dict], schedule: dict, today: date):
    km, _ = current_odometer(vehicle, events)
    profile = vehicle.get("vehicle") or {}
    rows = []

    for item in schedule.get("items", []):
        if not applies(item, profile):
            continue

        interval_km = item.get("interval_km") or 0
        interval_months = item.get("interval_months") or 0
        last = latest_event(events, item["id"])

        row = {
            "id": item["id"],
            "name": item["name"],
            "risk": item.get("risk", "medium"),
            "spec": item.get("spec", ""),
            "notes": item.get("notes", ""),
            "if_unknown": item.get("if_unknown", ""),
            "cost_band": item.get("cost_band"),
            "last_km": None,
            "last_date": None,
            "due_km": None,
            "due_date": None,
            "remaining_km": None,
            "remaining_days": None,
            "status": "UNKNOWN",
        }

        if last is None:
            rows.append(row)
            continue

        row["last_km"] = last.get("km")
        row["last_date"] = last.get("date")

        if interval_km and row["last_km"] is not None:
            row["due_km"] = row["last_km"] + interval_km
            if km is not None:
                row["remaining_km"] = row["due_km"] - km

        if interval_months:
            try:
                last_day = datetime.strptime(last["date"], "%Y-%m-%d").date()
            except (KeyError, TypeError, ValueError):
                last_day = None
            if last_day:
                row["due_date"] = add_months(last_day, interval_months).isoformat()
                row["remaining_days"] = (add_months(last_day, interval_months) - today).days

        row["status"] = bucket(row["remaining_km"], row["remaining_days"])
        rows.append(row)

    rows.sort(key=priority)
    return rows


def bucket(rem_km, rem_days) -> str:
    if rem_km is None and rem_days is None:
        return "UNKNOWN"
    if (rem_km is not None and rem_km <= 0) or (rem_days is not None and rem_days <= 0):
        return "OVERDUE"
    if (rem_km is not None and rem_km <= 1000) or (rem_days is not None and rem_days <= 30):
        return "DUE"
    if (rem_km is not None and rem_km <= 3000) or (rem_days is not None and rem_days <= 90):
        return "SOON"
    return "OK"


def priority(row: dict):
    status = row["status"]
    risk = RISK_ORDER.get(row["risk"], 9)
    if status == "OVERDUE":
        return (0, risk)
    if status == "UNKNOWN" and row["risk"] == "critical":
        return (1, risk)
    if status == "DUE":
        return (2, risk)
    if status == "UNKNOWN":
        return (3, risk)
    if status == "SOON":
        return (4, risk)
    return (5, risk)


def fuel_rows(events: list[dict]):
    fills = [e for e in events if e.get("type") == "fuel" and e.get("liters")]
    fills.sort(key=lambda e: e.get("km") or 0)
    fulls = [e for e in fills if e.get("full")]
    rows = []
    for before, after in zip(fulls, fulls[1:]):
        distance = (after.get("km") or 0) - (before.get("km") or 0)
        if distance > 0:
            rows.append(
                {
                    "date": after.get("date"),
                    "km": after.get("km"),
                    "distance": distance,
                    "l_per_100km": round(100 * float(after["liters"]) / distance, 2),
                }
            )
    return rows


def report_totals(events: list[dict]):
    total = 0
    by_year: dict[str, int] = {}
    for event in events:
        cost = event.get("cost")
        if isinstance(cost, (int, float)) and cost > 0:
            total += int(cost)
            year = (event.get("date") or "")[:4]
            by_year[year] = by_year.get(year, 0) + int(cost)
    return total, dict(sorted(by_year.items()))


# ---------------------------------------------------------------- documents

SKIP_NAMES = {".gitkeep", ".gitignore", ".DS_Store"}


def docs_dirs(root: Path):
    base = root / "documents"
    return base, base / "inbox", base / "archive"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def docs_index_path(root: Path) -> Path:
    return data_dir(root) / "documents.json"


def load_docs_index(root: Path) -> dict:
    return read_json(docs_index_path(root), {"version": 1, "documents": []})


def save_docs_index(root: Path, index: dict) -> None:
    path = docs_index_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def scan_documents(root: Path) -> list[Path]:
    _, inbox, archive = docs_dirs(root)
    files = []
    for folder in (inbox, archive):
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_file() and path.name not in SKIP_NAMES:
                files.append(path)
    return files


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "documento"


def cmd_docs(args) -> int:
    root = project_root(args.root)
    base, _, _ = docs_dirs(root)
    if not base.exists():
        raise SystemExit(f"Missing {base}. Create documents/inbox and documents/archive.")

    index = load_docs_index(root)
    indexed = {entry["path"]: entry for entry in index.get("documents", [])}
    events = load_events(data_dir(root) / "events.jsonl")

    linked: dict[str, list[str]] = {}
    for event in events:
        document = event.get("document")
        if document:
            linked.setdefault(document, []).append(event.get("id", ""))

    rows = []
    on_disk = set()
    for path in scan_documents(root):
        relative = str(path.relative_to(root))
        on_disk.add(relative)
        entry = indexed.get(relative)
        if entry is None:
            status = "NEW"
        elif entry.get("sha256") != file_hash(path):
            status = "CHANGED"
        else:
            status = "INDEXED"
        rows.append(
            {
                "status": status,
                "path": relative,
                "kind": (entry or {}).get("kind"),
                "doc_date": (entry or {}).get("doc_date"),
                "km": (entry or {}).get("km"),
                "size": path.stat().st_size,
                "events": linked.get(relative, []),
            }
        )

    for relative, entry in indexed.items():
        if relative not in on_disk:
            rows.append(
                {
                    "status": "MISSING",
                    "path": relative,
                    "kind": entry.get("kind"),
                    "doc_date": entry.get("doc_date"),
                    "km": entry.get("km"),
                    "size": 0,
                    "events": linked.get(relative, []),
                }
            )

    order = {"NEW": 0, "CHANGED": 1, "MISSING": 2, "INDEXED": 3}
    rows.sort(key=lambda row: (order[row["status"]], row["path"]))
    pending = [row for row in rows if row["status"] in ("NEW", "CHANGED")]

    if args.json:
        print(
            json.dumps(
                {
                    "pending": len(pending),
                    "missing": len([row for row in rows if row["status"] == "MISSING"]),
                    "documents": rows,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    print(f"DOCUMENTS - {base}")
    print("")
    if not rows:
        print("No documents. Put invoices, service sheets, inspections or photos in documents/inbox.")
        return 0

    print(f"{'STATUS':<9} {'KIND':<11} {'DATE':<11} {'KM':>9}  {'EVENTS':<20} PATH")
    print("-" * 112)
    for row in rows:
        km = fmt_int(row["km"]) if row["km"] is not None else "-"
        print(
            f"{row['status']:<9} {(row['kind'] or '-'):<11} {(row['doc_date'] or '-'):<11} "
            f"{km:>9}  {','.join(row['events'])[:20]:<20} {row['path']}"
        )

    print("")
    new_files = [row for row in rows if row["status"] in ("NEW", "CHANGED")]
    missing = [row for row in rows if row["status"] == "MISSING"]
    if new_files:
        print(f"{len(new_files)} file(s) need processing. Read each one, then file it:")
        print("  car.py docs archive <path> --date YYYY-MM-DD --km N --kind factura")
    if missing:
        print(f"{len(missing)} indexed file(s) are missing on disk. Restore the file or file it again.")
    if not new_files and not missing:
        print("All documents are filed.")
    return 0


def cmd_docs_archive(args) -> int:
    root = project_root(args.root)
    _, _, archive = docs_dirs(root)
    path = Path(args.path)
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    try:
        old_relative = str(path.relative_to(root))
    except ValueError:
        old_relative = str(path)

    digest = file_hash(path)
    index = load_docs_index(root)
    for entry in index.get("documents", []):
        if entry.get("sha256") == digest and entry.get("path") != old_relative:
            print(f"WARNING: identical file already filed as {entry['path']}", file=sys.stderr)

    doc_date = args.date or date.today().isoformat()
    try:
        datetime.strptime(doc_date, "%Y-%m-%d")
    except ValueError:
        raise SystemExit("--date must be YYYY-MM-DD")

    kind = slugify(args.kind or "otro")
    slug = slugify(args.slug or path.stem)
    prefix = f"{doc_date}_{args.km}" if args.km is not None else doc_date
    stem = f"{prefix}_{kind}_{slug}"

    target_dir = archive / doc_date[:4]
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{stem}{path.suffix.lower()}"
    counter = 2
    while target.exists():
        target = target_dir / f"{stem}-{counter}{path.suffix.lower()}"
        counter += 1

    shutil.move(str(path), str(target))
    relative = str(target.relative_to(root))

    index["documents"] = [
        entry for entry in index.get("documents", []) if entry.get("path") != old_relative
    ]
    index["documents"].append(
        {
            "path": relative,
            "sha256": digest,
            "size": target.stat().st_size,
            "kind": kind,
            "doc_date": doc_date,
            "km": args.km,
            "filed": date.today().isoformat(),
            "notes": args.notes or "",
        }
    )
    index["documents"].sort(key=lambda entry: entry["path"])
    save_docs_index(root, index)

    print(f"Filed -> {relative}")
    print(f"Link it to the work: car.py log ... --doc {relative}")
    return 0


# ---------------------------------------------------------------- rendering


def header_line(vehicle: dict, km, when) -> str:
    v = vehicle.get("vehicle", {})
    name = " ".join(
        part for part in [v.get("make"), v.get("model"), str(v.get("model_year") or "")] if part
    )
    engine = v.get("engine") or v.get("engine_code") or "engine UNKNOWN"
    gearbox = v.get("gearbox") or "gearbox UNKNOWN"
    odo = f"{fmt_int(km)} km ({when or 'date unknown'})" if km is not None else "odometer UNKNOWN"
    return f"{name} | {engine} | {gearbox} | {odo}"


def missing_profile(vehicle: dict) -> list[str]:
    v = vehicle.get("vehicle", {})
    missing = []
    for field in ("engine_code", "gearbox", "tire_size", "vin"):
        if not v.get(field):
            missing.append(field)
    if not (vehicle.get("baseline") or {}).get("km"):
        missing.append("baseline.km")
    if (vehicle.get("usage") or {}).get("region") is None:
        missing.append("usage.region")
    if v.get("conversion") is None:
        missing.append("conversion")
    return missing


def upcoming_appointments(events: list[dict], today: date) -> list[dict]:
    return sorted(
        [
            event
            for event in events
            if event.get("type") == "appointment"
            and (event.get("date") or "") >= today.isoformat()
        ],
        key=lambda event: event.get("date") or "",
    )


def print_status(vehicle: dict, events: list[dict], schedule: dict) -> None:
    today = date.today()
    km, when = current_odometer(vehicle, events)
    rows = compute_rows(vehicle, events, schedule, today)

    print(header_line(vehicle, km, when))
    print("")

    missing = missing_profile(vehicle)
    if missing:
        print(f"PROFILE INCOMPLETE: {', '.join(missing)}")
        print("  Unknown fields make intervals and diagnoses unreliable. Run: car.py doctor")
        print("")

    width = 46
    print(f"{'STATUS':<10} {'ITEM':<{width}} {'LAST':<18} {'NEXT':<18} REMAINING")
    print("-" * (10 + width + 18 + 18 + 22))
    for row in rows:
        last = (
            f"{fmt_int(row['last_km'])} / {row['last_date']}"
            if row["last_km"] is not None
            else "-"
        )
        nxt = (
            f"{fmt_int(row['due_km'])} / {row['due_date']}"
            if row["due_km"] is not None and row["due_date"]
            else (fmt_int(row["due_km"]) if row["due_km"] is not None else row["due_date"] or "-")
        )
        print(
            f"{row['status']:<10} {row['name'][:width]:<{width}} {last:<18} {nxt:<18} "
            f"{remaining_text(row['remaining_km'], row['remaining_days'])}"
        )

    appts = upcoming_appointments(events, today)
    if appts:
        print("")
        print("APPOINTMENTS")
        for event in appts:
            print(f"  {event.get('date','')}  {event.get('notes') or 'appointment'}")

    unknown = [r for r in rows if r["status"] == "UNKNOWN" and r["risk"] in ("critical", "high")]
    critical = [r for r in unknown if r["risk"] == "critical"]
    if critical:
        print("")
        print("NO HISTORY - CRITICAL ITEMS")
        for row in critical:
            print(f"  - {row['name']}: {row['if_unknown']}")
        rest = len(unknown) - len(critical)
        if rest:
            print(f"  Plus {rest} high-risk item(s) with no history. See the table above.")

    fuels = fuel_rows(events)
    if fuels:
        print("")
        last = fuels[-1]
        average = sum(f["l_per_100km"] for f in fuels) / len(fuels)
        print(
            f"FUEL: last {last['l_per_100km']} L/100km over {fmt_int(last['distance'])} km "
            f"| average {average:.2f} L/100km over {len(fuels)} "
            f"{'tank' if len(fuels) == 1 else 'tanks'}"
        )


def cmd_status(args) -> int:
    root = project_root(args.root)
    vehicle = read_json(data_dir(root) / "vehicle.json")
    if vehicle is None:
        raise SystemExit("data/vehicle.json not found. Run: car.py init")
    schedule = load_schedule(root)
    events = load_events(data_dir(root) / "events.jsonl")

    if args.json:
        today = date.today()
        km, when = current_odometer(vehicle, events)
        payload = {
            "odometer": km,
            "odometer_date": when,
            "profile_missing": missing_profile(vehicle),
            "items": compute_rows(vehicle, events, schedule, today),
            "fuel": fuel_rows(events),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print_status(vehicle, events, schedule)
    total, by_year = report_totals(events)
    if total:
        print("")
        print(f"RECORDED SPEND: {fmt_int(total)} {CURRENCY} total | " + ", ".join(
            f"{year}: {fmt_int(value)}" for year, value in by_year.items()
        ))
    return 0


def cmd_doctor(args) -> int:
    root = project_root(args.root)
    vehicle = read_json(data_dir(root) / "vehicle.json")
    if vehicle is None:
        raise SystemExit("data/vehicle.json not found. Run: car.py init")

    v = vehicle.get("vehicle", {})
    checks = [
        ("engine_code", v.get("engine_code"),
         "Belt kit, plugs, filters and oil capacity all depend on it."),
        ("gearbox", v.get("gearbox"),
         "Selects manual gearbox oil versus AL4 ATF, and the clutch items."),
        ("tire_size", v.get("tire_size"),
         "Pressure, rotation and replacement cost."),
        ("vin", v.get("vin"),
         "Recall and campaign checks are done by VIN."),
        ("baseline.km", (vehicle.get("baseline") or {}).get("km"),
         "Every km-based due date needs a starting point."),
        ("usage.region", vehicle.get("usage", {}).get("region"),
         "Sets the local inspection rule and the climate and road severity."),
        ("conversion", v.get("conversion"),
         "An LPG or CNG conversion changes intervals, valve care and inspection items."),
    ]

    print(f"PROFILE CHECK - {root}")
    print("")
    pending = 0
    for name, value, why in checks:
        if value is None or value == "":
            pending += 1
            print(f"  [MISSING] {name}: {why}")
        else:
            print(f"  [ok]      {name} = {value}")

    print("")
    if pending:
        print(f"{pending} field(s) missing. Complete them in data/vehicle.json.")
        print("Sources: registration document (VIN, engine code, year), tire sidewall, engine plate.")
        return 1
    print("Profile complete. Run: car.py status")
    return 0


def parse_km_arg(raw):
    """--km accepts an integer or the words unknown/none/?. Returns int or None."""
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    text = str(raw).strip().lower()
    if text in ("unknown", "none", "?", "null"):
        return None
    try:
        return int(text)
    except ValueError:
        raise SystemExit(f"--km must be an integer or 'unknown', got '{raw}'")


def cmd_log(args) -> int:
    root = project_root(args.root)
    vehicle = read_json(data_dir(root) / "vehicle.json") or {}
    events_path = data_dir(root) / "events.jsonl"
    events = load_events(events_path)
    schedule = load_schedule(root)
    known = {item["id"] for item in schedule.get("items", [])}

    current_km, current_when = current_odometer(vehicle, events)
    when = args.date or date.today().isoformat()
    try:
        datetime.strptime(when, "%Y-%m-%d")
    except ValueError:
        raise SystemExit("--date must be YYYY-MM-DD")

    if args.type == "appointment":
        km = parse_km_arg(args.km) if args.km is not None else None
    elif args.km is None:
        # A backdated event must not inherit the newest odometer reading.
        if current_km is None:
            raise SystemExit("No odometer known. Pass --km N or --km unknown.")
        if current_when and when < current_when:
            raise SystemExit(
                f"{when} is earlier than the last odometer reading ({current_when}, "
                f"{fmt_int(current_km)} km). Pass --km N, or --km unknown if the "
                "odometer for that date is not recorded."
            )
        km = current_km
    else:
        km = parse_km_arg(args.km)

    if events and km is not None and current_km is not None and km < current_km:
        print(f"WARNING: km {km} is lower than the last known {current_km}. Check for a typo.",
              file=sys.stderr)

    items = args.item or []
    for item in items:
        if item not in known:
            print(f"WARNING: '{item}' is not in references/schedule.json", file=sys.stderr)

    sequence = sum(1 for event in events if event.get("date") == when) + 1
    event = {
        "id": f"{when}-{sequence:03d}",
        "date": when,
        "km": km,
        "type": args.type,
        "items": items,
        "cost": args.cost,
        "shop": args.shop,
        "document": args.doc,
        "notes": args.notes,
    }
    append_event(events_path, event)
    where = "km unknown" if km is None else f"{fmt_int(km)} km"
    print(f"Logged {event['id']}: {args.type} at {where}"
          + (f" | {', '.join(items)}" if items else ""))
    return 0


def cmd_fuel(args) -> int:
    root = project_root(args.root)
    vehicle = read_json(data_dir(root) / "vehicle.json") or {}
    events_path = data_dir(root) / "events.jsonl"
    events = load_events(events_path)

    when = args.date or date.today().isoformat()
    sequence = sum(1 for event in events if event.get("date") == when) + 1
    event = {
        "id": f"{when}-{sequence:03d}",
        "date": when,
        "km": args.km,
        "type": "fuel",
        "items": [],
        "liters": args.liters,
        "full": not args.partial,
        "cost": args.cost,
        "shop": args.shop,
        "notes": args.notes,
    }
    append_event(events_path, event)
    print(f"Fuel logged: {args.liters} L at {fmt_int(args.km)} km"
          + ("" if event["full"] else " (partial fill, excluded from consumption)"))

    events.append(event)
    rows = fuel_rows(events)
    if rows:
        last = rows[-1]
        print(f"Last tank: {last['l_per_100km']} L/100km over {fmt_int(last['distance'])} km")
    return 0


def cmd_history(args) -> int:
    root = project_root(args.root)
    events = load_events(data_dir(root) / "events.jsonl")
    if not events:
        print("No events recorded.")
        return 0
    events.sort(key=lambda e: (e.get("date", ""), e.get("km") or 0), reverse=True)
    limit = args.limit or len(events)
    print(f"{'DATE':<12} {'KM':>9}  {'TYPE':<11} {'ITEMS':<34} {'COST':>10}  SHOP")
    print("-" * 100)
    for event in events[:limit]:
        items = ",".join(event.get("items") or [])
        cost = event.get("cost")
        print(
            f"{event.get('date',''):<12} {fmt_int(event.get('km')):>9}  "
            f"{event.get('type',''):<11} {items[:34]:<34} "
            f"{(fmt_int(cost) if cost else '-'):>10}  {event.get('shop') or ''}"
        )
    return 0


def cmd_report(args) -> int:
    root = project_root(args.root)
    vehicle = read_json(data_dir(root) / "vehicle.json") or {}
    schedule = load_schedule(root)
    events = load_events(data_dir(root) / "events.jsonl")
    today = date.today()
    km, when = current_odometer(vehicle, events)
    rows = compute_rows(vehicle, events, schedule, today)

    lines = [
        f"# Mechanical status - {today.isoformat()}",
        "",
        header_line(vehicle, km, when),
        "",
        "## Due and overdue",
        "",
        "| Status | Item | Last | Next | Remaining | Risk |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        last = f"{fmt_int(row['last_km'])} / {row['last_date']}" if row["last_km"] is not None else "-"
        nxt = f"{fmt_int(row['due_km'])} / {row['due_date']}" if row["due_km"] is not None else "-"
        lines.append(
            f"| {row['status']} | {row['name']} | {last} | {nxt} | "
            f"{remaining_text(row['remaining_km'], row['remaining_days'])} | {row['risk']} |"
        )

    unknown = [r for r in rows if r["status"] == "UNKNOWN" and r["risk"] in ("critical", "high")]
    if unknown:
        lines += ["", "## No history - decide now", ""]
        for row in unknown:
            lines.append(f"- **{row['name']}**: {row['if_unknown']} ({row['spec']})")

    appts = upcoming_appointments(events, today)
    if appts:
        lines += ["", "## Appointments", ""]
        for event in appts:
            lines.append(f"- {event.get('date','')}: {event.get('notes') or 'appointment'}")

    total, by_year = report_totals(events)
    if total:
        lines += ["", "## Recorded spend", "", f"Total: {fmt_int(total)} {CURRENCY}".strip(), ""]
        for year, value in by_year.items():
            lines.append(f"- {year}: {fmt_int(value)} {CURRENCY}".strip())

    fuels = fuel_rows(events)
    if fuels:
        average = sum(f["l_per_100km"] for f in fuels) / len(fuels)
        lines += ["", "## Fuel", "", f"Average: {average:.2f} L/100km over {len(fuels)} "
                  f"{'tank' if len(fuels) == 1 else 'tanks'}", ""]

    lines += ["", "## Next actions", ""]
    actions = [
        row
        for row in rows
        if row["status"] in ("OVERDUE", "DUE", "UNKNOWN")
    ][:3]
    if not actions:
        lines.append("No urgent action recorded. Keep logging events.")
    for number, row in enumerate(actions, 1):
        lines.append(f"{number}. {row['name']} - {row['status']} - {money(row['cost_band'])}")

    target = root / "reports" / f"status-{today.isoformat()}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {target}")
    return 0


def cmd_init(args) -> int:
    root = project_root(args.root)
    data = data_dir(root)
    data.mkdir(parents=True, exist_ok=True)
    vehicle_path = data / "vehicle.json"
    events_path = data / "events.jsonl"
    template = SKILL_DIR / "assets" / "vehicle.template.json"

    if not vehicle_path.exists():
        if not template.exists():
            raise SystemExit(f"Template missing: {template}")
        shutil.copyfile(template, vehicle_path)
        print(f"Created {vehicle_path} from template")
    if not events_path.exists():
        events_path.touch()

    for folder in (root / "documents" / "inbox", root / "documents" / "archive", root / "reports"):
        folder.mkdir(parents=True, exist_ok=True)

    docs_index = data / "documents.json"
    if not docs_index.exists():
        docs_index.write_text("{}\n", encoding="utf-8")

    schedule_target = root / "schedule.json"
    schedule_template = SKILL_DIR / "references" / "schedule.template.json"
    if not schedule_target.exists() and schedule_template.exists():
        shutil.copyfile(schedule_template, schedule_target)
        print(f"Created {schedule_target} from template - replace its example items")

    print(f"Data directory ready: {data}")
    print("Next: car.py doctor")
    return 0


# ---------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintenance state calculator for one car")
    parser.add_argument("--root", help="project root (default: search upward for data/vehicle.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show due and overdue items")
    status.add_argument("--json", action="store_true", help="machine-readable output")
    status.set_defaults(func=cmd_status)

    doctor = sub.add_parser("doctor", help="check profile completeness")
    doctor.set_defaults(func=cmd_doctor)

    log = sub.add_parser("log", help="append an event")
    log.add_argument("--date", help="YYYY-MM-DD (default: today)")
    log.add_argument("--km", type=str,
                     help="odometer reading for the event, or 'unknown' if it is not recorded")
    log.add_argument("--type", default="service",
                     choices=["service", "repair", "inspection", "note", "tire", "appointment"])
    log.add_argument("--item", action="append", help="schedule item id (repeatable)")
    log.add_argument("--cost", type=int, help="cost in the currency of your schedule")
    log.add_argument("--shop", help="shop or dealer")
    log.add_argument("--doc", help="filed document path, e.g. documents/archive/2026/...")
    log.add_argument("--notes", help="free text")
    log.set_defaults(func=cmd_log)

    fuel = sub.add_parser("fuel", help="append a fuel fill")
    fuel.add_argument("--km", type=int, required=True)
    fuel.add_argument("--liters", type=float, required=True)
    fuel.add_argument("--cost", type=int)
    fuel.add_argument("--date", help="YYYY-MM-DD (default: today)")
    fuel.add_argument("--partial", action="store_true", help="partial fill: skip consumption")
    fuel.add_argument("--shop")
    fuel.add_argument("--notes")
    fuel.set_defaults(func=cmd_fuel)

    history = sub.add_parser("history", help="list events")
    history.add_argument("--limit", type=int)
    history.set_defaults(func=cmd_history)

    docs = sub.add_parser("docs", help="list documents, or file one")
    docs.add_argument("--json", action="store_true", help="machine-readable output")
    docs.set_defaults(func=cmd_docs)
    docs_sub = docs.add_subparsers(dest="docs_action")
    docs_archive = docs_sub.add_parser("archive", help="file and index a document")
    docs_archive.add_argument("path", help="file in documents/inbox or an absolute path")
    docs_archive.add_argument("--date", help="document date, YYYY-MM-DD (default: today)")
    docs_archive.add_argument("--km", type=int, help="odometer on the document")
    docs_archive.add_argument("--kind", default="otro",
                              help="invoice, service, inspection, quote, photo, insurance, conversion, other")
    docs_archive.add_argument("--slug", help="short name for the file")
    docs_archive.add_argument("--notes", help="free text")
    docs_archive.set_defaults(func=cmd_docs_archive)

    report = sub.add_parser("report", help="write a markdown status report")
    report.set_defaults(func=cmd_report)

    init = sub.add_parser("init", help="prepare the data directory")
    init.set_defaults(func=cmd_init)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
