# U-AIP TUI - Beautiful Terminal Interface

A modern, beautiful Terminal User Interface (TUI) for the U-AIP Scoping Assistant, built with Ink, React, and TypeScript.

## Features

- 🎨 Beautiful, interactive terminal UI
- ⚡ Real-time question and answer flow
- 📊 Visual progress tracking across 5 stages
- 🤖 AI-powered quality validation with feedback
- 🎯 Robust error handling
- ⌨️  Smooth keyboard navigation

## Tech Stack

- **Ink 5.x** - React for terminal UIs
- **React 19** - Component-based architecture
- **TypeScript 5.7** - Type safety
- **Zustand 5.x** - Lightweight state management
- **Axios** - API communication
- **Chalk** - Terminal colors
- **Figures** - Unicode symbols

## Installation

```bash
# Install dependencies
npm install

# Build the project
npm run build
```

## Usage

### Development Mode

```bash
# Run in development with hot reload
npm run dev
```

### Production Mode

```bash
# Build and run
npm run build
npm start

# Or install globally and use the `uaip` command
npm install -g .
uaip
```

## Architecture

```
src/
├── components/          # React components for each view
│   ├── App.tsx         # Main app orchestrator
│   ├── Welcome.tsx     # Welcome screen
│   ├── SessionStart.tsx # Session creation
│   ├── Question.tsx    # Question display & answer input
│   ├── QualityFeedback.tsx # AI feedback display
│   ├── Progress.tsx    # Progress bar and stage indicator
│   └── ErrorDisplay.tsx # Error handling
├── state/
│   └── store.ts        # Zustand state management
├── utils/
│   └── api.ts          # Backend API client
└── index.tsx           # Entry point
```

## State Management

The app uses Zustand for state management with the following key states:

- `session` - Current interview session
- `currentQuestion` - Active question being answered
- `answers` - Array of submitted answers
- `currentView` - Active view ('welcome', 'session-start', 'question', etc.)
- `isLoading` / `isProcessing` - Loading states
- `error` - Error messages

## Views

1. **Welcome** - Intro screen with stage overview
2. **SessionStart** - Collect user ID and project name
3. **Question** - Display question and collect answer
4. **QualityFeedback** - Show AI feedback for improvement
5. **StageComplete** - Stage transition screen
6. **FinalComplete** - Completion celebration

## API Integration

The TUI communicates with the U-AIP backend API at `http://localhost:38937/api/v1`.

Configure the API URL via environment variable:

```bash
export UAIP_API_URL=http://your-api-url/api/v1
npm run dev
```

## Development

### Type Checking

```bash
npm run type-check
```

### Building

```bash
npm run build
```

The build outputs to `dist/` directory.

## Design Philosophy

This TUI follows the design principles of modern CLI tools like Claude Code:

- **Non-intrusive** - Clean, minimal interface
- **Fast** - Instant feedback and smooth transitions
- **Beautiful** - Professional color scheme and typography
- **Robust** - Graceful error handling and recovery
- **Accessible** - Clear labels and keyboard navigation

## Known Limitations

- Multiline input currently uses single-line input (can be extended with custom component)
- No session resume functionality yet (future enhancement)
- Requires Node.js 18+ for ESM support

## Future Enhancements

- [ ] Multiline text editor for long answers
- [ ] Session persistence and resume
- [ ] Arrow key navigation for multiple choice
- [ ] Export charter from TUI
- [ ] Offline mode with local storage
- [ ] Customizable themes
- [ ] Vim keybindings support

## License

MIT
