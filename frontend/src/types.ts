export type Dashboard = {
  simulated: boolean; period_days: number; tariff_inr_per_kwh: number; carbon_factor_kg_per_kwh: number;
  metrics: { total_energy_kwh: number; current_power_watts: number; monthly_bill_inr: number; carbon_kg: number; health_score: number };
  daily_consumption: {date: string; kwh: number}[]; room_consumption: {name: string; kwh: number}[];
  top_appliances: {name: string; category: string; room: string; kwh: number}[];
  alerts: {severity: string; title: string; detail: string}[];
}

export type RoomSummary = { name: string; area_sqft: number; energy_kwh: number; cost_inr: number; percentage: number; baseline_kwh: number; variance_percent: number; status: string; waste_detected: boolean }
export type RoomAnalytics = { simulated: boolean; period_days: number; tariff_inr_per_kwh: number; building_total_kwh: number; highest_consumption_room: RoomSummary | null; rooms: RoomSummary[] }
export type RoomDetail = { simulated: boolean; tariff_inr_per_kwh: number; room: RoomSummary; connected_appliances: {name: string; category: string; rated_watts: number; energy_kwh: number; cost_inr: number}[]; consumption_history: {date: string; kwh: number}[]; recommendations: string[] }
