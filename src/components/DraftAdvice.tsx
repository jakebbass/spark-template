import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Player, DraftAdvice } from '@/lib/types';
import { generateDraftAdvice } from '@/lib/draftLogic';
import { Brain, TrendingUp, Users } from '@phosphor-icons/react';
import PlayerCard from './PlayerCard';

interface DraftAdviceProps {
  availablePlayers: Player[];
  userRoster: Player[];
  currentRound: number;
  currentPick: number;
  userTeam: string;
  onDraftPlayer: (player: Player) => void;
}

export default function DraftAdviceComponent({ 
  availablePlayers, 
  userRoster, 
  currentRound, 
  currentPick,
  userTeam,
  onDraftPlayer 
}: DraftAdviceProps) {
  const [advice, setAdvice] = useState<DraftAdvice | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAdvice = async () => {
      setIsLoading(true);
      try {
        const newAdvice = await generateDraftAdvice(
          availablePlayers,
          userRoster,
          currentRound,
          userTeam
        );
        setAdvice(newAdvice);
      } catch (error) {
        console.error('Failed to generate advice:', error);
        // Fallback advice
        const topPlayers = availablePlayers
          .filter(p => !p.isDrafted)
          .sort((a, b) => b.vorp - a.vorp)
          .slice(0, 5);
        
        setAdvice({
          recommendations: topPlayers.map(player => ({
            player,
            reason: `Strong value with ${player.vorp.toFixed(1)} VORP`,
            priority: player.vorp
          })),
          rationale: 'Focus on best available value while considering positional needs.',
          alternatives: []
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAdvice();
  }, [availablePlayers, userRoster, currentRound, userTeam]);

  const positionNeeds = () => {
    const counts = userRoster.reduce((acc, player) => {
      acc[player.position] = (acc[player.position] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const needs = [];
    if ((counts.QB || 0) < 1) needs.push('QB');
    if ((counts.RB || 0) < 2) needs.push('RB');
    if ((counts.WR || 0) < 2) needs.push('WR');
    if ((counts.TE || 0) < 1) needs.push('TE');
    
    return needs;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Draft Advice
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-16 w-full" />
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!advice) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Draft Advice
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Unable to generate advice. Please try again.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            AI Draft Advice
            <Badge variant="outline">Round {currentRound}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-muted/50 p-3 rounded-lg mb-4">
            <p className="text-sm leading-relaxed">{advice.rationale}</p>
          </div>
          
          {positionNeeds().length > 0 && (
            <div className="flex items-center gap-2 mb-4">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Position needs:</span>
              <div className="flex gap-1">
                {positionNeeds().map(pos => (
                  <Badge key={pos} variant="outline" className="text-xs">
                    {pos}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="h-4 w-4" />
            Top Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {advice.recommendations.map((rec, index) => (
            <div key={rec.player.id} className="relative">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-accent text-accent-foreground rounded-full flex items-center justify-center text-xs font-semibold">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <PlayerCard 
                    player={rec.player} 
                    onDraft={onDraftPlayer}
                    isRecommended={index === 0}
                  />
                  <p className="text-xs text-muted-foreground mt-2 px-3">
                    {rec.reason}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {advice.alternatives.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Alternative Options</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {advice.alternatives.map((alt, index) => (
              <div key={alt.player.id} className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <PlayerCard 
                    player={alt.player} 
                    onDraft={onDraftPlayer}
                  />
                  <p className="text-xs text-muted-foreground mt-2 px-3">
                    {alt.reason}
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}