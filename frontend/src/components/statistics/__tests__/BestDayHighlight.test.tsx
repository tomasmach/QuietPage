/**
 * Unit tests for BestDayHighlight component.
 *
 * Tests rendering of best day data display including date formatting,
 * word count, entry count, trophy icon, and empty state handling.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BestDayHighlight, type BestDayData } from '../BestDayHighlight'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

describe('BestDayHighlight', () => {
  const mockBestDayData: BestDayData = {
    date: '2025-12-15',
    wordCount: 1234,
    entryCount: 2,
  }

  describe('with best day data', () => {
    it('renders the component with data', () => {
      render(<BestDayHighlight data={mockBestDayData} />)

      // Check title is rendered
      expect(
        screen.getByText('statistics.bestDay.title')
      ).toBeInTheDocument()
    })

    it('displays formatted date', () => {
      render(<BestDayHighlight data={mockBestDayData} />)

      // Check date is formatted and displayed (en-US long format)
      // Date should contain 'December', '15', and '2025'
      expect(screen.getByText(/december/i)).toBeInTheDocument()
      expect(screen.getByText(/15/)).toBeInTheDocument()
      expect(screen.getByText(/2025/)).toBeInTheDocument()
    })

    it('displays word count with label', () => {
      render(<BestDayHighlight data={mockBestDayData} />)

      // Check word count is displayed (formatted with locale)
      expect(screen.getByText('1,234')).toBeInTheDocument()

      // Check words label
      expect(
        screen.getByText('statistics.bestDay.words')
      ).toBeInTheDocument()
    })

    it('displays entry count with label', () => {
      render(<BestDayHighlight data={mockBestDayData} />)

      // Check entry count is displayed
      expect(screen.getByText('2')).toBeInTheDocument()

      // Check entries label
      expect(
        screen.getByText('statistics.bestDay.entries')
      ).toBeInTheDocument()
    })

    it('renders Trophy icon', () => {
      const { container } = render(<BestDayHighlight data={mockBestDayData} />)

      // Check SVG icons are present (component has both decorative and header trophy)
      const icons = container.querySelectorAll('svg')
      expect(icons.length).toBeGreaterThanOrEqual(1)
    })

    it('has accent styling for celebration', () => {
      const { container } = render(<BestDayHighlight data={mockBestDayData} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-accent')
      expect(card).toHaveClass('bg-accent')
      expect(card).toHaveClass('text-accent-fg')
    })
  })

  describe('empty state (no data)', () => {
    it('renders empty state when data is undefined', () => {
      render(<BestDayHighlight data={undefined} />)

      // Check title is still rendered
      expect(
        screen.getByText('statistics.bestDay.title')
      ).toBeInTheDocument()

      // Check encouraging message is displayed
      expect(
        screen.getByText('statistics.bestDay.noData')
      ).toBeInTheDocument()
    })

    it('renders Pencil icon in empty state', () => {
      const { container } = render(<BestDayHighlight data={undefined} />)

      // Check SVG icon is present
      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })

    it('has panel styling for empty state', () => {
      const { container } = render(<BestDayHighlight data={undefined} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-border')
      expect(card).toHaveClass('bg-bg-panel')
    })

    it('does not display word count or entry count labels', () => {
      render(<BestDayHighlight data={undefined} />)

      expect(
        screen.queryByText('statistics.bestDay.words')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('statistics.bestDay.entries')
      ).not.toBeInTheDocument()
    })
  })

  describe('card structure', () => {
    it('has correct base styling classes', () => {
      const { container } = render(<BestDayHighlight data={mockBestDayData} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('border-2')
      expect(card).toHaveClass('p-6')
      expect(card).toHaveClass('rounded-none')
      expect(card).toHaveClass('shadow-hard')
    })

    it('contains stats section with word and entry counts', () => {
      render(<BestDayHighlight data={mockBestDayData} />)

      // Both stats should be present
      expect(
        screen.getByText('statistics.bestDay.words')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.bestDay.entries')
      ).toBeInTheDocument()
    })
  })

  describe('data formatting', () => {
    it('formats large word counts with locale separators', () => {
      const largeWordCount: BestDayData = {
        date: '2025-01-01',
        wordCount: 12345,
        entryCount: 5,
      }

      render(<BestDayHighlight data={largeWordCount} />)

      // en-US locale should format as 12,345
      expect(screen.getByText('12,345')).toBeInTheDocument()
    })

    it('handles single entry count', () => {
      const singleEntry: BestDayData = {
        date: '2025-06-20',
        wordCount: 750,
        entryCount: 1,
      }

      render(<BestDayHighlight data={singleEntry} />)

      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('750')).toBeInTheDocument()
    })

    it('handles zero word count edge case', () => {
      const zeroWords: BestDayData = {
        date: '2025-03-10',
        wordCount: 0,
        entryCount: 1,
      }

      render(<BestDayHighlight data={zeroWords} />)

      expect(screen.getByText('0')).toBeInTheDocument()
    })
  })
})
