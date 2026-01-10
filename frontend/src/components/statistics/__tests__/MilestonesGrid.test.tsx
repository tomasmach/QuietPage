/**
 * Unit tests for MilestonesGrid component.
 *
 * Tests rendering of milestone badges including achieved/unachieved states,
 * category grouping (entries, words, streaks), progress display, and
 * empty state handling.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MilestonesGrid } from '../MilestonesGrid'
import type { Milestones } from '../../../types/statistics'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

describe('MilestonesGrid', () => {
  const mockMilestonesData: Milestones = {
    milestones: [
      { type: 'entries', value: 10, achieved: true, current: 15 },
      { type: 'entries', value: 50, achieved: false, current: 15 },
      { type: 'words', value: 1000, achieved: true, current: 2500 },
      { type: 'words', value: 10000, achieved: false, current: 2500 },
      { type: 'streak', value: 7, achieved: true, current: 12 },
      { type: 'streak', value: 30, achieved: false, current: 12 },
    ],
  }

  describe('achieved milestones styling', () => {
    it('renders achieved milestones with accent styling', () => {
      const achievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={achievedData} />)

      // Find the milestone badge (the inner div with p-4)
      const badge = container.querySelector('.bg-accent')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveClass('shadow-hard')
      expect(badge).not.toHaveClass('border-dashed')
    })

    it('displays check icon for achieved milestones', () => {
      const achievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={achievedData} />)

      // Check for the achieved indicator container with the check icon
      const checkContainer = container.querySelector('.bg-accent-fg')
      expect(checkContainer).toBeInTheDocument()
    })

    it('displays achieved label for achieved milestones', () => {
      const achievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      render(<MilestonesGrid data={achievedData} />)

      expect(
        screen.getByText('statistics.milestones.achieved')
      ).toBeInTheDocument()
    })
  })

  describe('unachieved milestones styling', () => {
    it('renders unachieved milestones with muted styling', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 50, achieved: false, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={unachievedData} />)

      // Find the milestone badge with dashed border (unachieved style)
      const badge = container.querySelector('.border-dashed')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveClass('bg-bg-panel')
      expect(badge).toHaveClass('text-text-muted')
    })

    it('does not display check icon for unachieved milestones', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 50, achieved: false, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={unachievedData} />)

      // Check that there's no achieved indicator
      const checkContainer = container.querySelector('.bg-accent-fg')
      expect(checkContainer).not.toBeInTheDocument()
    })

    it('does not display achieved label for unachieved milestones', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 50, achieved: false, current: 15 },
        ],
      }

      render(<MilestonesGrid data={unachievedData} />)

      expect(
        screen.queryByText('statistics.milestones.achieved')
      ).not.toBeInTheDocument()
    })
  })

  describe('progress display', () => {
    it('shows progress bar for unachieved milestones', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 100, achieved: false, current: 25 },
        ],
      }

      const { container } = render(<MilestonesGrid data={unachievedData} />)

      // Check for progress bar container
      const progressBar = container.querySelector('.h-2.border-2')
      expect(progressBar).toBeInTheDocument()
    })

    it('displays current/target values for unachieved milestones', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 100, achieved: false, current: 25 },
        ],
      }

      render(<MilestonesGrid data={unachievedData} />)

      // Should show "25 / 100"
      expect(screen.getByText('25 / 100')).toBeInTheDocument()
    })

    it('displays progress percentage for unachieved milestones', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 100, achieved: false, current: 25 },
        ],
      }

      render(<MilestonesGrid data={unachievedData} />)

      // Should show 25% progress
      expect(screen.getByText('25%')).toBeInTheDocument()
    })

    it('caps progress percentage at 99% for unachieved milestones', () => {
      const almostAchievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 100, achieved: false, current: 100 },
        ],
      }

      render(<MilestonesGrid data={almostAchievedData} />)

      // Should cap at 99% (not 100%) since it's not achieved
      expect(screen.getByText('99%')).toBeInTheDocument()
    })

    it('does not show progress bar for achieved milestones', () => {
      const achievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={achievedData} />)

      // Check that there's no progress bar (the h-2 is only for unachieved)
      const progressBar = container.querySelector('.h-2.border-2')
      expect(progressBar).not.toBeInTheDocument()
    })
  })

  describe('milestone grouping by category', () => {
    it('groups entries milestones together', () => {
      render(<MilestonesGrid data={mockMilestonesData} />)

      // Should have entries category header
      const headers = screen.getAllByText('statistics.milestones.entries')
      expect(headers.length).toBeGreaterThanOrEqual(1)
    })

    it('groups words milestones together', () => {
      render(<MilestonesGrid data={mockMilestonesData} />)

      // Should have words category header
      const headers = screen.getAllByText('statistics.milestones.words')
      expect(headers.length).toBeGreaterThanOrEqual(1)
    })

    it('groups streak milestones together', () => {
      render(<MilestonesGrid data={mockMilestonesData} />)

      // Should have streaks category header
      const headers = screen.getAllByText('statistics.milestones.streaks')
      expect(headers.length).toBeGreaterThanOrEqual(1)
    })

    it('renders category labels in correct order', () => {
      const { container } = render(<MilestonesGrid data={mockMilestonesData} />)

      // Get all category headers (the h4 elements with category labels)
      const categoryHeaders = container.querySelectorAll('h4')
      expect(categoryHeaders.length).toBe(3)

      // Verify order: entries, words, streak
      expect(categoryHeaders[0]).toHaveTextContent('statistics.milestones.entries')
      expect(categoryHeaders[1]).toHaveTextContent('statistics.milestones.words')
      expect(categoryHeaders[2]).toHaveTextContent('statistics.milestones.streaks')
    })

    it('does not render empty category sections', () => {
      const onlyCategoriesData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={onlyCategoriesData} />)

      // Should only have one category header (entries)
      const categoryHeaders = container.querySelectorAll('h4')
      expect(categoryHeaders.length).toBe(1)
      expect(categoryHeaders[0]).toHaveTextContent('statistics.milestones.entries')
    })
  })

  describe('empty/undefined data handling', () => {
    it('renders empty state when data is undefined', () => {
      render(<MilestonesGrid data={undefined} />)

      // Check title is still rendered
      expect(
        screen.getByText('statistics.milestones.title')
      ).toBeInTheDocument()

      // Check no data message is displayed
      expect(
        screen.getByText('statistics.milestones.noData')
      ).toBeInTheDocument()
    })

    it('renders empty state when milestones array is empty', () => {
      const emptyData: Milestones = {
        milestones: [],
      }

      render(<MilestonesGrid data={emptyData} />)

      // Check no data message is displayed
      expect(
        screen.getByText('statistics.milestones.noData')
      ).toBeInTheDocument()
    })

    it('renders Trophy icon in empty state', () => {
      const { container } = render(<MilestonesGrid data={undefined} />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has centered text in empty state', () => {
      const { container } = render(<MilestonesGrid data={undefined} />)

      const emptyCard = container.firstChild as HTMLElement
      expect(emptyCard).toHaveClass('text-center')
    })
  })

  describe('value formatting', () => {
    it('formats values in thousands with k suffix', () => {
      const largeData: Milestones = {
        milestones: [
          { type: 'words', value: 10000, achieved: true, current: 15000 },
        ],
      }

      render(<MilestonesGrid data={largeData} />)

      // Should format 10000 as "10k"
      expect(screen.getByText('10k')).toBeInTheDocument()
    })

    it('formats values in millions with M suffix', () => {
      const hugeData: Milestones = {
        milestones: [
          { type: 'words', value: 1000000, achieved: true, current: 1500000 },
        ],
      }

      render(<MilestonesGrid data={hugeData} />)

      // Should format 1000000 as "1M"
      expect(screen.getByText('1M')).toBeInTheDocument()
    })

    it('displays small values without suffix', () => {
      const smallData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      render(<MilestonesGrid data={smallData} />)

      // Should display "10" without suffix
      expect(screen.getByText('10')).toBeInTheDocument()
    })

    it('formats progress values correctly in progress bar', () => {
      const progressData: Milestones = {
        milestones: [
          { type: 'words', value: 10000, achieved: false, current: 2500 },
        ],
      }

      render(<MilestonesGrid data={progressData} />)

      // Should show "2.5k / 10k"
      expect(screen.getByText('2.5k / 10k')).toBeInTheDocument()
    })
  })

  describe('milestone icons', () => {
    it('renders Target icon for entries milestones', () => {
      const entriesData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={entriesData} />)

      // Check that SVG icon is present in the icon container
      const iconContainer = container.querySelector('.w-10.h-10')
      expect(iconContainer).toBeInTheDocument()
      expect(iconContainer?.querySelector('svg')).toBeInTheDocument()
    })

    it('renders Star icon for words milestones', () => {
      const wordsData: Milestones = {
        milestones: [
          { type: 'words', value: 1000, achieved: true, current: 2500 },
        ],
      }

      const { container } = render(<MilestonesGrid data={wordsData} />)

      // Check that SVG icon is present in the icon container
      const iconContainer = container.querySelector('.w-10.h-10')
      expect(iconContainer).toBeInTheDocument()
      expect(iconContainer?.querySelector('svg')).toBeInTheDocument()
    })

    it('renders Flame icon for streak milestones', () => {
      const streakData: Milestones = {
        milestones: [
          { type: 'streak', value: 7, achieved: true, current: 12 },
        ],
      }

      const { container } = render(<MilestonesGrid data={streakData} />)

      // Check that SVG icon is present in the icon container
      const iconContainer = container.querySelector('.w-10.h-10')
      expect(iconContainer).toBeInTheDocument()
      expect(iconContainer?.querySelector('svg')).toBeInTheDocument()
    })

    it('applies accent color to icon for achieved milestones', () => {
      const achievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={achievedData} />)

      // Check icon has accent color class
      const icon = container.querySelector('.w-10.h-10 svg')
      expect(icon).toHaveClass('text-accent-fg')
    })

    it('applies muted color to icon for unachieved milestones', () => {
      const unachievedData: Milestones = {
        milestones: [
          { type: 'entries', value: 50, achieved: false, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={unachievedData} />)

      // Check icon has muted color class
      const icon = container.querySelector('.w-10.h-10 svg')
      expect(icon).toHaveClass('text-text-muted')
    })
  })

  describe('card structure', () => {
    it('has correct base styling classes for main container', () => {
      const { container } = render(<MilestonesGrid data={mockMilestonesData} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-2')
      expect(card).toHaveClass('border-border')
      expect(card).toHaveClass('bg-bg-panel')
      expect(card).toHaveClass('p-6')
      expect(card).toHaveClass('shadow-hard')
      expect(card).toHaveClass('rounded-none')
    })

    it('renders main title with Trophy icon', () => {
      const { container } = render(<MilestonesGrid data={mockMilestonesData} />)

      // Check title is present
      expect(
        screen.getByText('statistics.milestones.title')
      ).toBeInTheDocument()

      // Check title container has Trophy icon
      const titleContainer = container.querySelector('h3')
      expect(titleContainer?.querySelector('svg')).toBeInTheDocument()
    })

    it('renders milestone badges in a grid layout', () => {
      const { container } = render(<MilestonesGrid data={mockMilestonesData} />)

      // Check for grid container with responsive columns
      const grid = container.querySelector('.grid')
      expect(grid).toBeInTheDocument()
      expect(grid).toHaveClass('grid-cols-2')
      expect(grid).toHaveClass('md:grid-cols-3')
      expect(grid).toHaveClass('lg:grid-cols-4')
    })
  })

  describe('mixed milestone states', () => {
    it('renders both achieved and unachieved milestones correctly', () => {
      const mixedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
          { type: 'entries', value: 50, achieved: false, current: 15 },
        ],
      }

      const { container } = render(<MilestonesGrid data={mixedData} />)

      // Should have one achieved badge with shadow-hard
      const achievedBadges = container.querySelectorAll('.bg-accent.shadow-hard')
      expect(achievedBadges.length).toBe(1)

      // Should have one unachieved badge with dashed border
      const unachievedBadges = container.querySelectorAll('.border-dashed')
      expect(unachievedBadges.length).toBe(1)
    })

    it('shows achieved label only on achieved milestones', () => {
      const mixedData: Milestones = {
        milestones: [
          { type: 'entries', value: 10, achieved: true, current: 15 },
          { type: 'entries', value: 50, achieved: false, current: 15 },
        ],
      }

      render(<MilestonesGrid data={mixedData} />)

      // Should have exactly one "achieved" label
      const achievedLabels = screen.getAllByText('statistics.milestones.achieved')
      expect(achievedLabels.length).toBe(1)
    })
  })
})
