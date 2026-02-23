interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyFn: (row: T, index: number) => string | number;
  emptyMessage?: string;
}

export default function DataTable<T>({ columns, data, keyFn, emptyMessage = 'No data' }: DataTableProps<T>) {
  if (data.length === 0) {
    return <p className="text-gray-500 text-sm py-8 text-center">{emptyMessage}</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-100 border-b border-gray-200">
            {columns.map((col) => (
              <th key={col.key} className={`px-4 py-2.5 text-left font-medium text-gray-600 ${col.className ?? ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={keyFn(row, i)} className={`border-b border-gray-100 ${i % 2 === 1 ? 'bg-gray-50' : 'bg-white'}`}>
              {columns.map((col) => (
                <td key={col.key} className={`px-4 py-2.5 ${col.className ?? ''}`}>
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
