import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Accounts from './pages/Accounts.tsx';
import Transactions from './pages/Transactions.tsx';
import ImportCsv from './pages/ImportCsv.tsx';
import Reports from './pages/Reports.tsx';
import Statements from './pages/Statements.tsx';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="accounts" element={<Accounts />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="import" element={<ImportCsv />} />
            <Route path="reports" element={<Reports />} />
            <Route path="statements" element={<Statements />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
