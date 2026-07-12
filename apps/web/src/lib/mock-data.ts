/**
 * Placeholder sample data for the UI, mirroring the mockup screenshots.
 * Replace with real API calls (via the api-client) once the endpoints exist.
 */

export type VehicleStatus = "Available" | "On Trip" | "In Shop" | "Retired";
export type DriverStatus = "Available" | "On Trip" | "Off Duty" | "Suspended";
export type TripStatus = "Draft" | "Dispatched" | "Completed" | "Cancelled";
export type MaintenanceStatus = "Active" | "Completed";
export type ExpenseStatus = "Available" | "Completed";

export type Vehicle = {
  id: number;
  regNo: string;
  nameModel: string;
  type: "Van" | "Truck" | "Mini";
  capacityKg: number;
  odometer: number;
  acquisitionCost: number;
  status: VehicleStatus;
};

export type Driver = {
  id: number;
  name: string;
  licenseNo: string;
  category: "LMV" | "HMV";
  expiry: string;
  expired?: boolean;
  contact: string;
  safetyScore: number;
  status: DriverStatus;
};

export type Trip = {
  id: number;
  code: string;
  source: string;
  destination: string;
  vehicle: string;
  driver: string;
  status: TripStatus;
  eta: string;
  cargoKg: number;
  distanceKm: number;
};

export type Maintenance = {
  id: number;
  vehicle: string;
  service: string;
  cost: number;
  date: string;
  status: MaintenanceStatus;
};

export type FuelLog = {
  id: number;
  vehicle: string;
  date: string;
  liters: number;
  cost: number;
};

export type Expense = {
  id: number;
  trip: string;
  vehicle: string;
  toll: number;
  other: number;
  amount: number;
  status: ExpenseStatus;
};

export const vehicles: Vehicle[] = [
  {
    id: 1,
    regNo: "GJ01AB4521",
    nameModel: "VAN-05",
    type: "Van",
    capacityKg: 500,
    odometer: 74000,
    acquisitionCost: 620000,
    status: "Available",
  },
  {
    id: 2,
    regNo: "GJ01AB9985",
    nameModel: "TRUCK-11",
    type: "Truck",
    capacityKg: 5000,
    odometer: 182000,
    acquisitionCost: 2450000,
    status: "On Trip",
  },
  {
    id: 3,
    regNo: "GJ01AB1120",
    nameModel: "MINI-03",
    type: "Mini",
    capacityKg: 1000,
    odometer: 66000,
    acquisitionCost: 410000,
    status: "In Shop",
  },
  {
    id: 4,
    regNo: "GJ01AB0008",
    nameModel: "VAN-09",
    type: "Van",
    capacityKg: 750,
    odometer: 241900,
    acquisitionCost: 590000,
    status: "Retired",
  },
  {
    id: 5,
    regNo: "GJ01AB7742",
    nameModel: "TRUCK-04",
    type: "Truck",
    capacityKg: 8000,
    odometer: 98500,
    acquisitionCost: 2900000,
    status: "Available",
  },
  {
    id: 6,
    regNo: "GJ01AB5510",
    nameModel: "MINI-08",
    type: "Mini",
    capacityKg: 900,
    odometer: 51200,
    acquisitionCost: 380000,
    status: "On Trip",
  },
];

export const drivers: Driver[] = [
  {
    id: 1,
    name: "Alex",
    licenseNo: "DL-88213",
    category: "LMV",
    expiry: "12/2028",
    contact: "98765xxxxx",
    safetyScore: 96,
    status: "Available",
  },
  {
    id: 2,
    name: "John",
    licenseNo: "DL-44120",
    category: "HMV",
    expiry: "03/2025",
    expired: true,
    contact: "98220xxxxx",
    safetyScore: 81,
    status: "Suspended",
  },
  {
    id: 3,
    name: "Priya",
    licenseNo: "DL-77031",
    category: "LMV",
    expiry: "08/2027",
    contact: "99110xxxxx",
    safetyScore: 99,
    status: "On Trip",
  },
  {
    id: 4,
    name: "Suresh",
    licenseNo: "DL-90045",
    category: "HMV",
    expiry: "01/2027",
    contact: "97440xxxxx",
    safetyScore: 88,
    status: "Off Duty",
  },
];

export const trips: Trip[] = [
  {
    id: 1,
    code: "TR001",
    source: "Gandhinagar Depot",
    destination: "Ahmedabad Hub",
    vehicle: "VAN-05",
    driver: "Alex",
    status: "Dispatched",
    eta: "45 min",
    cargoKg: 450,
    distanceKm: 58,
  },
  {
    id: 2,
    code: "TR002",
    source: "Vatva",
    destination: "Rajkot Yard",
    vehicle: "TRUCK-11",
    driver: "John",
    status: "Completed",
    eta: "—",
    cargoKg: 3200,
    distanceKm: 214,
  },
  {
    id: 3,
    code: "TR003",
    source: "Sabarmati",
    destination: "Nadiad",
    vehicle: "MINI-08",
    driver: "Priya",
    status: "Dispatched",
    eta: "1h 10m",
    cargoKg: 620,
    distanceKm: 74,
  },
  {
    id: 4,
    code: "TR004",
    source: "Vatva Industrial Area",
    destination: "Sanand Warehouse",
    vehicle: "TRUCK-04",
    driver: "Suresh",
    status: "Draft",
    eta: "Awaiting driver",
    cargoKg: 5200,
    distanceKm: 39,
  },
  {
    id: 5,
    code: "TR006",
    source: "Mansa",
    destination: "Kalol Depot",
    vehicle: "—",
    driver: "—",
    status: "Cancelled",
    eta: "Vehicle sent to shop",
    cargoKg: 0,
    distanceKm: 0,
  },
];

export const maintenanceLogs: Maintenance[] = [
  {
    id: 1,
    vehicle: "VAN-05",
    service: "Oil Change",
    cost: 2500,
    date: "2026-07-09",
    status: "Active",
  },
  {
    id: 2,
    vehicle: "TRUCK-11",
    service: "Engine Repair",
    cost: 18000,
    date: "2026-07-02",
    status: "Completed",
  },
  {
    id: 3,
    vehicle: "MINI-03",
    service: "Tyre Replace",
    cost: 6200,
    date: "2026-07-05",
    status: "Active",
  },
];

export const fuelLogs: FuelLog[] = [
  { id: 1, vehicle: "VAN-09", date: "2026-07-06", liters: 42, cost: 3860 },
  { id: 2, vehicle: "TRUCK-11", date: "2026-07-06", liters: 60, cost: 5400 },
  { id: 3, vehicle: "MINI-03", date: "2026-07-06", liters: 28, cost: 2040 },
];

export const expenses: Expense[] = [
  {
    id: 1,
    trip: "TR001",
    vehicle: "VAN-09",
    toll: 120,
    other: 0,
    amount: 120,
    status: "Available",
  },
  {
    id: 2,
    trip: "TR002",
    vehicle: "TRUCK-11",
    toll: 640,
    other: 360,
    amount: 18000,
    status: "Completed",
  },
];

export const dashboardKpis = [
  { label: "Active Vehicles", value: "53", tone: "default" as const },
  { label: "Available Vehicles", value: "42", tone: "success" as const },
  { label: "Vehicles in Maintenance", value: "05", tone: "warning" as const },
  { label: "Active Trips", value: "18", tone: "info" as const },
  { label: "Pending Trips", value: "09", tone: "default" as const },
  { label: "Drivers on Duty", value: "26", tone: "default" as const },
  { label: "Fleet Utilization", value: "81%", tone: "success" as const },
];

export const vehicleStatusBreakdown: {
  status: VehicleStatus;
  count: number;
}[] = [
  { status: "Available", count: 42 },
  { status: "On Trip", count: 18 },
  { status: "In Shop", count: 5 },
  { status: "Retired", count: 3 },
];

export const analyticsKpis = [
  { label: "Fuel Efficiency", value: "8.4 km/l" },
  { label: "Fleet Utilization", value: "81%" },
  { label: "Operational Cost", value: "₹34,070" },
  { label: "Vehicle ROI", value: "14.2%" },
];

export const monthlyRevenue = [
  { month: "Jan", value: 42 },
  { month: "Feb", value: 55 },
  { month: "Mar", value: 48 },
  { month: "Apr", value: 61 },
  { month: "May", value: 58 },
  { month: "Jun", value: 72 },
  { month: "Jul", value: 66 },
];

export const costliestVehicles = [
  { vehicle: "TRUCK-11", cost: 96 },
  { vehicle: "MINI-03", cost: 61 },
  { vehicle: "VAN-05", cost: 24 },
];

export const costBreakdown = [
  { category: "Fuel", value: 15200 },
  { category: "Maintenance", value: 26700 },
  { category: "Toll", value: 4300 },
];
