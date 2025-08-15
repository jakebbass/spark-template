import { Player } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, Activity, Clock } from '@phosphor-icons/react';

interface PlayerCardProps {
  player: Player;
  onDraft: (player: Player) => void;
  showDraftButton?: boolean;
  isRecommended?: boolean;
}

export default function PlayerCard({ 
  player, 
  onDraft, 
  showDraftButton = true,
  isRecommended = false 
}: PlayerCardProps) {
  const getTierColor = (tier: number) => {
    switch (tier) {
      case 1: return 'bg-green-100 text-green-800 border-green-200';
      case 2: return 'bg-blue-100 text-blue-800 border-blue-200';
      case 3: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 4: return 'bg-orange-100 text-orange-800 border-orange-200';
      case 5: return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getInjuryColor = (status?: string) => {
    switch (status) {
      case 'Healthy': return 'bg-green-100 text-green-800';
      case 'Questionable': return 'bg-yellow-100 text-yellow-800';
      case 'Doubtful': return 'bg-orange-100 text-orange-800';
      case 'Out': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPositionColor = (position: string) => {
    switch (position) {
      case 'QB': return 'bg-purple-100 text-purple-800';
      case 'RB': return 'bg-emerald-100 text-emerald-800';
      case 'WR': return 'bg-blue-100 text-blue-800';
      case 'TE': return 'bg-orange-100 text-orange-800';
      case 'K': return 'bg-pink-100 text-pink-800';
      case 'DST': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${
      player.isDrafted ? 'opacity-50 bg-muted' : ''
    } ${isRecommended ? 'ring-2 ring-accent' : ''}`}>
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-sm truncate">{player.name}</h3>
              {isRecommended && (
                <Badge className="bg-accent text-accent-foreground text-xs">
                  Recommended
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <span>{player.team}</span>
              <span>•</span>
              <span>Bye {player.byeWeek}</span>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge className={getPositionColor(player.position)}>
              {player.position}
            </Badge>
            <Badge variant="outline" className={getTierColor(player.tier)}>
              T{player.tier}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-muted-foreground">ADP:</span>
              <span className="font-medium">{player.adp.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Proj:</span>
              <span className="font-medium">{player.projectedPoints.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">VORP:</span>
              <span className={`font-medium ${player.vorp > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {player.vorp.toFixed(1)}
              </span>
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Floor:</span>
              <div className="flex items-center gap-1">
                <TrendingDown className="h-3 w-3 text-red-500" />
                <span className="font-medium">{player.floor.toFixed(0)}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Ceiling:</span>
              <div className="flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-500" />
                <span className="font-medium">{player.ceiling.toFixed(0)}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Start:</span>
              <div className="flex items-center gap-1">
                <Activity className="h-3 w-3" />
                <span className="font-medium">{player.startableWeeks.length}w</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex gap-1">
            {player.injuryStatus && player.injuryStatus !== 'Healthy' && (
              <Badge variant="outline" className={getInjuryColor(player.injuryStatus)}>
                {player.injuryStatus}
              </Badge>
            )}
            {player.depthRank > 1 && (
              <Badge variant="outline" className="text-xs">
                Depth {player.depthRank}
              </Badge>
            )}
            {player.startableWeeks.includes(1) && player.startableWeeks.includes(2) && (
              <Badge variant="outline" className="text-xs bg-green-50 text-green-700">
                Early Value
              </Badge>
            )}
          </div>

          {showDraftButton && !player.isDrafted && (
            <Button 
              size="sm" 
              onClick={() => onDraft(player)}
              className="ml-2"
            >
              Draft
            </Button>
          )}
          
          {player.isDrafted && (
            <Badge variant="secondary">
              {player.draftedBy} - R{player.draftedRound}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}