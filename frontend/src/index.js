// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Okay, find the root element in the HTML
const container = document.getElementById('root');

// Let's create a root with the new React 18 API
// The older way was ReactDOM.render(), but this is better for concurrent features
const root = ReactDOM.createRoot(container);

// Here we go! This is where the app actually gets rendered.
root.render(
  // StrictMode helps us find potential problems in the app. Good practice!
  <React.StrictMode>
    <App />
  </React.StrictMode>
);