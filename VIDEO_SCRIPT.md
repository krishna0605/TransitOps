# TransitOps — Demo Video Walkthrough Script

**Target runtime:** ~4–6 minutes · **Format:** screen recording with voice-over

TransitOps is a fleet-operations management app: a **Next.js** front end talking to a **FastAPI** back end.
This script is written as paired **ON SCREEN** (what to click/show) and **SAY** (narration) beats so you can
record it in one pass. Four login roles each see and can act on a different slice of the app, so the tour is
organized role by role.

All demo accounts use the password **`transitops`**.

| Role | Email | Can do |
| --- | --- | --- |
| Fleet Manager | `manager@transitops.dev` | Full access to everything |
| Dispatcher | `dispatcher@transitops.dev` | View vehicles/drivers; full trip lifecycle (create, dispatch, complete, cancel) |
| Safety Officer | `safety@transitops.dev` | Driver create / update / suspend / restore; documents |
| Financial Analyst | `finance@transitops.dev` | Fuel + expenses (incl. approve); reports view / export |

---

## Setup / pre-recording checklist

Do all of this **before** you hit record so the take is clean.

- [ ] **Start the back end and front end:** from the repo root run `pnpm dev` (starts the FastAPI API and the Next.js web app together).
- [ ] **Seed the demo logins:** run `.venv/Scripts/python.exe scripts/seed_demo.py` to create the "TransitOps" org and the four role logins below. (Add a few vehicles, drivers, and trips by hand on camera — that *is* the demo — or pre-populate them before recording.)
- [ ] **Open the browser to** `http://localhost:3000` and confirm the marketing/landing page loads.
- [ ] **Zoom / window:** set browser zoom to ~110–125% and use a clean, full-screen window (hide bookmarks bar, extra tabs, notifications).
- [ ] **Have the four credentials on a sticky note / clipboard** so login is instant on camera.
- [ ] **Log out between roles** (Settings → sign out, or clear the session) so each role starts fresh at the login page.
- [ ] **Optional:** pick a consistent light or dark theme via the theme toggle so the recording looks uniform.

> Tip: if you fat-finger a form on camera, just keep going — the modals validate inline and you can re-open them.

---

## 1. Intro (about 25–30 sec)

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Landing page at `http://localhost:3000`. Slowly scroll the hero, then hover the "Sign in" / login entry point. |
| **SAY** | "This is TransitOps — a fleet-operations management platform for running vehicles, drivers, and trips end to end. The front end is built with Next.js, and it talks to a FastAPI back end that enforces all the business rules. What makes it interesting is role-based access: four different operational roles each log in and see exactly the tools they're responsible for. Let's walk through each one." |

---

## 2. Fleet Manager — the full tour

**Log in:** `manager@transitops.dev` / `transitops`

The Fleet Manager has full access, so use this section to show the complete app: Dashboard, Fleet, Drivers,
Trips (the new list-first flow, end to end), and Maintenance.

### 2a. Dashboard

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | After login, land on the **Dashboard**. Pan across the KPI cards and any status widgets. Point out the left-hand nav (Dashboard, Fleet, Drivers, Trips, Maintenance, Fuel & Expenses, Analytics, Settings). |
| **SAY** | "As Fleet Manager I get the full picture — a dashboard summarizing the fleet, and the complete navigation on the left. Because I'm the manager, every section is unlocked. Let's start with the vehicles." |

### 2b. Fleet registry — + Add vehicle

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Click **Fleet** in the nav. Show the vehicle registry table (reg. no., name/model, type, capacity, odometer, acquisition cost, status). Use the search box and the Type / Status filters briefly. Then click the **Add vehicle** button (top-right) — a modal opens. Fill Registration no. `GJ01AB1234`, Name/model `VAN-11`, Type `Van`, Max capacity `800`, Acquisition cost `650000`, and click **Save vehicle**. Watch the toast and the new row. |
| **SAY** | "This is the vehicle registry — every vehicle in the fleet with capacity, odometer, and status. I can search and filter by type or status. To register a new one I hit 'Add vehicle', fill in the details, and save. Registration numbers have to be unique, and a new vehicle starts out as Available. Notice retired or in-shop vehicles are automatically hidden from the trip dispatcher, so you can't accidentally dispatch something that isn't roadworthy." |

### 2c. Drivers & safety — + Add driver, safety scores

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Click **Drivers**. Show the table: driver, license no., category, expiry, contact, the **safety score bar** (green/amber/red), and the inline status control. Click **Add driver**, fill Name `Priya Shah`, License no. `DL-24815`, Category `LMV`, Expiry `08/2030`, Contact `9876500011`, and **Save driver**. Then open the status dropdown on any driver to show Available / Off Duty / Suspended. |
| **SAY** | "Here are the drivers with their license validity and a color-coded safety score — green is healthy, amber is watch, red is a problem. Adding a driver is the same pattern: one form, and every new driver starts with a perfect safety score of 100. I can change a driver's status right in the row. The rule that matters: an expired license or a suspended driver is blocked from being assigned to a trip." |

### 2d. Trips — the new list-first flow, end to end

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Click **Trips**. Emphasize the layout: a **table of trips** with the lifecycle strip (Draft → Dispatched → Completed → Cancelled) above it, and a **+ New trip** button in the top-right. |
| **SAY** | "Trips use our new list-first design. Instead of a form dominating the page, you get a clean table of every trip and its status — and a single 'New trip' button in the corner." |
| **ON SCREEN** | Click **+ New trip**. The create form opens in a **modal dialog**. Fill Source `Gandhinagar Depot`, Destination `Ahmedabad Hub`, pick an available Vehicle and an available Driver, Cargo `450`, Distance `58`. Point at the **live capacity check** banner turning green ("within capacity"). Optionally bump cargo above capacity to show it turn red and block, then set it back. Click **Dispatch**. |
| **SAY** | "The create form opens in a dialog. It only offers vehicles and drivers that are actually available, and it live-checks cargo against the vehicle's capacity — if I overload it, dispatch is blocked right here. Within capacity, I dispatch, and the trip goes straight onto the board." |
| **ON SCREEN** | Back on the table, find a **Draft** trip and click its per-row **Dispatch** action. Then on a **Dispatched** trip, click **Complete**. On another Dispatched trip, click **Cancel** to show that path too. |
| **SAY** | "Each row carries its own lifecycle actions. A draft trip gets a Dispatch button; a dispatched trip can be Completed or Cancelled — no separate screens. When a trip completes, the system automatically rolls the odometer forward, writes a fuel log and expenses, and returns the vehicle and driver to Available. One click, and the books stay consistent." |

### 2e. Maintenance — service log

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Click **Maintenance**. Show the **service-log table** (vehicle, service, cost, date, trip, status) with the **+ New maintenance** button top-right. Click it — the modal opens. Select a Vehicle, Service type `Brake Service`, Cost `4200`, a Date, Status `Active (In Shop)`, and **Save record**. Then in the table, on an **Active** row, click the per-row **Close** action. |
| **SAY** | "Maintenance follows the exact same list-first pattern — a service log, with 'New maintenance' in the corner. Logging an active record moves that vehicle to 'In Shop', which pulls it out of the dispatcher automatically. When the work is done I hit Close on the row, and the vehicle returns to Available. Fuel and maintenance costs both feed the operational-cost totals the finance team sees later." |

---

## 3. Dispatcher

**Log out, then log in:** `dispatcher@transitops.dev` / `transitops`

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Land in the app. Point out the trimmed navigation — the dispatcher can view vehicles and drivers but their job is Trips. Click through **Fleet** and **Drivers** quickly to show read-only visibility, then land on **Trips**. |
| **SAY** | "Now I'm signed in as a Dispatcher. I can see the fleet and the drivers to know what's available, but my real workspace is Trips — and I own the entire trip lifecycle." |
| **ON SCREEN** | On the Trips list, click **+ New trip**, fill the modal (source, destination, an available vehicle and driver, cargo, distance), watch the green capacity check, and **Dispatch**. Then use the per-row **Dispatch**, **Complete**, and **Cancel** actions on existing trips. |
| **SAY** | "Same list-first flow: I create a trip in the dialog, the app enforces availability and capacity, and I dispatch. From the table I can dispatch drafts, complete runs as they finish, or cancel — the full lifecycle, right from the list. This is the dispatcher's day, all on one screen." |

---

## 4. Safety Officer

**Log out, then log in:** `safety@transitops.dev` / `transitops`

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Land in the app and go to **Drivers**. |
| **SAY** | "Signed in as a Safety Officer, my focus is the people behind the wheel — driver records, licensing, and safety." |
| **ON SCREEN** | Click **Add driver**, create a driver in the modal (Name, License no., Category, Expiry, Contact), and **Save**. Then on an existing driver, open the inline status control and set it to **Suspended**; on a suspended driver, set it back to **Available** to show restore. Point at the safety-score bars. |
| **SAY** | "I can onboard a new driver, update their details, and manage their standing. If someone needs to be pulled off the road I suspend them right from the row — and a suspended driver, or one with an expired license, is automatically blocked from any trip assignment. When they're cleared, I restore them. Safety is enforced by the system, not just by policy." |

---

## 5. Financial Analyst

**Log out, then log in:** `finance@transitops.dev` / `transitops`

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Land in the app and open **Fuel & Expenses**. Show the **Fuel logs** table and the **Other expenses (toll / other)** table, plus the highlighted **Total operational cost** card at the bottom. |
| **SAY** | "As a Financial Analyst, I live in the money side of operations. Here are the fuel logs and the toll and other expenses, and at the bottom the total operational cost — fuel plus maintenance — calculated automatically." |
| **ON SCREEN** | Click **Log fuel**, fill the modal (Vehicle, Date, Liters `40`, Cost `3600`) and **Save fuel log**. Then click **Add expense**, pick a Vehicle, enter Toll `250` and Other `120`, and **Save expense**. Point at the expense **status badge** and approve any pending expense. |
| **SAY** | "I log fuel and add expenses through these dialogs, and I approve expenses that are pending so they roll into the operational totals." |
| **ON SCREEN** | Click **Analytics**. Show the KPI cards (fuel logs, fleet utilization, operational cost, completed trips), the charts (monthly revenue, top costliest vehicles, cost breakdown pie), then click **Export CSV** and show the download. |
| **SAY** | "And in Analytics I get the reporting view — utilization, cost breakdown, the costliest vehicles — and I can export it all to CSV for finance reviews. Everything you saw the other roles do flows into these numbers in real time." |

---

## 6. Closing (about 15–20 sec)

| Beat | Detail |
| --- | --- |
| **ON SCREEN** | Return to the **Dashboard** (or a clean shot of the app). Slow zoom-out or hold on the nav. |
| **SAY** | "That's TransitOps: a Next.js and FastAPI platform where fleet managers, dispatchers, safety officers, and finance each get a focused, role-based workspace — with a consistent list-first design and business rules enforced end to end. From registering a vehicle to dispatching a trip to closing the books, it all stays in sync. Thanks for watching." |

---

### Quick shot list (for editing)
1. Landing page → login
2. Manager: Dashboard → Fleet (+Add vehicle) → Drivers (+Add driver, safety scores) → Trips (list-first, create-in-modal, dispatch/complete/cancel) → Maintenance (log + close)
3. Dispatcher: Trips full lifecycle
4. Safety Officer: Drivers create / suspend / restore
5. Financial Analyst: Fuel & Expenses (log/add/approve) → Analytics (charts + Export CSV)
6. Closing on Dashboard
