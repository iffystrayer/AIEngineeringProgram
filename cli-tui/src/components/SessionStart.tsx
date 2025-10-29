import React, { useState } from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';
import Spinner from 'ink-spinner';
import chalk from 'chalk';
import { useStore } from '../state/store.js';
import { apiClient } from '../utils/api.js';

export const SessionStart: React.FC = () => {
  const [step, setStep] = useState<'user_id' | 'project_name' | 'creating'>('user_id');
  const [userId, setUserId] = useState('');
  const [projectName, setProjectName] = useState('');

  const { setSession, setLoading, setError, setCurrentView } = useStore();

  const handleUserIdSubmit = (value: string) => {
    if (value.trim()) {
      setUserId(value.trim());
      setStep('project_name');
    }
  };

  const handleProjectNameSubmit = async (value: string) => {
    if (value.trim()) {
      setProjectName(value.trim());
      setStep('creating');
      setLoading(true);

      try {
        const session = await apiClient.createSession(userId, value.trim());
        setSession(session);
        setLoading(false);
        setCurrentView('question');
      } catch (error) {
        setLoading(false);
        setError(error instanceof Error ? error.message : 'Failed to create session');
        setStep('user_id');
      }
    }
  };

  return (
    <Box flexDirection="column" padding={1}>
      <Box marginBottom={1}>
        <Text bold color="cyan">
          🚀 U-AIP Scoping Assistant - New Session
        </Text>
      </Box>

      <Box marginBottom={1}>
        <Text dimColor>
          Let's create your AI Project Charter through a guided interview process.
        </Text>
      </Box>

      {step === 'user_id' && (
        <Box flexDirection="column" marginTop={1}>
          <Box marginBottom={1}>
            <Text>
              {chalk.bold('Enter your user ID:')} {chalk.dim('(e.g., your email or username)')}
            </Text>
          </Box>
          <Box>
            <Text color="green">❯ </Text>
            <TextInput
              value={userId}
              onChange={setUserId}
              onSubmit={handleUserIdSubmit}
              placeholder="user@example.com"
            />
          </Box>
        </Box>
      )}

      {step === 'project_name' && (
        <Box flexDirection="column" marginTop={1}>
          <Box marginBottom={1}>
            <Text dimColor>User ID: {userId} ✓</Text>
          </Box>
          <Box marginBottom={1}>
            <Text>
              {chalk.bold('Enter your project name:')} {chalk.dim('(describe what you want to build)')}
            </Text>
          </Box>
          <Box>
            <Text color="green">❯ </Text>
            <TextInput
              value={projectName}
              onChange={setProjectName}
              onSubmit={handleProjectNameSubmit}
              placeholder="Customer Churn Prediction System"
            />
          </Box>
        </Box>
      )}

      {step === 'creating' && (
        <Box marginTop={1}>
          <Text color="green">
            <Spinner type="dots" />
          </Text>
          <Text> Creating your session...</Text>
        </Box>
      )}
    </Box>
  );
};
