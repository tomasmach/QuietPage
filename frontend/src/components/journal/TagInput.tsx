import { useState, type KeyboardEvent, type ChangeEvent } from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function TagInput({
  value,
  onChange,
  placeholder = 'Add tags...',
  disabled = false,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !value.includes(trimmedTag)) {
      onChange([...value, trimmedTag]);
      setInputValue('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  return (
    <div className={cn('w-full', className)}>
      <label className="block mb-2 text-sm font-bold uppercase tracking-wider text-text-muted font-mono">
        Tags
      </label>
      <div className="w-full bg-bg-panel border-2 border-border p-2 min-h-[42px]">
        <div className="flex flex-wrap gap-2">
          {value.map((tag) => (
            <Badge key={tag} variant="default" className="flex items-center gap-1">
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                disabled={disabled}
                className="ml-1 hover:text-accent transition-colors disabled:cursor-not-allowed"
                aria-label={`Remove tag ${tag}`}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={value.length === 0 ? placeholder : ''}
            disabled={disabled}
            className={cn(
              'flex-1 min-w-[120px] bg-transparent border-none outline-none',
              'text-text-main font-mono text-sm',
              'placeholder:text-text-muted',
              'disabled:cursor-not-allowed'
            )}
          />
        </div>
      </div>
      <p className="mt-1 text-sm text-text-muted font-mono">
        Press Enter or comma to add tag
      </p>
    </div>
  );
}
