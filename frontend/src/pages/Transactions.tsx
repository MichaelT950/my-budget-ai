import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchTransactions, updateTransaction, deleteTransaction } from '../api/transactions.ts';
import { fetchAccounts } from '../api/accounts.ts';
import { fetchCategories } from '../api/categories.ts';
import DataTable from '../components/DataTable.tsx';
import type { Transaction, Category, Account } from '../types/index.ts';
import { formatCurrency, formatDate, formatTransactionType } from '../utils/formatters.ts';

const TYPE_COLORS: Record<string, string> = {
  income: 'text-green-700 bg-green-50',
  expense: 'text-red-700 bg-red-50',
  transfer: 'text-gray-600 bg-gray-100',
};

export default function Transactions() {
  const queryClient = useQueryClient();
  const [filterAccountId, setFilterAccountId] = useState<string>('');
  const [search, setSearch] = useState('');

  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['transactions', filterAccountId],
    queryFn: () => fetchTransactions(filterAccountId ? { account_id: parseInt(filterAccountId) } : undefined),
  });

  const { data: accounts = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });
  const { data: categories = [] } = useQuery({ queryKey: ['categories'], queryFn: fetchCategories });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { category_id?: number | null; notes?: string | null } }) =>
      updateTransaction(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  });

  const deleteMut = useMutation({
    mutationFn: deleteTransaction,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['transactions'] }),
  });

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
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Transactions</h2>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          placeholder="Search descriptions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1 max-w-xs"
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
