interface BoardProps {
  players: Array<{
    id: string
    name: string
    team: string
    position: string
    vorp: number
    tier: number
  }>
  onPlayerSelect: (playerId: string) => void
}

export default function Board({ players, onPlayerSelect }: BoardProps) {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Draft Board</h3>
        <div className="mt-5">
          <div className="grid grid-cols-1 gap-4">
            {players.map((player) => (
              <div
                key={player.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 cursor-pointer"
                onClick={() => onPlayerSelect(player.id)}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <span className="inline-flex items-center justify-center h-10 w-10 rounded-full bg-gray-500 text-white text-sm font-medium">
                      {player.position}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{player.name}</p>
                    <p className="text-sm text-gray-500">{player.team}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">VORP: {player.vorp.toFixed(1)}</p>
                  <p className="text-sm text-gray-500">Tier {player.tier}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}