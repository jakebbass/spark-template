export interface Player {
  id: string;
  name: string;
  position: 'QB' | 'RB' | 'WR' | 'TE' | 'K' | 'DST';
  team: string;
  byeWeek: number;
  tier: number;
  adp: number;
  projectedPoints: number;
  vorp: number;
  floor: number;
  ceiling: number;
  startableWeeks: number[];
  injuryStatus?: 'Healthy' | 'Questionable' | 'Doubtful' | 'Out';
  depthRank: number;
  isDrafted: boolean;
  draftedBy?: string;
  draftedRound?: number;
  draftedPick?: number;
}

export interface DraftPick {
  round: number;
  pick: number;
  player: Player | null;
  team: string;
  timestamp?: Date;
}

export interface Roster {
  [team: string]: Player[];
}

export interface DraftAdvice {
  recommendations: {
    player: Player;
    reason: string;
    priority: number;
  }[];
  rationale: string;
  alternatives: {
    player: Player;
    reason: string;
  }[];
}

export interface FilterState {
  position: string[];
  tier: number | null;
  byeWeek: number | null;
  team: string[];
  availableOnly: boolean;
  injuryStatus: string[];
}

export interface ScoringSettings {
  passingYards: number;
  passingTds: number;
  interceptions: number;
  rushingYards: number;
  rushingTds: number;
  receptions: number;
  receivingYards: number;
  receivingTds: number;
  fumbles: number;
}

export const DEFAULT_SCORING: ScoringSettings = {
  passingYards: 0.04,
  passingTds: 4,
  interceptions: -2,
  rushingYards: 0.1,
  rushingTds: 6,
  receptions: 1,
  receivingYards: 0.1,
  receivingTds: 6,
  fumbles: -2,
};

export const TEAMS = [
  'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN',
  'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV', 'LAC', 'LAR', 'MIA',
  'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB',
  'TEN', 'WAS'
];

export const POSITIONS = ['QB', 'RB', 'WR', 'TE', 'K', 'DST'] as const;