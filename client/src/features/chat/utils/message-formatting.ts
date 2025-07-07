// Message formatting utilities for chat components
export const formatMessageContent = (content: string): string => {
  let formattedContent = content;
  
  // Convert [text](url) links to <a> tags
  formattedContent = formattedContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="break-all">$1</a>');
  
  // Convert **bold** to <strong>
  formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert *italic* to <em>
  formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Convert numbered lists (1. item) to proper HTML lists
  if (/^\d+\.\s/m.test(formattedContent)) {
    const lines = formattedContent.split('\n');
    let inList = false;
    let listType = '';
    const processedLines: string[] = [];
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      const numberListMatch = trimmedLine.match(/^(\d+)\.\s(.+)$/);
      
      if (numberListMatch) {
        if (!inList || listType !== 'ol') {
          if (inList) processedLines.push(`</${listType}>`);
          processedLines.push('<ol>');
          inList = true;
          listType = 'ol';
        }
        processedLines.push(`<li>${numberListMatch[2]}</li>`);
      } else if (trimmedLine.startsWith('- ')) {
        if (!inList || listType !== 'ul') {
          if (inList) processedLines.push(`</${listType}>`);
          processedLines.push('<ul>');
          inList = true;
          listType = 'ul';
        }
        processedLines.push(`<li>${trimmedLine.substring(2)}</li>`);
      } else {
        if (inList) {
          processedLines.push(`</${listType}>`);
          inList = false;
          listType = '';
        }
        if (trimmedLine) {
          processedLines.push(`<p>${trimmedLine}</p>`);
        }
      }
    });
    
    if (inList) {
      processedLines.push(`</${listType}>`);
    }
    
    formattedContent = processedLines.join('');
  } else {
    // Just wrap paragraphs if no lists
    const paragraphs = formattedContent.split('\n\n');
    formattedContent = paragraphs
      .filter(p => p.trim())
      .map(p => `<p>${p.trim().replace(/\n/g, '<br>')}</p>`)
      .join('');
  }
  
  return formattedContent;
}; 