'use client';

import { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useSteeringStore } from '@/store/steeringStore';
import { generateText } from '@/lib/api';
import Message from './Message';
import InputArea from './InputArea';
import styles from './ChatInterface.module.css';

export default function ChatInterface() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const {
    messages,
    isGenerating,
    error,
    numTokens,
    addMessage,
    clearMessages,
    setGenerating,
    setError
  } = useChatStore();

  const { getPCValues } = useSteeringStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (content: string) => {
    // Add user message
    const userMessage = { role: 'user' as const, content };
    addMessage(userMessage);
    setError(null);

    // Generate response
    setGenerating(true);
    try {
      const updatedMessages = [...messages, userMessage];
      const response = await generateText(
        updatedMessages,
        getPCValues(),
        numTokens,
        false
      );

      addMessage({
        role: 'assistant',
        content: response.content
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Chat</h2>
        <button
          className={styles.clearButton}
          onClick={clearMessages}
          disabled={isGenerating || messages.length === 0}
        >
          Clear
        </button>
      </div>

      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.placeholder}>
            Start a conversation by typing a message below
          </div>
        ) : (
          messages.map((msg, idx) => (
            <Message key={idx} role={msg.role} content={msg.content} />
          ))
        )}
        {isGenerating && (
          <div className={styles.generating}>Generating...</div>
        )}
        {error && (
          <div className={styles.error}>Error: {error}</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <InputArea
        onSend={handleSend}
        disabled={isGenerating}
        placeholder="Type your message..."
      />
    </div>
  );
}