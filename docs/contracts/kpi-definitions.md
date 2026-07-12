# TransitOps KPI Definitions

All calculations apply the caller's permitted region and date filters. Empty or zero-denominator metrics
return `null`, not a misleading zero.

## Dashboard counts

- **Active vehicles:** all non-retired vehicles.
- **Available vehicles:** vehicles with `AVAILABLE` status.
- **Vehicles in maintenance:** vehicles with `IN_SHOP` status.
- **Active trips:** trips with `DISPATCHED` status.
- **Pending trips:** trips with `DRAFT` status.
- **Drivers on duty:** drivers with `AVAILABLE` or `ON_TRIP` status.

## Current fleet utilization

```text
ON_TRIP vehicles
────────────────────────────────────── × 100
AVAILABLE vehicles + ON_TRIP vehicles
```

Retired and in-shop vehicles are excluded from the serviceable denominator.

## Fuel efficiency

```text
Total completed-trip actual distance
────────────────────────────────────
Total fuel litres associated with those trips
```

Use the ratio of totals rather than averaging per-trip ratios. Return `null` when associated fuel is zero.

## Core operational cost

```text
Fuel cost + maintenance actual cost
```

## Total operating cost

```text
Fuel + maintenance + toll + parking + insurance + permit + other operating expenses
```

Rejected expenses are excluded. Pending-expense inclusion must be explicit in the report filter.

## Vehicle ROI

```text
Vehicle revenue − vehicle core operational cost
────────────────────────────────────────────── × 100
Vehicle acquisition cost
```

Return `null` when acquisition cost is zero. Revenue and costs must use the same currency.

## Trip profitability

```text
Trip revenue − trip fuel cost − approved trip expenses
```

A negative result is valid and represents a loss.

## Units and precision

- Counts: integer
- Percentages: numeric percentage from 0 to 100 where naturally bounded
- Fuel efficiency: kilometres per litre
- Costs and revenue: decimal currency amounts
- Distance: decimal kilometres
- Fuel: decimal litres
