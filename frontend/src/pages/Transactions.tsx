import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchTransactions, createTransaction, updateTransaction, deleteTransaction } from '../api/transactions.ts';
import { fetchAccounts } from '../api/accounts.ts';
import { fetchCategories } from '../api/categories.ts';
import DataTable from '../components/DataTable.tsx';
import type { Transaction, Category, Account, TransactionCreate } from '../types/index.ts';
import { formatCurrency, formatDate, formatTransactionType } from '../utils/formatters.ts';

const TYPE_COLORS: Record<string, string> = {
  income: 'text-green-700 bg-green-50',
  expense: 'text-red-700 bg-red-50',
  transfer: 'text-gray-600 bg-gray-100',
};

const EMPTY_FORM: TransactionCreate = {
  account_id: 0,
  type: 'expense',
  amount: 0,
  description: '',
  category_id: null,
  date: new Date().toISOString().slice(0, 10),
  transfer_to_account_id: null,
  notes: null,
};

export default function Transactions() {
  const queryClient = useQueryClient();
  const [filterAccountId, setFilterAccountId] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<TransactionCreate>({ ...EMPTY_FORM });

  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['transactions', filterAccountId, startDate, endDate],
    queryFn: () => fetchTransactions({
      ...(filterAccountId ? { account_id: parseInt(filterAccountId) } : {}),
      ...(startDate ? { start_date: startDate } : {}),
      ...(endDate ? { end_date: endDate } : {}),
    }),
  });

  const { data: accounts = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  const { data: categories = [] } = useQuery({ queryKey: ['categories'], queryFn: fetchCategories });

  const createMut = useMutation({
    mutationFn: createTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      resetForm();
    },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { category_id?: number | null; notes?: string | null } }) =>
      updateTransaction(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  });

  const deleteMut = useMutation({
    mutationFn: deleteTransaction,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  });

  function resetForm() {
    setForm({ ...EMPTY_FORM });
    setShowForm(false);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload: TransactionCreate = {
      ...form,
      category_id: form.type === 'expense' ? (form.category_id ?? null) : null,
      transfer_to_account_id: form.type === 'transfer' ? (form.transfer_to_account_id ?? null) : null,
    };
    createMut.mutate(payload);
  }

  const accountMap = new Map(accounts.map((a: Account) => [a.id, a]));

  const filtered = search
    ? transactions.filter((t: Transaction) => t.description.toLowerCase().includes(search.toLowerCase()))
    : transactions;

  const columns = [
    {
      key: 'date', header: 'Date',
      render: (t: Transaction) => <span className="text-gray-600">{formatDate(t.date)}</span>,
    },
    {
      key: 'description', header: 'Description',
      render: (t: Transaction) => <span className="font-medium">{t.description}</span>,
    },
    {
      key: 'account', header: 'Account',
      render: (t: Transaction) => accountMap.get(t.account_id)?.name ?? '—',
    },
    {
      key: 'type', header: 'Type',
      render: (t: Transaction) => (
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${TYPE_COLORS[t.type] ?? ''}`}>
          {formatTransactionType(t.type)}
        </span>
      ),
    },
    {
      key: 'category', header: 'Category',
      render: (t: Transaction) => (
          <select
            value={t.category_id ?? ''}
            onChange={(e) => {
              const val = e.target.value ? parseInt(e.target.value) : null;
              updateMut.mutate({ id: t.id, data: { category_id: val } });
            }}
            className="border border-gray-200 rounded px-1.5 py-0.5 text-xs"
          >
            <option value="">—</option>
            {categories.map((c: Category) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
      ),
    },
    {
      key: 'amount', header: 'Amount',
      render: (t: Transaction) => (
        <span className={t.type === 'expense' ? 'text-red-600' : t.type === 'income' ? 'text-green-700' : 'text-gray-600'}>
          {formatCurrency(t.amount)}
        </span>
      ),
      className: 'text-right',
    },
    {
      key: 'notes', header: 'Notes',
      render: (t: Transaction) => (
        <input
          type="text"
          defaultValue={t.notes ?? ''}
          placeholder="Add note..."
          onBlur={(e) => {
            if (e.target.value !== (t.notes ?? '')) {
              updateMut.mutate({ id: t.id, data: { notes: e.target.value || null } });
            }
          }}
          className="border border-gray-200 rounded px-2 py-0.5 text-xs w-full max-w-[140px]"
        />
      ),
    },
    {
      key: 'actions', header: '',
      render: (t: Transaction) => (
        <button
          onClick={() => { if (confirm('Delete this transaction?')) deleteMut.mutate(t.id); }}
          className="text-red-500 hover:text-red-700 text-xs"
        >
          Delete
        </button>
      ),
      className: 'text-right',
    },
  ];

  if (isLoading) return <p className="text-gray-500">Loading transactions...</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Transactions</h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
        >
          {showForm ? 'Cancel' : 'Add Transaction'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-4 mb-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Account</label>
              <select
                required
                value={form.account_id || ''}
                onChange={(e) => setForm({ ...form, account_id: parseInt(e.target.value) })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              >
                <option value="">Select account...</option>
                {accounts.map((a: Account) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm({
                  ...form,
                  type: e.target.value as TransactionCreate['type'],
                  category_id: null,
                  transfer_to_account_id: null,
                })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
                <option value="transfer">Transfer</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Amount</label>
              <input
                type="number"
                required
                min="0.01"
                step="0.01"
                value={form.amount || ''}
                onChange={(e) => setForm({ ...form, amount: parseFloat(e.target.value) || 0 })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Date</label>
              <input
                type="date"
                required
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-600 mb-1">Description</label>
              <input
                type="text"
                required
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            {form.type === 'expense' && (
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Category</label>
                <select
                  value={form.category_id ?? ''}
                  onChange={(e) => setForm({ ...form, category_id: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                >
                  <option value="">— None —</option>
                  {categories.map((c: Category) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}
            {form.type === 'transfer' && (
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Transfer To Account</label>
                <select
                  required
                  value={form.transfer_to_account_id ?? ''}
                  onChange={(e) => setForm({ ...form, transfer_to_account_id: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                >
                  <option value="">Select account...</option>
                  {accounts
                    .filter((a: Account) => a.id !== form.account_id)
                    .map((a: Account) => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                </select>
              </div>
            )}
            <div className={form.type === 'expense' || form.type === 'transfer' ? '' : 'col-span-2'}>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Notes <span className="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={form.notes ?? ''}
                onChange={(e) => setForm({ ...form, notes: e.target.value || null })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
          </div>
          <div className="flex gap-2 items-center">
            <button
              type="submit"
              disabled={createMut.isPending}
              className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {createMut.isPending ? 'Saving...' : 'Create Transaction'}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="border border-gray-300 px-4 py-1.5 rounded text-sm hover:bg-gray-50"
            >
              Cancel
            </button>
            {createMut.isError && (
              <p className="text-red-600 text-sm">Error saving transaction.</p>
            )}
          </div>
        </form>
      )}

      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Search descriptions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1 min-w-[160px] max-w-xs"
        />
        <select
          value={filterAccountId}
          onChange={(e) => setFilterAccountId(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="">All Accounts</option>
          {accounts.map((a: Account) => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
        <div className="flex items-center gap-1.5">
          <label className="text-sm text-gray-500">From</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          />
        </div>
        <div className="flex items-center gap-1.5">
          <label className="text-sm text-gray-500">To</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          />
        </div>
        {(startDate || endDate) && (
          <button
            onClick={() => { setStartDate(''); setEndDate(''); }}
            className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 rounded px-2 py-1"
          >
            Clear dates
          </button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={filtered}
        keyFn={(t) => t.id}
        emptyMessage="No transactions found"
      />
    </div>
  );
}
