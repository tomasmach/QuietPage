import { forwardRef, useId, type TextareaHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, id, rows = 4, ...props }, ref) => {
    const generatedId = useId();
    const textareaId = id ?? (label ? label.toLowerCase().replace(/\s+/g, '-') : generatedId);

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block mb-2 text-xs font-bold uppercase tracking-wider text-text-muted font-mono"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          rows={rows}
          spellCheck={false}
          className={cn(
            'w-full bg-bg-panel border-2 text-text-main font-mono px-3 py-2',
            'focus:outline-none focus:ring-2 focus:ring-accent',
            'transition-all duration-150 resize-vertical',
            error ? 'border-red-500' : 'border-border',
            className
          )}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={
            error ? `${textareaId}-error` : helperText ? `${textareaId}-helper` : undefined
          }
          {...props}
        />
        {error && (
          <p
            id={`${textareaId}-error`}
            className="mt-2 text-xs text-red-500 font-mono"
            role="alert"
          >
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={`${textareaId}-helper`} className="mt-2 text-xs text-text-muted font-mono">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export { Textarea };
