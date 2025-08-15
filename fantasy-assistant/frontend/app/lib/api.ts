/**
 * API client for the fantasy assistant backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Player {
  id: string
  name: string
  team: string
  position: string
  fantasy_points: number
  vorp: number
  tier: number
  bye_week?: number
  injury_status?: string
  depth_rank?: number
  p10?: number
  p50?: number
  p90?: number
  startable_weeks?: number[]
  early_season_value?: number
}

export interface DraftPick {
  league_id: string
  player_id: string
  team_slot?: string
  round: number
  pick: number
}

export interface DraftAdvice {
  top5: Array<{
    player: Player
    reason: string
    priority: number
  }>
  rationale: string
  fallbacks: Player[]
  exposure_warnings: string[]
  opponent_predictions: Array<{
    player: Player
    probability: number
    reason: string
  }>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request to ${endpoint} failed:`, error)
      throw error
    }
  }

  async getRankings(params?: {
    pos?: string
    limit?: number
    scoring_profile?: string
  }): Promise<{ players: Player[]; total: number }> {
    const searchParams = new URLSearchParams()
    if (params?.pos) searchParams.append('pos', params.pos)
    if (params?.limit) searchParams.append('limit', params.limit.toString())
    if (params?.scoring_profile) searchParams.append('scoring_profile', params.scoring_profile)

    const query = searchParams.toString() ? `?${searchParams.toString()}` : ''
    return this.request(`/rankings/${query}`)
  }

  async makeDraftPick(pick: DraftPick): Promise<{ success: boolean; player_id: string }> {
    return this.request('/draft/pick', {
      method: 'POST',
      body: JSON.stringify(pick),
    })
  }

  async getDraftAdvice(params: {
    league_id: string
    round: number
    pick: number
    roster_state?: string
  }): Promise<DraftAdvice> {
    const searchParams = new URLSearchParams({
      league_id: params.league_id,
      round: params.round.toString(),
      pick: params.pick.toString(),
    })
    if (params.roster_state) {
      searchParams.append('roster_state', params.roster_state)
    }

    return this.request(`/advice/?${searchParams.toString()}`)
  }

  async syncSleeperLeague(league_id: string): Promise<{ success: boolean; league_id: string }> {
    return this.request('/sync/sleeper', {
      method: 'POST',
      body: JSON.stringify({ league_id }),
    })
  }

  async healthCheck(): Promise<{ ok: boolean }> {
    return this.request('/healthz')
  }
}

// Export singleton instance
export const apiClient = new ApiClient()

// Export types and client class
export { ApiClient }