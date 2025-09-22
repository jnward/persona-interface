import { create } from 'zustand';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  terminating?: boolean;
}

interface ChatState {
  messages: Message[];
  isGenerating: boolean;
  error: string | null;
  numTokens: number;
  continuationIndex: number | null;

  // Actions
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  setNumTokens: (tokens: number) => void;
  removeLastMessage: () => void;
  updateLastMessage: (content: string, terminating?: boolean) => void;
  appendToAssistantMessage: (index: number, content: string, terminating: boolean) => void;
  setContinuationIndex: (index: number | null) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isGenerating: false,
  error: null,
  numTokens: 50,
  continuationIndex: null,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  clearMessages: () =>
    set({ messages: [], continuationIndex: null }),

  setGenerating: (isGenerating) =>
    set({ isGenerating }),

  setError: (error) =>
    set({ error }),

  setNumTokens: (tokens) =>
    set({ numTokens: tokens }),

  removeLastMessage: () =>
    set((state) => ({
      messages: state.messages.slice(0, -1),
      continuationIndex: null
    })),

  updateLastMessage: (content, terminating) =>
    set((state) => {
      if (state.messages.length === 0) return state;
      const messages = [...state.messages];
      const lastIndex = messages.length - 1;
      const lastMessage = messages[lastIndex];
      messages[lastIndex] = {
        ...lastMessage,
        content,
        ...(terminating !== undefined ? { terminating } : {})
      };
      return { messages };
    }),

  appendToAssistantMessage: (index, content, terminating) =>
    set((state) => {
      if (index < 0 || index >= state.messages.length) return state;
      const target = state.messages[index];
      if (target.role !== 'assistant') return state;

      const messages = [...state.messages];
      messages[index] = {
        ...target,
        content: target.content + content,
        terminating
      };

      return { messages };
    }),

  setContinuationIndex: (index) =>
    set({ continuationIndex: index }),
}));
