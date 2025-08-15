#!/bin/bash

# Database seeding script
set -e

echo "🌱 Seeding database with sample data..."

# Check if we're running in Docker or local environment
if [ -n "$DOCKER_DB_HOST" ]; then
    DB_HOST="$DOCKER_DB_HOST"
else
    DB_HOST="localhost"
fi

POSTGRES_URL="postgresql://postgres:postgres@${DB_HOST}:5432/fantasy"

echo "📊 Connecting to database at ${DB_HOST}..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h "$DB_HOST" -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Create sample data directory if it doesn't exist
DATA_DIR="../backend/data"
mkdir -p "$DATA_DIR"

# Generate sample player data if it doesn't exist
if [ ! -f "$DATA_DIR/players.csv" ]; then
    echo "📄 Generating sample player data..."
    cat > "$DATA_DIR/players.csv" << 'EOF'
name,team,position,bye_week,age,height,weight
Josh Allen,BUF,QB,7,28,6-5,237
Lamar Jackson,BAL,QB,14,27,6-2,212
Patrick Mahomes,KC,QB,10,29,6-3,230
Joe Burrow,CIN,QB,12,27,6-4,221
Tua Tagovailoa,MIA,QB,6,26,6-1,217
Christian McCaffrey,SF,RB,9,28,5-11,205
Austin Ekeler,LAC,RB,5,29,5-10,200
Derrick Henry,TEN,RB,7,30,6-3,247
Jonathan Taylor,IND,RB,14,25,5-10,226
Saquon Barkley,NYG,RB,11,27,6-0,233
Cooper Kupp,LAR,WR,7,31,6-2,208
Davante Adams,LV,WR,6,32,6-1,215
Tyreek Hill,MIA,WR,6,30,5-10,185
Stefon Diggs,BUF,WR,7,31,6-0,191
DeAndre Hopkins,ARI,WR,13,32,6-1,212
Travis Kelce,KC,TE,10,35,6-5,260
Mark Andrews,BAL,TE,14,29,6-5,256
George Kittle,SF,TE,9,31,6-4,249
Darren Waller,LV,TE,6,32,6-6,255
T.J. Hockenson,DET,TE,6,27,6-5,248
EOF
fi

# Generate sample projections if they don't exist
if [ ! -f "$DATA_DIR/projections.csv" ]; then
    echo "📄 Generating sample projection data..."
    cat > "$DATA_DIR/projections.csv" << 'EOF'
player_name,season,source,pass_yd,pass_td,int,rush_yd,rush_td,rec,rec_yd,rec_td,fumble,fantasy_points
Josh Allen,2024,FantasyPros,4200,32,12,800,8,0,0,0,4,285.2
Lamar Jackson,2024,FantasyPros,3500,24,8,950,6,0,0,0,3,265.4
Patrick Mahomes,2024,FantasyPros,4800,38,10,300,2,0,0,0,2,298.6
Christian McCaffrey,2024,FantasyPros,0,0,0,1400,12,90,800,4,2,312.0
Austin Ekeler,2024,FantasyPros,0,0,0,950,8,85,650,6,1,265.5
Cooper Kupp,2024,FantasyPros,0,0,0,0,0,120,1650,14,0,324.0
Davante Adams,2024,FantasyPros,0,0,0,0,0,110,1500,12,0,293.0
Travis Kelce,2024,FantasyPros,0,0,0,0,0,95,1200,9,0,273.5
EOF
fi

# Run Python seeding script
echo "🐍 Running Python seeding script..."

# Create a simple Python seeding script
cat > "$DATA_DIR/seed.py" << 'EOF'
import asyncio
import csv
import uuid
from datetime import datetime
import asyncpg
import os

async def seed_database():
    """Seed the database with sample data."""
    db_url = os.getenv('POSTGRES_URL', 'postgresql://postgres:postgres@localhost:5432/fantasy')
    
    # Replace postgresql+asyncpg:// with postgresql://
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    conn = await asyncpg.connect(db_url)
    
    try:
        # Clear existing data
        print("🧹 Clearing existing data...")
        await conn.execute("DELETE FROM draft_picks")
        await conn.execute("DELETE FROM projections")
        await conn.execute("DELETE FROM historical_stats") 
        await conn.execute("DELETE FROM depth_charts")
        await conn.execute("DELETE FROM injuries")
        await conn.execute("DELETE FROM adp")
        await conn.execute("DELETE FROM players")
        
        # Seed players
        print("👤 Seeding players...")
        with open('players.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                await conn.execute("""
                    INSERT INTO players (id, name, team, position, bye_week, age, height, weight, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, 
                str(uuid.uuid4()),
                row['name'],
                row['team'],
                row['position'],
                int(row['bye_week']),
                int(row['age']),
                row['height'],
                int(row['weight']),
                datetime.utcnow()
                )
        
        # Seed projections (linking by name for simplicity)
        print("📈 Seeding projections...")
        with open('projections.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get player ID by name
                player_id = await conn.fetchval(
                    "SELECT id FROM players WHERE name = $1", 
                    row['player_name']
                )
                
                if player_id:
                    stats = {
                        k: float(v) if v else 0 
                        for k, v in row.items() 
                        if k not in ['player_name', 'season', 'source']
                    }
                    
                    await conn.execute("""
                        INSERT INTO projections (id, player_id, season, source, stats, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    str(uuid.uuid4()),
                    player_id,
                    int(row['season']),
                    row['source'],
                    stats,
                    datetime.utcnow()
                    )
        
        # Add sample ADP data
        print("📊 Seeding ADP data...")
        players = await conn.fetch("SELECT id, name, position FROM players ORDER BY name")
        for i, player in enumerate(players):
            await conn.execute("""
                INSERT INTO adp (id, player_id, platform, adp, sample_size, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
            str(uuid.uuid4()),
            player['id'],
            'sleeper',
            float(i + 1),  # Simple sequential ADP
            100,
            datetime.utcnow()
            )
        
        # Add sample injury data (all healthy for now)
        print("🏥 Seeding injury data...")
        for player in players:
            await conn.execute("""
                INSERT INTO injuries (id, player_id, status, note, updated_at)
                VALUES ($1, $2, $3, $4, $5)
            """,
            str(uuid.uuid4()),
            player['id'],
            'Healthy',
            None,
            datetime.utcnow()
            )
        
        print("✅ Database seeded successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
EOF

# Install required Python package if not already installed
pip install asyncpg || echo "asyncpg already installed or pip not available"

# Set environment variable for database connection
export POSTGRES_URL="postgresql://postgres:postgres@${DB_HOST}:5432/fantasy"

# Run the seeding script
cd "$DATA_DIR"
python seed.py

echo "✅ Database seeding completed!"