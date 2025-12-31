import { Toast } from './Toast';
import type { Toast as ToastType, ToastPosition } from '@/contexts/ToastContext';

interface ToastContainerProps {
  toasts: ToastType[];
  position: ToastPosition;
  onRemove: (id: string) => void;
}

const positionClasses: Record<ToastPosition, string> = {
  'top-left': 'top-4 left-4',
  'top-center': 'top-4 left-1/2 -translate-x-1/2',
  'top-right': 'top-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  'bottom-right': 'bottom-4 right-4',
};

export function ToastContainer({ toasts, position, onRemove }: ToastContainerProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className={`fixed z-[100] flex flex-col gap-2 w-full max-w-sm ${positionClasses[position]}`}
      aria-label="Notifikace"
    >
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}
