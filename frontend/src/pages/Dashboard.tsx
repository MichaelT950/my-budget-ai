import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { fetchDashboard } from '../api/dashboard.ts';
import AlertBanner from '../components/AlertBanner.tsx';
import DataTable from '../components/DataTable.tsx';
import type { Account } from '../types/index.ts';
import { formatCurrency, formatAccountType, getCategoryColor } from '../utils/formatters.ts';

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
  });

  if (isLoading) return <p className="text-gray-500">Loading dashboard...</p>;
  if (error) return <p className="text-red-600">Error loading dashboard</p>;
  if (!data) return null;

  const cashFlowData = [
    { name: 'Income', value: data.cash_flow.total_income, fill: '#43A047' },
    { name: 'Expenses', value: data.cash_flow.total_expenses, fill: '#E53935' },
  ];

  const categoryData = Object.entries(data.cash_flow.expenses_by_category).map(([name, total]) => ({
    name,
    value: total,
  }));

  const accountColumns = [
    { key: 'name', header: 'Account', render: (a: Account) => <span className="font-medium">{a.name}</span> },
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
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Dashboard</h2>

      <AlertBanner alerts={data.alerts} />

      {/* Balance Sheet Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Total Assets</p>
          <p className="text-2xl font-bold text-green-700">{formatCurrency(data.balance_sheet.total_assets)}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Total Liabilities</p>
          <p className="text-2xl font-bold text-red-600">{formatCurrency(data.balance_sheet.total_liabilities)}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Net Worth</p>
          <p className={`text-2xl font-bold ${data.balance_sheet.net_worth >= 0 ? 'text-green-700' : 'text-red-600'}`}>
            {formatCurrency(data.balance_sheet.net_worth)}
          </p>
        </div>
      </div>

      {/* Cash Flow + Category Breakdown */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Monthly Cash Flow</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={cashFlowData}>
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(v) => formatCurrency(Number(v ?? 0))} />
              <Bar dataKey="value" fill="#8884d8">
                {cashFlowData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <p className="text-center text-sm mt-2">
            Net: <span className={data.cash_flow.net_cash_flow >= 0 ? 'text-green-700' : 'text-red-600'}>
              {formatCurrency(data.cash_flow.net_cash_flow)}
            </span>
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Expenses by Category</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name }) => name}>
                  {categoryData.map((entry, i) => (
                    <Cell key={i} fill={getCategoryColor(entry.name)} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => formatCurrency(Number(v ?? 0))} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-8">No expenses this month</p>
          )}
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-600 mb-3">Accounts</h3>
        <DataTable columns={accountColumns} data={data.accounts} keyFn={(a) => a.id} emptyMessage="No accounts yet" />
      </div>
    </div>
  );
}
