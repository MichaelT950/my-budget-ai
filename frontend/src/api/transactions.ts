import type { Transaction, TransactionCreate, TransactionUpdate } from '../types/index.ts';
import { get, post, put, del } from './client.ts';

interface TransactionFilters {
  start_date?: string;
  end_date?: string;
  account_id?: number;
}

export function fetchTransactions(filters?: TransactionFilters): Promise<Transaction[]> {
  const params = new URLSearchParams();
  if (filters?.start_date) params.set('start_date', filters.start_date);
  if (filters?.end_date) params.set('end_date', filters.end_date);
  if (filters?.account_id) params.set('account_id', String(filters.account_id));
  const qs = params.toString();
  return get<Transaction[]>(`/transactions${qs ? `?${qs}` : ''}`);
}

export function createTransaction(data: TransactionCreate): Promise<Transaction> {
  return post<Transaction>('/transactions', data);
}

export function updateTransaction(id: number, data: TransactionUpdate): Promise<Transaction> {
  return put<Transaction>(`/transactions/${id}`, data);
}

export function deleteTransaction(id: number): Promise<void> {
  return del(`/transactions/${id}`);
}
