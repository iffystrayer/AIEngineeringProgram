# TUI Modernization Plan
**Beautiful Terminal Interface with Ink + React + TypeScript**

Inspired by Claude Code's approach

**Status:** Planning Phase
**Timeline:** 1-2 weeks
**Priority:** HIGH (Better UX)

---

## 🎯 Vision

Transform the CLI from a basic Python/Rich/Click interface into a **beautiful, modern, stateful TUI** using the same stack as Claude Code:

- **Ink** - React for terminal UIs
- **React** - Component-based, declarative UI
- **TypeScript** - Type safety and better DX
- **Yoga** - Consistent layout engine

---

## 📊 Current vs Future

### Current CLI (Python/Rich/Click)

**Stack:**
- Python 3.11+
- Rich (terminal formatting)
- Click (command framework)
- Synchronous I/O

**Limitations:**
- ❌ Basic question/answer flow
- ❌ No real state management
- ❌ Hard to maintain complex UI
- ❌ Limited interactivity
- ❌ No live updates during LLM calls
- ❌ Difficult to test UI logic
- ❌ Can "fall apart" with complex flows

**What it does well:**
- ✅ Simple commands work fine
- ✅ Good error messages
- ✅ Colorful output

---

### Future TUI (Ink/React/TypeScript)

**Stack:**
- Node.js 18+
- Ink 4.x (React for terminal)
- React 18+ (component model)
- TypeScript 5+ (type safety)
- Yoga (layout engine)
- Zustand or React Context (state management)

**Benefits:**
- ✅ **Stateful components** - React state management
- ✅ **Smooth UI** - No "falling apart"
- ✅ **Live updates** - Real-time progress during LLM calls
- ✅ **Keyboard navigation** - Arrow keys, Tab, Enter
- ✅ **Component reuse** - Build once, use everywhere
- ✅ **Modern DX** - TypeScript, hot reload, testing
- ✅ **Consistent layout** - Yoga handles terminal sizing
- ✅ **Similar to Claude Code** - Proven approach

---

## 🏗️ Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────┐
│              TUI Layer (Node.js/Ink)                │
│  - React components for UI                          │
│  - Ink rendering to terminal                        │
│  - Keyboard event handling                          │
│  - State management (Zustand)                       │
└────────────────┬────────────────────────────────────┘
                 │ HTTP / WebSocket
                 ▼
┌─────────────────────────────────────────────────────┐
│         Backend API (Python/FastAPI)                │
│  - REST API (13 endpoints)                          │
│  - WebSocket for live updates (optional)            │
│  - SSE for streaming progress                       │
│  - Multi-agent orchestration                        │
└─────────────────────────────────────────────────────┘
```

### Component Structure

```
src/
├── cli/
│   ├── index.tsx              # Entry point
│   ├── app.tsx                # Main App component
│   ├── components/
│   │   ├── SessionStart.tsx   # Start new session
│   │   ├── Question.tsx       # Single question component
│   │   ├── Answer.tsx         # Answer input component
│   │   ├── QualityFeedback.tsx # Quality score display
│   │   ├── ProgressBar.tsx    # Stage progress
│   │   ├── StageHeader.tsx    # Stage name/description
│   │   ├── CharterPreview.tsx # Final charter display
│   │   └── ErrorBoundary.tsx  # Error handling
│   ├── hooks/
│   │   ├── useSession.ts      # Session state
│   │   ├── useStage.ts        # Stage progression
│   │   ├── useApi.ts          # API calls
│   │   └── useKeyboard.ts     # Keyboard handling
│   ├── state/
│   │   └── store.ts           # Zustand store
│   ├── api/
│   │   └── client.ts          # API client (axios)
│   └── types/
│       └── index.ts           # TypeScript types
├── package.json
├── tsconfig.json
└── README.md
```

---

## 🎨 UI Components Design

### Component 1: SessionStart

**Purpose:** Welcome screen and project name input

**UI:**
```
╭─────────────────────────────────────────────────────╮
│           U-AIP Scoping Assistant                   │
│     AI Project Evaluation in 55 Minutes             │
╰─────────────────────────────────────────────────────╯

  What AI project would you like to scope?

  > Reduce customer churn by 25%                      │

  ↵ Press Enter to begin  ·  ^C to exit
```

**Features:**
- Text input with validation
- Real-time character count
- Enter to submit
- Loading spinner on submit

**Code Sketch:**
```tsx
export const SessionStart: FC = () => {
  const [projectName, setProjectName] = useState('')
  const { createSession, isLoading } = useApi()

  const handleSubmit = async () => {
    await createSession(projectName)
  }

  return (
    <Box flexDirection="column">
      <Box marginBottom={1}>
        <Text bold color="cyan">U-AIP Scoping Assistant</Text>
      </Box>
      <Text>What AI project would you like to scope?</Text>
      <TextInput
        value={projectName}
        onChange={setProjectName}
        onSubmit={handleSubmit}
      />
      {isLoading && <Spinner label="Creating session..." />}
    </Box>
  )
}
```

---

### Component 2: Question & Answer Flow

**Purpose:** Display question, capture answer, show quality feedback

**UI:**
```
╭─────────────────────────────────────────────────────╮
│ Stage 1/5: Business Translation              20%   │
╰─────────────────────────────────────────────────────╯

  📋 Question 1 of 7

  What is the primary business objective you want to
  achieve with AI?

  Be specific: Include measurable targets, timeframes,
  and success criteria.

  Your Answer:
  > We want to reduce monthly churn from 5.2% to 3.5%  │
  > within 6 months for our SaaS product.             │

  Quality Score: 8/10 ✅  Excellent!
  ✓ Specific target (5.2% → 3.5%)
  ✓ Clear timeframe (6 months)
  ✓ Measurable outcome

  ↵ Press Enter to continue  ·  ↑↓ to edit
```

**Features:**
- Multi-line text input
- Live quality feedback (via API)
- Progress indicator
- Keyboard navigation
- Clear visual hierarchy

**Code Sketch:**
```tsx
export const QuestionAnswer: FC<Props> = ({ question, onSubmit }) => {
  const [answer, setAnswer] = useState('')
  const [quality, setQuality] = useState<QualityScore | null>(null)
  const { evaluateQuality } = useApi()

  // Debounced quality check
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (answer.length > 20) {
        const score = await evaluateQuality(answer)
        setQuality(score)
      }
    }, 1000)
    return () => clearTimeout(timer)
  }, [answer])

  return (
    <Box flexDirection="column">
      <StageHeader stage={1} total={5} progress={20} />

      <Box marginY={1}>
        <Text bold>{question.text}</Text>
        {question.guidance && (
          <Text dimColor>{question.guidance}</Text>
        )}
      </Box>

      <Box flexDirection="column">
        <Text>Your Answer:</Text>
        <TextArea
          value={answer}
          onChange={setAnswer}
          onSubmit={() => onSubmit(answer)}
        />
      </Box>

      {quality && (
        <QualityFeedback score={quality.score} feedback={quality.feedback} />
      )}
    </Box>
  )
}
```

---

### Component 3: Live Progress During LLM Calls

**Purpose:** Show progress while backend calls LLM APIs

**UI:**
```
╭─────────────────────────────────────────────────────╮
│ Processing Your Response                            │
╰─────────────────────────────────────────────────────╯

  🤖 Analyzing response quality...           ⠋

  ✓ Checking specificity
  ✓ Evaluating measurability
  ⠋ Assessing completeness
  ⏳ Generating feedback

  This may take 10-15 seconds...

  Tokens used: 234 / 1000
  Estimated cost: $0.003
```

**Features:**
- Animated spinner
- Step-by-step progress
- Token usage tracking
- Time estimates
- Can be updated via SSE

**Code Sketch:**
```tsx
export const ProcessingIndicator: FC<Props> = ({ steps }) => {
  return (
    <Box flexDirection="column">
      <Box marginBottom={1}>
        <Text bold color="cyan">Processing Your Response</Text>
        <Spinner />
      </Box>

      {steps.map(step => (
        <Box key={step.id}>
          {step.status === 'complete' ? (
            <Text color="green">✓ {step.name}</Text>
          ) : step.status === 'active' ? (
            <Text><Spinner type="dots" /> {step.name}</Text>
          ) : (
            <Text dimColor>⏳ {step.name}</Text>
          )}
        </Box>
      ))}

      <Box marginTop={1}>
        <Text dimColor>Tokens used: {tokens} / 1000</Text>
      </Box>
    </Box>
  )
}
```

---

### Component 4: Stage Progress

**Purpose:** Show overall progress through 5 stages

**UI:**
```
╭─────────────────────────────────────────────────────╮
│                 Session Progress                     │
╰─────────────────────────────────────────────────────╯

  ✅ Stage 1: Business Translation        (Complete)
  ✅ Stage 2: Value Quantification         (Complete)
  ⏳ Stage 3: Data Feasibility             (In Progress)
  ⬜ Stage 4: User Centricity              (Pending)
  ⬜ Stage 5: Ethical Governance           (Pending)

  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░  60% Complete

  Estimated time remaining: 22 minutes
```

**Features:**
- Clear visual progress
- Stage status icons
- Progress bar
- Time estimate
- Always visible (sticky header)

---

### Component 5: Quality Feedback Loop

**Purpose:** Show quality issues and request improvements

**UI:**
```
╭─────────────────────────────────────────────────────╮
│ Quality Feedback                           Score 4/10
╰─────────────────────────────────────────────────────╯

  Your response needs improvement:

  ⚠️ Too vague: "We want to improve retention"
     → Try: "Reduce monthly churn from X% to Y%"

  ⚠️ No timeframe specified
     → Try: "within 6 months" or "by Q4 2025"

  ⚠️ Missing measurable target
     → Try: Include specific numbers or percentages

  Let's try again. Can you provide more specific details?

  [Edit your answer below or press Tab for examples]

  > _                                                  │
```

**Features:**
- Clear issue identification
- Specific suggestions
- Examples provided
- Easy to retry
- Attempt counter (max 3)

---

## 🔧 Technical Implementation

### Phase 1: Setup (Day 1)

**1.1 Initialize Project**
```bash
# Create new Node.js project in cli-tui/
mkdir cli-tui && cd cli-tui
npm init -y
npm install ink react typescript
npm install --save-dev @types/react @types/node ts-node
```

**1.2 Install Dependencies**
```bash
npm install \
  ink \
  react \
  zustand \
  axios \
  commander \
  chalk \
  ora \
  boxen

npm install --save-dev \
  typescript \
  @types/react \
  @types/node \
  ts-node \
  @swc/core \
  @swc/cli \
  vitest \
  @testing-library/react
```

**1.3 Configure TypeScript**
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "jsx": "react",
    "jsxImportSource": "react",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**1.4 Package Scripts**
```json
// package.json
{
  "name": "uaip-cli",
  "version": "1.0.0",
  "bin": {
    "uaip": "./dist/index.js"
  },
  "scripts": {
    "dev": "ts-node src/index.tsx",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "vitest"
  }
}
```

---

### Phase 2: Core Components (Days 2-3)

**2.1 API Client**
```typescript
// src/api/client.ts
import axios from 'axios'

const API_URL = process.env.API_URL || 'http://localhost:38937/api/v1'

export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
})

export const createSession = async (projectName: string) => {
  const response = await api.post('/sessions', {
    user_id: 'cli-user', // TODO: Get from auth
    project_name: projectName,
  })
  return response.data
}

export const executeStage = async (sessionId: string, stageNumber: number) => {
  const response = await api.post(
    `/sessions/${sessionId}/stages/${stageNumber}/execute`
  )
  return response.data
}

export const evaluateQuality = async (sessionId: string, answer: string) => {
  // Call quality agent endpoint
  const response = await api.post('/quality/evaluate', {
    session_id: sessionId,
    response_text: answer,
  })
  return response.data
}
```

**2.2 State Management (Zustand)**
```typescript
// src/state/store.ts
import { create } from 'zustand'

interface SessionState {
  sessionId: string | null
  currentStage: number
  projectName: string
  answers: Record<string, string>

  setSession: (id: string) => void
  setStage: (stage: number) => void
  setAnswer: (questionId: string, answer: string) => void
}

export const useStore = create<SessionState>((set) => ({
  sessionId: null,
  currentStage: 1,
  projectName: '',
  answers: {},

  setSession: (id) => set({ sessionId: id }),
  setStage: (stage) => set({ currentStage: stage }),
  setAnswer: (questionId, answer) =>
    set((state) => ({
      answers: { ...state.answers, [questionId]: answer }
    })),
}))
```

**2.3 Main App Component**
```tsx
// src/app.tsx
import React, { useState, useEffect } from 'react'
import { Box, Text } from 'ink'
import { SessionStart } from './components/SessionStart'
import { QuestionAnswer } from './components/QuestionAnswer'
import { StageProgress } from './components/StageProgress'
import { useStore } from './state/store'

export const App: React.FC = () => {
  const { sessionId, currentStage } = useStore()
  const [screen, setScreen] = useState<'start' | 'question' | 'complete'>('start')

  if (screen === 'start') {
    return <SessionStart onComplete={() => setScreen('question')} />
  }

  if (screen === 'question') {
    return (
      <Box flexDirection="column">
        <StageProgress current={currentStage} total={5} />
        <QuestionAnswer
          stage={currentStage}
          onComplete={() => {
            if (currentStage < 5) {
              useStore.setState({ currentStage: currentStage + 1 })
            } else {
              setScreen('complete')
            }
          }}
        />
      </Box>
    )
  }

  return <Text>Charter generated! ✨</Text>
}
```

---

### Phase 3: Enhanced Features (Days 4-5)

**3.1 Live Updates via SSE**
```typescript
// src/hooks/useSSE.ts
import { useEffect, useState } from 'react'

export const useSSE = (sessionId: string) => {
  const [events, setEvents] = useState<any[]>([])

  useEffect(() => {
    const eventSource = new EventSource(
      `${API_URL}/sessions/${sessionId}/stream`
    )

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setEvents(prev => [...prev, data])
    }

    return () => eventSource.close()
  }, [sessionId])

  return events
}
```

**3.2 Keyboard Navigation**
```typescript
// src/hooks/useKeyboard.ts
import { useInput } from 'ink'
import { useState } from 'react'

export const useKeyboard = (items: string[]) => {
  const [selectedIndex, setSelectedIndex] = useState(0)

  useInput((input, key) => {
    if (key.upArrow) {
      setSelectedIndex(i => Math.max(0, i - 1))
    }
    if (key.downArrow) {
      setSelectedIndex(i => Math.min(items.length - 1, i + 1))
    }
    if (key.return) {
      // Handle selection
    }
  })

  return { selectedIndex }
}
```

**3.3 Progress Animations**
```tsx
// src/components/AnimatedProgress.tsx
import React, { useEffect, useState } from 'react'
import { Box, Text } from 'ink'
import Spinner from 'ink-spinner'

export const AnimatedProgress: FC<Props> = ({ steps }) => {
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep(i => (i + 1) % steps.length)
    }, 2000)
    return () => clearInterval(timer)
  }, [])

  return (
    <Box flexDirection="column">
      {steps.map((step, i) => (
        <Box key={i}>
          {i < currentStep && <Text color="green">✓</Text>}
          {i === currentStep && <Spinner type="dots" />}
          {i > currentStep && <Text dimColor>⏳</Text>}
          <Text> {step.name}</Text>
        </Box>
      ))}
    </Box>
  )
}
```

---

### Phase 4: Testing & Polish (Days 6-7)

**4.1 Component Tests**
```typescript
// src/components/__tests__/Question.test.tsx
import { render } from 'ink-testing-library'
import { Question } from '../Question'

test('renders question text', () => {
  const { lastFrame } = render(
    <Question text="What is your goal?" />
  )
  expect(lastFrame()).toContain('What is your goal?')
})

test('accepts user input', async () => {
  const { stdin, lastFrame } = render(<Question />)

  stdin.write('My answer')
  await delay(100)

  expect(lastFrame()).toContain('My answer')
})
```

**4.2 Integration Tests**
```typescript
// src/__tests__/flow.test.tsx
test('complete session flow', async () => {
  const { stdin, lastFrame, waitUntilExit } = render(<App />)

  // Start session
  stdin.write('My Project\r')
  await delay(100)

  // Answer questions
  for (let i = 0; i < 5; i++) {
    stdin.write('Test answer\r')
    await delay(100)
  }

  // Should show completion
  expect(lastFrame()).toContain('Charter generated')
})
```

---

## 📦 Project Structure

```
cli-tui/
├── src/
│   ├── index.tsx              # CLI entry point
│   ├── app.tsx                # Main app component
│   ├── components/
│   │   ├── SessionStart.tsx
│   │   ├── Question.tsx
│   │   ├── Answer.tsx
│   │   ├── QualityFeedback.tsx
│   │   ├── StageProgress.tsx
│   │   ├── StageHeader.tsx
│   │   ├── ProcessingIndicator.tsx
│   │   ├── CharterPreview.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── __tests__/
│   ├── hooks/
│   │   ├── useSession.ts
│   │   ├── useStage.ts
│   │   ├── useApi.ts
│   │   ├── useSSE.ts
│   │   └── useKeyboard.ts
│   ├── state/
│   │   └── store.ts           # Zustand store
│   ├── api/
│   │   └── client.ts          # API client
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

---

## 🚀 Migration Strategy

### Option A: Side-by-Side (Recommended)

**Week 1:**
- Build new TUI in `cli-tui/` directory
- Keep old Python CLI in `src/cli/`
- Both call same backend API

**Week 2:**
- Test TUI thoroughly
- Get user feedback
- Fix issues

**Week 3:**
- Switch default to TUI
- Mark Python CLI as deprecated
- Eventually remove old CLI

**Benefits:**
- ✅ No disruption to existing users
- ✅ Can compare side-by-side
- ✅ Gradual migration
- ✅ Easy rollback if needed

---

### Option B: Replace Immediately

**Week 1-2:**
- Build TUI
- Replace Python CLI completely
- Update documentation

**Benefits:**
- ✅ Cleaner codebase
- ✅ Focus on one implementation
- ❌ Risk if TUI has issues
- ❌ Users must adapt immediately

**Recommendation:** Option A (side-by-side)

---

## 📋 Checklist

### Pre-Development
- [ ] Review this plan
- [ ] Decide: Side-by-side or replace?
- [ ] Set up Node.js environment
- [ ] Install dependencies

### Development (Week 1)
- [ ] Day 1: Project setup, basic structure
- [ ] Day 2: SessionStart component
- [ ] Day 3: Question/Answer components
- [ ] Day 4: Quality feedback loop
- [ ] Day 5: Stage progress tracking
- [ ] Day 6: Live updates (SSE)
- [ ] Day 7: Testing & polish

### Testing (Week 2)
- [ ] Unit tests for all components
- [ ] Integration tests for full flow
- [ ] Manual testing with real backend
- [ ] Performance testing (large responses)
- [ ] Error handling testing
- [ ] Cross-terminal testing (iTerm, Windows Terminal, etc.)

### Documentation
- [ ] TUI user guide
- [ ] Keyboard shortcuts reference
- [ ] Troubleshooting guide
- [ ] Migration guide (from old CLI)
- [ ] Video demo

### Deployment
- [ ] Build script
- [ ] Distribution (npm? standalone binary?)
- [ ] Auto-update mechanism
- [ ] Analytics (optional)

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Can complete full 5-stage session
- ✅ Quality feedback works in real-time
- ✅ Live progress during LLM calls
- ✅ Keyboard navigation smooth
- ✅ Error handling graceful
- ✅ Works on all major terminals

### Non-Functional Requirements
- ✅ Startup time < 1 second
- ✅ Responsive (updates < 100ms)
- ✅ Memory usage < 100MB
- ✅ No UI "breaking" or artifacts
- ✅ Beautiful and professional design

### User Experience
- ✅ Intuitive without documentation
- ✅ Clear visual feedback
- ✅ Recoverable from errors
- ✅ "Feels modern" (like Claude Code)

---

## 🔥 Quick Start (After Implementation)

```bash
# Install
npm install -g uaip-cli

# Run
uaip start "My AI Project"

# Or with local development
cd cli-tui
npm run dev
```

---

## 📊 Comparison to Claude Code

| Feature | Claude Code | Our TUI | Status |
|---------|-------------|---------|--------|
| **Framework** | Ink + React | Ink + React | ✅ Same |
| **Language** | TypeScript | TypeScript | ✅ Same |
| **Layout** | Yoga | Yoga | ✅ Same |
| **State** | Custom | Zustand | ✅ Similar |
| **Live Updates** | Yes | SSE/WebSocket | ✅ Planned |
| **Keyboard Nav** | Yes | Yes | ✅ Planned |
| **Components** | Modular | Modular | ✅ Planned |
| **Testing** | Comprehensive | Vitest | ✅ Planned |

---

## 💡 Future Enhancements

### Phase 2 (After MVP)
- **Voice Input:** Speak answers instead of typing
- **AI Suggestions:** Auto-complete based on similar projects
- **Themes:** Light/dark modes, custom colors
- **Shortcuts:** Vim-style keybindings
- **Session Recording:** Replay sessions for training
- **Collaborative Mode:** Multiple users in same session

### Advanced Features
- **Rich Media:** Display charts/graphs in terminal
- **Split Panes:** Show progress + question simultaneously
- **History:** Navigate previous answers with arrow keys
- **Templates:** Pre-fill answers from templates
- **Export:** Generate charter in real-time as you answer

---

## 🎖️ Team Roles

### Solo Developer
- Week 1: Build TUI components
- Week 2: Polish + test + deploy

### With Team
- **Frontend Dev:** TUI components (Days 1-5)
- **Backend Dev:** SSE endpoints, WebSocket (Days 1-3)
- **Designer:** UI mockups, component design (Days 1-2)
- **QA:** Testing, cross-platform (Days 6-7)

---

## 📞 Next Steps

1. **Review this plan** - Does this approach make sense?
2. **Decide on timeline** - Start now or after P2?
3. **Set up environment** - Node.js, TypeScript, Ink
4. **Build prototype** - Simple Q&A flow (1 day)
5. **Iterate** - Add features incrementally

---

**Status:** Ready to implement
**Estimated Time:** 1-2 weeks
**Priority:** HIGH (Better UX = Better adoption)
**Risk:** LOW (Proven stack, clear plan)

Let's build something beautiful! ✨
