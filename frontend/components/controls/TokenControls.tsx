'use client';

import { useChatStore } from '@/store/chatStore';
import styles from './TokenControls.module.css';

export default function TokenControls() {
  const { numTokens, setNumTokens } = useChatStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (value > 0 && value <= 500) {
      setNumTokens(value);
    }
  };

  return (
    <div className={styles.container}>
      <h3>Generation Settings</h3>

      <div className={styles.control}>
        <label htmlFor="tokens">Number of Tokens:</label>
        <input
          id="tokens"
          type="number"
          min="1"
          max="500"
          value={numTokens}
          onChange={handleChange}
          className={styles.input}
        />
        <span className={styles.hint}>1-500 tokens</span>
      </div>
    </div>
  );
}