import {cleanup, fireEvent, render} from '@testing-library/react';
import { BrowserRouter } from "react-router-dom";
import { Nav } from '../Nav';

describe('<Nav />', () => {

    it('Renders the nav without crashing', async () => {
        const component = render(
            <BrowserRouter>
                <Nav />
            </BrowserRouter>
        );
    })

});
