import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

interface FAQItemProps {
  question: string;
  answer: string;
  isOpen: boolean;
  onToggle: () => void;
}

const FAQItem: React.FC<FAQItemProps> = ({ question, answer, isOpen, onToggle }) => {
  return (
    <div className="border-2 border-border bg-bg-panel">
      {/* Question (clickable header) */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between text-left transition-colors duration-150 hover:bg-bg-app"
      >
        <span className="text-base font-medium text-text-main pr-4">
          {question}
        </span>
        <ChevronDown
          size={20}
          className={`text-accent flex-shrink-0 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Answer (collapsible content) */}
      <div
        className={`overflow-hidden transition-all duration-200 ${
          isOpen ? 'max-h-96' : 'max-h-0'
        }`}
      >
        <div className="p-4 pt-0 border-t-2 border-dashed border-border">
          <p className="text-sm text-text-muted leading-relaxed">
            {answer}
          </p>
        </div>
      </div>
    </div>
  );
};

export const FAQSection: React.FC = () => {
  const { t } = useLanguage();
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: t('landing.faq.q1.question'),
      answer: t('landing.faq.q1.answer'),
    },
    {
      question: t('landing.faq.q2.question'),
      answer: t('landing.faq.q2.answer'),
    },
    {
      question: t('landing.faq.q3.question'),
      answer: t('landing.faq.q3.answer'),
    },
    {
      question: t('landing.faq.q4.question'),
      answer: t('landing.faq.q4.answer'),
    },
  ];

  const handleToggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="mb-20">
      {/* Section title */}
      <h2 className="text-2xl md:text-3xl font-bold uppercase tracking-wider mb-8 text-text-main text-center">
        {t('landing.faq.title')}
      </h2>

      {/* FAQ items */}
      <div className="max-w-3xl mx-auto space-y-4">
        {faqs.map((faq, index) => (
          <FAQItem
            key={index}
            question={faq.question}
            answer={faq.answer}
            isOpen={openIndex === index}
            onToggle={() => handleToggle(index)}
          />
        ))}
      </div>
    </section>
  );
};
