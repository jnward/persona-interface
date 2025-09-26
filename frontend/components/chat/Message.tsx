import styles from './Message.module.css';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  terminating?: boolean;
  generatedByModel?: boolean;
  onContinue?: () => void;
  isContinuing?: boolean;
}

export default function Message({
  role,
  content,
  terminating = true,
  generatedByModel = false,
  onContinue,
  isContinuing = false
}: MessageProps) {
  const showContinueButton =
    !terminating &&
    onContinue &&
    (role === 'assistant' || generatedByModel);

  return (
    <div className={`${styles.message} ${styles[role]}`}>
      <div className={styles.roleRow}>
        <span className={styles.roleLabel}>{role === 'user' ? 'You' : 'Assistant'}</span>
        {generatedByModel && (
          <span className={styles.generatedTag}>model generated</span>
        )}
      </div>
      <div className={styles.content}>{content}</div>
      {showContinueButton && (
        <button
          type="button"
          className={styles.continueButton}
          onClick={onContinue}
          disabled={isContinuing}
        >
          {isContinuing ? 'Continuing…' : 'Continue message'}
        </button>
      )}
    </div>
  );
}
