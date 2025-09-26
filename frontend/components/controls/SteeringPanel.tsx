'use client';

import { useSteeringStore } from '@/store/steeringStore';
import PCSlider from './PCSlider';
import styles from './SteeringPanel.module.css';

export default function SteeringPanel() {
  const { resetAll, randomize, pcValues } = useSteeringStore();

  const hasAnyValues = Object.keys(pcValues).some(key => pcValues[Number(key)] !== 0);

  // PC labels with their descriptions and recommended directions
  const pcLabels = [
    { name: 'PC1', desc: 'complexity', direction: 'neg' },
    { name: 'PC2', desc: 'roleplaying', direction: 'neg' },
    { name: 'PC3', desc: 'humanity', direction: 'pos' },
    { name: 'PC4', desc: 'emotion', direction: 'neg' },
    { name: 'PC5', desc: 'wisdom', direction: 'pos' },
    { name: 'PC6', desc: 'confidence', direction: 'neg' },
    { name: 'PC7', desc: 'naivete', direction: 'pos' },
    { name: 'PC8', desc: '', direction: '' },
    { name: 'PC9', desc: '', direction: '' },
    { name: 'PC10', desc: '', direction: '' },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>PC Steering Controls</h2>
        <div className={styles.actions}>
          <button
            type="button"
            className={styles.randomizeButton}
            onClick={randomize}
          >
            Randomize
          </button>
          <button
            type="button"
            className={styles.resetAllButton}
            onClick={resetAll}
            disabled={!hasAnyValues}
          >
            Reset All
          </button>
        </div>
      </div>

      <div className={styles.sliders}>
        {pcLabels.map((pc, i) => (
          <PCSlider
            key={i}
            pcIndex={i}
            label={pc.name}
            description={pc.desc}
            recommendedDirection={pc.direction}
          />
        ))}
      </div>
    </div>
  );
}
