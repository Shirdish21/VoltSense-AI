import type { Dashboard, RoomAnalytics, RoomDetail } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export async function fetchDashboard(): Promise<Dashboard> {
  const response = await fetch(`${API_URL}/api/dashboard`)
  if (!response.ok) throw new Error(`Unable to load energy data (${response.status})`)
  return response.json()
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`)
  if (!response.ok) throw new Error(`Unable to load energy data (${response.status})`)
  return response.json()
}

export const fetchRoomAnalytics = () => get<RoomAnalytics>('/api/room-analytics')
export const fetchRoomDetail = (roomName: string) => get<RoomDetail>(`/api/room-analytics/${encodeURIComponent(roomName)}`)
