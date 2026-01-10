/**
 * Unit tests for GoalStreakCard component.
 *
 * Tests rendering of goal streak data including current/longest streaks,
 * active/inactive messaging, goal value display, flame icon visibility,
 * and empty state handling.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { GoalStreakCard } from '../GoalStreakCard'
import type { GoalStreak } from '../../../types/statistics'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      // Return key with interpolated params for newRecord test
      if (key === 'statistics.streakHistory.newRecord' && params?.days) {
        return `${key} ${params.days}`
      }
      return key
    },
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

describe('GoalStreakCard', () => {
  const mockActiveStreak: GoalStreak = {
    current: 15,
    longest: 30,
    goal: 750,
  }

  const mockInactiveStreak: GoalStreak = {
    current: 0,
    longest: 10,
    goal: 750,
  }

  describe('renders current and longest streak values', () => {
    it('displays current streak value', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(screen.getByText('15')).toBeInTheDocument()
    })

    it('displays longest streak value', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(screen.getByText('30')).toBeInTheDocument()
    })

    it('displays current streak label', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(
        screen.getByText('statistics.goalStreak.current', { exact: false })
      ).toBeInTheDocument()
    })

    it('displays longest streak label', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(
        screen.getByText('statistics.goalStreak.longest', { exact: false })
      ).toBeInTheDocument()
    })

    it('displays days label', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      const daysLabels = screen.getAllByText('statistics.goalStreak.days', {
        exact: false,
      })
      expect(daysLabels.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('active streak messaging (current > 0)', () => {
    it('shows active messaging when current streak is greater than 0', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(
        screen.getByText('statistics.goalStreak.active')
      ).toBeInTheDocument()
    })

    it('has amber/gold accent styling for active streaks', () => {
      const { container } = render(<GoalStreakCard data={mockActiveStreak} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-amber-500')
    })

    it('shows new record message when current equals longest', () => {
      const newRecordStreak: GoalStreak = {
        current: 20,
        longest: 20,
        goal: 750,
      }

      render(<GoalStreakCard data={newRecordStreak} />)

      expect(
        screen.getByText('statistics.streakHistory.newRecord 20')
      ).toBeInTheDocument()
    })

    it('shows new record message when current exceeds longest', () => {
      const newRecordStreak: GoalStreak = {
        current: 25,
        longest: 20,
        goal: 750,
      }

      render(<GoalStreakCard data={newRecordStreak} />)

      expect(
        screen.getByText('statistics.streakHistory.newRecord 25')
      ).toBeInTheDocument()
    })

    it('does not show new record message when current is below longest', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(
        screen.queryByText(/statistics\.streakHistory\.newRecord/)
      ).not.toBeInTheDocument()
    })
  })

  describe('inactive streak messaging (current = 0)', () => {
    it('shows inactive messaging when current streak is 0', () => {
      render(<GoalStreakCard data={mockInactiveStreak} />)

      expect(
        screen.getByText('statistics.goalStreak.inactive')
      ).toBeInTheDocument()
    })

    it('has standard panel styling for inactive streaks', () => {
      const { container } = render(<GoalStreakCard data={mockInactiveStreak} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-border')
      expect(card).toHaveClass('bg-bg-panel')
    })

    it('does not show new record message for inactive streak', () => {
      render(<GoalStreakCard data={mockInactiveStreak} />)

      expect(
        screen.queryByText(/statistics\.streakHistory\.newRecord/)
      ).not.toBeInTheDocument()
    })
  })

  describe('displays the goal value', () => {
    it('displays default 750 words goal', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      // Goal value and perDay label are in the same element
      expect(screen.getByText(/750/)).toBeInTheDocument()
      expect(
        screen.getByText(/statistics\.goalStreak\.perDay/)
      ).toBeInTheDocument()
    })

    it('displays custom goal value', () => {
      const customGoalStreak: GoalStreak = {
        current: 5,
        longest: 10,
        goal: 1000,
      }

      render(<GoalStreakCard data={customGoalStreak} />)

      // 1000 formats as "1,000" in en-US locale
      expect(screen.getByText(/1,000/)).toBeInTheDocument()
    })

    it('formats large goal values with locale separators', () => {
      const largeGoalStreak: GoalStreak = {
        current: 5,
        longest: 10,
        goal: 2500,
      }

      render(<GoalStreakCard data={largeGoalStreak} />)

      // 2500 formats as "2,500" in en-US locale
      expect(screen.getByText(/2,500/)).toBeInTheDocument()
    })
  })

  describe('handles undefined data gracefully', () => {
    it('renders empty state when data is undefined', () => {
      render(<GoalStreakCard data={undefined} />)

      // Check title is still rendered
      expect(
        screen.getByText('statistics.goalStreak.title')
      ).toBeInTheDocument()

      // Check inactive message is displayed
      expect(
        screen.getByText('statistics.goalStreak.inactive')
      ).toBeInTheDocument()
    })

    it('renders Target icon in empty state', () => {
      const { container } = render(<GoalStreakCard data={undefined} />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has panel styling for empty state', () => {
      const { container } = render(<GoalStreakCard data={undefined} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-border')
      expect(card).toHaveClass('bg-bg-panel')
    })

    it('does not display streak values in empty state', () => {
      render(<GoalStreakCard data={undefined} />)

      expect(
        screen.queryByText('statistics.goalStreak.current', { exact: false })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.goalStreak.longest', { exact: false })
      ).not.toBeInTheDocument()
    })
  })

  describe('flame icon is visible', () => {
    it('renders Flame icon for active streaks', () => {
      const { container } = render(<GoalStreakCard data={mockActiveStreak} />)

      // Check SVG icons are present
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBeGreaterThanOrEqual(1)
    })

    it('renders Flame icon for inactive streaks', () => {
      const { container } = render(<GoalStreakCard data={mockInactiveStreak} />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('renders decorative background flame for active streaks', () => {
      const { container } = render(<GoalStreakCard data={mockActiveStreak} />)

      // Active streaks have 2 flame icons (header + decorative background)
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBeGreaterThanOrEqual(2)
    })

    it('does not render decorative background flame for inactive streaks', () => {
      const { container } = render(<GoalStreakCard data={mockInactiveStreak} />)

      // Inactive streaks have only 1 flame icon (header only)
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBe(1)
    })

    it('applies white color to flame icon for active streaks', () => {
      const { container } = render(<GoalStreakCard data={mockActiveStreak} />)

      // Find the header flame icon (in the icon container)
      const iconContainer = container.querySelector('.p-2.border-2')
      const icon = iconContainer?.querySelector('svg')
      expect(icon).toHaveClass('text-white')
    })

    it('applies amber color to flame icon for inactive streaks', () => {
      const { container } = render(<GoalStreakCard data={mockInactiveStreak} />)

      // Find the header flame icon (in the icon container)
      const iconContainer = container.querySelector('.p-2.border-2')
      const icon = iconContainer?.querySelector('svg')
      expect(icon).toHaveClass('text-amber-500')
    })
  })

  describe('card structure', () => {
    it('has correct base styling classes', () => {
      const { container } = render(<GoalStreakCard data={mockActiveStreak} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-2')
      expect(card).toHaveClass('p-6')
      expect(card).toHaveClass('rounded-none')
      expect(card).toHaveClass('shadow-hard')
    })

    it('renders component title', () => {
      render(<GoalStreakCard data={mockActiveStreak} />)

      expect(
        screen.getByText('statistics.goalStreak.title')
      ).toBeInTheDocument()
    })

    it('has relative positioning for decorative elements', () => {
      const { container } = render(<GoalStreakCard data={mockActiveStreak} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('relative')
      expect(card).toHaveClass('overflow-hidden')
    })
  })

  describe('number formatting', () => {
    it('formats streak values with locale separators', () => {
      const largeStreakData: GoalStreak = {
        current: 1234,
        longest: 5678,
        goal: 750,
      }

      render(<GoalStreakCard data={largeStreakData} />)

      // en-US locale should format as 1,234 and 5,678
      expect(screen.getByText('1,234')).toBeInTheDocument()
      expect(screen.getByText('5,678')).toBeInTheDocument()
    })

    it('handles single digit values', () => {
      const smallStreakData: GoalStreak = {
        current: 1,
        longest: 3,
        goal: 750,
      }

      render(<GoalStreakCard data={smallStreakData} />)

      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })
})
