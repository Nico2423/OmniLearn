"use client"

import { cn } from "../../lib/utils"

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  // Simple markdown-like formatting for basic text
  const formatContent = (text: string) => {
    return text
      .split('\n')
      .map((line, index) => {
        // Handle headers
        if (line.startsWith('### ')) {
          return <h3 key={index} className="font-semibold text-sm mb-1">{line.substring(4)}</h3>
        }
        if (line.startsWith('## ')) {
          return <h2 key={index} className="font-semibold text-base mb-2">{line.substring(3)}</h2>
        }
        if (line.startsWith('# ')) {
          return <h1 key={index} className="font-semibold text-lg mb-2">{line.substring(2)}</h1>
        }
        
        // Handle bullet points
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return <li key={index} className="text-sm ml-4 list-disc">{line.substring(2)}</li>
        }
        
        // Handle numbered lists
        if (/^\d+\.\s/.test(line)) {
          return <li key={index} className="text-sm ml-4 list-decimal">{line.replace(/^\d+\.\s/, '')}</li>
        }
        
        // Handle empty lines
        if (line.trim() === '') {
          return <br key={index} />
        }
        
        // Regular paragraphs
        return <p key={index} className="text-sm mb-2 leading-relaxed">{line}</p>
      })
  }

  return (
    <div className={cn("space-y-2", className)}>
      {formatContent(content)}
    </div>
  )
}
