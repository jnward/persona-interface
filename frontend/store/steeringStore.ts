import { create } from 'zustand';

const DEFAULT_PC_VALUES: Record<number, number> = {
  0: 800,
  1: -1600,
  6: -1800
};

interface SteeringState {
  pcValues: Record<number, number>;

  // Actions
  setPCValue: (pcIndex: number, value: number) => void;
  resetPC: (pcIndex: number) => void;
  resetAll: () => void;
  randomize: () => void;
  getPCValues: () => Record<string, number>;
}

export const useSteeringStore = create<SteeringState>((set, get) => ({
  pcValues: { ...DEFAULT_PC_VALUES },

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

  randomize: () =>
    set(() => {
      const randomized: Record<number, number> = {};

      for (let i = 0; i < 10; i += 1) {
        if (Math.random() < 0.5) {
          continue;
        }

        const u1 = Math.random() || Number.EPSILON;
        const u2 = Math.random();
        const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        const value = Math.max(-3000, Math.min(3000, Math.round(z0 * 1250)));
        randomized[i] = value;
      }

      return { pcValues: randomized };
    }),

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
