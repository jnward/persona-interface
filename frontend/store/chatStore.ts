import { create } from 'zustand';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatState {
  messages: Message[];
  isGenerating: boolean;
  error: string | null;
  numTokens: number;

  // Actions
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  setNumTokens: (tokens: number) => void;
  removeLastMessage: () => void;
  updateLastMessage: (content: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isGenerating: false,
  error: null,
  numTokens: 50,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  clearMessages: () =>
    set({ messages: [] }),

  setGenerating: (isGenerating) =>
    set({ isGenerating }),

  setError: (error) =>
    set({ error }),

  setNumTokens: (tokens) =>
    set({ numTokens: tokens }),

  removeLastMessage: () =>
    set((state) => ({
      messages: state.messages.slice(0, -1)
    })),

  updateLastMessage: (content) =>
    set((state) => {
      if (state.messages.length === 0) return state;
      const messages = [...state.messages];
      messages[messages.length - 1].content = content;
      return { messages };
    }),
}));