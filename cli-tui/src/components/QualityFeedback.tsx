import React, { useState } from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';
import Spinner from 'ink-spinner';
import chalk from 'chalk';
import { useStore } from '../state/store.js';
import { apiClient } from '../utils/api.js';

export const QualityFeedback: React.FC = () => {
  const [improvedAnswer, setImprovedAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    session,
    currentQuestion,
    currentStage,
    answers,
    addAnswer,
    setCurrentQuestion,
    setError,
    setCurrentView,
  } = useStore();

  // Get the last answer for the current question
  const lastAnswer = answers.length > 0 ? answers[answers.length - 1] : null;

  const handleResubmit = async (value: string) => {
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
        // Still needs improvement - stay in feedback view
        setImprovedAnswer('');
      } else {
        // Accepted - move to next question
        setCurrentQuestion(null);
        setImprovedAnswer('');
        setCurrentView('question');
      }

      setIsSubmitting(false);
    } catch (error) {
      setIsSubmitting(false);
      setError(error instanceof Error ? error.message : 'Failed to submit answer');
    }
  };

  if (!lastAnswer || !lastAnswer.feedback) {
    return null;
  }

  return (
    <Box flexDirection="column" padding={1}>
      {/* Feedback header */}
      <Box marginBottom={1}>
        <Text bold color="yellow">
          ⚠️  Response Quality Feedback
        </Text>
      </Box>

      {/* Quality score */}
      {lastAnswer.qualityScore !== undefined && (
        <Box marginBottom={1}>
          <Text>
            Quality Score: {formatScore(lastAnswer.qualityScore)}
          </Text>
        </Box>
      )}

      {/* Feedback message */}
      <Box marginBottom={1} flexDirection="column">
        <Text color="yellow">{lastAnswer.feedback}</Text>
      </Box>

      {/* Original answer */}
      <Box marginBottom={1} flexDirection="column">
        <Text dimColor>Your previous answer:</Text>
        <Box paddingLeft={2}>
          <Text italic>"{lastAnswer.text}"</Text>
        </Box>
      </Box>

      {/* Improved answer input */}
      {!isSubmitting ? (
        <Box flexDirection="column">
          <Box marginBottom={1}>
            <Text bold>Please provide a more detailed response:</Text>
          </Box>
          <Box>
            <Text color="green">❯ </Text>
            <TextInput
              value={improvedAnswer}
              onChange={setImprovedAnswer}
              onSubmit={handleResubmit}
              placeholder="Improved answer..."
            />
          </Box>
        </Box>
      ) : (
        <Box>
          <Text color="green">
            <Spinner type="dots" />
          </Text>
          <Text> Re-analyzing your response...</Text>
        </Box>
      )}
    </Box>
  );
};

function formatScore(score: number): string {
  const emoji = score >= 8 ? '🟢' : score >= 6 ? '🟡' : '🔴';
  const color = score >= 8 ? 'green' : score >= 6 ? 'yellow' : 'red';
  return chalk[color](`${emoji} ${score.toFixed(1)}/10`);
}
