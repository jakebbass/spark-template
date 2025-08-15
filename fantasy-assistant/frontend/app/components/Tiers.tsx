interface TiersProps {
  players: Array<{
    id: string
    name: string
    position: string
    tier: number
    vorp: number
  }>
  selectedPosition?: string
}

export default function Tiers({ players, selectedPosition }: TiersProps) {
  // Group players by tier
  const playersByTier = players.reduce((acc, player) => {
    if (selectedPosition && player.position !== selectedPosition) {
      return acc
    }
    
    if (!acc[player.tier]) {
      acc[player.tier] = []
    }
    acc[player.tier].push(player)
    return acc
  }, {} as Record<number, typeof players>)

  const tiers = Object.keys(playersByTier)
    .map(Number)
    .sort((a, b) => a - b)

  const tierColors = [
    'bg-purple-100 border-purple-200',
    'bg-blue-100 border-blue-200', 
    'bg-green-100 border-green-200',
    'bg-yellow-100 border-yellow-200',
    'bg-red-100 border-red-200',
    'bg-gray-100 border-gray-200'
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Player Tiers</h3>
        {selectedPosition && (
          <span className="text-sm text-gray-500">Showing {selectedPosition} only</span>
        )}
      </div>

      {tiers.map((tier) => {
        const tierPlayers = playersByTier[tier]
        const colorClass = tierColors[tier - 1] || tierColors[tierColors.length - 1]

        return (
          <div key={tier} className={`border-2 rounded-lg p-4 ${colorClass}`}>
            <h4 className="text-md font-medium text-gray-900 mb-3">
              Tier {tier} ({tierPlayers.length} players)
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {tierPlayers.map((player) => (
                <div
                  key={player.id}
                  className="bg-white rounded-lg p-3 shadow-sm border"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm text-gray-900">{player.name}</p>
                      <p className="text-xs text-gray-500">{player.position}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-medium text-gray-600">
                        VORP: {player.vorp.toFixed(1)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      })}

      {tiers.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No players available for the selected position
        </div>
      )}
    </div>
  )
}