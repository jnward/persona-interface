'use client';

import { useSteeringStore } from '@/store/steeringStore';
import styles from './PCSlider.module.css';

interface PCSliderProps {
  pcIndex: number;
  label: string;
  description?: string;
  recommendedDirection?: string;
}

export default function PCSlider({ pcIndex, label, description, recommendedDirection }: PCSliderProps) {
  const { pcValues, setPCValue, resetPC } = useSteeringStore();
  const value = pcValues[pcIndex] || 0;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number(e.target.value);
    setPCValue(pcIndex, newValue);
  };

  const handleReset = () => {
    resetPC(pcIndex);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.labelGroup}>
          <label className={styles.label}>{label}</label>
          {description && (
            <span className={styles.description}>
              {description}
              {recommendedDirection && (
                <span className={styles.direction}>({recommendedDirection})</span>
              )}
            </span>
          )}
        </div>
        <span className={styles.value}>{value}</span>
      </div>

      <div className={styles.sliderRow}>
        <input
          type="range"
          className={styles.slider}
          min="-5000"
          max="5000"
          step="100"
          value={value}
          onChange={handleChange}
        />
        <button
          className={styles.resetButton}
          onClick={handleReset}
          disabled={value === 0}
        >
          Reset
        </button>
      </div>

      <div className={styles.labels}>
        <span>-5000</span>
        <span>0</span>
        <span>+5000</span>
      </div>
    </div>
  );
}