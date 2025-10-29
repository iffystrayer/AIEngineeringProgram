import React, { useState } from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';
import Spinner from 'ink-spinner';
import { useStore } from '../state/store.js';
import { apiClient } from '../utils/api.js';

export const Question: React.FC = () => {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    session,
    currentQuestion,
    currentStage,
    addAnswer,
    setCurrentQuestion,
    setError,
    setCurrentView,
  } = useStore();

  const handleSubmit = async (value: string) => {
    if (!value.trim() || !session || !currentQuestion) return;

    setIsSubmitting(true);

    try {
      const response = await apiClient.submitAnswer(
        session.session_id,
        currentStage,
        currentQuestion.id,
        value.trim()
      );

      addAnswer({
        questionId: currentQuestion.id,
        text: value.trim(),
        qualityScore: response.quality_score,
        feedback: response.feedback,
      });

      if (response.needs_improvement && response.feedback) {
        // Show quality feedback view
        setCurrentView('quality-feedback');
      } else {
        // Move to next question or stage
        setCurrentQuestion(null);
        setAnswer('');
      }

      setIsSubmitting(false);
    } catch (error) {
      setIsSubmitting(false);
      setError(error instanceof Error ? error.message : 'Failed to submit answer');
    }
  };

  if (!currentQuestion) {
    return (
      <Box padding={1}>
        <Text color="green">
          <Spinner type="dots" />
        </Text>
        <Text> Loading next question...</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" padding={1}>
      {/* Progress indicator */}
      <Box marginBottom={1}>
        <Text dimColor>
          Stage {currentStage}/5 · {getStageLabel(currentStage)}
        </Text>
      </Box>

      {/* Question */}
      <Box marginBottom={1} flexDirection="column">
        <Text bold color="cyan">
          {currentQuestion.text}
        </Text>
        {currentQuestion.placeholder && (
          <Text dimColor italic>
            Example: {currentQuestion.placeholder}
          </Text>
        )}
      </Box>

      {/* Answer input */}
      {!isSubmitting ? (
        <Box flexDirection="column">
          <Box>
            <Text color="green">❯ </Text>
            <TextInput
              value={answer}
              onChange={setAnswer}
              onSubmit={handleSubmit}
              placeholder={currentQuestion.placeholder || 'Type your answer...'}
            />
          </Box>
          <Box marginTop={1}>
            <Text dimColor>
              {currentQuestion.multiline
                ? 'Press Ctrl+D when done, or Enter for single line'
                : 'Press Enter to submit'}
            </Text>
          </Box>
        </Box>
      ) : (
        <Box>
          <Text color="green">
            <Spinner type="dots" />
          </Text>
          <Text> Analyzing your response...</Text>
        </Box>
      )}
    </Box>
  );
};

function getStageLabel(stage: number): string {
  const labels = {
    1: 'Business Context',
    2: 'Value Proposition',
    3: 'Data Assessment',
    4: 'User & Stakeholders',
    5: 'Ethics & Governance',
  };
  return labels[stage as keyof typeof labels] || 'Unknown';
}
