import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import CodeBlock from './CodeBlock'

function MarkdownMessage({ content }) {
  const [copied, setCopied] = useState(false)

  const handleCopyResponse = async () => {
    try {
      await navigator.clipboard.writeText(content)

      setCopied(true)

      setTimeout(() => {
        setCopied(false)
      }, 1500)
    } catch (err) {
      console.error(
        'Unable to copy response:',
        err
      )
    }
  }

  return (
    <div className="markdown-message">
      <div className="markdown-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            a: ({ ...props }) => (
              <a
                {...props}
                target="_blank"
                rel="noopener noreferrer"
              />
            ),

            table: ({ ...props }) => (
              <div className="markdown-table-wrapper">
                <table {...props} />
              </div>
            ),

            code: ({
              className,
              children,
              ...props
            }) => {
              const isBlock =
                className?.startsWith(
                  'language-'
                )

              if (isBlock) {
                return (
                  <CodeBlock
                    className={className}
                  >
                    {children}
                  </CodeBlock>
                )
              }

              return (
                <code
                  className="markdown-inline-code"
                  {...props}
                >
                  {children}
                </code>
              )
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>

      <div className="message-copy-row">
        <button
          type="button"
          className="copy-message-button"
          onClick={handleCopyResponse}
        >
          {copied ? 'Copied' : 'Copy response'}
        </button>
      </div>
    </div>
  )
}

export default MarkdownMessage