import { useEffect, useState } from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import type { Toast as ToastType } from '@/contexts/ToastContext';

interface ToastProps {
  toast: ToastType;
  onRemove: (id: string) => void;
}

const iconMap = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const colorMap = {
  success: 'bg-[var(--toast-success-bg)] text-[var(--toast-success-text)] border-[var(--toast-success-border)]',
  error: 'bg-[var(--toast-error-bg)] text-[var(--toast-error-text)] border-[var(--toast-error-border)]',
  warning: 'bg-[var(--toast-warning-bg)] text-[var(--toast-warning-text)] border-[var(--toast-warning-border)]',
  info: 'bg-[var(--toast-info-bg)] text-[var(--toast-info-text)] border-[var(--toast-info-border)]',
};

export function Toast({ toast, onRemove }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false);
  const Icon = iconMap[toast.type];

  // Auto-dismiss timer
  useEffect(() => {
    if (toast.duration) {
      const timer = setTimeout(() => {
        setIsExiting(true);
      }, toast.duration);

      return () => clearTimeout(timer);
    }
  }, [toast.duration]);

  // Remove after exit animation
  useEffect(() => {
    if (isExiting) {
      const timer = setTimeout(() => {
        onRemove(toast.id);
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [isExiting, toast.id, onRemove]);

  const handleDismiss = () => {
    setIsExiting(true);
  };

  return (
    <div
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      className={`
        ${colorMap[toast.type]}
        font-mono font-bold text-sm
        border-2 shadow-hard
        p-4 rounded-lg
        flex items-start gap-3
        transition-all duration-300 theme-aware
        ${isExiting ? 'toast-exit' : 'toast-enter'}
      `}
    >
      <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />

      <div className="flex-1">
        <p>{toast.message}</p>
      </div>

      <button
        onClick={handleDismiss}
        className="flex-shrink-0 hover:opacity-70 transition-opacity"
        aria-label="Zavřít notifikaci"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
}
