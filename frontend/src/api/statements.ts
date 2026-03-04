import type { Statement } from '../types/index.ts';
import { get, patch } from './client.ts';

export function fetchStatements(accountId?: number): Promise<Statement[]> {
  const qs = accountId ? `?account_id=${accountId}` : '';
  return get<Statement[]>(`/statements${qs}`);
}

export function fetchUnpaidStatements(): Promise<Statement[]> {
  return get<Statement[]>('/statements/unpaid');
}

export function markStatementPaid(id: number): Promise<void> {
  return patch(`/statements/${id}/paid`);
}
