/**
 * Unit tests for WritingPrompt component.
 *
 * Tests rendering of daily writing prompts based on day of year,
 * CTA button functionality, and i18n title display.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { WritingPrompt } from '../WritingPrompt';

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}));

// Mock translations
vi.mock('../../../locales', () => ({
  translations: {
    en: {
      dashboard: {
        prompts: [
          'What surprised you today?',
          'Describe a moment when you felt truly alive today.',
          'If you could change one thing about today, what would it be?',
        ],
      },
    },
  },
}));

describe('WritingPrompt', () => {
  const mockOnStartWriting = vi.fn();

  beforeEach(() => {
    mockOnStartWriting.mockClear();
  });

  describe('renders prompt text for current day', () => {
    it('displays a prompt from the prompts array', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      // Should show one of the prompts based on day of year
      const possiblePrompts = [
        'What surprised you today?',
        'Describe a moment when you felt truly alive today.',
        'If you could change one thing about today, what would it be?',
      ];

      // Find text that matches one of the prompts
      const foundPrompt = possiblePrompts.some((prompt) =>
        screen.queryByText(prompt)
      );
      expect(foundPrompt).toBe(true);
    });

    it('renders prompt in a paragraph element', () => {
      const { container } = render(
        <WritingPrompt onStartWriting={mockOnStartWriting} />
      );

      const promptParagraph = container.querySelector('p');
      expect(promptParagraph).toBeInTheDocument();
      expect(promptParagraph).toHaveClass('text-lg');
    });
  });

  describe('calls onStartWriting when CTA button clicked', () => {
    it('calls onStartWriting handler when button is clicked', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      const ctaButton = screen.getByRole('button');
      fireEvent.click(ctaButton);

      expect(mockOnStartWriting).toHaveBeenCalledTimes(1);
    });

    it('calls onStartWriting on multiple clicks', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      const ctaButton = screen.getByRole('button');
      fireEvent.click(ctaButton);
      fireEvent.click(ctaButton);
      fireEvent.click(ctaButton);

      expect(mockOnStartWriting).toHaveBeenCalledTimes(3);
    });
  });

  describe('shows correct i18n title', () => {
    it('displays the writing prompt title translation key', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      expect(
        screen.getByText('dashboard.writingPrompt.title')
      ).toBeInTheDocument();
    });

    it('displays the CTA button translation key', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      expect(screen.getByText('dashboard.writingPrompt.cta')).toBeInTheDocument();
    });
  });

  describe('component structure and styling', () => {
    it('renders Lightbulb icon', () => {
      const { container } = render(
        <WritingPrompt onStartWriting={mockOnStartWriting} />
      );

      const svgIcon = container.querySelector('svg');
      expect(svgIcon).toBeInTheDocument();
    });

    it('renders Card wrapper', () => {
      const { container } = render(
        <WritingPrompt onStartWriting={mockOnStartWriting} />
      );

      // Card component adds space-y-4 class
      const cardContent = container.querySelector('.space-y-4');
      expect(cardContent).toBeInTheDocument();
    });

    it('CTA button has correct styling classes', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      const ctaButton = screen.getByRole('button');
      expect(ctaButton).toHaveClass('bg-accent');
      expect(ctaButton).toHaveClass('text-accent-fg');
      expect(ctaButton).toHaveClass('font-bold');
      expect(ctaButton).toHaveClass('uppercase');
    });

    it('renders ArrowRight icon in button', () => {
      render(<WritingPrompt onStartWriting={mockOnStartWriting} />);

      const ctaButton = screen.getByRole('button');
      const arrowIcon = ctaButton.querySelector('svg');
      expect(arrowIcon).toBeInTheDocument();
    });
  });
});
