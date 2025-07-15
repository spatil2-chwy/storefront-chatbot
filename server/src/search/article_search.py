import chromadb
from typing import List, Dict, Any, Optional
import os

class ArticleService:
    def __init__(self):
        try:
            # Always use the project root chroma_db directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            chroma_db_path = os.path.join(project_root, "chroma_db")
            self.client = chromadb.PersistentClient(path=chroma_db_path)
            self.collection = self.client.get_collection(name="wordpress_articles")
        except Exception as e:
            print(f"Error initializing ChromaDB client: {e}")
            self.client = None
            self.collection = None

    def search_articles(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant articles based on user query.
        
        Args:
            query: The search query from the user
            n_results: Number of results to return (default 3)
            
        Returns:
            List of dictionaries containing article information
        """
        if not self.collection:
            print("ChromaDB collection not available")
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            articles = []
            if results["documents"] and results["metadatas"]:
                for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                    # Extract the first few paragraphs as a summary
                    content_lines = doc.split('\n')
                    summary_lines = []
                    for line in content_lines:
                        if line.strip() and not line.startswith('#'):
                            summary_lines.append(line.strip())
                            if len(' '.join(summary_lines)) > 1000:  # Keep summary under 1000 chars
                                break
                    
                    summary = ' '.join(summary_lines)[:1000] + "..." if len(' '.join(summary_lines)) > 1000 else ' '.join(summary_lines)
                    
                    articles.append({
                        'title': meta.get('title', 'Untitled'),
                        'link': meta.get('link', ''),
                        'summary': summary,
                        'full_content': doc
                    })
            
            return articles
            
        except Exception as e:
            print(f"Error searching articles: {e}")
            return []

    def get_article_summary_for_llm(self, articles: List[Dict[str, Any]]) -> str:
        """
        Format articles for LLM consumption.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Formatted string for LLM
        """
        if not articles:
            return "No relevant articles found."
        
        formatted_articles = []
        for i, article in enumerate(articles, 1):
            formatted_article = f"""Article {i}: {article['title']}
Summary: {article['summary']}
Link: {article['link']}
"""
            formatted_articles.append(formatted_article)
        
        return "\n".join(formatted_articles)
