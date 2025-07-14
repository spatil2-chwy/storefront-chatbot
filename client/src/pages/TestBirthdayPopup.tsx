import React from 'react';
import { formatMessageContent } from '../lib/utils';

// Safe HTML renderer component for testing
const SafeHtmlRenderer: React.FC<{ html: string; className?: string }> = ({ html, className }) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  
  React.useEffect(() => {
    if (containerRef.current) {
      // Create a temporary div to parse the HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      
      // Clear the container
      containerRef.current.innerHTML = '';
      
      // Safely append the parsed content
      while (tempDiv.firstChild) {
        containerRef.current.appendChild(tempDiv.firstChild);
      }
    }
  }, [html]);
  
  return <div ref={containerRef} className={className} />;
};

export default function TestBirthdayPopup() {
  // Test messages with various markdown content
  const testMessages = [
    {
      title: "Basic formatting",
      content: "This is **bold text** and *italic text*. Here's some `inline code` and a [link to Chewy](https://chewy.com)."
    },
    {
      title: "Lists",
      content: "Here's a numbered list:\n\n1. First item\n2. Second item\n3. Third item\n\nAnd a bullet list:\n\n- Item one\n- Item two\n- Item three"
    },
    {
      title: "Task Lists",
      content: "Here's a task list:\n\n[ ] Unchecked task\n[x] Completed task\n[ ] Another task to do\n[x] Another completed task"
    },
    {
      title: "Headers and blockquotes",
      content: "# Main Header\n\n## Sub Header\n\n### Small Header\n\n> This is a blockquote with some important information.\n\nRegular paragraph text."
    },
    {
      title: "Code blocks",
      content: "Here's a code block:\n\n```\nfunction example() {\n  return 'Hello World';\n}\n```\n\nAnd some inline `code` here."
    },
    {
      title: "Strikethrough and horizontal rules",
      content: "This text has ~~strikethrough~~ formatting.\n\n---\n\nThis is after a horizontal rule."
    },
    {
      title: "Simple Tables",
      content: "Here's a simple table:\n\n| Product | Price | Rating |\n|---------|-------|--------|\n| Dog Food | $29.99 | ⭐⭐⭐⭐⭐ |\n| Cat Toys | $12.99 | ⭐⭐⭐⭐ |\n| Bird Seed | $8.99 | ⭐⭐⭐⭐⭐ |"
    },
    {
      title: "Complex mixed content",
      content: "# Product Recommendations\n\nHere are some **great options** for your pet:\n\n1. **Premium Food** - *High quality ingredients*\n2. **Treats** - `Limited ingredients`\n3. **Toys** - [View on Chewy](https://chewy.com)\n\n## Shopping Checklist\n\n[ ] Check product reviews\n[x] Compare prices\n[ ] Read ingredient list\n[x] Check shipping options\n\n> **Note:** Always consult your vet before changing diets.\n\n---\n\nFor more information, see: [Chewy's Guide](https://chewy.com/guide)"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Message Formatting Test</h1>
        
        <div className="grid gap-6">
          {testMessages.map((test, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">{test.title}</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Raw content */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Raw Content:</h3>
                  <div className="bg-gray-100 p-4 rounded text-sm font-mono whitespace-pre-wrap">
                    {test.content}
                  </div>
                </div>
                
                {/* Formatted content */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Formatted Output:</h3>
                  <div className="bg-gray-100 p-4 rounded">
                    <SafeHtmlRenderer 
                      html={formatMessageContent(test.content)} 
                      className="prose prose-sm max-w-none"
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
