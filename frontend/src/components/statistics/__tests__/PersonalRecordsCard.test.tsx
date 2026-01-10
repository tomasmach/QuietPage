/**
 * Unit tests for PersonalRecordsCard component.
 *
 * Tests rendering of personal records including longest entry, most productive day,
 * longest streak, longest goal streak, empty state handling, date formatting,
 * title truncation, and icon visibility.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PersonalRecordsCard } from '../PersonalRecordsCard'
import type { PersonalRecords } from '../../../types/statistics'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

describe('PersonalRecordsCard', () => {
  const mockFullRecords: PersonalRecords = {
    longestEntry: {
      date: '2025-12-15',
      wordCount: 1500,
      title: 'My Best Writing Day',
      entryId: 'entry-123',
    },
    mostWordsInDay: {
      date: '2025-12-10',
      wordCount: 2500,
      entryCount: 3,
    },
    longestStreak: 30,
    longestGoalStreak: 15,
  }

  const mockRecordsWithoutTitle: PersonalRecords = {
    longestEntry: {
      date: '2025-12-15',
      wordCount: 1000,
      title: null,
      entryId: 'entry-456',
    },
    mostWordsInDay: null,
    longestStreak: 10,
    longestGoalStreak: 0,
  }

  const mockEmptyRecords: PersonalRecords = {
    longestEntry: null,
    mostWordsInDay: null,
    longestStreak: 0,
    longestGoalStreak: 0,
  }

  describe('renders all record types correctly', () => {
    it('displays longest entry record', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(
        screen.getByText('statistics.records.longestEntry')
      ).toBeInTheDocument()
      expect(screen.getByText(/1,500/)).toBeInTheDocument()
    })

    it('displays most productive day record', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(
        screen.getByText('statistics.records.mostProductiveDay')
      ).toBeInTheDocument()
      expect(screen.getByText(/2,500/)).toBeInTheDocument()
    })

    it('displays longest streak record', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(
        screen.getByText('statistics.records.longestStreak')
      ).toBeInTheDocument()
      expect(screen.getByText(/30/)).toBeInTheDocument()
    })

    it('displays longest goal streak record', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(
        screen.getByText('statistics.records.longestGoalStreak')
      ).toBeInTheDocument()
      // Check for "15 statistics.records.days" - the full value text
      expect(screen.getByText('15 statistics.records.days')).toBeInTheDocument()
    })

    it('displays entry count for most productive day', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      // Entry count is in the subtitle along with date
      // Check that the subtitle contains the entry count and label
      expect(
        screen.getByText(/3 statistics\.records\.entries/)
      ).toBeInTheDocument()
    })

    it('displays words label for entries', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      const wordsLabels = screen.getAllByText(/statistics\.records\.words/)
      expect(wordsLabels.length).toBeGreaterThanOrEqual(1)
    })

    it('displays days label for streaks', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      const daysLabels = screen.getAllByText(/statistics\.records\.days/)
      expect(daysLabels.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('handles missing optional fields', () => {
    it('renders without title when title is null', () => {
      render(<PersonalRecordsCard data={mockRecordsWithoutTitle} />)

      expect(
        screen.getByText('statistics.records.longestEntry')
      ).toBeInTheDocument()
      expect(screen.getByText(/1,000/)).toBeInTheDocument()
      // Should not contain title separator
      expect(screen.queryByText(/My Best Writing Day/)).not.toBeInTheDocument()
    })

    it('renders correctly when mostWordsInDay is null', () => {
      render(<PersonalRecordsCard data={mockRecordsWithoutTitle} />)

      expect(
        screen.queryByText('statistics.records.mostProductiveDay')
      ).not.toBeInTheDocument()
      // But longestEntry should still show
      expect(
        screen.getByText('statistics.records.longestEntry')
      ).toBeInTheDocument()
    })

    it('includes title in subtitle when provided', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(screen.getByText(/My Best Writing Day/)).toBeInTheDocument()
    })
  })

  describe('shows empty state when no records exist', () => {
    it('displays empty state message when all records are null/zero', () => {
      render(<PersonalRecordsCard data={mockEmptyRecords} />)

      expect(
        screen.getByText('statistics.records.noRecords')
      ).toBeInTheDocument()
    })

    it('displays title in empty state', () => {
      render(<PersonalRecordsCard data={mockEmptyRecords} />)

      expect(
        screen.getByText('statistics.records.title')
      ).toBeInTheDocument()
    })

    it('renders Trophy icon in empty state', () => {
      const { container } = render(
        <PersonalRecordsCard data={mockEmptyRecords} />
      )

      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('does not display any record rows in empty state', () => {
      render(<PersonalRecordsCard data={mockEmptyRecords} />)

      expect(
        screen.queryByText('statistics.records.longestEntry')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.records.mostProductiveDay')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.records.longestStreak')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.records.longestGoalStreak')
      ).not.toBeInTheDocument()
    })
  })

  describe('displays dates formatted correctly', () => {
    it('formats date in en-US locale for longest entry', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      // Dec 15, 2025 in en-US format - check the subtitle contains the date
      expect(screen.getByText(/Dec 15, 2025/)).toBeInTheDocument()
    })

    it('formats date in en-US locale for most productive day', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      // Dec 10, 2025 in en-US format - check the subtitle contains the date
      expect(screen.getByText(/Dec 10, 2025/)).toBeInTheDocument()
    })
  })

  describe('icons are visible for each record type', () => {
    it('renders Trophy icon in header', () => {
      const { container } = render(
        <PersonalRecordsCard data={mockFullRecords} />
      )

      // Check SVG icons are present
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBeGreaterThanOrEqual(1)
    })

    it('renders icons for all record rows', () => {
      const { container } = render(
        <PersonalRecordsCard data={mockFullRecords} />
      )

      // Should have icons for: header Trophy + Award (longest entry) + Medal (most productive) + Flame (streak) + Calendar (goal streak)
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBe(5)
    })

    it('renders fewer icons when some records are missing', () => {
      const { container } = render(
        <PersonalRecordsCard data={mockRecordsWithoutTitle} />
      )

      // Should have icons for: header Trophy + Award (longest entry) + Flame (streak)
      // mostWordsInDay is null and longestGoalStreak is 0
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBe(3)
    })
  })

  describe('only shows streak records when > 0', () => {
    it('hides longestStreak when it is 0', () => {
      const recordsWithZeroStreak: PersonalRecords = {
        longestEntry: mockFullRecords.longestEntry,
        mostWordsInDay: mockFullRecords.mostWordsInDay,
        longestStreak: 0,
        longestGoalStreak: 5,
      }

      render(<PersonalRecordsCard data={recordsWithZeroStreak} />)

      expect(
        screen.queryByText('statistics.records.longestStreak')
      ).not.toBeInTheDocument()
      expect(
        screen.getByText('statistics.records.longestGoalStreak')
      ).toBeInTheDocument()
    })

    it('hides longestGoalStreak when it is 0', () => {
      render(<PersonalRecordsCard data={mockRecordsWithoutTitle} />)

      expect(
        screen.queryByText('statistics.records.longestGoalStreak')
      ).not.toBeInTheDocument()
      expect(
        screen.getByText('statistics.records.longestStreak')
      ).toBeInTheDocument()
    })

    it('shows both streaks when both are > 0', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(
        screen.getByText('statistics.records.longestStreak')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.records.longestGoalStreak')
      ).toBeInTheDocument()
    })

    it('hides both streaks when both are 0', () => {
      const recordsWithNoStreaks: PersonalRecords = {
        longestEntry: mockFullRecords.longestEntry,
        mostWordsInDay: null,
        longestStreak: 0,
        longestGoalStreak: 0,
      }

      render(<PersonalRecordsCard data={recordsWithNoStreaks} />)

      expect(
        screen.queryByText('statistics.records.longestStreak')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.records.longestGoalStreak')
      ).not.toBeInTheDocument()
    })
  })

  describe('handles undefined data gracefully', () => {
    it('renders empty state when data is undefined', () => {
      render(<PersonalRecordsCard data={undefined} />)

      expect(
        screen.getByText('statistics.records.title')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.records.noRecords')
      ).toBeInTheDocument()
    })

    it('renders Trophy icon in undefined state', () => {
      const { container } = render(<PersonalRecordsCard data={undefined} />)

      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has panel styling for undefined state', () => {
      const { container } = render(<PersonalRecordsCard data={undefined} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-2')
      expect(card).toHaveClass('border-border')
      expect(card).toHaveClass('bg-bg-panel')
    })

    it('does not display any record rows when undefined', () => {
      render(<PersonalRecordsCard data={undefined} />)

      expect(
        screen.queryByText('statistics.records.longestEntry')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.records.mostProductiveDay')
      ).not.toBeInTheDocument()
    })
  })

  describe('card structure and styling', () => {
    it('has correct base styling classes', () => {
      const { container } = render(
        <PersonalRecordsCard data={mockFullRecords} />
      )

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-2')
      expect(card).toHaveClass('border-border')
      expect(card).toHaveClass('bg-bg-panel')
      expect(card).toHaveClass('p-6')
      expect(card).toHaveClass('rounded-none')
      expect(card).toHaveClass('shadow-hard')
    })

    it('renders component title', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      expect(
        screen.getByText('statistics.records.title')
      ).toBeInTheDocument()
    })

    it('renders record rows with border styling', () => {
      const { container } = render(
        <PersonalRecordsCard data={mockFullRecords} />
      )

      // Record rows have border-dashed class
      const rows = container.querySelectorAll('.border-dashed')
      expect(rows.length).toBeGreaterThan(0)
    })
  })

  describe('number formatting', () => {
    it('formats word counts with locale separators', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      // 1500 formats as "1,500" and 2500 as "2,500" in en-US locale
      expect(screen.getByText(/1,500/)).toBeInTheDocument()
      expect(screen.getByText(/2,500/)).toBeInTheDocument()
    })

    it('handles small word counts', () => {
      const smallRecords: PersonalRecords = {
        longestEntry: {
          date: '2025-12-15',
          wordCount: 50,
          title: null,
          entryId: 'entry-789',
        },
        mostWordsInDay: null,
        longestStreak: 1,
        longestGoalStreak: 0,
      }

      render(<PersonalRecordsCard data={smallRecords} />)

      expect(screen.getByText(/50/)).toBeInTheDocument()
    })

    it('handles large word counts', () => {
      const largeRecords: PersonalRecords = {
        longestEntry: {
          date: '2025-12-15',
          wordCount: 12500,
          title: null,
          entryId: 'entry-999',
        },
        mostWordsInDay: null,
        longestStreak: 365,
        longestGoalStreak: 100,
      }

      render(<PersonalRecordsCard data={largeRecords} />)

      // 12500 formats as "12,500" in en-US locale
      expect(screen.getByText(/12,500/)).toBeInTheDocument()
    })
  })

  describe('title truncation', () => {
    it('truncates long titles', () => {
      const longTitleRecords: PersonalRecords = {
        longestEntry: {
          date: '2025-12-15',
          wordCount: 1000,
          title: 'This is a very long title that should be truncated to fit properly',
          entryId: 'entry-long',
        },
        mostWordsInDay: null,
        longestStreak: 0,
        longestGoalStreak: 0,
      }

      render(<PersonalRecordsCard data={longTitleRecords} />)

      // Title should be truncated with "..."
      expect(screen.getByText(/\.\.\./)).toBeInTheDocument()
      // Should not show the full title
      expect(
        screen.queryByText('This is a very long title that should be truncated to fit properly')
      ).not.toBeInTheDocument()
    })

    it('does not truncate short titles', () => {
      render(<PersonalRecordsCard data={mockFullRecords} />)

      // "My Best Writing Day" is 19 chars, under the 30 char limit
      expect(screen.getByText(/My Best Writing Day/)).toBeInTheDocument()
    })
  })
})
