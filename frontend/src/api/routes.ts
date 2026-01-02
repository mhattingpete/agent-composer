export const APIRoutes = {
  // Use our combined endpoints that include both built-in and custom agents/teams
  // The AgentOS /agents and /teams endpoints only know about startup-time entities
  GetAgents: (agentOSUrl: string) => `${agentOSUrl}/config/all-agents`,

  // Agent run endpoints - use config endpoint for dynamic loading
  // This works for both built-in and custom agents
  AgentRun: (agentOSUrl: string, agentId: string) =>
    `${agentOSUrl}/config/agents/${agentId}/runs`,

  Status: (agentOSUrl: string) => `${agentOSUrl}/health`,
  GetSessions: (agentOSUrl: string) => `${agentOSUrl}/sessions`,
  GetSession: (agentOSUrl: string, sessionId: string) =>
    `${agentOSUrl}/sessions/${sessionId}/runs`,

  DeleteSession: (agentOSUrl: string, sessionId: string) =>
    `${agentOSUrl}/sessions/${sessionId}`,

  GetTeams: (agentOSUrl: string) => `${agentOSUrl}/config/all-teams`,

  // Team run endpoints - use config endpoint for dynamic loading
  TeamRun: (agentOSUrl: string, teamId: string) =>
    `${agentOSUrl}/config/teams/${teamId}/runs`,
  DeleteTeamSession: (agentOSUrl: string, teamId: string, sessionId: string) =>
    `${agentOSUrl}/v1//teams/${teamId}/sessions/${sessionId}`,

  // Config endpoints
  GetModels: (agentOSUrl: string) => `${agentOSUrl}/config/models`,
  GetCustomAgents: (agentOSUrl: string) => `${agentOSUrl}/config/agents`,
  CreateAgent: (agentOSUrl: string) => `${agentOSUrl}/config/agents`,
  UpdateAgent: (agentOSUrl: string, agentId: string) =>
    `${agentOSUrl}/config/agents/${agentId}`,
  DeleteAgent: (agentOSUrl: string, agentId: string) =>
    `${agentOSUrl}/config/agents/${agentId}`,
  GetCustomTeams: (agentOSUrl: string) => `${agentOSUrl}/config/teams`,
  CreateTeam: (agentOSUrl: string) => `${agentOSUrl}/config/teams`,
  UpdateTeam: (agentOSUrl: string, teamId: string) =>
    `${agentOSUrl}/config/teams/${teamId}`,
  DeleteTeam: (agentOSUrl: string, teamId: string) =>
    `${agentOSUrl}/config/teams/${teamId}`
}
