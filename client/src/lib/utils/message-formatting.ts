// Message formatting utilities for chat components
export const formatMessageContent = (content: string): string => {
  let formattedContent = content;

  // FIX INLINE BULLET POINTS AND NUMBERED LISTS
  // Replace inline bullet points with proper line breaks
  formattedContent = formattedContent.replace(/([^\n]) - /g, '$1\n- ');
  // Replace inline numbered lists with proper line breaks  
  formattedContent = formattedContent.replace(/([^\n])(\d+)\. /g, '$1\n$2. ');

  // Convert [text](url) links to <a> tags
  formattedContent = formattedContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline break-all">$1</a>');

  // Convert **bold** to <strong>
  formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');

  // Convert *italic* to <em>
  formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em class="text-gray-600 italic">$1</em>');

  // Convert ~~strikethrough~~ to <del>
  formattedContent = formattedContent.replace(/~~(.*?)~~/g, '<del class="line-through text-gray-500">$1</del>');

  // Handle standard headers (# Header)
  formattedContent = formattedContent.replace(/^### (.*$)/gm, '<h3 class="text-base font-semibold mt-4 mb-2 text-gray-900">$1</h3>');
  formattedContent = formattedContent.replace(/^## (.*$)/gm, '<h2 class="text-lg font-bold mt-4 mb-2 text-gray-900">$1</h2>');
  formattedContent = formattedContent.replace(/^# (.*$)/gm, '<h1 class="text-xl font-bold mt-4 mb-2 text-gray-900">$1</h1>');

  // Handle blockquotes (> quote)
  formattedContent = formattedContent.replace(/^> (.*$)/gm, '<blockquote class="border-l-3 border-blue-300 pl-3 italic text-gray-700 my-2 bg-blue-50 py-2 rounded-r text-sm">$1</blockquote>');

  // Handle horizontal rules (---)
  formattedContent = formattedContent.replace(/^---$/gm, '<hr class="my-3 border-gray-200">');

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

  // Convert numbered lists (1. item) and bullet lists (- item, * item) to HTML lists with clean styling
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
        processedLines.push('<ul class="list-none space-y-2 my-3">');
        inTaskList = true;
      }
      const isChecked = taskListMatch[1] === 'x';
      const checkbox = isChecked ? '☑' : '☐';
      processedLines.push(`<li class="flex items-center p-2 bg-gray-50 rounded-lg"><span class="mr-2 text-green-600">${checkbox}</span>${taskListMatch[2]}</li>`);
      return;
    }

    // Handle numbered lists (1. item)
    const numberListMatch = trimmedLine.match(/^(\d+)\.\s(.+)$/);
    if (numberListMatch) {
      const itemNumber = parseInt(numberListMatch[1]);
      const itemContent = numberListMatch[2];

      if (!inList || listType !== 'ol') {
        if (inList) processedLines.push(`</${listType}>`);
        if (inTaskList) {
          processedLines.push('</ul>');
          inTaskList = false;
        }
        // Use start attribute to begin numbering from the first number encountered
        processedLines.push(`<ol class="list-decimal list-outside space-y-1 my-3 ml-4" start="${itemNumber}">`);
        inList = true;
        listType = 'ol';
      }
      processedLines.push(`<li class="pl-2 py-0.5" value="${itemNumber}">${itemContent}</li>`);
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
        processedLines.push('<ul class="list-disc list-inside space-y-1 my-3">');
        inList = true;
        listType = 'ul';
      }
      processedLines.push(`<li class="ml-2 py-0.5">${trimmedLine.substring(2)}</li>`);
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
      // Don't wrap headers in <p> tags
      if (trimmedLine.match(/^<h[1-6]/) || trimmedLine.match(/^<div class="flex items-center/)) {
        processedLines.push(trimmedLine);
      } else {
        processedLines.push(`<p class="my-1.5 leading-relaxed text-sm">${trimmedLine}</p>`);
      }
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

  return formattedContent;
};

// Extract tags from content for quick response buttons
export const extractQuickResponseTags = (content: string): { cleanContent: string; tags: string[] } => {
  // Regular expression to match tags like <Wet><Dry><Senior> or <Wet> <Dry> <Senior> at the end of the message
  // Allow for optional spaces between tags
  const tagRegex = /(<[^>]+>(\s*<[^>]+>)*)\s*$/;
  const match = content.match(tagRegex);

  if (!match) {
    return { cleanContent: content, tags: [] };
  }

  // Extract individual tags
  const tagString = match[1];
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