import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';  // IMPORTANTE: Assicurati che questa riga ci sia!
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);