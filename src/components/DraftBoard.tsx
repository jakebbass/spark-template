import { Player, DraftPick } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Trophy } from '@phosphor-icons/react';

interface DraftBoardProps {
  draftPicks: DraftPick[];
  teamNames: Record<string, string>;
  userTeam: string;
}

export default function DraftBoard({ draftPicks, teamNames, userTeam }: DraftBoardProps) {
  const currentRound = Math.max(1, Math.floor((draftPicks.filter(p => p.player).length) / 12) + 1);
  const rounds = Array.from({ length: Math.min(currentRound + 2, 16) }, (_, i) => i + 1);
  
  const getPicksForRound = (round: number) => {
    const startPick = (round - 1) * 12;
    return draftPicks.slice(startPick, startPick + 12);
  };

  const getTeamColor = (team: string) => {
    if (team === userTeam) return 'bg-accent/20 border-accent';
    return 'bg-card border-border';
  };

  const isCurrentPick = (pick: DraftPick) => {
    return !pick.player && pick.pick === draftPicks.filter(p => p.player).length + 1;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          Draft Board
          <Badge variant="outline">Round {currentRound}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {rounds.map(round => (
            <div key={round} className="space-y-2">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-semibold">Round {round}</h4>
                {round === currentRound && (
                  <Badge className="bg-green-100 text-green-800">
                    Current
                  </Badge>
                )}
              </div>
              
              <div className="grid grid-cols-1 gap-2">
                {getPicksForRound(round).map((pick) => (
                  <div
                    key={`${round}-${pick.pick}`}
                    className={`
                      p-3 rounded-lg border transition-colors
                      ${getTeamColor(pick.team)}
                      ${isCurrentPick(pick) ? 'ring-2 ring-accent animate-pulse' : ''}
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {pick.pick}
                        </Badge>
                        <span className="text-sm font-medium truncate">
                          {teamNames[pick.team] || pick.team}
                        </span>
                        {pick.team === userTeam && (
                          <Trophy className="h-4 w-4 text-accent" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0 ml-4">
                        {pick.player ? (
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="font-semibold truncate">
                                {pick.player.name}
                              </span>
                              <Badge className="text-xs bg-secondary">
                                {pick.player.position}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {pick.player.team}
                              </span>
                            </div>
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <span>{pick.player.projectedPoints.toFixed(0)} pts</span>
                              <span>•</span>
                              <span className={pick.player.vorp > 0 ? 'text-green-600' : 'text-red-600'}>
                                {pick.player.vorp > 0 ? '+' : ''}{pick.player.vorp.toFixed(1)} VORP
                              </span>
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between">
                            {isCurrentPick(pick) ? (
                              <span className="text-accent font-medium">
                                On the Clock
                              </span>
                            ) : (
                              <span className="text-muted-foreground italic">
                                Upcoming pick
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}