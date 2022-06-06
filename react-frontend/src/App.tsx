import { ErrorBoundary, FallbackProps } from 'react-error-boundary';
import { Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from 'react-query';
import { Nav } from './components/Nav';
import { HomePage } from './pages/HomePage';
import { ComposePage } from './pages/ComposePage';
import { TodosPage } from './pages/TodosPage';
import { QuestionsPage } from './pages/QuestionsPage';
import { LinksPage } from './pages/LinksPage';
import { DefinitionsPage } from './pages/DefinitionsPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { LocationsPage } from './pages/LocationsPage';
import { CalendarPage } from './pages/CalendarPage';
import { SearchPage } from './pages/SearchPage';
import { ViewPage } from './pages/ViewPage';
import { SettingsPage } from './pages/SettingsPage';
import styled from 'styled-components';

const Content = styled.div`
  background-color: white;
  width: calc(100% - 5rem);
  height: 100vh;
  margin-left: 5rem;
  overflow: scroll;`

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: false,
    },
  },
});

function ErrorFallback({error, resetErrorBoundary}: FallbackProps) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Nav></Nav>
      <Content className="ContentEl">
        <ErrorBoundary
          FallbackComponent={ErrorFallback}
          onReset={() => {
            // reset the state of your app so the error doesn't happen again
          }}
        >
          <Routes>
            <Route path="/home" element={<HomePage />} />
            <Route path="/compose" element={<ComposePage />} />

            <Route path="/todos" element={<TodosPage />} />
            <Route path="/questions" element={<QuestionsPage />} />
            <Route path="/links" element={<LinksPage />} />
            <Route path="/definitions" element={<DefinitionsPage />} />
            <Route path="/datasets" element={<DatasetsPage />} />
            <Route path="/locations" element={<LocationsPage />} />

            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/view" element={<ViewPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </ErrorBoundary>
      </Content>
    </QueryClientProvider>
  );
}

export default App;
