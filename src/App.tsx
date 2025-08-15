import { useState, useMemo, useEffect } from 'react';
import { useKV } from '@github/spark/hooks';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

import { Player, DraftPick, FilterState } from '@/lib/types';
import { mockPlayers, TEAM_NAMES, generateDraftOrder } from '@/lib/mockData';
import { calculateVORP, calculateTiers } from '@/lib/draftLogic';

import Filters from '@/components/Filters';
import PlayerCard from '@/components/PlayerCard';
import DraftAdvice from '@/components/DraftAdvice';
import DraftBoard from '@/components/DraftBoard';

import { TrendingUp, Users, Brain, Search, RotateCcw } from '@phosphor-icons/react';

function App() {
  // Persistent state
  const [players, setPlayers] = useKV('draft-players', calculateTiers(calculateVORP(mockPlayers)));
  const [draftPicks, setDraftPicks] = useKV('draft-picks', generateDraftOrder());
  const [userTeam, setUserTeam] = useKV('user-team', 'Team 1');
  
  // Local state
  const [filters, setFilters] = useState<FilterState>({
    position: [],
    tier: null,
    byeWeek: null,
    team: [],
    availableOnly: true,
    injuryStatus: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'vorp' | 'adp' | 'projectedPoints' | 'ceiling'>('vorp');

  // Computed values
  const currentPick = draftPicks.findIndex(pick => !pick.player);
  const currentPickNumber = currentPick >= 0 ? currentPick + 1 : draftPicks.length + 1;
  const currentRound = Math.ceil(currentPickNumber / 12);
  const userRoster = players.filter(p => p.isDrafted && p.draftedBy === userTeam);
  
  const availablePlayers = useMemo(() => {
    let filtered = players.filter(player => {
      if (filters.availableOnly && player.isDrafted) return false;
      if (filters.position.length > 0 && !filters.position.includes(player.position)) return false;
      if (filters.tier !== null && player.tier !== filters.tier) return false;
      if (filters.byeWeek !== null && player.byeWeek !== filters.byeWeek) return false;
      if (filters.team.length > 0 && !filters.team.includes(player.team)) return false;
      if (filters.injuryStatus.length > 0 && !filters.injuryStatus.includes(player.injuryStatus || 'Healthy')) return false;
      if (searchQuery && !player.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      
      return true;
    });

    // Sort players
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'adp':
          return a.adp - b.adp;
        case 'projectedPoints':
          return b.projectedPoints - a.projectedPoints;
        case 'ceiling':
          return b.ceiling - a.ceiling;
        case 'vorp':
        default:
          return b.vorp - a.vorp;
      }
    });

    return filtered;
  }, [players, filters, searchQuery, sortBy]);

  const handleDraftPlayer = (player: Player) => {
    if (player.isDrafted) {
      toast.error('Player already drafted!');
      return;
    }

    const currentPickData = draftPicks.find(pick => !pick.player);
    if (!currentPickData) {
      toast.error('Draft is complete!');
      return;
    }

    // Update player
    const updatedPlayers = players.map(p => 
      p.id === player.id 
        ? { 
            ...p, 
            isDrafted: true, 
            draftedBy: currentPickData.team, 
            draftedRound: currentPickData.round,
            draftedPick: currentPickData.pick
          }
        : p
    );

    // Update draft pick
    const updatedDraftPicks = draftPicks.map(pick => 
      pick.pick === currentPickData.pick 
        ? { ...pick, player: { ...player, isDrafted: true, draftedBy: currentPickData.team } }
        : pick
    );

    setPlayers(updatedPlayers);
    setDraftPicks(updatedDraftPicks);

    toast.success(`${player.name} drafted by ${TEAM_NAMES[currentPickData.team] || currentPickData.team}!`);
  };

  const resetDraft = () => {
    const resetPlayers = mockPlayers.map(p => ({ ...p, isDrafted: false, draftedBy: undefined, draftedRound: undefined, draftedPick: undefined }));
    setPlayers(calculateTiers(calculateVORP(resetPlayers)));
    setDraftPicks(generateDraftOrder());
    toast.success('Draft reset successfully!');
  };

  const isUserPick = () => {
    const currentPickData = draftPicks.find(pick => !pick.player);
    return currentPickData?.team === userTeam;
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Fantasy Draft Assistant</h1>
              <p className="text-muted-foreground mt-1">
                AI-powered draft analysis and recommendations
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Your Team</div>
                <Select value={userTeam} onValueChange={setUserTeam}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(TEAM_NAMES).map(([key, name]) => (
                      <SelectItem key={key} value={key}>
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button variant="outline" onClick={resetDraft}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset Draft
              </Button>
            </div>
          </div>
          
          <div className="mt-4 flex items-center gap-4">
            <Badge variant="outline" className="text-sm">
              Round {currentRound} • Pick {currentPickNumber}
            </Badge>
            {isUserPick() && (
              <Badge className="bg-accent text-accent-foreground animate-pulse">
                Your Pick!
              </Badge>
            )}
            <Badge variant="secondary">
              {userRoster.length}/16 players drafted
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="rankings" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="rankings" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Rankings
            </TabsTrigger>
            <TabsTrigger value="draft-board" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Draft Board
            </TabsTrigger>
            <TabsTrigger value="advice" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              AI Advice
            </TabsTrigger>
            <TabsTrigger value="roster" className="flex items-center gap-2">
              Your Roster ({userRoster.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="rankings" className="space-y-6">
            <Filters 
              filters={filters} 
              onFiltersChange={setFilters}
              players={players}
            />
            
            <div className="flex items-center gap-4 mb-6">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search players..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vorp">Sort by VORP</SelectItem>
                  <SelectItem value="adp">Sort by ADP</SelectItem>
                  <SelectItem value="projectedPoints">Sort by Projection</SelectItem>
                  <SelectItem value="ceiling">Sort by Ceiling</SelectItem>
                </SelectContent>
              </Select>
              
              <div className="text-sm text-muted-foreground">
                {availablePlayers.length} players shown
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {availablePlayers.map(player => (
                <PlayerCard
                  key={player.id}
                  player={player}
                  onDraft={handleDraftPlayer}
                />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="draft-board">
            <DraftBoard 
              draftPicks={draftPicks}
              teamNames={TEAM_NAMES}
              userTeam={userTeam}
            />
          </TabsContent>

          <TabsContent value="advice">
            {isUserPick() ? (
              <DraftAdvice
                availablePlayers={availablePlayers}
                userRoster={userRoster}
                currentRound={currentRound}
                currentPick={currentPickNumber}
                userTeam={userTeam}
                onDraftPlayer={handleDraftPlayer}
              />
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">Waiting for Your Turn</h3>
                    <p className="text-muted-foreground mb-4">
                      AI advice will be available when it's your pick
                    </p>
                    <Badge variant="outline">
                      Next pick: {draftPicks.find(p => !p.player)?.team && TEAM_NAMES[draftPicks.find(p => !p.player)!.team]}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="roster">
            <Card>
              <CardHeader>
                <CardTitle>Your Roster - {TEAM_NAMES[userTeam]}</CardTitle>
              </CardHeader>
              <CardContent>
                {userRoster.length === 0 ? (
                  <div className="text-center py-8">
                    <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No players drafted yet</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {userRoster
                      .sort((a, b) => (a.draftedPick || 0) - (b.draftedPick || 0))
                      .map(player => (
                        <PlayerCard
                          key={player.id}
                          player={player}
                          onDraft={() => {}}
                          showDraftButton={false}
                        />
                      ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;