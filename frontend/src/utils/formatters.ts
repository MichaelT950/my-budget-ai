export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function formatAccountType(type: string): string {
  switch (type) {
    case 'credit_card': return 'Credit Card';
    case 'checking': return 'Checking';
    case 'savings': return 'Savings';
    default: return type;
  }
}

export function formatTransactionType(type: string): string {
  return type.charAt(0).toUpperCase() + type.slice(1);
}

const CATEGORY_COLORS: Record<string, string> = {
  Health: '#E53935',
  'Food & Drink': '#FB8C00',
  Shopping: '#FDD835',
  Travel: '#43A047',
  Transportation: '#1E88E5',
  Services: '#8E24AA',
  Entertainment: '#D81B60',
  Uncategorized: '#757575',
};

export function getCategoryColor(name: string): string {
  return CATEGORY_COLORS[name] ?? '#757575';
}
