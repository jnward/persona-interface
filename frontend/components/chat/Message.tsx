import styles from './Message.module.css';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
}

export default function Message({ role, content }: MessageProps) {
  return (
    <div className={`${styles.message} ${styles[role]}`}>
      <div className={styles.role}>{role === 'user' ? 'You' : 'Assistant'}</div>
      <div className={styles.content}>{content}</div>
    </div>
  );
}