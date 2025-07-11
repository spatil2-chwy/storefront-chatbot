// Message formatting utilities for chat components
export const formatMessageContent = (content: string): string => {
  let formattedContent = content;
  
  // Handle code blocks (```code```) to prevent markdown processing
  const codeBlocks: string[] = [];
  formattedContent = formattedContent.replace(/```([\s\S]*?)```/g, (match, code) => {
    const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
    codeBlocks.push(`<pre class="bg-gray-100 p-3 rounded text-sm overflow-x-auto"><code>${escapeHtml(code)}</code></pre>`);
    return placeholder;
  });

  // Handle inline code (`code`)
  formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">$1</code>');
  
  // Convert [text](url) links to <a> tags
  formattedContent = formattedContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline break-all">$1</a>');
  
  // Convert **bold** to <strong>
  formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert *italic* to <em>
  formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Convert ~~strikethrough~~ to <del>
  formattedContent = formattedContent.replace(/~~(.*?)~~/g, '<del class="line-through">$1</del>');
  
  // Handle headers (# Header)
  formattedContent = formattedContent.replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
  formattedContent = formattedContent.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-4 mb-2">$1</h2>');
  formattedContent = formattedContent.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>');
  
  // Handle blockquotes (> quote)
  formattedContent = formattedContent.replace(/^> (.*$)/gm, '<blockquote class="border-l-4 border-gray-300 pl-4 italic text-gray-700 my-2">$1</blockquote>');
  
  // Handle horizontal rules (---)
  formattedContent = formattedContent.replace(/^---$/gm, '<hr class="my-4 border-gray-300">');
  
  // Handle simple tables (basic support)
  formattedContent = formattedContent.replace(/\|(.+)\|/g, (match, content) => {
    const cells = content.split('|').map((cell: string) => cell.trim());
    if (cells.length > 1) {
      return `<tr>${cells.map((cell: string) => `<td class="border border-gray-300 px-2 py-1">${cell}</td>`).join('')}</tr>`;
    }
    return match;
  });
  
  // Wrap table rows in table structure if detected
  if (formattedContent.includes('<tr>')) {
    formattedContent = formattedContent.replace(/(<tr>.*?<\/tr>)/g, '<table class="border-collapse border border-gray-300 my-2"><tbody>$1</tbody></table>');
  }
  
  // Convert numbered lists (1. item) and bullet lists (- item, * item) to HTML lists
  const lines = formattedContent.split('\n');
  let inList = false;
  let listType = '';
  let inTaskList = false;
  const processedLines: string[] = [];
  
  lines.forEach(line => {
    const trimmedLine = line.trim();
    
    // Handle task lists ([ ] item, [x] item)
    const taskListMatch = trimmedLine.match(/^\[([ x])\] (.+)$/);
    if (taskListMatch) {
      if (!inTaskList) {
        if (inList) {
          processedLines.push(`</${listType}>`);
          inList = false;
          listType = '';
        }
        processedLines.push('<ul class="list-none space-y-1 my-2">');
        inTaskList = true;
      }
      const isChecked = taskListMatch[1] === 'x';
      const checkbox = isChecked ? '☑' : '☐';
      processedLines.push(`<li class="flex items-center ml-2"><span class="mr-2">${checkbox}</span>${taskListMatch[2]}</li>`);
      return;
    }
    
    // Handle numbered lists (1. item)
    const numberListMatch = trimmedLine.match(/^(\d+)\.\s(.+)$/);
    if (numberListMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) processedLines.push(`</${listType}>`);
        if (inTaskList) {
          processedLines.push('</ul>');
          inTaskList = false;
        }
        processedLines.push('<ol class="list-decimal list-inside space-y-1 my-2">');
        inList = true;
        listType = 'ol';
      }
      processedLines.push(`<li class="ml-2">${numberListMatch[2]}</li>`);
      return;
    }
    
    // Handle bullet lists (- item, * item)
    if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
      if (!inList || listType !== 'ul') {
        if (inList) processedLines.push(`</${listType}>`);
        if (inTaskList) {
          processedLines.push('</ul>');
          inTaskList = false;
        }
        processedLines.push('<ul class="list-disc list-inside space-y-1 my-2">');
        inList = true;
        listType = 'ul';
      }
      processedLines.push(`<li class="ml-2">${trimmedLine.substring(2)}</li>`);
      return;
    }
    
    // Handle regular text (not list items)
    if (inList || inTaskList) {
      if (inList) {
        processedLines.push(`</${listType}>`);
        inList = false;
        listType = '';
      }
      if (inTaskList) {
        processedLines.push('</ul>');
        inTaskList = false;
      }
    }
    
    if (trimmedLine) {
      processedLines.push(`<p class="my-2">${trimmedLine}</p>`);
    }
  });
  
  // Close any open lists
  if (inList) {
    processedLines.push(`</${listType}>`);
  }
  if (inTaskList) {
    processedLines.push('</ul>');
  }
  
  formattedContent = processedLines.join('');
  
  // Restore code blocks
  codeBlocks.forEach((block, index) => {
    formattedContent = formattedContent.replace(`__CODE_BLOCK_${index}__`, block);
  });
  
  return formattedContent;
};

// Extract tags from content for quick response buttons
export const extractQuickResponseTags = (content: string): { cleanContent: string; tags: string[] } => {
  // Regular expression to match tags like <Wet><Dry><Senior> at the end of the message
  const tagRegex = /(<[^>]+>)+\s*$/;
  const match = content.match(tagRegex);
  
  if (!match) {
    return { cleanContent: content, tags: [] };
  }
  
  // Extract individual tags
  const tagString = match[0];
  const individualTagRegex = /<([^>]+)>/g;
  const tags: string[] = [];
  let tagMatch;
  
  while ((tagMatch = individualTagRegex.exec(tagString)) !== null) {
    tags.push(tagMatch[1].trim());
  }
  
  // Remove tags from content
  const cleanContent = content.replace(tagRegex, '').trim();
  
  return { cleanContent, tags };
};

// Escape HTML in code blocks
function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}