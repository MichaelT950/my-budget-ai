import type { ImportPreviewResponse, ImportConfirmRequest, ImportConfirmResponse } from '../types/index.ts';
import { post, postFormData } from './client.ts';

export function previewImport(file: File, accountId: number): Promise<ImportPreviewResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('account_id', String(accountId));
  return postFormData<ImportPreviewResponse>('/import/preview', formData);
}

export function confirmImport(data: ImportConfirmRequest): Promise<ImportConfirmResponse> {
  return post<ImportConfirmResponse>('/import/confirm', data);
}
