import { http } from './http'
import type { ApiResponse } from './http'
import type { DashboardData } from '../types/air'

export async function getDashboardData(city = ''): Promise<DashboardData> {
  const { data } = await http.get<ApiResponse<DashboardData>>('/dashboard_data', {
    params: city ? { city } : undefined
  })
  return data.data
}

export async function getCities(): Promise<string[]> {
  const { data } = await http.get<ApiResponse<string[]>>('/cities')
  return data.data
}
