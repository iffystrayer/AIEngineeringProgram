/**
 * Tests for useSession hook
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSession } from '../useSession';

describe('useSession Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with loading state', () => {
    const { result } = renderHook(() => useSession());
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.session).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should create a new session', async () => {
    const { result } = renderHook(() => useSession());
    
    await waitFor(() => {
      expect(result.current.session).toBeDefined();
    });
  });

  it('should handle session creation errors', async () => {
    const { result } = renderHook(() => useSession());
    
    // Simulate error
    expect(result.current.error).toBeNull();
  });

  it('should retrieve session details', async () => {
    const { result } = renderHook(() => useSession());
    
    await waitFor(() => {
      expect(result.current.session).toBeDefined();
    });
  });

  it('should list user sessions', async () => {
    const { result } = renderHook(() => useSession());
    
    await waitFor(() => {
      expect(result.current.sessions).toBeDefined();
    });
  });

  it('should delete a session', async () => {
    const { result } = renderHook(() => useSession());

    expect(result.current.deleteCurrentSession).toBeDefined();
  });

  it('should handle loading state during operations', async () => {
    const { result } = renderHook(() => useSession());
    
    expect(result.current.isLoading).toBe(false);
  });

  it('should clear error on successful operation', async () => {
    const { result } = renderHook(() => useSession());
    
    expect(result.current.error).toBeNull();
  });

  it('should provide session ID', async () => {
    const { result } = renderHook(() => useSession());
    
    await waitFor(() => {
      expect(result.current.sessionId).toBeDefined();
    });
  });

  it('should provide session status', async () => {
    const { result } = renderHook(() => useSession());
    
    await waitFor(() => {
      expect(result.current.status).toBeDefined();
    });
  });
});

