import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchStatements, fetchUnpaidStatements, markStatementPaid } from '../api/statements.ts';
import { fetchAccounts } from '../api/accounts.ts';
import DataTable from '../components/DataTable.tsx';
import type { Statement, Account } from '../types/index.ts';
import { formatCurrency, formatDate } from '../utils/formatters.ts';

const TODAY = new Date().toISOString().split('T')[0];

function isOverdue(statement: Statement): boolean {
  return !statement.is_paid && statement.due_date < TODAY;
}

export default function Statements() {
  const queryClient = useQueryClient();
  const [filterAccountId, setFilterAccountId] = useState<string>('');
  const [showUnpaidOnly, setShowUnpaidOnly] = useState(false);

  const { data: allStatements = [], isLoading: loadingAll } = useQuery({
    queryKey: ['statements', filterAccountId],
    queryFn: () => fetchStatements(filterAccountId ? parseInt(filterAccountId) : undefined),
    enabled: !showUnpaidOnly,
  });

  const { data: unpaidStatements = [], isLoading: loadingUnpaid } = useQuery({
    queryKey: ['statements', 'unpaid'],
    queryFn: fetchUnpaidStatements,
    enabled: showUnpaidOnly,
  });

  const { data: accounts = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });

  const markPaidMut = useMutation({
    mutationFn: (id: number) => markStatementPaid(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['statements'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const accountMap = new Map(accounts.map((a: Account) => [a.id, a.name]));

  const isLoading = showUnpaidOnly ? loadingUnpaid : loadingAll;
  const statements = showUnpaidOnly ? unpaidStatements : allStatements;

  // When showing unpaid only, filter by account client-side since the endpoint has no account filter
  const displayed = showUnpaidOnly && filterAccountId
    ? statements.filter((s: Statement) => s.account_id === parseInt(filterAccountId))
    : statements;

  const columns = [
    {
      key: 'statement_date',
      header: 'Statement Date',
      render: (s: Statement) => (
        <span className={isOverdue(s) ? 'text-red-600 font-medium' : 'text-gray-600'}>
          {formatDate(s.statement_date)}
        </span>
      ),
    },
    {
      key: 'account',
      header: 'Account',
      render: (s: Statement) => (
        <span className={isOverdue(s) ? 'text-red-600 font-medium' : ''}>
          {accountMap.get(s.account_id) ?? '—'}
        </span>
      ),
    },
    {
      key: 'balance',
      header: 'Balance',
      render: (s: Statement) => (
        <span className={isOverdue(s) ? 'text-red-600 font-medium' : 'text-gray-800'}>
          {formatCurrency(s.balance)}
        </span>
      ),
      className: 'text-right',
    },
    {
      key: 'due_date',
      header: 'Due Date',
      render: (s: Statement) => (
        <span className={isOverdue(s) ? 'text-red-600 font-semibold' : 'text-gray-600'}>
          {formatDate(s.due_date)}
          {isOverdue(s) && (
            <span className="ml-1.5 px-1.5 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium">
              Overdue
            </span>
          )}
        </span>
      ),
    },
    {
      key: 'is_paid',
      header: 'Status',
      render: (s: Statement) => (
        s.is_paid ? (
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-50 text-green-700">
            Paid
          </span>
        ) : (
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${isOverdue(s) ? 'bg-red-100 text-red-700' : 'bg-yellow-50 text-yellow-700'}`}>
            Unpaid
          </span>
        )
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (s: Statement) =>
        !s.is_paid ? (
          <button
            onClick={() => markPaidMut.mutate(s.id)}
            disabled={markPaidMut.isPending}
            className="px-2.5 py-1 text-xs font-medium rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Mark Paid
          </button>
        ) : null,
      className: 'text-right',
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Statements</h2>

      <div className="flex gap-3 mb-4 items-center flex-wrap">
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

        <div className="flex rounded-lg border border-gray-300 overflow-hidden text-sm">
          <button
            onClick={() => setShowUnpaidOnly(false)}
            className={`px-4 py-1.5 transition-colors ${
              !showUnpaidOnly
                ? 'bg-blue-600 text-white font-medium'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setShowUnpaidOnly(true)}
            className={`px-4 py-1.5 transition-colors border-l border-gray-300 ${
              showUnpaidOnly
                ? 'bg-blue-600 text-white font-medium'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Unpaid Only
          </button>
        </div>
      </div>

      {isLoading ? (
        <p className="text-gray-500">Loading statements...</p>
      ) : (
        <DataTable
          columns={columns}
          data={displayed}
          keyFn={(s) => s.id}
          emptyMessage="No statements found"
        />
      )}
    </div>
  );
}
