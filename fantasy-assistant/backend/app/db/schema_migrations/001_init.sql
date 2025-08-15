-- Initial schema migration for Fantasy Draft Assistant
-- Version: 001
-- Description: Create all base tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Players table
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    team VARCHAR(10) NOT NULL,
    position VARCHAR(10) NOT NULL,
    bye_week INTEGER,
    age INTEGER,
    height VARCHAR(10),
    weight INTEGER,
    xrefs JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projections table
CREATE TABLE projections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    season INTEGER NOT NULL,
    source VARCHAR(50) NOT NULL,
    stats JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Historical stats table
CREATE TABLE historical_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    season INTEGER NOT NULL,
    stats JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Depth charts table
CREATE TABLE depth_charts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team VARCHAR(10) NOT NULL,
    position VARCHAR(10) NOT NULL,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Injuries table
CREATE TABLE injuries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    note TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ADP table
CREATE TABLE adp (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    adp NUMERIC(5, 2) NOT NULL,
    sample_size INTEGER NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Draft picks table
CREATE TABLE draft_picks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    league_id VARCHAR(100) NOT NULL,
    round INTEGER NOT NULL,
    pick INTEGER NOT NULL,
    player_id UUID REFERENCES players(id),
    team_slot VARCHAR(50),
    ts TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User settings table
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL,
    scoring JSONB NOT NULL,
    exposure_limits JSONB DEFAULT '{}',
    strategy JSONB DEFAULT '{}'
);

-- Leagues table
CREATE TABLE leagues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    settings JSONB NOT NULL,
    scoring JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_team ON players(team);
CREATE INDEX idx_depth_charts_team_position ON depth_charts(team, position, rank);
CREATE INDEX idx_projections_player_season ON projections(player_id, season);
CREATE INDEX idx_historical_stats_player_season ON historical_stats(player_id, season);
CREATE INDEX idx_adp_platform ON adp(platform, adp);
CREATE INDEX idx_draft_picks_league_round ON draft_picks(league_id, round, pick);
CREATE INDEX idx_injuries_updated_at ON injuries(updated_at);
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);

-- Comments for documentation
COMMENT ON TABLE players IS 'Master table of all fantasy football players';
COMMENT ON TABLE projections IS 'Projected fantasy points and stats for upcoming season';
COMMENT ON TABLE historical_stats IS 'Historical performance data';
COMMENT ON TABLE depth_charts IS 'Team depth charts by position';
COMMENT ON TABLE injuries IS 'Current injury status and notes';
COMMENT ON TABLE adp IS 'Average draft position across platforms';
COMMENT ON TABLE draft_picks IS 'Record of picks made in leagues';
COMMENT ON TABLE user_settings IS 'User-specific scoring and strategy settings';
COMMENT ON TABLE leagues IS 'League configuration and settings';