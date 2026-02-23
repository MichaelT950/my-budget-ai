import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { fetchCashFlow, fetchBalanceSheet, fetchPeriodSummary } from '../api/reports.ts';
import { fetchAccounts } from '../api/accounts.ts';
import type { Account } from '../types/index.ts';
import { formatCurrency, getCategoryColor } from '../utils/formatters.ts';

type Tab = 'cash-flow' | 'balance-sheet' | 'period-summary';

function getMonthRange(): { start: string; end: string } {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = now;
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10),
  };
}

export default function Reports() {
  const [tab, setTab] = useState<Tab>('cash-flow');
  const range = getMonthRange();
  const [startDate, setStartDate] = useState(range.start);
  const [endDate, setEndDate] = useState(range.end);
  const [accountId, setAccountId] = useState<string>('');

  const { data: accounts = [] } = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Reports</h2>

      <div className="flex gap-1 mb-4 bg-gray-100 rounded-lg p-1 w-fit">
        {(['cash-flow', 'balance-sheet', 'period-summary'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded text-sm transition-colors ${
              tab === t ? 'bg-white font-medium shadow-sm' : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {t === 'cash-flow' ? 'Cash Flow' : t === 'balance-sheet' ? 'Balance Sheet' : 'Period Summary'}
          </button>
        ))}
      </div>

      {tab !== 'balance-sheet' && (
        <div className="flex gap-3 mb-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Start Date</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">End Date</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm" />
          </div>
          {tab === 'cash-flow' && (
            <div>
              <label className="block text-xs text-gray-500 mb-1">Account</label>
              <select value={accountId} onChange={(e) => setAccountId(e.target.value)}
                className="border border-gray-300 rounded px-3 py-1.5 text-sm">
                <option value="">All Accounts</option>
                {accounts.map((a: Account) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
          )}
        </div>
      )}

      {tab === 'cash-flow' && <CashFlowTab startDate={startDate} endDate={endDate} accountId={accountId ? parseInt(accountId) : undefined} />}
      {tab === 'balance-sheet' && <BalanceSheetTab />}
      {tab === 'period-summary' && <PeriodSummaryTab startDate={startDate} endDate={endDate} />}
    </div>
  );
}

function CashFlowTab({ startDate, endDate, accountId }: { startDate: string; endDate: string; accountId?: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['cash-flow', startDate, endDate, accountId],
    queryFn: () => fetchCashFlow(startDate, endDate, accountId),
    enabled: !!startDate && !!endDate,
  });

  if (isLoading) return <p className="text-gray-500 text-sm">Loading...</p>;
  if (!data) return null;

  const barData = [
    { name: 'Income', value: data.total_income, fill: '#43A047' },
    { name: 'Expenses', value: data.total_expenses, fill: '#E53935' },
  ];

  const categoryData = Object.entries(data.expenses_by_category)
    .map(([name, total]) => ({ name, value: total }))
    .sort((a, b) => b.value - a.value);

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-600 mb-3">Income vs Expenses</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={barData}>
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v) => formatCurrency(Number(v ?? 0))} />
            <Bar dataKey="value">
              {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-3 text-center text-sm">
          Net Cash Flow:{' '}
          <span className={data.net_cash_flow >= 0 ? 'text-green-700 font-medium' : 'text-red-600 font-medium'}>
            {formatCurrency(data.net_cash_flow)}
          </span>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-600 mb-3">Expenses by Category</h3>
        {categoryData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90}>
                  {categoryData.map((entry, i) => <Cell key={i} fill={getCategoryColor(entry.name)} />)}
                </Pie>
                <Tooltip formatter={(v) => formatCurrency(Number(v ?? 0))} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 space-y-1">
              {categoryData.map((c) => (
                <div key={c.name} className="flex justify-between text-xs">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: getCategoryColor(c.name) }} />
                    {c.name}
                  </span>
                  <span>{formatCurrency(c.value)}</span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-gray-400 text-sm text-center py-8">No expenses in this period</p>
        )}
      </div>
    </div>
  );
}

function BalanceSheetTab() {
  const { data, isLoading } = useQuery({
    queryKey: ['balance-sheet'],
    queryFn: fetchBalanceSheet,
  });

  if (isLoading) return <p className="text-gray-500 text-sm">Loading...</p>;
  if (!data) return null;

  const assetData = Object.entries(data.assets).map(([name, value]) => ({ name, value }));
  const liabilityData = Object.entries(data.liabilities).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Total Assets</p>
          <p className="text-2xl font-bold text-green-700">{formatCurrency(data.total_assets)}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Total Liabilities</p>
          <p className="text-2xl font-bold text-red-600">{formatCurrency(data.total_liabilities)}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Net Worth</p>
          <p className={`text-2xl font-bold ${data.net_worth >= 0 ? 'text-green-700' : 'text-red-600'}`}>
            {formatCurrency(data.net_worth)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Assets</h3>
          {assetData.length > 0 ? (
            <div className="space-y-2">
              {assetData.map((a) => (
                <div key={a.name} className="flex justify-between text-sm">
                  <span>{a.name}</span>
                  <span className="text-green-700 font-medium">{formatCurrency(a.value)}</span>
                </div>
              ))}
            </div>
          ) : <p className="text-gray-400 text-sm">No assets</p>}
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Liabilities</h3>
          {liabilityData.length > 0 ? (
            <div className="space-y-2">
              {liabilityData.map((l) => (
                <div key={l.name} className="flex justify-between text-sm">
                  <span>{l.name}</span>
                  <span className="text-red-600 font-medium">{formatCurrency(l.value)}</span>
                </div>
              ))}
            </div>
          ) : <p className="text-gray-400 text-sm">No liabilities</p>}
        </div>
      </div>
    </div>
  );
}

function PeriodSummaryTab({ startDate, endDate }: { startDate: string; endDate: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['period-summary', startDate, endDate],
    queryFn: () => fetchPeriodSummary(startDate, endDate),
    enabled: !!startDate && !!endDate,
  });

  if (isLoading) return <p className="text-gray-500 text-sm">Loading...</p>;
  if (!data) return null;

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-600 mb-3">{data.period_label}</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-500">Income</p>
            <p className="text-lg font-bold text-green-700">{formatCurrency(data.total_income)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Expenses</p>
            <p className="text-lg font-bold text-red-600">{formatCurrency(data.total_expenses)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Net</p>
            <p className={`text-lg font-bold ${data.net >= 0 ? 'text-green-700' : 'text-red-600'}`}>
              {formatCurrency(data.net)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Top Category</p>
            <p className="text-lg font-bold text-gray-800">{data.top_category || '—'}</p>
          </div>
        </div>
      </div>

      {data.expenses_by_category.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Category Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.expenses_by_category} layout="vertical">
              <XAxis type="number" tickFormatter={(v) => `$${v}`} />
              <YAxis type="category" dataKey="name" width={120} />
              <Tooltip formatter={(v) => formatCurrency(Number(v ?? 0))} />
              <Bar dataKey="total">
                {data.expenses_by_category.map((entry, i) => (
                  <Cell key={i} fill={getCategoryColor(entry.name)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
