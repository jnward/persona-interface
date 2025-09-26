'use client';

import { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useSteeringStore } from '@/store/steeringStore';
import { generateText, generateUserMessage } from '@/lib/api';
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
    appendToMessage,
    setContinuationIndex,
    continuationIndex,
    autoRun,
    setAutoRun
  } = useChatStore();

  const { getPCValues } = useSteeringStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateAssistantMessage = async (
    options: { manageGenerating?: boolean } = {}
  ) => {
    const { manageGenerating = true } = options;
    if (manageGenerating) {
      setGenerating(true);
    }

    try {
      const currentMessages = useChatStore.getState().messages;
      const lastMessage = currentMessages[currentMessages.length - 1];

      if (!lastMessage || lastMessage.role !== 'user') {
        throw new Error('Cannot generate assistant response without a user message');
      }

      const response = await generateText(
        currentMessages,
        getPCValues(),
        numTokens,
        false
      );

      addMessage({
        role: 'assistant',
        content: response.content,
        terminating: response.terminating
      });

      return response;
    } finally {
      if (manageGenerating) {
        setGenerating(false);
      }
    }
  };

  const handleSend = async (content: string) => {
    if (isGenerating) return;

    const userMessage = { role: 'user' as const, content };
    addMessage(userMessage);
    setError(null);
    setGenerating(true);

    try {
      await generateAssistantMessage({ manageGenerating: false });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateUserMessage = async () => {
    if (isGenerating) return;

    setError(null);
    setGenerating(true);

    try {
      const currentMessages = useChatStore.getState().messages;

      const response = await generateUserMessage(
        currentMessages,
        numTokens,
        false
      );

      addMessage({
        role: 'user',
        content: response.content,
        terminating: response.terminating,
        generatedByModel: true
      });

      if (response.terminating) {
        await generateAssistantMessage({ manageGenerating: false });
      }
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

      const targetMessage = currentMessages[index];
      const isAssistantMessage = targetMessage?.role === 'assistant';
      const isGeneratedUser =
        targetMessage?.role === 'user' && targetMessage.generatedByModel;

      if (
        index !== lastIndex ||
        !targetMessage ||
        !(isAssistantMessage || isGeneratedUser) ||
        targetMessage.terminating !== false
      ) {
        throw new Error('Message is not eligible for continuation');
      }

      const response = isAssistantMessage
        ? await generateText(
            currentMessages,
            getPCValues(),
            numTokens,
            true
          )
        : await generateUserMessage(
            currentMessages,
            numTokens,
            true
          );

      appendToMessage(index, response.content, response.terminating);

      if (!isAssistantMessage && response.terminating) {
        await generateAssistantMessage({ manageGenerating: false });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGenerating(false);
      setContinuationIndex(null);
    }
  };

  useEffect(() => {
    if (!autoRun || isGenerating || error) {
      return;
    }

    const runAuto = async () => {
      const currentMessages = useChatStore.getState().messages;

      if (currentMessages.length === 0) {
        await handleGenerateUserMessage();
        return;
      }

      const lastIndex = currentMessages.length - 1;
      const lastMessage = currentMessages[lastIndex];
      const isModelGeneratedUser =
        lastMessage.role === 'user' && lastMessage.generatedByModel;
      const canContinue =
        lastMessage.terminating === false &&
        (lastMessage.role === 'assistant' || isModelGeneratedUser);

      if (canContinue) {
        await handleContinue(lastIndex);
        return;
      }

      if (isModelGeneratedUser && lastMessage.terminating !== false) {
        await generateAssistantMessage();
        return;
      }

      if (lastMessage.role === 'assistant' && lastMessage.terminating !== false) {
        await handleGenerateUserMessage();
      }
    };

    void runAuto();
  }, [autoRun, isGenerating, messages, error]);

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
            const isModelGeneratedUser =
              msg.role === 'user' && msg.generatedByModel;
            const canContinue =
              idx === messages.length - 1 &&
              msg.terminating === false &&
              (msg.role === 'assistant' || isModelGeneratedUser);

            return (
              <Message
                key={idx}
                role={msg.role}
                content={msg.content}
                terminating={msg.terminating}
                generatedByModel={msg.generatedByModel}
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
        onGenerateUserMessage={handleGenerateUserMessage}
        onToggleAutoRun={setAutoRun}
        autoRun={autoRun}
        disabled={isGenerating}
        placeholder="Type your message..."
      />
    </div>
  );
}
