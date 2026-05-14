"""
ClariComp — demo query runner
Runs a set of illustrative queries against claricomp.db and prints the results.

Usage:
    python3 query_db.py            # run all demo queries
    python3 query_db.py --shell    # drop into an interactive SQL shell
"""

import sqlite3, sys, os, math, textwrap

DB_PATH = os.path.join(os.path.dirname(__file__), "claricomp.db")


# ── Pretty-print helpers ──────────────────────────────────────────────────────

BOLD  = "\033[1m"
DIM   = "\033[2m"
GREEN = "\033[32m"
NAVY  = "\033[34m"
TEAL  = "\033[36m"
RESET = "\033[0m"

def hr(char="─", width=72):
    print(DIM + char * width + RESET)

def section(title: str) -> None:
    print()
    hr("═")
    print(f"{BOLD}{NAVY}  {title}{RESET}")
    hr("═")

def subsection(title: str) -> None:
    print(f"\n{TEAL}  {title}{RESET}")
    hr()

def table(headers: list, rows: list, col_widths: list | None = None) -> None:
    if not rows:
        print(DIM + "    (no rows)" + RESET)
        return
    widths = col_widths or [
        max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    print(BOLD + fmt.format(*headers) + RESET)
    print(DIM + "  " + "  ".join("─" * w for w in widths) + RESET)
    for row in rows:
        cells = [str(c) if c is not None else "–" for c in row]
        print(fmt.format(*cells))


# ── Queries ───────────────────────────────────────────────────────────────────

def q_cities(cur):
    section("CITIES")

    subsection("Count by region")
    rows = cur.execute("""
        SELECT region, COUNT(*) AS cities,
               ROUND(AVG(latitude),1) AS avg_lat,
               ROUND(AVG(longitude),1) AS avg_lng
        FROM cities
        GROUP BY region
        ORDER BY cities DESC
    """).fetchall()
    table(["Region", "Cities", "Avg lat", "Avg lng"], rows)

    subsection("UK cities (north to south)")
    rows = cur.execute("""
        SELECT name, ROUND(latitude,4) AS lat, ROUND(longitude,4) AS lng
        FROM cities WHERE region='UK'
        ORDER BY latitude DESC
    """).fetchall()
    table(["City", "Latitude", "Longitude"], rows)

    subsection("Cities furthest from London (Haversine, top 10)")
    # Haversine in SQLite using custom function registered below
    rows = cur.execute("""
        SELECT name, region,
               ROUND(haversine(51.5074, -0.1278, latitude, longitude)) AS dist_km
        FROM cities
        WHERE name != 'London'
        ORDER BY dist_km DESC
        LIMIT 10
    """).fetchall()
    table(["City", "Region", "Distance from London (km)"], rows, [22, 14, 26])


def q_emission_factors(cur):
    section("EMISSION FACTORS  (DEFRA 2025 Table 5)")

    subsection("All factors ordered by kgCO₂e (low → high)")
    rows = cur.execute("""
        SELECT mode_label,
               COALESCE(class_label, '–') AS class,
               unit,
               PRINTF('%.6f', factor_kgco2e) AS factor
        FROM emission_factors
        ORDER BY factor_kgco2e
    """).fetchall()
    table(["Mode", "Class/fuel", "Unit", "Factor kgCO₂e"], rows, [28, 18, 5, 14])

    subsection("Flight factors: economy vs business uplift")
    rows = cur.execute("""
        SELECT mode_label,
               class_label,
               PRINTF('%.6f', factor_kgco2e) AS factor,
               PRINTF('%.1f%%', (factor_kgco2e /
                   MIN(factor_kgco2e) OVER (PARTITION BY mode_label) - 1) * 100
               ) AS premium_over_economy
        FROM emission_factors
        WHERE mode_key LIKE 'Flight%'
        ORDER BY mode_label, factor_kgco2e
    """).fetchall()
    table(["Mode", "Class", "Factor kgCO₂e", "Premium vs cheapest"], rows, [20, 18, 14, 20])

    subsection("Vehicle vs passenger-km modes")
    rows = cur.execute("""
        SELECT unit, COUNT(*) AS count,
               PRINTF('%.6f', MIN(factor_kgco2e)) AS min_factor,
               PRINTF('%.6f', MAX(factor_kgco2e)) AS max_factor
        FROM emission_factors
        GROUP BY unit
    """).fetchall()
    table(["Unit", "Count", "Min factor", "Max factor"], rows)


def q_pricing(cur):
    section("PRICING TIERS")

    subsection("Tier overview")
    rows = cur.execute("""
        SELECT name,
               '£' || price_gbp_monthly || '/mo' AS price,
               size_description,
               CASE is_featured WHEN 1 THEN '★ RECOMMENDED' ELSE '' END AS badge
        FROM pricing_tiers
        ORDER BY price_gbp_monthly
    """).fetchall()
    table(["Tier", "Price", "Size", ""], rows, [18, 10, 34, 14])

    subsection("Features per tier (with sort order)")
    rows = cur.execute("""
        SELECT pt.name AS tier, tf.sort_order, tf.feature_text
        FROM tier_features tf
        JOIN pricing_tiers pt ON pt.id = tf.tier_id
        ORDER BY pt.price_gbp_monthly, tf.sort_order
    """).fetchall()
    table(["Tier", "#", "Feature"], rows, [18, 3, 46])

    subsection("Feature matrix (comparison table)")
    rows = cur.execute("""
        SELECT feature_name,
               CASE self_serve     WHEN 1 THEN '✓' ELSE '–' END,
               CASE compliance_pro WHEN 1 THEN '✓' ELSE '–' END,
               CASE enterprise     WHEN 1 THEN '✓' ELSE '–' END
        FROM feature_matrix
        ORDER BY sort_order
    """).fetchall()
    table(["Feature", "Self-Serve", "Compliance Pro", "Enterprise"], rows, [36, 10, 14, 10])

    subsection("Annual cost comparison")
    rows = cur.execute("""
        SELECT name,
               '£' || price_gbp_monthly || '/mo' AS monthly,
               '£' || (price_gbp_monthly * 12) || '/yr' AS annual
        FROM pricing_tiers
        ORDER BY price_gbp_monthly
    """).fetchall()
    table(["Tier", "Monthly", "Annual"], rows, [18, 10, 10])


def q_faq(cur):
    section("FAQ")

    subsection("Questions by category")
    rows = cur.execute("""
        SELECT category, COUNT(*) AS questions
        FROM faq_items GROUP BY category ORDER BY MIN(rowid)
    """).fetchall()
    table(["Category", "Questions"], rows)

    subsection("All questions (truncated answers)")
    rows = cur.execute("""
        SELECT category, sort_order,
               question,
               SUBSTR(answer, 1, 80) || '…' AS answer_preview
        FROM faq_items
        ORDER BY category, sort_order
    """).fetchall()
    for cat, order, q, a in rows:
        print(f"\n  {DIM}{cat} · Q{order}{RESET}")
        print(f"  {BOLD}{q}{RESET}")
        print("  " + textwrap.fill(a, width=70, subsequent_indent="  "))


def q_ppn(cur):
    section("PPN 06/21 REQUIREMENTS")

    rows = cur.execute("""
        SELECT ref_code, title, description, claricomp_output
        FROM ppn_requirements ORDER BY ref_code
    """).fetchall()

    for ref, title, desc, output in rows:
        print(f"\n  {BOLD}{TEAL}{ref}{RESET}  {BOLD}{title}{RESET}")
        print("  " + textwrap.fill(f"Requirement: {desc}", 68, subsequent_indent="  "))
        print("  " + textwrap.fill(f"ClariComp:   {output}", 68, subsequent_indent="  "))
    hr()


def q_pages(cur):
    section("SITE PAGES")

    rows = cur.execute("""
        SELECT section, filename, title, SUBSTR(description,1,55) AS description
        FROM pages ORDER BY section, rowid
    """).fetchall()
    table(["Section", "File", "Title", "Description"], rows, [8, 24, 26, 55])


def q_combined(cur):
    section("CROSS-TABLE INSIGHTS")

    subsection("Emission factor per UK route (London ↔ city, long-haul economy)")
    # Use haversine UDF
    rows = cur.execute("""
        SELECT c.name,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)) AS dist_km,
               ef.factor_kgco2e,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)
                     * ef.factor_kgco2e) AS kgco2e_one_way
        FROM cities c
        CROSS JOIN emission_factors ef
        WHERE c.region = 'UK'
          AND ef.mode_key = 'Train-National'
          AND c.name != 'London'
        ORDER BY dist_km DESC
        LIMIT 12
    """).fetchall()
    table(
        ["UK city", "Distance (km)", "Factor", "kgCO₂e (1 pax, one-way)"],
        rows, [18, 14, 8, 24],
    )

    subsection("Top 10 most carbon-intensive routes from London (flight, economy)")
    rows = cur.execute("""
        SELECT c.name, c.region,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)) AS dist_km,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)
                     * ef.factor_kgco2e) AS kgco2e
        FROM cities c
        CROSS JOIN emission_factors ef
        WHERE ef.mode_key = 'Flight-LongHaul-Economy'
          AND c.name != 'London'
        ORDER BY kgco2e DESC
        LIMIT 10
    """).fetchall()
    table(
        ["Destination", "Region", "Distance (km)", "kgCO₂e (1 pax)"],
        rows, [20, 14, 14, 16],
    )

    subsection("Business vs economy: extra kgCO₂e per person")
    rows = cur.execute("""
        SELECT c.name,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)) AS dist_km,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)
                     * (SELECT factor_kgco2e FROM emission_factors
                        WHERE mode_key='Flight-LongHaul-Business')) AS biz_kg,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)
                     * (SELECT factor_kgco2e FROM emission_factors
                        WHERE mode_key='Flight-LongHaul-Economy')) AS eco_kg,
               ROUND(haversine(51.5074, -0.1278, c.latitude, c.longitude)
                     * ((SELECT factor_kgco2e FROM emission_factors
                         WHERE mode_key='Flight-LongHaul-Business')
                        - (SELECT factor_kgco2e FROM emission_factors
                           WHERE mode_key='Flight-LongHaul-Economy'))) AS extra_kg
        FROM cities c
        WHERE c.name IN ('Dubai','Singapore','Tokyo','New York','Sydney','São Paulo')
        ORDER BY dist_km
    """).fetchall()
    table(
        ["Destination", "Dist (km)", "Business kg", "Economy kg", "Extra kg (biz−eco)"],
        rows, [14, 10, 12, 11, 20],
    )


# ── Interactive SQL shell ─────────────────────────────────────────────────────

def shell(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    con.create_function("haversine", 4, _haversine)
    cur = con.cursor()
    print(f"\n{BOLD}ClariComp SQL shell{RESET}  (type .quit to exit, .tables to list)\n")
    while True:
        try:
            line = input("sql> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line in (".quit", ".exit", "\\q"):
            break
        if line == ".tables":
            rows = cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            print("  " + "  ".join(r[0] for r in rows))
            continue
        if line.startswith(".schema"):
            t = line.split(maxsplit=1)[1] if len(line.split()) > 1 else None
            q = f"SELECT sql FROM sqlite_master WHERE type='table'"
            if t:
                q += f" AND name='{t}'"
            for (sql,) in cur.execute(q).fetchall():
                if sql:
                    print(textwrap.indent(sql, "  "))
            continue
        try:
            cur.execute(line)
            rows = cur.fetchall()
            if cur.description:
                headers = [d[0] for d in cur.description]
                table(headers, rows)
            else:
                print(f"  {cur.rowcount} row(s) affected")
        except sqlite3.Error as e:
            print(f"  {GREEN}Error:{RESET} {e}")
    con.close()
    print()


# ── Haversine UDF ─────────────────────────────────────────────────────────────

def _haversine(lat1, lng1, lat2, lng2):
    R = 6371
    def r(d): return d * math.pi / 180
    dlat = r(lat2 - lat1); dlng = r(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(DB_PATH):
        print(f"\n  claricomp.db not found. Run:  python3 seed_db.py\n")
        sys.exit(1)

    if "--shell" in sys.argv or "-s" in sys.argv:
        shell(DB_PATH)
        return

    con = sqlite3.connect(DB_PATH)
    con.create_function("haversine", 4, _haversine)
    cur = con.cursor()

    q_cities(cur)
    q_emission_factors(cur)
    q_pricing(cur)
    q_faq(cur)
    q_ppn(cur)
    q_pages(cur)
    q_combined(cur)

    con.close()
    print()
    hr("═")
    print(f"\n{DIM}  Tip: python3 query_db.py --shell   to run your own SQL queries{RESET}\n")


if __name__ == "__main__":
    main()
