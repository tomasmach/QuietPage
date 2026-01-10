import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';
import { useFocusTrap, useOverlay } from '@/hooks/useFocusTrap';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Modal({ isOpen, onClose, title, children, className }: ModalProps) {
  useOverlay(isOpen, onClose);
  const modalRef = useFocusTrap(isOpen);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
      aria-hidden="true"
    >
      <div
        ref={modalRef as React.RefObject<HTMLDivElement>}
        className={cn(
          'bg-bg-panel border-2 border-border shadow-hard max-w-lg w-full mx-4 theme-aware',
          className
        )}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        {title && (
          <div className="flex items-center justify-between border-b-2 border-border pb-4 mb-4 px-6 pt-6 theme-aware">
            <h2
              id="modal-title"
              className="text-lg font-bold uppercase tracking-wider font-mono text-text-main theme-aware"
            >
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-text-muted hover:text-text-main transition-colors theme-aware"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
        {!title && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-text-muted hover:text-text-main transition-colors theme-aware"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        )}
        <div className={cn('px-6', title ? 'pb-6' : 'py-6')}>{children}</div>
      </div>
    </div>
  );
}
