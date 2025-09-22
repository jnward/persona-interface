import styles from './Message.module.css';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  terminating?: boolean;
  onContinue?: () => void;
  isContinuing?: boolean;
}

export default function Message({
  role,
  content,
  terminating = true,
  onContinue,
  isContinuing = false
}: MessageProps) {
  return (
    <div className={`${styles.message} ${styles[role]}`}>
      <div className={styles.role}>{role === 'user' ? 'You' : 'Assistant'}</div>
      <div className={styles.content}>{content}</div>
      {role === 'assistant' && !terminating && onContinue && (
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
