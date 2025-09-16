import { create } from 'zustand';

interface SteeringState {
  pcValues: Record<number, number>;

  // Actions
  setPCValue: (pcIndex: number, value: number) => void;
  resetPC: (pcIndex: number) => void;
  resetAll: () => void;
  getPCValues: () => Record<string, number>;
}

export const useSteeringStore = create<SteeringState>((set, get) => ({
  pcValues: {},

  setPCValue: (pcIndex, value) =>
    set((state) => ({
      pcValues: {
        ...state.pcValues,
        [pcIndex]: value
      }
    })),

  resetPC: (pcIndex) =>
    set((state) => {
      const newValues = { ...state.pcValues };
      delete newValues[pcIndex];
      return { pcValues: newValues };
    }),

  resetAll: () =>
    set({ pcValues: {} }),

  getPCValues: () => {
    // Convert to string keys for API
    const values = get().pcValues;
    const result: Record<string, number> = {};
    Object.entries(values).forEach(([key, value]) => {
      if (Math.abs(value) > 1) { // Only include non-zero values
        result[key] = value;
      }
    });
    return result;
  }
}));