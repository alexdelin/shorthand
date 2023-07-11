import { lazy, Suspense, useState } from 'react';
import { ErrorBoundary, FallbackProps } from 'react-error-boundary';
import { Routes, Route, Link } from "react-router-dom";
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import BottomNavigation from '@mui/material/BottomNavigation';
import BottomNavigationAction from '@mui/material/BottomNavigationAction';
import { SuspenseFallback } from './components/SuspenseFallback';
import { Nav } from './components/Nav';
import { FileSearchModal } from './components/FileSearchModal';
import { HomePage } from './pages/HomePage';
import { ComposePage } from './pages/ComposePage';
import { QuestionsPage } from './pages/QuestionsPage';
import { LinksPage } from './pages/LinksPage';
import { DefinitionsPage } from './pages/DefinitionsPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { LocationsPage } from './pages/LocationsPage';
import { CalendarPage } from './pages/CalendarPage';
import { SearchPage } from './pages/SearchPage';
import { SettingsPage } from './pages/SettingsPage';
import { MobileNotesPage } from './mobilePages/MobileNotesPage';
import { MobileComposePage } from './mobilePages/MobileComposePage';
import { MobileViewPage } from './mobilePages/MobileViewPage';
import styled from 'styled-components';


// Lazy-load pages with heavy dependencies
const ViewPage = lazy(() => import(
  /* webpackChunkName: "ViewPage" */
  './pages/ViewPage'
));
const TodosPage = lazy(() => import(
  /* webpackChunkName: "TodosPage" */
  './pages/TodosPage'
));

const Content = styled.div`
  background-color: white;
  width: calc(100% - 5rem);
  height: 100vh;
  margin-left: 5rem;
  overflow: scroll;
  position: relative;`

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

function isMobileDevice() {
  let check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor);
  return check;
};

function App() {
  return isMobileDevice() ? <MobileApp /> : <DesktopApp />;
}

const MobileContent = styled.div`
  height: calc(100vh - 3.5rem);
`

const mobileDarkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function MobileApp() {

  const [navPage, setNavPage] = useState(0);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={mobileDarkTheme}>
        <MobileContent>
          <Routes>
            <Route path="/notes" element={<MobileNotesPage />} />
            <Route path="/compose" element={<MobileComposePage />} />
            <Route path="/view" element={<MobileViewPage />} />
          </Routes>
        </MobileContent>
        <BottomNavigation
          value={navPage}
          onChange={(event, newValue) => {
            setNavPage(newValue);
          }}
        >
          <BottomNavigationAction
            component={Link}
            label="Files"
            icon={<i className="bi bi-bar-chart-steps" />}
            to="/notes"
          />
          <BottomNavigationAction
            component={Link}
            label="Compose"
            icon={<i className="bi bi-pen" />}
            to="/compose"
          />
          <BottomNavigationAction
            component={Link}
            label="View"
            icon={<i className="bi bi-file-earmark-richtext" />}
            to="/view"
          />
        </BottomNavigation>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

function DesktopApp() {
  return (
    <QueryClientProvider client={queryClient}>
      <Nav></Nav>
      <FileSearchModal />
      <Content id="ContentEl">
        <ErrorBoundary
          FallbackComponent={ErrorFallback}
          onReset={() => {
            // reset the state of your app so the error doesn't happen again
          }}
        >
          <Suspense fallback={<div>Loading...</div>}>
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
          </Suspense>
        </ErrorBoundary>
      </Content>
    </QueryClientProvider>
  );
}

export default App;
