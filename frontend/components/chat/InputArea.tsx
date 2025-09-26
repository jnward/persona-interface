'use client';

import { useState, KeyboardEvent } from 'react';
import styles from './InputArea.module.css';

interface InputAreaProps {
  onSend: (message: string) => void;
  onGenerateUserMessage: () => void;
  onToggleAutoRun: (value: boolean) => void;
  autoRun: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export default function InputArea({
  onSend,
  onGenerateUserMessage,
  onToggleAutoRun,
  autoRun,
  disabled,
  placeholder = 'Type a message...'
}: InputAreaProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.inputRow}>
        <textarea
          className={styles.textarea}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={3}
        />
        <button
          className={styles.sendButton}
          onClick={handleSend}
          disabled={disabled || !input.trim()}
        >
          Send
        </button>
      </div>
      <div className={styles.actionsRow}>
        <button
          type="button"
          className={styles.generateButton}
          onClick={onGenerateUserMessage}
          disabled={disabled}
        >
          Generate user message
        </button>
        <label className={styles.autoRunToggle}>
          <input
            type="checkbox"
            checked={autoRun}
            onChange={(event) => onToggleAutoRun(event.target.checked)}
          />
          Auto-run
        </label>
      </div>
    </div>
  );
}
