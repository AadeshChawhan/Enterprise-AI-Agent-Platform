import { useState } from 'react'

function CodeBlock({ children, className }) {
  const [copied, setCopied] = useState(false)

  const codeText = String(children).replace(/\n$/, '')

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeText)

      setCopied(true)

      setTimeout(() => {
        setCopied(false)
      }, 1500)
    } catch (err) {
      console.error('Unable to copy code:', err)
    }
  }

  return (
    <div className="code-block-wrapper">
      <div className="code-block-toolbar">
        <span className="code-language">
          {className?.replace('language-', '') || 'code'}
        </span>

        <button
          type="button"
          className="copy-code-button"
          onClick={handleCopy}
        >
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>

      <pre className="markdown-code-block">
        <code className={className}>
          {codeText}
        </code>
      </pre>
    </div>
  )
}

export default CodeBlock