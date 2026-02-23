import type { Alert } from '../types/index.ts';
import { formatCurrency } from '../utils/formatters.ts';

interface AlertBannerProps {
  alerts: Alert[];
}

const ALERT_STYLES: Record<string, string> = {
  payment_due: 'bg-amber-50 border-amber-300 text-amber-800',
  overdraft: 'bg-red-50 border-red-300 text-red-800',
  high_expenses: 'bg-orange-50 border-orange-300 text-orange-800',
};

export default function AlertBanner({ alerts }: AlertBannerProps) {
  if (alerts.length === 0) return null;

  return (
    <div className="space-y-2 mb-4">
      {alerts.map((alert, i) => (
        <div
          key={i}
          className={`px-4 py-3 rounded-lg border text-sm ${ALERT_STYLES[alert.alert_type] ?? 'bg-gray-50 border-gray-300 text-gray-800'}`}
        >
          <span className="font-medium">{alert.account_name}:</span>{' '}
          {alert.message} ({formatCurrency(alert.balance)})
        </div>
      ))}
    </div>
  );
}
