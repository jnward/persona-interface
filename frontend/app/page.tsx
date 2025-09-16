'use client';

import ChatInterface from '@/components/chat/ChatInterface';
import SteeringPanel from '@/components/controls/SteeringPanel';
import TokenControls from '@/components/controls/TokenControls';
import styles from './page.module.css';

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <h1>Persona Steering Interface</h1>
        <p>Control Gemma-3-12b behavior with PC-based steering</p>
      </div>

      <div className={styles.content}>
        <div className={styles.leftColumn}>
          <ChatInterface />
        </div>

        <div className={styles.rightColumn}>
          <TokenControls />
          <SteeringPanel />
        </div>
      </div>
    </main>
  );
}