/**
 * Frontend configuration loaded from environment variables.
 */
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  appName: 'Agent Composer',
  version: '0.1.0',
} as const
