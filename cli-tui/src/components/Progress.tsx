import React from 'react';
import { Box, Text } from 'ink';
import chalk from 'chalk';
import { useStore } from '../state/store.js';

export const Progress: React.FC = () => {
  const { currentStage, totalStages, stageProgress } = useStore();

  const percentage = Math.round(((currentStage - 1) / totalStages) * 100 + (stageProgress / totalStages));

  return (
    <Box flexDirection="column">
      {/* Progress bar */}
      <Box marginBottom={1}>
        <Text>{renderProgressBar(percentage)}</Text>
      </Box>

      {/* Stage indicators */}
      <Box>
        {Array.from({ length: totalStages }, (_, i) => {
          const stageNum = i + 1;
          const isComplete = stageNum < currentStage;
          const isCurrent = stageNum === currentStage;
          const isPending = stageNum > currentStage;

          return (
            <Box key={stageNum} marginRight={1}>
              {isComplete && <Text color="green">✓ {stageNum}</Text>}
              {isCurrent && <Text bold color="cyan">● {stageNum}</Text>}
              {isPending && <Text dimColor>○ {stageNum}</Text>}
            </Box>
          );
        })}
      </Box>

      {/* Stage labels */}
      <Box marginTop={1}>
        <Text dimColor>{getStageLabel(currentStage)}</Text>
      </Box>
    </Box>
  );
};

function renderProgressBar(percentage: number, width: number = 40): string {
  const filled = Math.round((width * percentage) / 100);
  const empty = width - filled;

  const filledBar = chalk.green('█'.repeat(filled));
  const emptyBar = chalk.gray('░'.repeat(empty));

  return `${filledBar}${emptyBar} ${percentage}%`;
}

function getStageLabel(stage: number): string {
  const labels = {
    1: 'Stage 1: Business Context & Objectives',
    2: 'Stage 2: Value Proposition & Success Metrics',
    3: 'Stage 3: Data Assessment & Readiness',
    4: 'Stage 4: User Experience & Stakeholder Analysis',
    5: 'Stage 5: Ethics, Risks & Governance',
  };
  return labels[stage as keyof typeof labels] || 'Complete';
}
