# TransitOps Demo Seed Data

Seeded by `scripts/seed_demo.py` (idempotent — wipes and reseeds every run, roles untouched).
Re-run: `PYTHONPATH="apps/api" .venv/Scripts/python.exe scripts/seed_demo.py`

> **Volume + date spread for analytics.** The dataset is scaled up (12 vehicles,
> 9 drivers, 45 trips, 45 fuel logs, 45 maintenance logs, 48 expenses) and every
> time-stamped record is distributed across the **last ~3 months
> (2026-04-15 → 2026-07-12)** so **Screen 7** analytics (Monthly Revenue / cost
> trends) plots **multiple months** instead of a single spike. Trip status is
> weighted toward **Completed (25) and Dispatched (12)** so the charts have
> volume. Generation is deterministic (fixed RNG seed) — re-runs produce the
> same data.

> Note: integer PKs come from Postgres sequences that are **not** reset between
> re-runs, so the exact `trip_id`/`vehicle_id`/etc. values shift each reseed.
> The IDs below reflect the current seed; identify records by route / reg_no /
> name if in doubt, and re-check the script's printed summary after any rerun.

## Login credentials

All users share the password **`Test1234!`**.

| Email                            | Password   | Role              | Name          |
|----------------------------------|------------|-------------------|---------------|
| fleet.manager@transitops.test    | Test1234!  | Fleet Manager     | Fatima Sheikh |
| dispatcher@transitops.test       | Test1234!  | Dispatcher        | Dan Ortiz     |
| safety.officer@transitops.test   | Test1234!  | Safety Officer    | Sara Khan     |
| financial.analyst@transitops.test| Test1234!  | Financial Analyst | Farhan Ali    |

> These four users exist in the DB with **argon2** password hashes (via
> `pwdlib`), one per role, so the login flow can authenticate against real
> records. Real auth is being wired up against exactly these rows — the seed
> **keeps the 4 users intact** on every re-run, so use the credentials above to
> sign in. (If auth is still mid-integration when you test, the four users are
> nonetheless present and correctly hashed.)

## What each record demonstrates

### Vehicles (12) — every status covered
The status spread that matters for the fleet screen is preserved; extra rows add
volume. Status mix: **Available 6, On Trip 2, In Shop 2, Retired 2.** The five
"anchor" vehicles below carry the demo relationships; the other seven are fleet
volume.

| reg_no      | model                    | type  | status    | note                                   |
|-------------|--------------------------|-------|-----------|----------------------------------------|
| MH12AB1234  | Tata Ace Gold            | Mini  | Available | ran the **star** Completed trip        |
| MH14CD5678  | Ashok Leyland Dost       | Van   | On Trip   | currently on the anchor Dispatched trip|
| MH04EF9012  | Eicher Pro 2049          | Truck | In Shop   | has the **Active** maintenance record  |
| MH01GH3456  | Mahindra Bolero Pik-Up   | Van   | Retired   | high odometer, retired from service    |
| MH12JK7890  | Tata 407                 | Truck | Available | free capacity for the Draft trip       |
| MH12LM2345  | Tata Intra V30           | Mini  | Available | fleet volume                           |
| MH14NO6789  | Mahindra Furio 7         | Truck | Available | fleet volume                           |
| MH02PQ1122  | Ashok Leyland Bada Dost  | Van   | On Trip   | fleet volume                           |
| MH03RS3344  | Eicher Pro 3015          | Truck | Available | fleet volume                           |
| MH05TU5566  | Force Traveller Delivery | Van   | In Shop   | fleet volume                           |
| MH06VW7788  | Tata Yodha Pik-Up        | Mini  | Available | fleet volume                           |
| MH07XY9900  | Mahindra Jeeto           | Mini  | Retired   | high odometer, retired                 |

> Trips/fuel/maintenance are generated only against **Available/On Trip**
> vehicles (In Shop and Retired are left idle, matching their status).

### Drivers (9) — safety/eligibility edge cases preserved
The two required edge cases (**expired license**, **suspended**) are kept; the
rest add volume with varied safety scores, license categories, and expiries.

| name             | license      | category | expiry     | safety | status    | note                        |
|------------------|--------------|----------|------------|--------|-----------|-----------------------------|
| Ravi Kumar       | DLLMV2019001 | LMV      | 2025-01-15 | 72.0   | Available | **EXPIRED license** (past)  |
| Imran Shaikh     | DLHMV2021002 | HMV      | 2027-08-30 | 61.0   | Suspended | **Suspended** driver        |
| Priya Nair       | DLLMV2023003 | LMV      | 2028-05-20 | 96.5   | Available | top safety score            |
| Suresh Patil     | DLHMV2022004 | HMV      | 2029-11-10 | 88.0   | On Trip   | on the anchor Dispatched trip|
| Anjali Deshmukh  | DLLMV2020005 | LMV      | 2026-12-05 | 83.5   | Available | near-term expiry            |
| Vikram Rao       | DLHMV2019006 | HMV      | 2027-03-18 | 90.0   | Available | volume                      |
| Neha Gupta       | DLLMV2024007 | LMV      | 2029-06-25 | 94.0   | Off Duty  | Off Duty status covered     |
| Arjun Mehta      | DLHMV2023008 | HMV      | 2028-09-12 | 78.5   | Available | volume                      |
| Kiran Joshi      | DLHMV2021009 | HMV      | 2030-02-28 | 85.0   | On Trip   | volume                      |

> The expired- and suspended-license drivers are **excluded** from generated
> trip assignments (only valid, non-suspended drivers are dispatched).

### Trips (45) — every status covered, weighted for chart volume
Status mix: **Completed 25, Dispatched 12, Draft 4, Cancelled 4.** The four
**anchor** trips below preserve every status and pin the attribution chain;
the remaining 41 are generated across the ~3-month window.

- **Completed** trips set `dispatched_at` + `completed_at` + `final_odometer`.
- **Dispatched** trips set `dispatched_at` (+ `dispatched_by` = Dispatcher), no `completed_at`/`final_odometer`.
- **Draft** trips set none of the timestamps.
- **Cancelled** trips carry a `dispatched_by` but no dispatch/complete timestamps.

| route          | status     | dispatched_by | fields set                                      |
|----------------|------------|---------------|-------------------------------------------------|
| Mumbai -> Pune | Completed  | Dispatcher    | dispatched_at + completed_at + final_odometer (the **star** trip) |
| Mumbai -> Nashik| Dispatched| Dispatcher    | dispatched_at set, final_odometer NULL          |
| Pune -> Nagpur | Draft      | (none)        | no dispatched_at / completed_at                 |
| Mumbai -> Surat| Cancelled  | Dispatcher    | never dispatched                                |

All `dispatched_at`/`completed_at` are spread across **2026-04 → 2026-07**
(roughly Apr 7 / May 14 / Jun 13 / Jul trips), so the Screen 7 time series has
multiple months of data.

### The star of the demo — trip -> cost attribution

**The anchor Completed trip `Mumbai -> Pune` (vehicle MH12AB1234)** carries the
full attribution chain the presenter should point at:

- **Fuel log** linked to it (28.5 L, ₹2,565) — plus a second fuel log linked to
  the anchor Dispatched trip, and ~43 more fuel logs (about half linked to trips,
  the rest depot fills with `trip_id NULL`).
- **Maintenance log** linked to it: "Brake pad replacement", ₹3,200, status
  **Completed**.
- **Auto-linked expense**: category **Maintenance**, ₹3,200, with **both**
  `trip_id` **and** `maintenance_id` set. This demonstrates the
  expense ↔ maintenance **one-to-one** link plus trip attribution (a
  maintenance-generated expense posted against the trip).

> The exact IDs shift each reseed (sequences aren't reset) — identify this trip
> by route **Mumbai → Pune** / reg_no **MH12AB1234**, or read the script's
> printed summary. There are now **5 auto-linked maintenance expenses** in total
> (the anchor plus a handful generated on other trip-linked completed jobs), each
> with both `trip_id` and `maintenance_id` set.

So the same trip shows fuel + maintenance + an auto-posted maintenance expense —
ideal for the **Screen 7 analytics cost breakdown** (fuel vs maintenance vs toll
per trip/vehicle), and the ~3-month spread gives the **Monthly Revenue / cost
trend** charts real month-over-month movement.

### Other records
- **Active maintenance** ("Engine overhaul", ₹45,000, status **Active**) on the
  **In Shop** vehicle MH04EF9012 — matches its status for the maintenance screen.
  The 45 maintenance logs are a mix of **Active/Completed**, some trip-linked,
  spread across the window.
- **Expenses (48 total)** across all three categories:
  - **Maintenance** — 5 auto-linked (trip + maintenance) plus vehicle-only rows.
  - **Toll** — attributed to most trips that actually ran.
  - **Other** — miscellaneous vehicle-only expenses.

## Verified row counts
| table            | rows |
|------------------|------|
| role (untouched) | 4    |
| user             | 4    |
| vehicle          | 12   |
| driver           | 9    |
| trip             | 45   |
| fuel_log         | 45   |
| maintenance_log  | 45   |
| expense          | 48   |

Trip/fuel/maintenance dates span **2026-04-17 → 2026-07-12** (dispatched-at by
month: Apr 7, May 14, Jun 13, Jul 3), giving Screen 7 a multi-month series.
