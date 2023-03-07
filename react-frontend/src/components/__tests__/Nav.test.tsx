import {cleanup, fireEvent, render} from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from "react-router-dom";
import { Nav } from '../Nav';


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: false,
    },
  },
});

describe('<Nav />', () => {

  it('Renders the nav without crashing', async () => {
    const component = render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Nav />
        </BrowserRouter>
      </QueryClientProvider>
    );
  })

});
