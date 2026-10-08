"""Reporte de balance del Brawl 3v3 a partir de los CSV de BrawlBalanceDev.

Uso:
  py -3 Tools/Balance/brawl_report.py Recordings/brawl_balance/<tanda>
  py -3 Tools/Balance/brawl_report.py Recordings/brawl_balance/<nueva> --vs Recordings/brawl_balance/<base>

Lee matches.csv y fighters.csv (separador ';'), imprime el resumen y lo guarda en report.md
dentro de la carpeta de la tanda. Con --vs agrega la columna de la tanda base para comparar.
"""
import csv
import math
import os
import statistics as st
import sys
from collections import defaultdict

WING_BAND = (40.0, 60.0)
FAMILY_BAND = (40.0, 60.0)
SKILL_BAND = (35.0, 65.0)
ROLE_BAND = (40.0, 60.0)
DURATION_BAND = (45.0, 70.0)
SUDDEN_BAND = (5.0, 15.0)
COMEBACK_MIN = 15.0
MIN_N = 12


def load(folder):
    def read(name):
        path = os.path.join(folder, name)
        with open(path, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f, delimiter=";"))
    return read("matches.csv"), read("fighters.csv")


def num(row, key, default=0.0):
    value = row.get(key, "")
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def pct(values):
    return 100.0 * sum(values) / len(values) if values else float("nan")


def ci95(p, n):
    if n == 0:
        return float("nan")
    q = p / 100.0
    return 196.0 * math.sqrt(max(q * (1 - q), 1e-9) / n)


def quantile(values, q):
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def healer(row):
    return row["wing"] == "W1" or row["hornRole"] == "Support" or row["backRole"] == "Support"


def match_summary(matches):
    n = len(matches)
    durations = [num(m, "duration") for m in matches if m["timeout"] != "1"]
    sudden = [1 if m["sudden"] == "1" else 0 for m in matches]
    comeback = [1 if m["comeback"] == "1" else 0 for m in matches]
    stand = [m for m in matches if m["lastStandTeam"] not in ("", "None")]
    stand_won = [1 if m["lastStandWon"] == "1" else 0 for m in stand]
    decided = [m for m in matches if m["winner"] in ("Player", "Rival")]
    blue = [1 if m["winner"] == "Player" else 0 for m in decided]
    real = [num(m, "real") for m in matches]
    in_band = [1 if DURATION_BAND[0] <= d <= DURATION_BAND[1] else 0 for d in durations]

    pairs = defaultdict(list)
    for m in matches:
        if m["winner"] not in ("Player", "Rival"):
            continue
        first_side_won = (m["winner"] == "Player") == (m["mirror"] == "0")
        pairs[m["seed"]].append(1 if first_side_won else 0)
    full = [v for v in pairs.values() if len(v) == 2]
    sweeps = [1 if sum(v) in (0, 2) else 0 for v in full]

    return {
        "partidas": n,
        "empates": sum(1 for m in matches if m["winner"] not in ("Player", "Rival")),
        "timeouts": sum(1 for m in matches if m["timeout"] == "1"),
        "duracion media": st.mean(durations) if durations else float("nan"),
        "duracion p10": quantile(durations, 0.1),
        "duracion mediana": quantile(durations, 0.5),
        "duracion p90": quantile(durations, 0.9),
        "% en 45-70 s": pct(in_band),
        "% muerte subita": pct(sudden),
        "% remontadas": pct(comeback),
        "% con ultimo en pie": pct([1] * len(stand) + [0] * (n - len(stand))),
        "% ultimo en pie que gana": pct(stand_won),
        "% gana azul": pct(blue),
        "% espejos 2-0": pct(sweeps),
        "real s/partida": st.mean(real) if real else float("nan"),
    }


def group(fighters, keyfn, usesfn=None):
    groups = defaultdict(list)
    for row in fighters:
        keys = keyfn(row)
        if isinstance(keys, str):
            keys = [keys]
        for key in set(keys):
            if key:
                groups[key].append(row)
    result = {}
    for key, rows in groups.items():
        won = [num(r, "won") for r in rows]
        p = pct(won)
        uses = [usesfn(r, key) for r in rows] if usesfn else []
        result[key] = {
            "n": len(rows),
            "win": p,
            "ci": ci95(p, len(rows)),
            "dmg": st.mean(num(r, "dmg") for r in rows),
            "heal": st.mean(num(r, "heal") for r in rows),
            "kos": st.mean(num(r, "kos") for r in rows),
            "alive": pct([num(r, "alive") for r in rows]),
            "uses": st.mean(uses) if uses else float("nan"),
        }
    return result


def label(row, slot):
    part = row.get(slot + "Part") or ""
    title = row.get(slot + "Title") or ""
    if part and title and part != title:
        return f"{part} · {title}"
    return part or title


def skill_keys(row):
    return [label(row, "horn"), label(row, "back")]


def skill_uses(row, key):
    total = 0.0
    if label(row, "horn") == key:
        total += num(row, "hornUses")
    if label(row, "back") == key:
        total += num(row, "backUses")
    return total


def posture_bold(row):
    return row["posture"].split(" · ")[0] if row["posture"] else ""


def posture_social(row):
    parts = row["posture"].split(" · ")
    return parts[1] if len(parts) > 1 else ""


AXES = [
    ("Alas", lambda r: label(r, "wing"), lambda r, k: num(r, "attacks"), WING_BAND),
    ("Familias", lambda r: [r["hornFamily"], r["backFamily"]], None, FAMILY_BAND),
    ("Roles", lambda r: [r["hornRole"], r["backRole"]], None, ROLE_BAND),
    ("Habilidades", skill_keys, skill_uses, SKILL_BAND),
    ("Osadia", posture_bold, None, ROLE_BAND),
    ("Sociabilidad", posture_social, None, ROLE_BAND),
    ("Cuerpo", lambda r: r["body"], None, ROLE_BAND),
]


def team_rows(fighters):
    teams = defaultdict(list)
    for row in fighters:
        teams[(row["seed"], row["mirror"], row["team"])].append(row)
    return teams


def healer_table(fighters, matches):
    by_match = {(m["seed"], m["mirror"]): m for m in matches}
    win_by_count = defaultdict(list)
    dur_by_total = defaultdict(list)
    totals = defaultdict(int)
    for (seed, mirror, team), rows in team_rows(fighters).items():
        count = sum(1 for r in rows if healer(r))
        win_by_count[count].append(num(rows[0], "won"))
        totals[(seed, mirror)] += count
    for key, total in totals.items():
        m = by_match.get(key)
        if m and m["timeout"] != "1":
            dur_by_total[total].append(num(m, "duration"))
    return win_by_count, dur_by_total


def flag(value, band, n):
    if n < MIN_N or math.isnan(value):
        return " "
    return "!" if value < band[0] or value > band[1] else " "


def fmt(value, digits=1):
    return "-" if value is None or (isinstance(value, float) and math.isnan(value)) else f"{value:.{digits}f}"


def render(folder, base_folder=None):
    matches, fighters = load(folder)
    base = load(base_folder) if base_folder else None
    out = []
    out.append(f"# Reporte Brawl · {os.path.basename(os.path.normpath(folder))}")
    if base_folder:
        out.append(f"(comparado con {os.path.basename(os.path.normpath(base_folder))})")
    out.append("")

    summary = match_summary(matches)
    base_summary = match_summary(base[0]) if base else None
    out.append("## Partidas")
    out.append("")
    out.append("| Metrica | Valor |" + (" Base |" if base else ""))
    out.append("|---|---|" + ("---|" if base else ""))
    for key, value in summary.items():
        line = f"| {key} | {fmt(value)} |"
        if base:
            line += f" {fmt(base_summary[key])} |"
        out.append(line)
    out.append("")
    out.append(f"Metas: duracion {DURATION_BAND[0]:.0f}-{DURATION_BAND[1]:.0f} s · muerte subita {SUDDEN_BAND[0]:.0f}-{SUDDEN_BAND[1]:.0f} % · remontadas >= {COMEBACK_MIN:.0f} %")
    checks = [
        ("duracion media", DURATION_BAND[0] <= summary["duracion media"] <= DURATION_BAND[1]),
        ("muerte subita", SUDDEN_BAND[0] <= summary["% muerte subita"] <= SUDDEN_BAND[1]),
        ("remontadas", summary["% remontadas"] >= COMEBACK_MIN),
    ]
    out.append("Estado: " + " · ".join(f"{name} {'OK' if ok else 'FUERA'}" for name, ok in checks))
    out.append("")

    for title, keyfn, usesfn, band in AXES:
        rows = group(fighters, keyfn, usesfn)
        base_rows = group(base[1], keyfn, usesfn) if base else {}
        out.append(f"## {title} (meta {band[0]:.0f}-{band[1]:.0f} %)")
        out.append("")
        head = "| | Parte | n | Gana % | ±IC95 | Daño | Curación | KOs | Vivo % | Usos |"
        sep = "|---|---|---|---|---|---|---|---|---|---|"
        if base:
            head += " Base % |"
            sep += "---|"
        out.append(head)
        out.append(sep)
        for key, r in sorted(rows.items(), key=lambda kv: -kv[1]["win"]):
            line = (f"| {flag(r['win'], band, r['n'])} | {key} | {r['n']} | {fmt(r['win'])} | {fmt(r['ci'])} | "
                    f"{fmt(r['dmg'], 0)} | {fmt(r['heal'], 0)} | {fmt(r['kos'], 2)} | {fmt(r['alive'])} | {fmt(r['uses'], 1)} |")
            if base:
                b = base_rows.get(key)
                line += f" {fmt(b['win']) if b else '-'} |"
            out.append(line)
        out.append("")

    win_by_count, dur_by_total = healer_table(fighters, matches)
    out.append("## Sanadores por equipo (ala Colibrí o habilidad de apoyo)")
    out.append("")
    out.append("| Sanadores en el equipo | n | Gana % |")
    out.append("|---|---|---|")
    for count in sorted(win_by_count):
        values = win_by_count[count]
        out.append(f"| {count} | {len(values)} | {fmt(pct(values))} |")
    out.append("")
    out.append("| Sanadores en la partida | n | Duración media |")
    out.append("|---|---|---|")
    for total in sorted(dur_by_total):
        values = dur_by_total[total]
        out.append(f"| {total} | {len(values)} | {fmt(st.mean(values))} |")
    out.append("")
    out.append("`!` = fuera de la meta con n >= %d. Gana %% cuenta empates como medio punto." % MIN_N)
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    folder = argv[1]
    base_folder = None
    if "--vs" in argv:
        base_folder = argv[argv.index("--vs") + 1]
    text = render(folder, base_folder)
    with open(os.path.join(folder, "report.md"), "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
