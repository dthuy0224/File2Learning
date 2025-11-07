import ReactMarkdown from 'react-markdown';

interface MarkdownTextProps {
  children: string;
  className?: string;
}

/**
 * Component to render markdown text in flashcards
 * Supports basic markdown like **bold**, *italic*, `code`, etc.
 */
export default function MarkdownText({ children, className = '' }: MarkdownTextProps) {
  return (
    <div className={className}>
      <ReactMarkdown
        components={{
          // Customize rendering to fit inline text better
          p: ({ children }) => <span>{children}</span>,
          strong: ({ children }) => <strong className="font-bold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          code: ({ children }) => (
            <code className="bg-gray-100 px-1 py-0.5 rounded text-sm">{children}</code>
          ),
          ul: ({ children }) => <ul className="list-disc list-inside">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside">{children}</ol>,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

