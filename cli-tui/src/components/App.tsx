import React from 'react';
import { Box, Text } from 'ink';
import { useStore } from '../state/store.js';
import { Welcome } from './Welcome.js';
import { SessionStart } from './SessionStart.js';
import { Question } from './Question.js';
import { QualityFeedback } from './QualityFeedback.js';
import { Progress } from './Progress.js';
import { ErrorDisplay } from './ErrorDisplay.js';

export const App: React.FC = () => {
  const { currentView, error, setCurrentView, setError } = useStore();

  const handleStartSession = () => {
    setCurrentView('session-start');
  };

  return (
    <Box flexDirection="column">
      {/* Error display (overlay) */}
      {error && (
        <Box marginBottom={1}>
          <ErrorDisplay error={error} onDismiss={() => setError(null)} />
        </Box>
      )}

      {/* Progress bar (shown during question flow) */}
      {(currentView === 'question' || currentView === 'quality-feedback') && (
        <Box marginBottom={1}>
          <Progress />
        </Box>
      )}

      {/* Main content based on current view */}
      {currentView === 'welcome' && <Welcome onStart={handleStartSession} />}

      {currentView === 'session-start' && <SessionStart />}

      {currentView === 'question' && <Question />}

      {currentView === 'quality-feedback' && <QualityFeedback />}

      {currentView === 'stage-complete' && (
        <Box padding={1}>
          <StageComplete />
        </Box>
      )}

      {currentView === 'final-complete' && (
        <Box padding={1}>
          <FinalComplete />
        </Box>
      )}
    </Box>
  );
};

// Stage completion component
const StageComplete: React.FC = () => {
  const { currentStage, setCurrentView } = useStore();

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentView('question');
    }, 3000);
    return () => clearTimeout(timer);
  }, [setCurrentView]);

  return (
    <Box flexDirection="column">
      <Box marginBottom={1}>
        <Text bold color="green">
          ✓ Stage {currentStage - 1} Complete!
        </Text>
      </Box>
      <Box>
        <Text dimColor>Moving to next stage...</Text>
      </Box>
    </Box>
  );
};

// Final completion component
const FinalComplete: React.FC = () => {
  return (
    <Box flexDirection="column" padding={2}>
      <Box marginBottom={1}>
        <Text bold color="green">
          🎉 Congratulations!
        </Text>
      </Box>
      <Box marginBottom={1}>
        <Text>
          You've completed all 5 stages of the U-AIP Scoping Assistant!
        </Text>
      </Box>
      <Box>
        <Text dimColor>
          Your AI Project Charter has been generated and saved.
        </Text>
      </Box>
    </Box>
  );
};
