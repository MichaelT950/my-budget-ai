import type { DashboardResponse } from '../types/index.ts';
import { get } from './client.ts';

export function fetchDashboard(): Promise<DashboardResponse> {
  return get<DashboardResponse>('/dashboard');
}
