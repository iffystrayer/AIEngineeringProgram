#!/usr/bin/env node

import React from 'react';
import { render } from 'ink';
import { App } from './components/App.js';

// Render the app
const { unmount, waitUntilExit } = render(<App />);

// Handle exit signals
process.on('SIGINT', () => {
  unmount();
  process.exit(0);
});

process.on('SIGTERM', () => {
  unmount();
  process.exit(0);
});

// Wait for the app to exit
await waitUntilExit();
