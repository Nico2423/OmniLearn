"use client"

import * as React from "react"
import { ChevronDownIcon } from "@heroicons/react/24/outline"
import { cn } from "../../lib/utils"

interface CollapsibleProps {
  children: React.ReactNode
  title: string
  defaultOpen?: boolean
  className?: string
}

export function Collapsible({ children, title, defaultOpen = false, className }: CollapsibleProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen)

  return (
    <div className={cn("border rounded-lg", className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="font-medium">{title}</span>
        <ChevronDownIcon
          className={cn(
            "h-5 w-5 transition-transform duration-200",
            isOpen ? "transform rotate-180" : ""
          )}
        />
      </button>
      {isOpen && (
        <div className="px-4 pb-4 border-t">
          {children}
        </div>
      )}
    </div>
  )
}
