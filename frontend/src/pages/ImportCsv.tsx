import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { previewImport, confirmImport } from '../api/import.ts';
import { fetchAccounts } from '../api/accounts.ts';
import DataTable from '../components/DataTable.tsx';
import type { ImportPreviewTransaction, Account } from '../types/index.ts';
import { formatCurrency, formatDate, formatTransactionType } from '../utils/formatters.ts';

type Step = 'select' | 'preview' | 'done';

export default function ImportCsv() {
  const queryClient = useQueryClient();
  const [step, setStep] = useState<Step>('select');
  const [file, setFile] = useState<File | null>(null);
  const [accountId, setAccountId] = useState<string>('');
  const [preview, setPreview] = useState<ImportPreviewTransaction[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [importedCount, setImportedCount] = useState(0);

  const { data: accounts = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });

  const previewMut = useMutation({
    mutationFn: () => previewImport(file!, parseInt(accountId)),
    onSuccess: (data) => {
      setPreview(data.transactions);
      setErrors(data.errors);
      setStep('preview');
    },
  });

  const confirmMut = useMutation({
    mutationFn: () => confirmImport({ account_id: parseInt(accountId), transactions: preview }),
    onSuccess: (data) => {
      setImportedCount(data.imported_count);
      setStep('done');
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  function handleReset() {
    setStep('select');
    setFile(null);
    setAccountId('');
    setPreview([]);
    setErrors([]);
    setImportedCount(0);
  }

  const previewColumns = [
    { key: 'date', header: 'Date', render: (t: ImportPreviewTransaction) => formatDate(t.date) },
    { key: 'description', header: 'Description', render: (t: ImportPreviewTransaction) => t.description },
    {
      key: 'type', header: 'Type',
      render: (t: ImportPreviewTransaction) => (
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
          t.type === 'expense' ? 'text-red-700 bg-red-50' :
          t.type === 'income' ? 'text-green-700 bg-green-50' : 'text-gray-600 bg-gray-100'
        }`}>
          {formatTransactionType(t.type)}
        </span>
      ),
    },
    {
      key: 'amount', header: 'Amount',
      render: (t: ImportPreviewTransaction) => formatCurrency(t.amount),
      className: 'text-right',
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Import CSV</h2>

      {step === 'select' && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">CSV File</label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Account</label>
              <select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              >
                <option value="">Select account...</option>
                {accounts.map((a: Account) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>
            <button
              onClick={() => previewMut.mutate()}
              disabled={!file || !accountId || previewMut.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {previewMut.isPending ? 'Processing...' : 'Preview'}
            </button>
            {previewMut.isError && (
              <p className="text-red-600 text-sm">Error processing file</p>
            )}
          </div>
        </div>
      )}

      {step === 'preview' && (
        <div>
          {errors.length > 0 && (
            <div className="bg-amber-50 border border-amber-300 rounded-lg p-3 mb-4">
              <p className="text-sm font-medium text-amber-800 mb-1">Warnings:</p>
              {errors.map((err, i) => (
                <p key={i} className="text-xs text-amber-700">{err}</p>
              ))}
            </div>
          )}

          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">{preview.length} transactions to import</p>
            <div className="flex gap-2">
              <button
                onClick={() => confirmMut.mutate()}
                disabled={preview.length === 0 || confirmMut.isPending}
                className="bg-green-600 text-white px-4 py-1.5 rounded text-sm hover:bg-green-700 disabled:opacity-50"
              >
                {confirmMut.isPending ? 'Importing...' : 'Confirm Import'}
              </button>
              <button onClick={handleReset} className="border border-gray-300 px-4 py-1.5 rounded text-sm hover:bg-gray-50">
                Cancel
              </button>
            </div>
          </div>

          <DataTable
            columns={previewColumns}
            data={preview}
            keyFn={(_row, i) => i}
            emptyMessage="No valid transactions found"
          />
        </div>
      )}

      {step === 'done' && (
        <div className="bg-green-50 border border-green-300 rounded-lg p-6 text-center">
          <p className="text-lg font-medium text-green-800">
            Successfully imported {importedCount} transactions
          </p>
          <button
            onClick={handleReset}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
          >
            Import Another
          </button>
        </div>
      )}
    </div>
  );
}
