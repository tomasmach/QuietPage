/**
 * Unit tests for DashboardPage component.
 *
 * Tests rendering of the dashboard page including conditional rendering
 * of FeaturedEntry component based on featuredEntry data availability.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { DashboardPage } from '../DashboardPage';
import type { DashboardData } from '../../hooks/useDashboard';

// Mock the useLanguage hook
vi.mock('../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => {
      if (key === 'dashboard.featuredEntry.title') {
        return 'Featured Entry';
      }
      if (key.startsWith('dashboard.greeting.')) {
        return 'Good morning';
      }
      if (key === 'meta.wordsToday') {
        return 'Words today';
      }
      return key;
    },
    language: 'en',
    setLanguage: vi.fn(),
  }),
}));

// Mock the useAuth hook
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      timezone: 'UTC',
      daily_word_goal: 750,
      current_streak: 5,
      longest_streak: 10,
      onboarding_completed: true,
    },
    isLoading: false,
    isAuthenticated: true,
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    checkAuth: vi.fn(),
  }),
}));

// Mock the useTheme hook
vi.mock('../../contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'midnight',
    setTheme: vi.fn(),
  }),
}));

// Mock the useDashboard hook
const mockUseDashboard = vi.fn();
vi.mock('../../hooks/useDashboard', () => ({
  useDashboard: () => mockUseDashboard(),
}));

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

// Wrapper component with MemoryRouter and HelmetProvider
function renderWithRouter(ui: React.ReactElement) {
  return render(
    <HelmetProvider>
      <MemoryRouter>{ui}</MemoryRouter>
    </HelmetProvider>
  );
}

describe('DashboardPage', () => {
  const baseMockData: DashboardData = {
    greeting: 'morning',
    stats: {
      todayWords: 500,
      dailyGoal: 750,
      currentStreak: 5,
      longestStreak: 10,
      totalEntries: 25,
    },
    recentEntries: [
      {
        id: 'entry-1',
        title: 'Recent Entry 1',
        content_preview: 'This is a recent entry...',
        created_at: '2025-12-18T10:00:00Z',
        mood_rating: 4,
        word_count: 300,
      },
    ],
    quote: null,
    hasEntries: true,
    featuredEntry: {
      id: 'featured-1',
      title: 'Featured Entry Title',
      content_preview: 'This is a featured entry from the past...',
      created_at: '2025-12-10T15:00:00Z',
      word_count: 800,
      days_ago: 8,
    },
    weeklyStats: {
      totalWords: 3500,
      bestDay: {
        date: '2025-12-15',
        words: 1200,
        weekday: 'Monday',
      },
    },
  };

  beforeEach(() => {
    mockUseDashboard.mockClear();
  });

  describe('conditional rendering of FeaturedEntry', () => {
    it('does not render FeaturedEntry when featuredEntry is null', () => {
      const mockData = { ...baseMockData, featuredEntry: null };
      mockUseDashboard.mockReturnValue({
        data: mockData,
        isLoading: false,
        error: null,
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      renderWithRouter(<DashboardPage />);

      expect(screen.queryByText('Featured Entry')).not.toBeInTheDocument();
    });

    it('renders FeaturedEntry when featuredEntry is provided', () => {
      mockUseDashboard.mockReturnValue({
        data: baseMockData,
        isLoading: false,
        error: null,
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      renderWithRouter(<DashboardPage />);

      expect(screen.getByText('Featured Entry')).toBeInTheDocument();
    });

    it('does not render FeaturedEntry component when featuredEntry is null', () => {
      const mockData = { ...baseMockData, featuredEntry: null };
      mockUseDashboard.mockReturnValue({
        data: mockData,
        isLoading: false,
        error: null,
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      const { container } = renderWithRouter(<DashboardPage />);

      // Verify the featured entry content is not in the DOM
      expect(screen.queryByText('Featured Entry Title')).not.toBeInTheDocument();

      // Verify no link to the featured entry exists
      const links = container.querySelectorAll('a[href^="/entries/featured-"]');
      expect(links.length).toBe(0);
    });
  });

  describe('loading state', () => {
    it('displays spinner when loading', () => {
      mockUseDashboard.mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      renderWithRouter(<DashboardPage />);

      // Spinner should be present with role="status"
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('displays error message when error occurs', () => {
      mockUseDashboard.mockReturnValue({
        data: null,
        isLoading: false,
        error: new Error('Failed to load dashboard'),
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      renderWithRouter(<DashboardPage />);

      expect(screen.getByText(/Failed to load dashboard/)).toBeInTheDocument();
    });
  });

  describe('dashboard content', () => {
    it('displays today word count', () => {
      mockUseDashboard.mockReturnValue({
        data: baseMockData,
        isLoading: false,
        error: null,
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      renderWithRouter(<DashboardPage />);

      expect(screen.getByText('500')).toBeInTheDocument();
      expect(screen.getByText('Words today')).toBeInTheDocument();
    });

    it('displays greeting', () => {
      mockUseDashboard.mockReturnValue({
        data: baseMockData,
        isLoading: false,
        error: null,
        refreshFeaturedEntry: vi.fn(),
        isRefreshingFeatured: false,
      });

      renderWithRouter(<DashboardPage />);

      expect(screen.getByText('Good morning')).toBeInTheDocument();
    });
  });
});
