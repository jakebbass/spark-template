import { Player, ScoringSettings, DraftAdvice } from './types';

export function calculateFantasyPoints(
  player: Player,
  scoring: ScoringSettings
): number {
  // Base calculation using projections and position-specific multipliers
  const positionMultipliers = {
    QB: { passing: 1.0, rushing: 0.8, receiving: 0 },
    RB: { passing: 0, rushing: 1.0, receiving: 0.7 },
    WR: { passing: 0, rushing: 0.3, receiving: 1.0 },
    TE: { passing: 0, rushing: 0.1, receiving: 0.9 },
    K: { kicking: 1.0 },
    DST: { defense: 1.0 }
  };

  // Simplified calculation - in reality this would use detailed stat projections
  return player.projectedPoints;
}

export function calculateVORP(players: Player[]): Player[] {
  const baselines = {
    QB: 12, // QB12
    RB: 24, // RB24 
    WR: 36, // WR36
    TE: 12, // TE12
    K: 12,   // K12
    DST: 12  // DST12
  };

  const playersByPosition = players.reduce((acc, player) => {
    if (!acc[player.position]) acc[player.position] = [];
    acc[player.position].push(player);
    return acc;
  }, {} as Record<string, Player[]>);

  return players.map(player => {
    const positionPlayers = playersByPosition[player.position]
      .sort((a, b) => b.projectedPoints - a.projectedPoints);
    
    const baselineIndex = baselines[player.position] - 1;
    const baseline = positionPlayers[baselineIndex]?.projectedPoints || 0;
    
    return {
      ...player,
      vorp: player.projectedPoints - baseline
    };
  });
}

export function calculateTiers(players: Player[]): Player[] {
  const playersByPosition = players.reduce((acc, player) => {
    if (!acc[player.position]) acc[player.position] = [];
    acc[player.position].push(player);
    return acc;
  }, {} as Record<string, Player[]>);

  return players.map(player => {
    const positionPlayers = playersByPosition[player.position]
      .sort((a, b) => b.vorp - a.vorp);
    
    const playerIndex = positionPlayers.findIndex(p => p.id === player.id);
    let tier = 1;
    
    // Simple tier calculation based on VORP gaps
    if (player.vorp < 50) tier = 2;
    if (player.vorp < 25) tier = 3;
    if (player.vorp < 10) tier = 4;
    if (player.vorp < 0) tier = 5;
    
    return { ...player, tier };
  });
}

export async function generateDraftAdvice(
  availablePlayers: Player[],
  roster: Player[],
  round: number,
  userTeam: string
): Promise<DraftAdvice> {
  // Analyze roster needs
  const positionCounts = roster.reduce((acc, player) => {
    acc[player.position] = (acc[player.position] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const needs = {
    QB: Math.max(0, 2 - (positionCounts.QB || 0)),
    RB: Math.max(0, 4 - (positionCounts.RB || 0)),
    WR: Math.max(0, 5 - (positionCounts.WR || 0)),
    TE: Math.max(0, 2 - (positionCounts.TE || 0)),
    K: Math.max(0, 1 - (positionCounts.K || 0)),
    DST: Math.max(0, 1 - (positionCounts.DST || 0))
  };

  // Sort available players by value
  const sortedPlayers = availablePlayers
    .filter(p => !p.isDrafted)
    .sort((a, b) => b.vorp - a.vorp);

  // Generate recommendations based on value + need
  const recommendations = sortedPlayers
    .slice(0, 10)
    .map(player => {
      let priority = player.vorp;
      let reason = `Elite value with ${player.vorp.toFixed(1)} VORP`;

      // Boost priority for positions of need
      if (needs[player.position] > 0) {
        priority += 20;
        reason = `Fills ${player.position} need with strong ${player.vorp.toFixed(1)} VORP`;
      }

      // Early round considerations
      if (round <= 3 && player.tier > 2) {
        priority -= 30;
        reason = `High-upside pick but consider tier ${player.tier} risk`;
      }

      // Injury concerns
      if (player.injuryStatus && player.injuryStatus !== 'Healthy') {
        priority -= 15;
        reason += `. Monitor ${player.injuryStatus.toLowerCase()} status`;
      }

      return { player, reason, priority };
    })
    .sort((a, b) => b.priority - a.priority)
    .slice(0, 5);

  // Generate rationale using LLM
  const topPick = recommendations[0];
  let rationale = '';
  
  try {
    if (window.spark?.llm) {
      const prompt = spark.llmPrompt`You are a fantasy football expert. Based on this draft situation, explain why ${topPick.player.name} (${topPick.player.position}, ${topPick.player.team}) is the best pick right now. Current roster: ${roster.map(p => `${p.name} (${p.position})`).join(', ')}. Round ${round}. Keep it to 2 sentences max and focus on value and roster construction.`;
      
      rationale = await spark.llm(prompt, 'gpt-4o-mini');
    } else {
      rationale = `${topPick.player.name} offers excellent value at pick ${round} with ${topPick.player.vorp.toFixed(1)} VORP. This addresses your ${topPick.player.position} needs while maintaining strong upside potential.`;
    }
  } catch (error) {
    rationale = `${topPick.player.name} offers excellent value at pick ${round} with ${topPick.player.vorp.toFixed(1)} VORP. This addresses your ${topPick.player.position} needs while maintaining strong upside potential.`;
  }

  // Generate alternatives
  const alternatives = recommendations.slice(1, 3).map(rec => ({
    player: rec.player,
    reason: `Alternative: ${rec.reason.split('.')[0]}`
  }));

  return {
    recommendations,
    rationale,
    alternatives
  };
}