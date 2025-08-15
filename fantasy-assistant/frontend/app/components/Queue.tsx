import { StarIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid'

interface QueueProps {
  queuedPlayers: Array<{
    id: string
    name: string
    position: string
    team: string
    vorp: number
    rank: number
  }>
  onRemoveFromQueue: (playerId: string) => void
  onReorderQueue: (fromIndex: number, toIndex: number) => void
}

export default function Queue({ queuedPlayers, onRemoveFromQueue, onReorderQueue }: QueueProps) {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">My Draft Queue</h3>
          <span className="text-sm text-gray-500">{queuedPlayers.length} players</span>
        </div>

        {queuedPlayers.length === 0 ? (
          <div className="text-center py-8">
            <StarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No players in your queue</p>
            <p className="text-sm text-gray-400 mt-1">
              Add players to track your draft targets
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {queuedPlayers.map((player, index) => (
              <div
                key={player.id}
                className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-gray-300"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                    <StarSolidIcon className="h-4 w-4 text-yellow-500" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{player.name}</p>
                    <p className="text-sm text-gray-500">
                      {player.position} • {player.team} • VORP: {player.vorp.toFixed(1)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {/* Move up button */}
                  {index > 0 && (
                    <button
                      onClick={() => onReorderQueue(index, index - 1)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Move up"
                    >
                      ↑
                    </button>
                  )}

                  {/* Move down button */}
                  {index < queuedPlayers.length - 1 && (
                    <button
                      onClick={() => onReorderQueue(index, index + 1)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Move down"
                    >
                      ↓
                    </button>
                  )}

                  {/* Remove button */}
                  <button
                    onClick={() => onRemoveFromQueue(player.id)}
                    className="p-1 text-red-400 hover:text-red-600"
                    title="Remove from queue"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {queuedPlayers.length > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Pro tip:</strong> Your queue helps you stay organized during fast drafts.
              The AI will consider your queue when giving recommendations.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}