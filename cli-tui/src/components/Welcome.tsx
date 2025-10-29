import React from 'react';
import { Box, Text } from 'ink';
import chalk from 'chalk';
import figures from 'figures';

interface WelcomeProps {
  onStart: () => void;
}

export const Welcome: React.FC<WelcomeProps> = ({ onStart }) => {
  // Auto-start after showing welcome
  React.useEffect(() => {
    const timer = setTimeout(() => {
      onStart();
    }, 2000);
    return () => clearTimeout(timer);
  }, [onStart]);

  return (
    <Box flexDirection="column" padding={2}>
      {/* Banner */}
      <Box marginBottom={1} justifyContent="center">
        <Text bold color="cyan">
          {`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🤖  U-AIP Scoping Assistant  🤖                  ║
║                                                           ║
║         AI Project Charter Generation Tool                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
          `}
        </Text>
      </Box>

      {/* Description */}
      <Box marginBottom={1} flexDirection="column" paddingX={2}>
        <Text>
          Welcome to the <Text bold color="cyan">Universal AI Project (U-AIP)</Text> Scoping Assistant!
        </Text>
        <Text> </Text>
        <Text dimColor>
          This interactive tool guides you through a structured 5-stage interview
          to create a comprehensive AI Project Charter.
        </Text>
      </Box>

      {/* Stages overview */}
      <Box marginBottom={1} flexDirection="column" paddingX={2}>
        <Text bold>The 5 Stages:</Text>
        <Text> </Text>
        <Text>{chalk.green(figures.pointer)} <Text bold>Stage 1:</Text> Business Context & Objectives</Text>
        <Text>{chalk.green(figures.pointer)} <Text bold>Stage 2:</Text> Value Proposition & Success Metrics</Text>
        <Text>{chalk.green(figures.pointer)} <Text bold>Stage 3:</Text> Data Assessment & Readiness</Text>
        <Text>{chalk.green(figures.pointer)} <Text bold>Stage 4:</Text> User Experience & Stakeholder Analysis</Text>
        <Text>{chalk.green(figures.pointer)} <Text bold>Stage 5:</Text> Ethics, Risks & Governance</Text>
      </Box>

      {/* Features */}
      <Box marginBottom={1} flexDirection="column" paddingX={2}>
        <Text bold>Features:</Text>
        <Text> </Text>
        <Text>✓ AI-powered quality validation</Text>
        <Text>✓ Real-time feedback and suggestions</Text>
        <Text>✓ Cross-stage consistency checking</Text>
        <Text>✓ Governance risk assessment</Text>
      </Box>

      {/* Loading message */}
      <Box marginTop={1} justifyContent="center">
        <Text dimColor>Starting in a moment...</Text>
      </Box>
    </Box>
  );
};
