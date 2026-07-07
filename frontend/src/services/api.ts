// API client for SkillSync backend

import { MatchPreferences, MatchResponse, Options } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  async getHealth() {
    return fetchApi<{ status: string }>('/api/health');
  },

  async getOptions(): Promise<Options> {
    return fetchApi<Options>('/api/options');
  },

  async findMatches(preferences: MatchPreferences): Promise<MatchResponse> {
    return fetchApi<MatchResponse>('/api/matches', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  },
};

export { ApiError };
