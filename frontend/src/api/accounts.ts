import type { Account, AccountCreate, AccountUpdate } from '../types/index.ts';
import { get, post, put, del } from './client.ts';

export function fetchAccounts(): Promise<Account[]> {
  return get<Account[]>('/accounts');
}

export function fetchAccount(id: number): Promise<Account> {
  return get<Account>(`/accounts/${id}`);
}

export function createAccount(data: AccountCreate): Promise<Account> {
  return post<Account>('/accounts', data);
}

export function updateAccount(id: number, data: AccountUpdate): Promise<Account> {
  return put<Account>(`/accounts/${id}`, data);
}

export function deleteAccount(id: number): Promise<void> {
  return del(`/accounts/${id}`);
}
