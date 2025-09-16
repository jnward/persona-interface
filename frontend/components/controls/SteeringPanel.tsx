'use client';

import { useSteeringStore } from '@/store/steeringStore';
import PCSlider from './PCSlider';
import styles from './SteeringPanel.module.css';

export default function SteeringPanel() {
  const { resetAll, pcValues } = useSteeringStore();

  const hasAnyValues = Object.keys(pcValues).some(key => pcValues[Number(key)] !== 0);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>PC Steering Controls</h2>
        <button
          className={styles.resetAllButton}
          onClick={resetAll}
          disabled={!hasAnyValues}
        >
          Reset All
        </button>
      </div>

      <div className={styles.sliders}>
        {Array.from({ length: 10 }, (_, i) => (
          <PCSlider
            key={i}
            pcIndex={i}
            label={`PC${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}