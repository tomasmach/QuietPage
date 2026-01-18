/**
 * Unit tests for FeaturedEntry component.
 *
 * Tests rendering of featured historical entries including null state handling,
 * entry title and content preview display, days ago text, refresh button
 * functionality, and loading state.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { FeaturedEntry } from '../FeaturedEntry';
import type { FeaturedEntry as FeaturedEntryType } from '../../../hooks/useDashboard';

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      if (key === 'dashboard.featuredEntry.daysAgo' && params?.count !== undefined) {
        return `${params.count} days ago`;
      }
      return key;
    },
    language: 'en',
    setLanguage: vi.fn(),
  }),
}));

// Wrapper component with MemoryRouter for Link components
function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('FeaturedEntry', () => {
  const mockOnRefresh = vi.fn();

  const mockEntry: FeaturedEntryType = {
    id: 'entry-123',
    title: 'My Wonderful Day',
    content_preview: 'Today was an amazing day. I went for a walk in the park...',
    created_at: '2025-12-15T10:30:00Z',
    word_count: 750,
    days_ago: 5,
  };

  const mockEntryNoTitle: FeaturedEntryType = {
    id: 'entry-456',
    title: '',
    content_preview: 'An entry without a title but with content.',
    created_at: '2025-12-10T08:00:00Z',
    word_count: 500,
    days_ago: 10,
  };

  beforeEach(() => {
    mockOnRefresh.mockClear();
  });

  describe('returns null when entry is null', () => {
    it('renders nothing when entry prop is null', () => {
      const { container } = renderWithRouter(
        <FeaturedEntry entry={null} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(container.firstChild).toBeNull();
    });

    it('does not call onRefresh when entry is null', () => {
      renderWithRouter(
        <FeaturedEntry entry={null} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(mockOnRefresh).not.toHaveBeenCalled();
    });
  });

  describe('renders entry title and content preview when entry provided', () => {
    it('displays entry title', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(screen.getByText('My Wonderful Day')).toBeInTheDocument();
    });

    it('displays content preview', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(
        screen.getByText('Today was an amazing day. I went for a walk in the park...')
      ).toBeInTheDocument();
    });

    it('does not render title element when title is empty', () => {
      renderWithRouter(
        <FeaturedEntry
          entry={mockEntryNoTitle}
          onRefresh={mockOnRefresh}
          isRefreshing={false}
        />
      );

      // h4 element should not exist for entries without titles
      const headings = screen.queryAllByRole('heading', { level: 4 });
      expect(headings.length).toBe(0);
    });

    it('displays word count', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(screen.getByText(/750/)).toBeInTheDocument();
    });

    it('displays formatted date', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      // Date should be formatted as "Dec 15, 2025" or similar locale format
      expect(screen.getByText(/Dec/i)).toBeInTheDocument();
      expect(screen.getByText(/15/)).toBeInTheDocument();
    });
  });

  describe('shows days ago text', () => {
    it('displays days ago for entry', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(screen.getByText('5 days ago')).toBeInTheDocument();
    });

    it('displays correct days ago for different entry', () => {
      renderWithRouter(
        <FeaturedEntry
          entry={mockEntryNoTitle}
          onRefresh={mockOnRefresh}
          isRefreshing={false}
        />
      );

      expect(screen.getByText('10 days ago')).toBeInTheDocument();
    });
  });

  describe('calls onRefresh when refresh button clicked', () => {
    it('calls onRefresh handler when button is clicked', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      const refreshButton = screen.getByRole('button');
      fireEvent.click(refreshButton);

      expect(mockOnRefresh).toHaveBeenCalledTimes(1);
    });

    it('displays refresh button text', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(
        screen.getByText('dashboard.featuredEntry.refresh')
      ).toBeInTheDocument();
    });
  });

  describe('shows loading state when isRefreshing is true', () => {
    it('displays refreshing text when isRefreshing is true', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={true} />
      );

      expect(
        screen.getByText('dashboard.featuredEntry.refreshing')
      ).toBeInTheDocument();
    });

    it('disables button when isRefreshing is true', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={true} />
      );

      const refreshButton = screen.getByRole('button');
      expect(refreshButton).toBeDisabled();
    });

    it('shows spinning animation on icon when isRefreshing', () => {
      const { container } = renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={true} />
      );

      const spinningIcon = container.querySelector('.animate-spin');
      expect(spinningIcon).toBeInTheDocument();
    });

    it('does not show spinning animation when not refreshing', () => {
      const { container } = renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      const spinningIcon = container.querySelector('.animate-spin');
      expect(spinningIcon).not.toBeInTheDocument();
    });
  });

  describe('component structure and styling', () => {
    it('displays the featured entry title translation key', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      expect(
        screen.getByText('dashboard.featuredEntry.title')
      ).toBeInTheDocument();
    });

    it('renders History icon', () => {
      const { container } = renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      const svgIcons = container.querySelectorAll('svg');
      expect(svgIcons.length).toBeGreaterThanOrEqual(1);
    });

    it('renders link to entry detail page', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      const link = screen.getByRole('link');
      expect(link).toHaveAttribute('href', '/entries/entry-123');
    });

    it('content preview has line-clamp styling', () => {
      renderWithRouter(
        <FeaturedEntry entry={mockEntry} onRefresh={mockOnRefresh} isRefreshing={false} />
      );

      const contentPreview = screen.getByText(
        'Today was an amazing day. I went for a walk in the park...'
      );
      expect(contentPreview).toHaveClass('line-clamp-3');
    });
  });
});
