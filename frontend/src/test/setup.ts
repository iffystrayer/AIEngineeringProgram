import '@testing-library/jest-dom'
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock EventSource
class MockEventSource {
  onmessage: ((event: any) => void) | null = null
  onerror: ((event: any) => void) | null = null

  constructor(public url: string) {}

  close = vi.fn()
  addEventListener = vi.fn()
  removeEventListener = vi.fn()
}

Object.defineProperty(window, 'EventSource', {
  writable: true,
  value: MockEventSource,
})

