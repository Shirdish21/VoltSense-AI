import { useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { AlertTriangle, Cloud, Gauge, IndianRupee, Leaf, Zap } from 'lucide-react'
import { fetchDashboard } from './api'
import { MetricCard } from './components/MetricCard'
import { Sidebar } from './components/Sidebar'
import type { Dashboard } from './types'
import { RoomAnalytics } from './pages/RoomAnalytics'

const roomColors = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24']
const fmt = new Intl.NumberFormat('en-IN')

function Overview() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { fetchDashboard().then(setData).catch(err => setError(err.message)) }, [])
  return <main className="main"><header className="mb-8 flex flex-wrap items-center justify-between gap-4"><div><p className="eyebrow">Energy command center</p><h2 className="mt-1 text-2xl font-semibold text-white">Good afternoon, Shird.</h2><p className="mt-1 text-sm text-slate-400">Here’s how your building is using energy today.</p></div><div className="flex items-center gap-3"><span className="simulated">● Simulated readings</span><select aria-label="Building selector" className="select"><option>VoltSense Residence</option></select></div></header>
  {error && <div className="mb-6 rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-200">{error}. Ensure the FastAPI server is running on port 8000.</div>}
  {!data && !error && <div className="card animate-pulse text-slate-400">Loading calculated energy readings…</div>}
  {data && <DashboardView data={data}/>}</main>
}

function DashboardView({data}: {data: Dashboard}) { const m = data.metrics; return <><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5"><MetricCard icon={Zap} label="Total Energy" value={`${m.total_energy_kwh} kWh`} detail={`Last ${data.period_days} simulated days`}/><MetricCard icon={Gauge} label="Current Power" value={`${fmt.format(m.current_power_watts)} W`} detail="Latest simulated hourly load"/><MetricCard icon={IndianRupee} label="Estimated Bill" value={`₹${fmt.format(m.monthly_bill_inr)}`} detail={`At ₹${data.tariff_inr_per_kwh}/kWh`}/><MetricCard icon={Cloud} label="Carbon Estimate" value={`${m.carbon_kg} kg`} detail={`${data.carbon_factor_kg_per_kwh} kg CO₂e per kWh`}/><MetricCard icon={Leaf} label="Energy Health" value={`${m.health_score}/100`} detail={m.health_score > 70 ? 'Good efficiency profile' : 'Efficiency needs attention'} accent="green"/></section>
  <section className="mt-6 grid gap-6 xl:grid-cols-3"><article className="card xl:col-span-2"><div className="mb-6"><p className="card-title">Daily energy consumption</p><p className="text-sm text-slate-400">Measured from deterministic simulated sensors</p></div><div className="h-72"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data.daily_consumption}><defs><linearGradient id="energy" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#38bdf8" stopOpacity={.35}/><stop offset="100%" stopColor="#38bdf8" stopOpacity={0}/></linearGradient></defs><CartesianGrid vertical={false} stroke="#21334a"/><XAxis dataKey="date" tick={{fill:'#7c8da5',fontSize:11}} tickLine={false} axisLine={false} interval={4}/><YAxis tick={{fill:'#7c8da5',fontSize:11}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#0d1b2d',border:'1px solid #21334a',borderRadius:10}}/><Area type="monotone" dataKey="kwh" stroke="#38bdf8" strokeWidth={2} fill="url(#energy)"/></AreaChart></ResponsiveContainer></div></article>
  <article className="card"><p className="card-title">Room consumption</p><p className="mb-5 text-sm text-slate-400">Last 31 days</p><div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.room_consumption} layout="vertical" margin={{left:15}}><XAxis type="number" hide/><YAxis dataKey="name" type="category" tick={{fill:'#b6c2d2',fontSize:12}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#0d1b2d',border:'1px solid #21334a',borderRadius:10}}/><Bar dataKey="kwh" radius={[0,6,6,0]}>{data.room_consumption.map((_, i)=><Cell key={i} fill={roomColors[i]}/>)}</Bar></BarChart></ResponsiveContainer></div></article></section>
  <section className="mt-6 grid gap-6 xl:grid-cols-5"><article className="card xl:col-span-3"><div className="mb-4"><p className="card-title">Highest-consuming appliances</p><p className="text-sm text-slate-400">Ranked by calculated energy use</p></div><div className="overflow-x-auto"><table><thead><tr><th>Appliance</th><th>Room</th><th>Type</th><th className="text-right">Energy</th></tr></thead><tbody>{data.top_appliances.map(a=><tr key={a.name}><td className="font-medium text-slate-200">{a.name}</td><td>{a.room}</td><td><span className="badge">{a.category}</span></td><td className="text-right font-medium text-sky-300">{a.kwh} kWh</td></tr>)}</tbody></table></div></article>
  <article className="card xl:col-span-2"><div className="mb-4 flex items-center gap-2"><AlertTriangle size={18} className="text-amber-300"/><p className="card-title">Recent energy alerts</p></div><div className="space-y-4">{data.alerts.map(a=><div key={a.title} className="border-l-2 border-sky-400/70 pl-3"><p className="text-sm font-medium text-slate-200">{a.title}</p><p className="mt-1 text-xs leading-5 text-slate-400">{a.detail}</p></div>)}</div></article></section></> }
function App() { return <div className="min-h-screen bg-ink text-slate-200"><Sidebar/><Routes><Route path="/" element={<Overview/>}/><Route path="/rooms" element={<RoomAnalytics/>}/></Routes></div> }
export default App
