export interface CityAir {
  city: string
  province: string
  aqi: number
  quality_level: string
  pm25: number
  pm10: number
  so2: number
  no2: number
  co: number
  o3: number
  lat: number
  lng: number
}

export interface TrendPoint {
  date: string
  aqi: number
  pm25: number
}

export interface DashboardData {
  total_cities: number
  avg_aqi: number
  good_cities: number
  polluted_cities: number
  city_ranking: CityAir[]
  region_stats: Record<string, number>
  level_distribution: Record<string, number>
  selected_city: string
  trend: TrendPoint[]
  update_time: string
}
