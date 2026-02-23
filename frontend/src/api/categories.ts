import type { Category } from '../types/index.ts';
import { get } from './client.ts';

export function fetchCategories(): Promise<Category[]> {
  return get<Category[]>('/categories');
}
