import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface FiltersProps {
  filters: {
    position: string[]
    tier: number | null
    byeWeek: number | null
    team: string[]
    availableOnly: boolean
    injuryStatus: string[]
  }
  onFilterChange: (filters: any) => void
}

export default function Filters({ filters, onFilterChange }: FiltersProps) {
  const positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']
  const tiers = [1, 2, 3, 4, 5, 6]
  const byeWeeks = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
  const injuryStatuses = ['Healthy', 'Questionable', 'Doubtful', 'Out']

  const hasActiveFilters = 
    filters.position.length > 0 ||
    filters.tier !== null ||
    filters.byeWeek !== null ||
    filters.team.length > 0 ||
    filters.injuryStatus.length > 0

  const clearAllFilters = () => {
    onFilterChange({
      position: [],
      tier: null,
      byeWeek: null,
      team: [],
      availableOnly: filters.availableOnly,
      injuryStatus: []
    })
  }

  const togglePosition = (pos: string) => {
    const newPositions = filters.position.includes(pos)
      ? filters.position.filter(p => p !== pos)
      : [...filters.position, pos]
    onFilterChange({ ...filters, position: newPositions })
  }

  const toggleInjuryStatus = (status: string) => {
    const newStatuses = filters.injuryStatus.includes(status)
      ? filters.injuryStatus.filter(s => s !== status)
      : [...filters.injuryStatus, status]
    onFilterChange({ ...filters, injuryStatus: newStatuses })
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <FunnelIcon className="h-5 w-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Filters</h3>
          </div>
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
            >
              <XMarkIcon className="h-4 w-4 mr-1" />
              Clear all
            </button>
          )}
        </div>

        <div className="space-y-4">
          {/* Available Only Toggle */}
          <div className="flex items-center">
            <input
              id="available-only"
              type="checkbox"
              checked={filters.availableOnly}
              onChange={(e) => onFilterChange({ ...filters, availableOnly: e.target.checked })}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="available-only" className="ml-2 text-sm text-gray-900">
              Available players only
            </label>
          </div>

          {/* Position Filter */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">Position</label>
            <div className="flex flex-wrap gap-2">
              {positions.map((pos) => (
                <button
                  key={pos}
                  onClick={() => togglePosition(pos)}
                  className={`px-3 py-1 rounded-full text-sm font-medium border ${
                    filters.position.includes(pos)
                      ? 'bg-blue-100 text-blue-800 border-blue-200'
                      : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200'
                  }`}
                >
                  {pos}
                </button>
              ))}
            </div>
          </div>

          {/* Tier Filter */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">Tier</label>
            <select
              value={filters.tier || ''}
              onChange={(e) => onFilterChange({ 
                ...filters, 
                tier: e.target.value ? parseInt(e.target.value) : null 
              })}
              className="w-full rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All tiers</option>
              {tiers.map((tier) => (
                <option key={tier} value={tier}>
                  Tier {tier}
                </option>
              ))}
            </select>
          </div>

          {/* Bye Week Filter */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">Bye Week</label>
            <select
              value={filters.byeWeek || ''}
              onChange={(e) => onFilterChange({ 
                ...filters, 
                byeWeek: e.target.value ? parseInt(e.target.value) : null 
              })}
              className="w-full rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All weeks</option>
              {byeWeeks.map((week) => (
                <option key={week} value={week}>
                  Week {week}
                </option>
              ))}
            </select>
          </div>

          {/* Injury Status Filter */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">Health Status</label>
            <div className="space-y-2">
              {injuryStatuses.map((status) => (
                <div key={status} className="flex items-center">
                  <input
                    id={`injury-${status}`}
                    type="checkbox"
                    checked={filters.injuryStatus.includes(status)}
                    onChange={() => toggleInjuryStatus(status)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor={`injury-${status}`} className="ml-2 text-sm text-gray-900">
                    {status}
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}