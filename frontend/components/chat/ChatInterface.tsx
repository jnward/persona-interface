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
    setError,
    appendToAssistantMessage,
    setContinuationIndex,
    continuationIndex
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
        content: response.content,
        terminating: response.terminating
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleContinue = async (index: number) => {
    if (isGenerating) return;

    setError(null);
    setGenerating(true);
    setContinuationIndex(index);

    try {
      const currentMessages = useChatStore.getState().messages;
      const lastIndex = currentMessages.length - 1;

      if (
        index !== lastIndex ||
        currentMessages[index]?.role !== 'assistant' ||
        currentMessages[index]?.terminating !== false
      ) {
        throw new Error('Message is not eligible for continuation');
      }

      const response = await generateText(
        currentMessages,
        getPCValues(),
        numTokens,
        true
      );

      appendToAssistantMessage(index, response.content, response.terminating);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
      setContinuationIndex(null);
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
          messages.map((msg, idx) => {
            const canContinue =
              msg.role === 'assistant' &&
              msg.terminating === false &&
              idx === messages.length - 1;

            return (
              <Message
                key={idx}
                role={msg.role}
                content={msg.content}
                terminating={msg.terminating}
                onContinue={canContinue ? () => handleContinue(idx) : undefined}
                isContinuing={continuationIndex === idx && isGenerating}
              />
            );
          })
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
