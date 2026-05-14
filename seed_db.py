"""
ClariComp — database seeder
Pulls every structured data point from the static site into a SQLite database.

Usage:
    python3 seed_db.py

Creates: claricomp.db
Tables:  cities, emission_factors, pricing_tiers, tier_features,
         feature_matrix, faq_items, ppn_requirements, pages
"""

import sqlite3, os, textwrap

DB_PATH = os.path.join(os.path.dirname(__file__), "claricomp.db")


# ── Schema ───────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS cities (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    region    TEXT NOT NULL,
    latitude  REAL NOT NULL,
    longitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS emission_factors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    mode_key       TEXT UNIQUE,
    mode_label     TEXT NOT NULL,
    class_label    TEXT,
    unit           TEXT NOT NULL CHECK(unit IN ('pkm','vkm')),
    factor_kgco2e  REAL NOT NULL,
    source         TEXT NOT NULL DEFAULT 'DEFRA 2025 Table 5 · Business Travel',
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS pricing_tiers (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    slug                TEXT UNIQUE NOT NULL,
    name                TEXT NOT NULL,
    price_gbp_monthly   INTEGER,
    size_description    TEXT,
    tagline             TEXT,
    is_featured         INTEGER NOT NULL DEFAULT 0,
    cta_label           TEXT,
    cta_href            TEXT
);

CREATE TABLE IF NOT EXISTS tier_features (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_id      INTEGER NOT NULL REFERENCES pricing_tiers(id),
    feature_text TEXT NOT NULL,
    sort_order   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS feature_matrix (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name   TEXT NOT NULL,
    self_serve     INTEGER NOT NULL DEFAULT 0,
    compliance_pro INTEGER NOT NULL DEFAULT 0,
    enterprise     INTEGER NOT NULL DEFAULT 0,
    sort_order     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS faq_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    category   TEXT NOT NULL,
    question   TEXT NOT NULL,
    answer     TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ppn_requirements (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_code            TEXT NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT NOT NULL,
    claricomp_output    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    section     TEXT
);
"""


# ── Seed data ─────────────────────────────────────────────────────────────────

CITIES = [
    # (name, region, lat, lng)
    # UK
    ("London",        "UK", 51.5074,  -0.1278),
    ("Birmingham",    "UK", 52.4862,  -1.8904),
    ("Manchester",    "UK", 53.4808,  -2.2426),
    ("Edinburgh",     "UK", 55.9533,  -3.1883),
    ("Glasgow",       "UK", 55.8642,  -4.2518),
    ("Bristol",       "UK", 51.4545,  -2.5879),
    ("Leeds",         "UK", 53.8008,  -1.5491),
    ("Liverpool",     "UK", 53.4084,  -2.9916),
    ("Cardiff",       "UK", 51.4816,  -3.1791),
    ("Belfast",       "UK", 54.5973,  -5.9301),
    ("Newcastle",     "UK", 54.9783,  -1.6178),
    ("Sheffield",     "UK", 53.3811,  -1.4701),
    ("Nottingham",    "UK", 52.9548,  -1.1581),
    ("Leicester",     "UK", 52.6369,  -1.1398),
    ("Southampton",   "UK", 50.9097,  -1.4044),
    ("Oxford",        "UK", 51.7520,  -1.2577),
    ("Cambridge",     "UK", 52.2053,   0.1218),
    ("Exeter",        "UK", 50.7260,  -3.5275),
    ("Norwich",       "UK", 52.6309,   1.2974),
    ("Derby",         "UK", 52.9225,  -1.4746),
    # Europe
    ("Paris",         "Europe", 48.8566,   2.3522),
    ("Berlin",        "Europe", 52.5200,  13.4050),
    ("Amsterdam",     "Europe", 52.3676,   4.9041),
    ("Brussels",      "Europe", 50.8503,   4.3517),
    ("Dublin",        "Europe", 53.3498,  -6.2603),
    ("Madrid",        "Europe", 40.4168,  -3.7038),
    ("Barcelona",     "Europe", 41.3851,   2.1734),
    ("Rome",          "Europe", 41.9028,  12.4964),
    ("Milan",         "Europe", 45.4654,   9.1859),
    ("Frankfurt",     "Europe", 50.1109,   8.6821),
    ("Munich",        "Europe", 48.1351,  11.5820),
    ("Vienna",        "Europe", 48.2082,  16.3738),
    ("Zurich",        "Europe", 47.3769,   8.5417),
    ("Geneva",        "Europe", 46.2044,   6.1432),
    ("Lisbon",        "Europe", 38.7223,  -9.1393),
    ("Stockholm",     "Europe", 59.3293,  18.0686),
    ("Oslo",          "Europe", 59.9139,  10.7522),
    ("Copenhagen",    "Europe", 55.6761,  12.5683),
    ("Helsinki",      "Europe", 60.1699,  24.9384),
    ("Warsaw",        "Europe", 52.2297,  21.0122),
    ("Prague",        "Europe", 50.0755,  14.4378),
    ("Budapest",      "Europe", 47.4979,  19.0402),
    ("Bucharest",     "Europe", 44.4268,  26.1025),
    ("Athens",        "Europe", 37.9838,  23.7275),
    ("Istanbul",      "Europe", 41.0082,  28.9784),
    ("Kyiv",          "Europe", 50.4501,  30.5234),
    ("Reykjavik",     "Europe", 64.1355, -21.8954),
    # Americas
    ("New York",      "Americas", 40.7128,  -74.0060),
    ("Los Angeles",   "Americas", 34.0522, -118.2437),
    ("Chicago",       "Americas", 41.8781,  -87.6298),
    ("Toronto",       "Americas", 43.6532,  -79.3832),
    ("Montreal",      "Americas", 45.5017,  -73.5673),
    ("Vancouver",     "Americas", 49.2827, -123.1207),
    ("Mexico City",   "Americas", 19.4326,  -99.1332),
    ("São Paulo",     "Americas",-23.5505,  -46.6333),
    ("Buenos Aires",  "Americas",-34.6037,  -58.3816),
    ("Bogotá",        "Americas",  4.7110,  -74.0721),
    ("Lima",          "Americas",-12.0464,  -77.0428),
    ("Santiago",      "Americas",-33.4489,  -70.6693),
    ("Miami",         "Americas", 25.7617,  -80.1918),
    ("Boston",        "Americas", 42.3601,  -71.0589),
    ("Washington",    "Americas", 38.9072,  -77.0369),
    ("San Francisco", "Americas", 37.7749, -122.4194),
    ("Houston",       "Americas", 29.7604,  -95.3698),
    ("Dallas",        "Americas", 32.7767,  -96.7970),
    ("Atlanta",       "Americas", 33.7490,  -84.3880),
    ("Seattle",       "Americas", 47.6062, -122.3321),
    # Middle East
    ("Dubai",         "Middle East", 25.2048,  55.2708),
    ("Abu Dhabi",     "Middle East", 24.4539,  54.3773),
    ("Doha",          "Middle East", 25.2854,  51.5310),
    ("Riyadh",        "Middle East", 24.6877,  46.7219),
    ("Jeddah",        "Middle East", 21.5433,  39.1728),
    ("Kuwait City",   "Middle East", 29.3759,  47.9774),
    ("Muscat",        "Middle East", 23.5880,  58.3829),
    ("Beirut",        "Middle East", 33.8938,  35.5018),
    ("Tel Aviv",      "Middle East", 32.0853,  34.7818),
    ("Amman",         "Middle East", 31.9454,  35.9284),
    ("Bahrain",       "Middle East", 26.0667,  50.5577),
    # Asia Pacific
    ("Singapore",     "Asia Pacific",  1.3521, 103.8198),
    ("Hong Kong",     "Asia Pacific", 22.3193, 114.1694),
    ("Tokyo",         "Asia Pacific", 35.6762, 139.6503),
    ("Osaka",         "Asia Pacific", 34.6937, 135.5023),
    ("Seoul",         "Asia Pacific", 37.5665, 126.9780),
    ("Beijing",       "Asia Pacific", 39.9042, 116.4074),
    ("Shanghai",      "Asia Pacific", 31.2304, 121.4737),
    ("Mumbai",        "Asia Pacific", 19.0760,  72.8777),
    ("Delhi",         "Asia Pacific", 28.7041,  77.1025),
    ("Bangalore",     "Asia Pacific", 12.9716,  77.5946),
    ("Chennai",       "Asia Pacific", 13.0827,  80.2707),
    ("Hyderabad",     "Asia Pacific", 17.3850,  78.4867),
    ("Bangkok",       "Asia Pacific", 13.7563, 100.5018),
    ("Jakarta",       "Asia Pacific", -6.2088, 106.8456),
    ("Kuala Lumpur",  "Asia Pacific",  3.1390, 101.6869),
    ("Sydney",        "Asia Pacific",-33.8688, 151.2093),
    ("Melbourne",     "Asia Pacific",-37.8136, 144.9631),
    ("Brisbane",      "Asia Pacific",-27.4698, 153.0251),
    ("Perth",         "Asia Pacific",-31.9505, 115.8605),
    ("Auckland",      "Asia Pacific",-36.8485, 174.7633),
    ("Taipei",        "Asia Pacific", 25.0330, 121.5654),
    ("Colombo",       "Asia Pacific",  6.9271,  79.8612),
    ("Dhaka",         "Asia Pacific", 23.8103,  90.4125),
    ("Karachi",       "Asia Pacific", 24.8607,  67.0011),
    ("Lahore",        "Asia Pacific", 31.5204,  74.3587),
    ("Islamabad",     "Asia Pacific", 33.7294,  73.0931),
    ("Kathmandu",     "Asia Pacific", 27.7172,  85.3240),
    ("Yangon",        "Asia Pacific", 16.8661,  96.1951),
    ("Ho Chi Minh",   "Asia Pacific", 10.8231, 106.6297),
    ("Hanoi",         "Asia Pacific", 21.0245, 105.8412),
    ("Manila",        "Asia Pacific", 14.5995, 120.9842),
    # Africa
    ("Cairo",         "Africa", 30.0444,  31.2357),
    ("Lagos",         "Africa",  6.5244,   3.3792),
    ("Nairobi",       "Africa", -1.2921,  36.8219),
    ("Johannesburg",  "Africa",-26.2041,  28.0473),
    ("Cape Town",     "Africa",-33.9249,  18.4241),
    ("Accra",         "Africa",  5.6037,  -0.1870),
    ("Casablanca",    "Africa", 33.5731,  -7.5898),
    ("Addis Ababa",   "Africa",  9.0300,  38.7400),
    ("Dar es Salaam", "Africa", -6.7924,  39.2083),
    ("Kampala",       "Africa",  0.3476,  32.5825),
    ("Tunis",         "Africa", 36.8065,  10.1815),
    ("Dakar",         "Africa", 14.7167, -17.4677),
    ("Algiers",       "Africa", 36.7372,   3.0865),
    ("Kigali",        "Africa", -1.9441,  30.0619),
    ("Abidjan",       "Africa",  5.3600,  -4.0083),
]

# (mode_key, mode_label, class_label, unit, factor, notes)
EMISSION_FACTORS = [
    # Air
    ("Flight-Domestic",           "Air – domestic",           "Average passenger",  "pkm", 0.246550, "Haversine Great Circle distance"),
    ("Flight-ShortHaul-Economy",  "Air – short-haul",         "Economy",            "pkm", 0.151378, "Haversine Great Circle distance"),
    ("Flight-ShortHaul-Business", "Air – short-haul",         "Business",           "pkm", 0.227067, "Haversine Great Circle distance"),
    ("Flight-LongHaul-Economy",   "Air – long-haul",          "Economy",            "pkm", 0.148040, "Haversine Great Circle distance"),
    ("Flight-LongHaul-PremEcon",  "Air – long-haul",          "Premium economy",    "pkm", 0.236864, "Haversine Great Circle distance"),
    ("Flight-LongHaul-Business",  "Air – long-haul",          "Business",           "pkm", 0.429316, "Haversine Great Circle distance"),
    ("Flight-LongHaul-First",     "Air – long-haul",          "First",              "pkm", 0.592160, "Haversine Great Circle distance"),
    ("Flight-International-Avg",  "Air – international",      "Average",            "pkm", 0.197915, "Haversine Great Circle distance"),
    # Rail
    ("Train-National",            "Rail – national",          None,                 "pkm", 0.035463, "UK national rail network"),
    ("Train-LightRail",           "Rail – light & trams",     None,                 "pkm", 0.027750, None),
    ("Train-Eurostar",            "Rail – Eurostar",          None,                 "pkm", 0.004426, "London–Paris/Brussels/Amsterdam"),
    ("Train-Underground",         "Underground – London",     None,                 "pkm", 0.027840, None),
    # Road (passenger)
    ("Coach",                     "Coach",                    None,                 "pkm", 0.027184, None),
    ("Bus-Local",                 "Bus – local",              None,                 "pkm", 0.118030, None),
    # Road (vehicle)
    ("Car-Average-UnknownFuel",   "Car – average",            "Unknown fuel",       "vkm", 0.168350, "Default when fuel type absent"),
    ("Car-Small-Petrol",          "Car – small",              "Petrol",             "vkm", 0.142810, None),
    ("Car-Medium-Diesel",         "Car – medium",             "Diesel",             "vkm", 0.166130, None),
    ("Car-Large-Diesel",          "Car – large",              "Diesel",             "vkm", 0.207430, None),
    ("Car-PHEV",                  "Car – plug-in hybrid",     None,                 "vkm", 0.067940, None),
    ("Car-BEV",                   "Car – battery EV",         None,                 "vkm", 0.047520, None),
    ("Motorbike-Average",         "Motorbike – average",      None,                 "vkm", 0.113810, None),
    ("Taxi-Regular",              "Taxi – regular",           None,                 "vkm", 0.148790, None),
    ("Taxi-BlackCab",             "Taxi – black cab",         None,                 "vkm", 0.207110, None),
    # Ferry
    ("Ferry-Foot",                "Ferry – foot passenger",   None,                 "pkm", 0.018928, None),
    ("Ferry-Car",                 "Ferry – car passenger",    None,                 "pkm", 0.130630, None),
]

PRICING_TIERS = [
    # (slug, name, price_gbp_monthly, size_description, tagline, is_featured, cta_label, cta_href)
    (
        "self-serve",
        "Self-Serve",
        150,
        "Under 100 staff · billed monthly",
        "Basic emissions logging for organisations not yet bound by SECR or PPN 06/21.",
        0,
        "Start with the preview",
        "preview.html",
    ),
    (
        "compliance-pro",
        "Compliance Pro",
        450,
        "250–500 employees · billed monthly",
        "The full SECR + PPN 06/21 stack. Everything required for a defensible tender submission and a signable statutory filing.",
        1,
        "Try the preview first →",
        "preview.html",
    ),
    (
        "enterprise",
        "Enterprise",
        1200,
        "Multi-site · billed monthly",
        "For organisations consolidating multiple subsidiaries or sites under one SECR filing.",
        0,
        "Talk to Seyi",
        "contact.html",
    ),
]

# (tier_slug, feature_text, sort_order)
TIER_FEATURES = [
    # Self-Serve
    ("self-serve", "CSV / XLSX upload", 1),
    ("self-serve", "DEFRA 2025 factor set, 6-dp precision", 2),
    ("self-serve", "Haversine Great Circle for flights", 3),
    ("self-serve", "Dashboard with mode breakdown", 4),
    ("self-serve", "Preview PDF export", 5),
    ("self-serve", "Email support, response within 48h", 6),
    # Compliance Pro
    ("compliance-pro", "Everything in Self-Serve", 1),
    ("compliance-pro", "SECR-compliant annual report", 2),
    ("compliance-pro", "PPN 06/21 Carbon Reduction Plan, one click", 3),
    ("compliance-pro", "Methodology statement appendix", 4),
    ("compliance-pro", "Immutable formula trail per row", 5),
    ("compliance-pro", "Public verification URL", 6),
    ("compliance-pro", "Director signature block", 7),
    ("compliance-pro", "Factor-set version stamp", 8),
    ("compliance-pro", "Priority support, response within 24h", 9),
    # Enterprise
    ("enterprise", "Everything in Compliance Pro", 1),
    ("enterprise", "Multi-site roll-up reporting", 2),
    ("enterprise", "API access for travel-system integration", 3),
    ("enterprise", "Dedicated auditor liaison", 4),
    ("enterprise", "SAML SSO", 5),
    ("enterprise", "Custom factor-set support", 6),
    ("enterprise", "Same-day support response", 7),
]

# (feature_name, self_serve, compliance_pro, enterprise, sort_order)
FEATURE_MATRIX = [
    ("CSV / XLSX upload",                    1, 1, 1, 1),
    ("DEFRA 2025 factor set",                1, 1, 1, 2),
    ("Haversine Great Circle aviation",      1, 1, 1, 3),
    ("Distance Matrix · road & rail",        1, 1, 1, 4),
    ("Indicative preview PDF",               1, 1, 1, 5),
    ("SECR-compliant annual report",         0, 1, 1, 6),
    ("PPN 06/21 Carbon Reduction Plan",      0, 1, 1, 7),
    ("Formula trail appendix",               0, 1, 1, 8),
    ("Public verification URL",              0, 1, 1, 9),
    ("Director signature block",             0, 1, 1, 10),
    ("Multi-site consolidation",             0, 0, 1, 11),
    ("API access",                           0, 0, 1, 12),
    ("Dedicated auditor liaison",            0, 0, 1, 13),
    ("SAML SSO",                             0, 0, 1, 14),
]

# (category, question, answer, sort_order)
FAQ_ITEMS = [
    # The product
    (
        "The product",
        "Does ClariComp produce a PPN 06/21 compliant document?",
        "Yes — on the Compliance Pro and Enterprise tiers. The Carbon Reduction Plan output includes the four artefacts PPN 06/21 requires: a methodology statement, a Net Zero commitment with a target year, a Director-level signature block, and a public verification URL that procurement can check. The Self-Serve tier produces an indicative preview only, not a tender-ready CRP.",
        1,
    ),
    (
        "The product",
        "Is the preview the same as the final report?",
        "The numbers are. The artefacts aren't. The preview uses the same calculation engine, the same DEFRA 2025 factor set, the same Haversine method — but the output is a clearly-labelled indicative PDF, not the SECR annual report or the PPN 06/21 CRP. Upgrading turns the same data into the full documents without re-uploading.",
        2,
    ),
    (
        "The product",
        "Does ClariComp cover Scope 1 and 2?",
        "No. ClariComp covers Scope 3 Category 6 — Business Travel — only. If you need Scope 1 (direct fuel) or Scope 2 (electricity), or other Scope 3 categories, this is not the right tool. The product is deliberately narrow: one category, done properly, at one price.",
        3,
    ),
    (
        "The product",
        "What transport modes are supported?",
        "Air (domestic, short-haul, long-haul, international, with class differentiation); rail (national, light rail, Eurostar, Underground); coach and bus; car (by size, fuel type, EV, plug-in hybrid); motorbike; taxi (regular and black cab); ferry (foot and car passenger).",
        4,
    ),
    (
        "The product",
        "How accurate is the preview?",
        "As accurate as your data lets it be. The calculation precision is six decimal places throughout. The preview reports an aggregate confidence score: 98.7% on a sample dataset means the methodology applied is unambiguous for 98.7% of the emissions accounted for. Lower confidence usually means missing transport class or missing destinations on a small number of rows.",
        5,
    ),
    (
        "The product",
        "Can I use ClariComp without a sustainability team?",
        "That is the design brief. ClariComp was built for the finance, operations or compliance person handling carbon reporting alone. No accreditations needed, no carbon literacy required — the methodology is documented, the factors are referenced, and the formula trail explains itself to your auditor.",
        6,
    ),
    # Your data
    (
        "Your data",
        "What columns does my spreadsheet need?",
        "Five required: trip_date, from_address, to_address, transport_mode, user_name. Optional: distance_km, class, fuel_type, passenger_count. Any column order. Headers are matched automatically; a missing distance is computed.",
        1,
    ),
    (
        "Your data",
        "What year of data should I upload?",
        "Last year. ClariComp only accepts data from the previous financial year. This is to ensure your preview reflects a complete reporting period — partial-year data produces a misleading total. Files containing current-year data are rejected at validation with an explicit message.",
        2,
    ),
    (
        "Your data",
        "What happens if my file has missing data?",
        "Rows with partial data are processed where possible; ClariComp flags assumptions on each row (e.g. 'aircraft class inferred as economy'). Rows that cannot be processed appear in a separate 'needs work' section with the reason. Your file is never rejected wholesale for a small number of incomplete rows.",
        3,
    ),
    (
        "Your data",
        "Can I import historical data?",
        "For trend baselines, yes — on the Compliance Pro tier and above. Historical years are stamped with the DEFRA factor set that was current at the time, not the latest set, so historical numbers don't shift when the tables update.",
        4,
    ),
    # Compliance & trust
    (
        "Compliance & trust",
        "What is the public verification URL?",
        "A unique, immutable URL on claricomp.co.uk/v/<your-co> that hosts your filed CRP. Procurement teams reviewing your bid can visit it directly. The page shows the factor set used, the reporting period, the total tonnage, the methodology version, and the Director signature — without exposing your underlying trip data.",
        1,
    ),
    (
        "Compliance & trust",
        "Is it GDPR compliant?",
        "Yes. Uploaded files are processed server-side and deleted after the preview is generated unless you're on a paid tier (where retention is required for re-export). No data is sold, shared or used for cross-customer benchmarking.",
        2,
    ),
    # Pricing
    (
        "Pricing",
        "Is the preview the same as the paid product?",
        "The calculation engine is identical. The preview produces a clearly-labelled indicative PDF. Compliance Pro produces the SECR annual report, the PPN 06/21 Carbon Reduction Plan, the formula trail appendix and the public verification URL.",
        1,
    ),
    (
        "Pricing",
        "Can I upgrade mid-year?",
        "Yes. Pro-rated monthly. Your existing data carries over and is re-stamped against the same factor set so the report is internally consistent.",
        2,
    ),
    (
        "Pricing",
        "How does billing work?",
        "Monthly. No annual lock-in. You're billed on the same date each month and can cancel any time, with no break-fee.",
        3,
    ),
    (
        "Pricing",
        "What if my company doesn't fit any tier?",
        "Email seyi@claricomp.co.uk. Edge cases (a holding company with three small subsidiaries, a JV with mixed reporting) are common — we'll quote.",
        4,
    ),
]

# (ref_code, title, description, claricomp_output)
PPN_REQUIREMENTS = [
    (
        "REQ-01",
        "A published Carbon Reduction Plan",
        "Hosted on your own website. Must include current emissions, reduction commitments, and a methodology statement.",
        "One-click CRP PDF, generated from your uploaded data. Drop it into a CMS page; that page is what procurement reviews.",
    ),
    (
        "REQ-02",
        "Net Zero commitment by 2050",
        "A stated target year and a reduction trajectory consistent with the science. Vague aspirations get marked down.",
        "Target year and baseline are configurable. The CRP carries the trajectory chart and the year-on-year reduction commitment.",
    ),
    (
        "REQ-03",
        "Public verification URL",
        "Procurement needs to verify the CRP exists and is current. The URL goes in your bid response.",
        "claricomp.co.uk/v/your-co — an immutable, timestamped public page tied to your filed CRP.",
    ),
    (
        "REQ-04",
        "Director-level signature",
        "A board-level signature on the CRP, dated, with a printed name and role.",
        "Director signature block built into the CRP template. The signed PDF is the same artefact you publish and submit.",
    ),
]

PAGES = [
    ("index.html",            "Home",                          "Audit-ready carbon reporting for UK manufacturers and contractors.",         "Core"),
    ("how-it-works.html",     "How it works",                  "Six steps from spreadsheet to signed report.",                               "Core"),
    ("methodology.html",      "Methodology",                   "DEFRA + Haversine methodology, factor table.",                               "Core"),
    ("compliance.html",       "Tender compliance",             "PPN 06/21 tender hub.",                                                      "Core"),
    ("pricing.html",          "Pricing",                       "Three tiers, comparison table.",                                             "Core"),
    ("preview.html",          "Try the preview",               "Trip logger demo with live emission calculation.",                           "Core"),
    ("results.html",          "Results dashboard",             "Preview dashboard with demo data.",                                          "Core"),
    ("sample-report.html",    "Sample report",                 "PDF mock and report contents.",                                              "Core"),
    ("guides.html",           "Guides",                        "Articles hub — practical writing on UK carbon reporting.",                   "Guides"),
    ("guide-crp.html",        "Guide: Carbon Reduction Plan",  "How to prepare a CRP for public tenders.",                                  "Guides"),
    ("guide-buyers.html",     "Guide: Buyers",                 "What buyers expect in UK tender carbon submissions.",                        "Guides"),
    ("guide-spreadsheet.html","Guide: Spreadsheet",            "Spreadsheet prep guide.",                                                    "Guides"),
    ("guide-auditor.html",    "Guide: Auditor",                "How to make carbon reporting audit-friendly.",                               "Guides"),
    ("faq.html",              "FAQ",                           "12 common questions.",                                                        "Support"),
    ("contact.html",          "Contact",                       "Direct email and booking.",                                                  "Support"),
    ("privacy.html",          "Privacy",                       "Data privacy statement.",                                                    "Support"),
]


# ── Build ─────────────────────────────────────────────────────────────────────

def build(db_path: str) -> None:
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"  removed old {os.path.basename(db_path)}")

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    # cities
    cur.executemany(
        "INSERT INTO cities (name, region, latitude, longitude) VALUES (?,?,?,?)",
        CITIES,
    )

    # emission_factors
    cur.executemany(
        """INSERT INTO emission_factors
           (mode_key, mode_label, class_label, unit, factor_kgco2e, notes)
           VALUES (?,?,?,?,?,?)""",
        EMISSION_FACTORS,
    )

    # pricing_tiers
    cur.executemany(
        """INSERT INTO pricing_tiers
           (slug, name, price_gbp_monthly, size_description, tagline, is_featured, cta_label, cta_href)
           VALUES (?,?,?,?,?,?,?,?)""",
        PRICING_TIERS,
    )

    # tier_features — resolve tier_id from slug
    for slug, feature, order in TIER_FEATURES:
        cur.execute("SELECT id FROM pricing_tiers WHERE slug=?", (slug,))
        row = cur.fetchone()
        if row:
            cur.execute(
                "INSERT INTO tier_features (tier_id, feature_text, sort_order) VALUES (?,?,?)",
                (row[0], feature, order),
            )

    # feature_matrix
    cur.executemany(
        """INSERT INTO feature_matrix
           (feature_name, self_serve, compliance_pro, enterprise, sort_order)
           VALUES (?,?,?,?,?)""",
        FEATURE_MATRIX,
    )

    # faq_items
    cur.executemany(
        "INSERT INTO faq_items (category, question, answer, sort_order) VALUES (?,?,?,?)",
        FAQ_ITEMS,
    )

    # ppn_requirements
    cur.executemany(
        """INSERT INTO ppn_requirements
           (ref_code, title, description, claricomp_output)
           VALUES (?,?,?,?)""",
        PPN_REQUIREMENTS,
    )

    # pages
    cur.executemany(
        "INSERT INTO pages (filename, title, description, section) VALUES (?,?,?,?)",
        PAGES,
    )

    con.commit()
    con.close()


def report(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()]
    print(f"\n  {'TABLE':<24} ROWS")
    print(f"  {'─'*24} ────")
    total = 0
    for t in tables:
        n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<24} {n:>4}")
        total += n
    print(f"  {'─'*24} ────")
    print(f"  {'TOTAL':<24} {total:>4}")
    con.close()


if __name__ == "__main__":
    print("\nClariComp — building database…\n")
    build(DB_PATH)
    report(DB_PATH)
    print(f"\n  Created: {DB_PATH}")
    print("\n  To explore:")
    print("    python3 query_db.py           # run the demo queries")
    print("    sqlite3 claricomp.db          # raw SQL shell")
    print("    DB Browser for SQLite (GUI)   # https://sqlitebrowser.org")
    print()
