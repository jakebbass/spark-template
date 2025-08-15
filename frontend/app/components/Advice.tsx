import { LightBulbIcon, ChartBarIcon, ClockIcon } from '@heroicons/react/24/outline'

interface AdviceProps {
  recommendations: Array<{
    player: {
      name: string
      position: string
      team: string
      vorp: number
    }
    reason: string
    priority: number
  }>
  rationale: string
  exposureWarnings?: string[]
  opponentPredictions?: Array<{
    player: {
      name: string
      position: string
    }
    probability: number
  }>
}

export default function Advice({ 
  recommendations, 
  rationale, 
  exposureWarnings = [],
  opponentPredictions = []
}: AdviceProps) {
  return (
    <div className="space-y-6">
      {/* Main Rationale */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <LightBulbIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-medium text-blue-900">AI Recommendation</h3>
            <p className="mt-2 text-blue-800">{rationale}</p>
          </div>
        </div>
      </div>

      {/* Top Recommendations */}
      <div>
        <h4 className="text-md font-medium text-gray-900 mb-3">Top 5 Picks</h4>
        <div className="space-y-3">
          {recommendations.slice(0, 5).map((rec, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center font-medium">
                  {index + 1}
                </span>
                <div>
                  <p className="font-medium text-gray-900">{rec.player.name}</p>
                  <p className="text-sm text-gray-500">
                    {rec.player.position} • {rec.player.team} • VORP: {rec.player.vorp.toFixed(1)}
                  </p>
                  <p className="text-sm text-blue-600 mt-1">{rec.reason}</p>
                </div>
              </div>
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
            </div>
          ))}
        </div>
      </div>

      {/* Exposure Warnings */}
      {exposureWarnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="text-md font-medium text-yellow-900 mb-2">Exposure Warnings</h4>
          <ul className="text-sm text-yellow-800 space-y-1">
            {exposureWarnings.map((warning, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 bg-yellow-600 rounded-full mr-2 flex-shrink-0"></span>
                {warning}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Opponent Predictions */}
      {opponentPredictions.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <ClockIcon className="h-5 w-5 text-red-600 mr-2" />
            <h4 className="text-md font-medium text-red-900">Likely Gone Before Your Next Pick</h4>
          </div>
          <div className="space-y-2">
            {opponentPredictions.map((pred, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-red-800">
                  {pred.player.name} ({pred.player.position})
                </span>
                <span className="text-sm font-medium text-red-700">
                  {Math.round(pred.probability * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}