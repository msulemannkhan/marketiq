"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  // Simple markdown parser for basic formatting
  const parseMarkdown = (text: string) => {
    // Split by lines and process each line
    const lines = text.split('\n');
    const elements: React.ReactElement[] = [];
    let listItems: string[] = [];
    let inList = false;

    const processList = () => {
      if (listItems.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="list-disc list-inside space-y-1 my-2">
            {listItems.map((item, index) => (
              <li key={index} className="text-sm">
                {parseInlineMarkdown(item)}
              </li>
            ))}
          </ul>
        );
        listItems = [];
        inList = false;
      }
    };

    const parseInlineMarkdown = (text: string) => {
      // Bold text **text**
      let processed = text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-foreground">$1</strong>');
      
      // Italic text *text*
      processed = processed.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
      
      // Code `code`
      processed = processed.replace(/`(.*?)`/g, '<code class="bg-muted px-1 py-0.5 rounded text-xs font-mono">$1</code>');
      
      return <span dangerouslySetInnerHTML={{ __html: processed }} />;
    };

    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // Empty line
      if (trimmedLine === '') {
        processList();
        elements.push(<br key={`br-${index}`} />);
        return;
      }

      // List item
      if (trimmedLine.startsWith('- ')) {
        if (!inList) {
          processList();
          inList = true;
        }
        listItems.push(trimmedLine.substring(2));
        return;
      }

      // Process any pending list
      if (inList) {
        processList();
      }

      // Headers
      if (trimmedLine.startsWith('#### ')) {
        elements.push(
          <h4 key={index} className="text-lg font-semibold text-foreground mt-4 mb-2">
            {parseInlineMarkdown(trimmedLine.substring(5))}
          </h4>
        );
        return;
      }

      if (trimmedLine.startsWith('### ')) {
        elements.push(
          <h3 key={index} className="text-xl font-semibold text-foreground mt-4 mb-2">
            {parseInlineMarkdown(trimmedLine.substring(4))}
          </h3>
        );
        return;
      }

      if (trimmedLine.startsWith('## ')) {
        elements.push(
          <h2 key={index} className="text-2xl font-semibold text-foreground mt-4 mb-2">
            {parseInlineMarkdown(trimmedLine.substring(3))}
          </h2>
        );
        return;
      }

      if (trimmedLine.startsWith('# ')) {
        elements.push(
          <h1 key={index} className="text-3xl font-bold text-foreground mt-4 mb-2">
            {parseInlineMarkdown(trimmedLine.substring(2))}
          </h1>
        );
        return;
      }

      // Regular paragraph
      elements.push(
        <p key={index} className="text-sm leading-relaxed mb-2">
          {parseInlineMarkdown(trimmedLine)}
        </p>
      );
    });

    // Process any remaining list
    processList();

    return elements;
  };

  return (
    <div className={cn("prose prose-sm max-w-none dark:prose-invert", className)}>
      {parseMarkdown(content)}
    </div>
  );
}
