import { describe, it, expect, beforeEach, vi } from 'vitest';
import { waitFor } from '../test-utils';
import { renderHook, act } from '@testing-library/react';

// Create mock client using vi.hoisted - all data must be defined inside
const mockClient = vi.hoisted(() => {
  const wizardStartResponse = {
    session_id: 'test-session-123',
    current_step: 0,
    total_steps: 6,
    current_step_info: {
      step: 0,
      title: 'Project Basics',
      description: 'Configure basic project settings',
    },
    current_answers: {},
  };

  const wizardStepResponse = {
    session_id: 'test-session-123',
    current_step: 1,
    is_complete: false,
    validation_errors: [],
    current_step_info: {
      step: 1,
      title: 'Next Step',
    },
    current_answers: {},
  };

  const wizardGenerateResponse = {
    success: true,
    destination: '/tmp/test-project',
    message: 'Project generated successfully',
  };

  const wizardCancelResponse = {
    success: true,
    message: 'Session cancelled',
  };

  return {
    connect: vi.fn().mockResolvedValue(undefined),
    disconnect: vi.fn().mockResolvedValue(undefined),

    listTools: vi.fn().mockResolvedValue([
      { name: 'wizard_start', description: 'Start wizard session' },
      { name: 'wizard_step', description: 'Advance wizard step' },
    ]),

    listResources: vi.fn().mockResolvedValue([
      { uri: 'riso://catalog/modules', name: 'Module Catalog' },
    ]),

    listPrompts: vi.fn().mockResolvedValue([]),

    callTool: vi.fn().mockImplementation((name: string) => {
      const responses: Record<string, unknown> = {
        wizard_start: wizardStartResponse,
        wizard_step: wizardStepResponse,
        wizard_generate: wizardGenerateResponse,
        wizard_cancel: wizardCancelResponse,
      };
      const data = responses[name] || {};
      return Promise.resolve({
        content: [{ type: 'text', text: JSON.stringify(data) }],
        isError: false,
      });
    }),

    readResource: vi.fn().mockImplementation((uri: string) => {
      if (uri === 'riso://catalog/modules') {
        return Promise.resolve([{
          uri,
          text: JSON.stringify({ modules: { cli: {}, api: {} } }),
          mimeType: 'application/json',
        }]);
      }
      return Promise.resolve([{ uri, text: '{}' }]);
    }),

    getPrompt: vi.fn().mockResolvedValue([]),

    wizardStart: vi.fn().mockResolvedValue(wizardStartResponse),
    wizardStep: vi.fn().mockResolvedValue(wizardStepResponse),
    wizardStatus: vi.fn().mockResolvedValue({
      session_id: 'test-session-123',
      current_step: 0,
      total_steps: 6,
      is_complete: false,
      current_answers: {},
    }),
    wizardGenerate: vi.fn().mockResolvedValue(wizardGenerateResponse),
    wizardCancel: vi.fn().mockResolvedValue(wizardCancelResponse),

    getTemplateCatalog: vi.fn().mockResolvedValue({ modules: {} }),
    getSampleConfig: vi.fn().mockResolvedValue('{}'),
    listSamples: vi.fn().mockResolvedValue('default\nfull-stack'),
    generateProject: vi.fn().mockResolvedValue({
      success: true,
      destination: '/tmp/test-project',
    }),

    connected: true,
    serverUrl: 'http://localhost:3000',
    wizardStepResponse, // Export for test access
  };
});

// Mock the MCP client module
vi.mock('@/lib/mcp-client', () => ({
  RisoMCPClient: vi.fn().mockImplementation(() => mockClient),
  getMCPClient: vi.fn(() => mockClient),
  resetMCPClient: vi.fn().mockResolvedValue(undefined),
}));

// Import after mocking
import { MCPProvider, useMCP, useMCPWizard } from '@/lib/useMCP';

describe('MCP Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockClient.connected = true;
  });

  describe('Connection Management', () => {
    it('provides connection state through context', async () => {
      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider>{children}</MCPProvider>,
      });

      expect(result.current.connected).toBe(false);
      expect(result.current.connecting).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('connects to MCP server on demand', async () => {
      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider>{children}</MCPProvider>,
      });

      await act(async () => {
        await result.current.connect();
      });

      expect(mockClient.connect).toHaveBeenCalledTimes(1);
      expect(result.current.connected).toBe(true);
    });

    it('auto-connects when autoConnect is true', async () => {
      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(mockClient.connect).toHaveBeenCalledTimes(1);
      });

      expect(result.current.connected).toBe(true);
    });

    it('handles connection errors gracefully', async () => {
      mockClient.connect.mockRejectedValueOnce(new Error('Connection refused'));

      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider>{children}</MCPProvider>,
      });

      await act(async () => {
        await result.current.connect();
      });

      expect(result.current.connected).toBe(false);
      expect(result.current.error).toContain('Connection refused');
    });

    it('disconnects from MCP server', async () => {
      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current.connected).toBe(true);
      });

      await act(async () => {
        await result.current.disconnect();
      });

      expect(mockClient.disconnect).toHaveBeenCalledTimes(1);
      expect(result.current.connected).toBe(false);
    });
  });

  describe('Wizard Workflow', () => {
    it('starts a wizard session', async () => {
      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        const success = await result.current.start();
        expect(success).toBe(true);
      });

      expect(mockClient.wizardStart).toHaveBeenCalledTimes(1);
      expect(result.current.sessionId).toBe('test-session-123');
      expect(result.current.currentStep).toBe(0);
      expect(result.current.totalSteps).toBe(6);
      expect(result.current.active).toBe(true);
    });

    it('starts wizard with preset', async () => {
      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        await result.current.start('full-stack');
      });

      expect(mockClient.wizardStart).toHaveBeenCalledWith('full-stack');
    });

    it('handles validation errors from MCP', async () => {
      mockClient.wizardStep.mockResolvedValueOnce({
        ...mockClient.wizardStepResponse,
        validation_errors: ['Project name is required', 'Invalid layout choice'],
      });

      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        await result.current.start();
      });

      await act(async () => {
        await result.current.step({ project_name: '' });
      });

      expect(result.current.error).toContain('Project name is required');
    });

    it('detects wizard completion', async () => {
      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        await result.current.start();
      });

      // Mock completion response
      mockClient.wizardStep.mockResolvedValueOnce({
        ...mockClient.wizardStepResponse,
        is_complete: true,
        current_step: 6,
      });

      await act(async () => {
        await result.current.step({ final_answer: 'yes' });
      });

      expect(result.current.complete).toBe(true);
      expect(result.current.currentStep).toBe(6);
    });

    it('generates project from wizard', async () => {
      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        await result.current.start();
      });

      let genResult: { success: boolean; destination?: string; message?: string } | null = null;
      await act(async () => {
        genResult = await result.current.generate('/tmp/my-project', false);
      });

      expect(genResult).not.toBeNull();
      expect(genResult!.success).toBe(true);
      expect(genResult!.destination).toBe('/tmp/test-project');
      expect(mockClient.wizardGenerate).toHaveBeenCalledWith(
        'test-session-123',
        '/tmp/my-project',
        false
      );
    });

    it('cancels wizard session', async () => {
      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        await result.current.start();
      });

      expect(result.current.sessionId).toBe('test-session-123');

      await act(async () => {
        await result.current.cancel();
      });

      expect(mockClient.wizardCancel).toHaveBeenCalledWith('test-session-123');
      expect(result.current.sessionId).toBe(null);
      expect(result.current.active).toBe(false);
    });

    it('requires connection before starting wizard', async () => {
      mockClient.connected = false;

      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider>{children}</MCPProvider>,
      });

      await act(async () => {
        const success = await result.current.start();
        expect(success).toBe(false);
      });

      expect(result.current.error).toContain('Not connected');
      expect(mockClient.wizardStart).not.toHaveBeenCalled();
    });
  });

  describe('Tool Calls', () => {
    it('lists available tools', async () => {
      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current.connected).toBe(true);
      });

      let tools;
      await act(async () => {
        tools = await result.current.client.listTools();
      });

      expect(mockClient.listTools).toHaveBeenCalledTimes(1);
      expect(tools).toHaveLength(2);
      expect(tools).toEqual(expect.arrayContaining([
        expect.objectContaining({ name: 'wizard_start' }),
        expect.objectContaining({ name: 'wizard_step' }),
      ]));
    });

    it('reads resources from MCP', async () => {
      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current.connected).toBe(true);
      });

      let catalog;
      await act(async () => {
        catalog = await result.current.client.getTemplateCatalog();
      });

      expect(mockClient.getTemplateCatalog).toHaveBeenCalledTimes(1);
      expect(catalog).toHaveProperty('modules');
    });

    it('handles resource read errors', async () => {
      mockClient.readResource.mockRejectedValueOnce(new Error('Resource not found'));

      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current.connected).toBe(true);
      });

      await expect(async () => {
        await result.current.client.readResource('riso://invalid');
      }).rejects.toThrow('Resource not found');
    });
  });

  describe('Error Handling', () => {
    it('handles network timeouts', async () => {
      mockClient.connect.mockImplementationOnce(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Connection timeout')), 100);
        });
      });

      const { result } = renderHook(() => useMCP(), {
        wrapper: ({ children }) => <MCPProvider>{children}</MCPProvider>,
      });

      await act(async () => {
        await result.current.connect();
      });

      expect(result.current.error).toContain('Connection timeout');
    });

    it('handles generation failures', async () => {
      const { result } = renderHook(() => useMCPWizard(), {
        wrapper: ({ children }) => <MCPProvider autoConnect>{children}</MCPProvider>,
      });

      await waitFor(() => {
        expect(result.current).toBeDefined();
      });

      await act(async () => {
        await result.current.start();
      });

      const sessionId = result.current.sessionId;

      // Mock generation failure after session is established
      mockClient.wizardGenerate.mockResolvedValueOnce({
        success: false,
        message: 'Destination already exists',
      });

      await act(async () => {
        await result.current.generate();
      });

      expect(result.current.sessionId).toBe(sessionId);
      expect(result.current.error).toContain('Destination already exists');
    });
  });
});
