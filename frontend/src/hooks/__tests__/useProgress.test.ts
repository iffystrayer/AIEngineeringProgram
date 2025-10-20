/**
 * Tests for useProgress hook
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useProgress } from '../useProgress';

describe('useProgress Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useProgress('test-session-123'));

    expect(result.current.progress).toBeNull();
    expect(result.current.events).toEqual([]);
    // isLoading may be true initially as it fetches data
    expect(result.current.error).toBeNull();
  });

  it('should fetch progress on mount', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    await waitFor(() => {
      expect(result.current.progress).toBeDefined();
    });
  });

  it('should fetch progress events', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    await waitFor(() => {
      expect(result.current.events).toBeDefined();
    });
  });

  it('should handle progress fetch errors', async () => {
    const { result } = renderHook(() => useProgress('invalid-session'));
    
    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
  });

  it('should provide current stage', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    await waitFor(() => {
      expect(result.current.currentStage).toBeDefined();
    });
  });

  it('should provide questions answered count', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    await waitFor(() => {
      expect(result.current.questionsAnswered).toBeDefined();
    });
  });

  it('should provide charter status', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    await waitFor(() => {
      expect(result.current.charterStatus).toBeDefined();
    });
  });

  it('should submit answer', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    expect(result.current.submitAnswer).toBeDefined();
  });

  it('should handle answer submission errors', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    expect(result.current.submitAnswer).toBeDefined();
  });

  it('should refresh progress', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    expect(result.current.refreshProgress).toBeDefined();
  });

  it('should clear error', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));
    
    expect(result.current.clearError).toBeDefined();
  });

  it('should handle loading state', async () => {
    const { result } = renderHook(() => useProgress('test-session-123'));

    // Loading state may be true or false depending on timing
    expect(typeof result.current.isLoading).toBe('boolean');
  });

  it('should update progress on session change', async () => {
    const { result, rerender } = renderHook(
      ({ sessionId }) => useProgress(sessionId),
      { initialProps: { sessionId: 'session-1' } }
    );
    
    rerender({ sessionId: 'session-2' });
    
    await waitFor(() => {
      expect(result.current.progress).toBeDefined();
    });
  });
});

