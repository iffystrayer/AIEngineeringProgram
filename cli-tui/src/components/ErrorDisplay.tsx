import React from 'react';
import { Box, Text } from 'ink';

interface ErrorDisplayProps {
  error: string;
  onDismiss?: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onDismiss }) => {
  // Auto-dismiss after 5 seconds
  React.useEffect(() => {
    if (onDismiss) {
      const timer = setTimeout(() => {
        onDismiss();
      }, 5000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [onDismiss]);

  return (
    <Box
      flexDirection="column"
      padding={1}
      borderStyle="round"
      borderColor="red"
    >
      <Box marginBottom={1}>
        <Text bold color="red">
          ❌ Error
        </Text>
      </Box>
      <Box>
        <Text>{error}</Text>
      </Box>
      {onDismiss && (
        <Box marginTop={1}>
          <Text dimColor>Dismissing in 5 seconds...</Text>
        </Box>
      )}
    </Box>
  );
};
