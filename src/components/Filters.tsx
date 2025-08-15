import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Player, FilterState, POSITIONS, TEAMS } from '@/lib/types';
import { Filter, X } from '@phosphor-icons/react';

interface FiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  players: Player[];
}

export default function Filters({ filters, onFiltersChange, players }: FiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.position.length > 0) count++;
    if (filters.tier !== null) count++;
    if (filters.byeWeek !== null) count++;
    if (filters.team.length > 0) count++;
    if (filters.availableOnly) count++;
    if (filters.injuryStatus.length > 0) count++;
    return count;
  }, [filters]);

  const clearAllFilters = () => {
    onFiltersChange({
      position: [],
      tier: null,
      byeWeek: null,
      team: [],
      availableOnly: false,
      injuryStatus: []
    });
  };

  const handlePositionChange = (position: string, checked: boolean) => {
    const newPositions = checked
      ? [...filters.position, position]
      : filters.position.filter(p => p !== position);
    onFiltersChange({ ...filters, position: newPositions });
  };

  const handleTeamChange = (team: string, checked: boolean) => {
    const newTeams = checked
      ? [...filters.team, team]
      : filters.team.filter(t => t !== team);
    onFiltersChange({ ...filters, team: newTeams });
  };

  const handleInjuryStatusChange = (status: string, checked: boolean) => {
    const newStatuses = checked
      ? [...filters.injuryStatus, status]
      : filters.injuryStatus.filter(s => s !== status);
    onFiltersChange({ ...filters, injuryStatus: newStatuses });
  };

  return (
    <div className="border-b bg-card p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5" />
          <h3 className="font-semibold">Filters</h3>
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeFilterCount}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          {activeFilterCount > 0 && (
            <Button variant="ghost" size="sm" onClick={clearAllFilters}>
              <X className="h-4 w-4 mr-1" />
              Clear All
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Less' : 'More'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Position</label>
          <div className="flex flex-wrap gap-2">
            {POSITIONS.map(position => (
              <label key={position} className="flex items-center space-x-2 cursor-pointer">
                <Checkbox
                  checked={filters.position.includes(position)}
                  onCheckedChange={(checked) => 
                    handlePositionChange(position, checked as boolean)
                  }
                />
                <span className="text-sm">{position}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Tier</label>
          <Select
            value={filters.tier?.toString() || ''}
            onValueChange={(value) => 
              onFiltersChange({ 
                ...filters, 
                tier: value ? parseInt(value) : null 
              })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Any tier" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Any tier</SelectItem>
              <SelectItem value="1">Tier 1</SelectItem>
              <SelectItem value="2">Tier 2</SelectItem>
              <SelectItem value="3">Tier 3</SelectItem>
              <SelectItem value="4">Tier 4</SelectItem>
              <SelectItem value="5">Tier 5</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Bye Week</label>
          <Select
            value={filters.byeWeek?.toString() || ''}
            onValueChange={(value) => 
              onFiltersChange({ 
                ...filters, 
                byeWeek: value ? parseInt(value) : null 
              })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Any bye" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Any bye</SelectItem>
              {Array.from(new Set(players.map(p => p.byeWeek)))
                .sort((a, b) => a - b)
                .map(week => (
                  <SelectItem key={week} value={week.toString()}>
                    Week {week}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="available-only"
            checked={filters.availableOnly}
            onCheckedChange={(checked) => 
              onFiltersChange({ 
                ...filters, 
                availableOnly: checked as boolean 
              })
            }
          />
          <label htmlFor="available-only" className="text-sm font-medium cursor-pointer">
            Available only
          </label>
        </div>
      </div>

      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <label className="text-sm font-medium mb-2 block">Teams</label>
            <div className="grid grid-cols-4 gap-2 max-h-32 overflow-y-auto">
              {TEAMS.map(team => (
                <label key={team} className="flex items-center space-x-1 cursor-pointer">
                  <Checkbox
                    checked={filters.team.includes(team)}
                    onCheckedChange={(checked) => 
                      handleTeamChange(team, checked as boolean)
                    }
                  />
                  <span className="text-xs">{team}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Injury Status</label>
            <div className="flex flex-col gap-2">
              {['Healthy', 'Questionable', 'Doubtful', 'Out'].map(status => (
                <label key={status} className="flex items-center space-x-2 cursor-pointer">
                  <Checkbox
                    checked={filters.injuryStatus.includes(status)}
                    onCheckedChange={(checked) => 
                      handleInjuryStatusChange(status, checked as boolean)
                    }
                  />
                  <span className="text-sm">{status}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}