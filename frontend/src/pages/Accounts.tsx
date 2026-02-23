import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchAccounts, createAccount, updateAccount, deleteAccount } from '../api/accounts.ts';
import DataTable from '../components/DataTable.tsx';
import type { Account, AccountCreate } from '../types/index.ts';
import { formatCurrency, formatAccountType } from '../utils/formatters.ts';

const EMPTY_FORM: AccountCreate = {
  name: '',
  type: 'checking',
  starting_balance: 0,
  credit_limit: null,
  statement_close_day: null,
  payment_due_day: null,
};

export default function Accounts() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<AccountCreate>({ ...EMPTY_FORM });

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
  });

  const createMut = useMutation({
    mutationFn: createAccount,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['accounts'] }); resetForm(); },
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AccountCreate }) => updateAccount(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['accounts'] }); resetForm(); },
  });

  const deleteMut = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  });

  function resetForm() {
    setForm({ ...EMPTY_FORM });
    setShowForm(false);
    setEditingId(null);
  }

  function startEdit(account: Account) {
    setForm({
      name: account.name,
      type: account.type,
      starting_balance: account.starting_balance,
      credit_limit: account.credit_limit,
      statement_close_day: account.statement_close_day,
      payment_due_day: account.payment_due_day,
    });
    setEditingId(account.id);
    setShowForm(true);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (editingId) {
      updateMut.mutate({ id: editingId, data: form });
    } else {
      createMut.mutate(form);
    }
  }

  const columns = [
    { key: 'name', header: 'Name', render: (a: Account) => <span className="font-medium">{a.name}</span> },
    { key: 'type', header: 'Type', render: (a: Account) => formatAccountType(a.type) },
    {
      key: 'balance',
      header: 'Balance',
      render: (a: Account) => (
        <span className={a.type === 'credit_card' ? 'text-red-600' : 'text-green-700'}>
          {formatCurrency(a.balance ?? 0)}
        </span>
      ),
      className: 'text-right',
    },
    {
      key: 'actions',
      header: '',
      render: (a: Account) => (
        <div className="flex gap-2 justify-end">
          <button onClick={() => startEdit(a)} className="text-blue-600 hover:text-blue-800 text-xs">Edit</button>
          <button onClick={() => { if (confirm('Delete this account?')) deleteMut.mutate(a.id); }} className="text-red-600 hover:text-red-800 text-xs">Delete</button>
        </div>
      ),
      className: 'text-right',
    },
  ];

  if (isLoading) return <p className="text-gray-500">Loading accounts...</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Accounts</h2>
        <button
          onClick={() => { resetForm(); setShowForm(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
        >
          Add Account
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-4 mb-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Name</label>
              <input
                type="text" required value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value as AccountCreate['type'] })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              >
                <option value="checking">Checking</option>
                <option value="savings">Savings</option>
                <option value="credit_card">Credit Card</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Starting Balance</label>
              <input
                type="number" step="0.01" value={form.starting_balance ?? 0}
                onChange={(e) => setForm({ ...form, starting_balance: parseFloat(e.target.value) || 0 })}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
              />
            </div>
            {form.type === 'credit_card' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Credit Limit</label>
                  <input
                    type="number" step="0.01" value={form.credit_limit ?? ''}
                    onChange={(e) => setForm({ ...form, credit_limit: e.target.value ? parseFloat(e.target.value) : null })}
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Statement Close Day</label>
                  <input
                    type="number" min="1" max="31" value={form.statement_close_day ?? ''}
                    onChange={(e) => setForm({ ...form, statement_close_day: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Payment Due Day</label>
                  <input
                    type="number" min="1" max="31" value={form.payment_due_day ?? ''}
                    onChange={(e) => setForm({ ...form, payment_due_day: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
              </>
            )}
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700">
              {editingId ? 'Update' : 'Create'}
            </button>
            <button type="button" onClick={resetForm} className="border border-gray-300 px-4 py-1.5 rounded text-sm hover:bg-gray-50">
              Cancel
            </button>
          </div>
        </form>
      )}

      <DataTable columns={columns} data={accounts} keyFn={(a) => a.id} emptyMessage="No accounts yet — add one to get started" />
    </div>
  );
}
