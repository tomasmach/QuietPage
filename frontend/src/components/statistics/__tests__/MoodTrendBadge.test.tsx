/**
 * Unit tests for MoodTrendBadge component.
 *
 * Tests rendering of mood trend states including improving, declining,
 * stable states and proper handling of undefined trend.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MoodTrendBadge } from '../MoodTrendBadge'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

describe('MoodTrendBadge', () => {
  describe('improving trend', () => {
    it('renders improving state with green styling', () => {
      const { container } = render(<MoodTrendBadge trend="improving" />)

      // Check label is rendered
      expect(
        screen.getByText('statistics.moodTrend.improving')
      ).toBeInTheDocument()

      // Check badge has green color classes
      const badge = container.querySelector('span')
      expect(badge).toHaveClass('text-green-600')
      expect(badge).toHaveClass('bg-green-100')
      expect(badge).toHaveClass('border-green-300')
    })

    it('renders TrendingUp icon for improving trend', () => {
      const { container } = render(<MoodTrendBadge trend="improving" />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has correct title attribute for improving trend', () => {
      render(<MoodTrendBadge trend="improving" />)

      const badge = screen.getByTitle('statistics.moodTrend.improving')
      expect(badge).toBeInTheDocument()
    })
  })

  describe('declining trend', () => {
    it('renders declining state with red styling', () => {
      const { container } = render(<MoodTrendBadge trend="declining" />)

      // Check label is rendered
      expect(
        screen.getByText('statistics.moodTrend.declining')
      ).toBeInTheDocument()

      // Check badge has red color classes
      const badge = container.querySelector('span')
      expect(badge).toHaveClass('text-red-600')
      expect(badge).toHaveClass('bg-red-100')
      expect(badge).toHaveClass('border-red-300')
    })

    it('renders TrendingDown icon for declining trend', () => {
      const { container } = render(<MoodTrendBadge trend="declining" />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has correct title attribute for declining trend', () => {
      render(<MoodTrendBadge trend="declining" />)

      const badge = screen.getByTitle('statistics.moodTrend.declining')
      expect(badge).toBeInTheDocument()
    })
  })

  describe('stable trend', () => {
    it('renders stable state with neutral styling', () => {
      const { container } = render(<MoodTrendBadge trend="stable" />)

      // Check label is rendered
      expect(
        screen.getByText('statistics.moodTrend.stable')
      ).toBeInTheDocument()

      // Check badge has neutral color classes
      const badge = container.querySelector('span')
      expect(badge).toHaveClass('text-text-muted')
      expect(badge).toHaveClass('bg-bg-panel')
      expect(badge).toHaveClass('border-border')
    })

    it('renders ArrowRight icon for stable trend', () => {
      const { container } = render(<MoodTrendBadge trend="stable" />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has correct title attribute for stable trend', () => {
      render(<MoodTrendBadge trend="stable" />)

      const badge = screen.getByTitle('statistics.moodTrend.stable')
      expect(badge).toBeInTheDocument()
    })
  })

  describe('undefined trend', () => {
    it('returns null when trend is undefined', () => {
      const { container } = render(<MoodTrendBadge trend={undefined} />)

      // Component should render nothing
      expect(container.firstChild).toBeNull()
    })
  })

  describe('badge structure', () => {
    it('has correct base styling classes', () => {
      const { container } = render(<MoodTrendBadge trend="improving" />)

      const badge = container.querySelector('span')
      expect(badge).toHaveClass('inline-flex')
      expect(badge).toHaveClass('items-center')
      expect(badge).toHaveClass('gap-1')
      expect(badge).toHaveClass('px-2')
      expect(badge).toHaveClass('py-0.5')
      expect(badge).toHaveClass('border')
      expect(badge).toHaveClass('font-mono')
      expect(badge).toHaveClass('text-xs')
      expect(badge).toHaveClass('font-bold')
      expect(badge).toHaveClass('uppercase')
      expect(badge).toHaveClass('tracking-wide')
    })

    it('contains both icon and text label', () => {
      const { container } = render(<MoodTrendBadge trend="stable" />)

      // Check SVG icon exists
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()

      // Check text label exists
      expect(
        screen.getByText('statistics.moodTrend.stable')
      ).toBeInTheDocument()
    })
  })
})
