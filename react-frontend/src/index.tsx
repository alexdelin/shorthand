import React from 'react';
import { BrowserRouter } from "react-router-dom";
import { createRoot } from 'react-dom/client';
import 'bootstrap-icons/font/bootstrap-icons.css';
import App from './App';
import 'normalize.css';
import './index.css';

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(
  <BrowserRouter>
      <App />
  </BrowserRouter>
);
