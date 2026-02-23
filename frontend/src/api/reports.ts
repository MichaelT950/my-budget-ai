import type { CashFlowResponse, BalanceSheetResponse, PeriodSummaryResponse } from '../types/index.ts';
import { get } from './client.ts';

export function fetchCashFlow(startDate: string, endDate: string, accountId?: number): Promise<CashFlowResponse> {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
  if (accountId) params.set('account_id', String(accountId));
  return get<CashFlowResponse>(`/reports/cash-flow?${params}`);
}

export function fetchBalanceSheet(): Promise<BalanceSheetResponse> {
  return get<BalanceSheetResponse>('/reports/balance-sheet');
}

export function fetchPeriodSummary(startDate: string, endDate: string): Promise<PeriodSummaryResponse> {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
  return get<PeriodSummaryResponse>(`/reports/period-summary?${params}`);
}
