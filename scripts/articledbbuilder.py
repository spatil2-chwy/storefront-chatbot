import json
import html
from bs4 import BeautifulSoup
from tqdm import tqdm
import chromadb

# === Load Articles ===
with open('../data/chromadb/all_wp_posts.json', 'r') as file:
    articles = json.load(file)

# === HTML to Markdown Conversion ===
def html_to_markdown(html_text):
    soup = BeautifulSoup(html_text or '', "html.parser")
    return soup.get_text(separator="\n").strip()

# === Article Parsing Functions ===
def format_author(author_list):
    if not author_list:
        return ""
    author = author_list[0]
    name = author.get("post_title", "Unknown Author")
    bio = html_to_markdown(author.get("post_content", ""))
    return f"**Author:** {name}\n{bio}\n"

def format_key_takeaways(template_list):
    takeaways = []
    for block in template_list:
        if block.get("acf_fc_layout") == "item_list":
            title = block.get("title", "Key Takeaways")
            items = [f"- {item['item'].strip()}" for item in block.get("items", [])]
            takeaways.append(f"### {title}\n" + "\n".join(items))
    return "\n".join(takeaways)

def format_content_blocks(template_list):
    sections = []
    for block in template_list:
        layout = block.get("acf_fc_layout")
        if layout == "heading":
            sections.append(f"## {block.get('heading_text', '').strip()}")
        elif layout == "text_area":
            text = html_to_markdown(block.get("wysiwyg_content", ""))
            sections.append(text)
        elif layout == "product_card_set":
            title = block.get("product_card_set", {}).get("post_title", "")
            if title:
                sections.append(f"**Product Card Set:** _{title}_")
    return "\n".join(sections)

def format_faq_section(template_list):
    faq_section = []
    for block in template_list:
        if block.get("acf_fc_layout") == "text_area" and "Q:" in block.get("wysiwyg_content", ""):
            text = html_to_markdown(block["wysiwyg_content"])
            faq_section.append("### FAQs\n" + text)
    return "\n".join(faq_section)

# === Convert Single Article to Markdown ===
def wordpress_article_to_markdown(article: dict) -> str:
    try:
        sub_heading = article.get("sub_heading", "").strip()
        intro = html_to_markdown(article.get("intro", ""))
        expert_input = html_to_markdown(article.get("expert_input", ""))
        key_takeaways = format_key_takeaways(article.get("template_standard_article", []))
        body = format_content_blocks(article.get("template_standard_article", []))
        faqs = format_faq_section(article.get("template_standard_article", []))

        doc = f"# {sub_heading}\n"

        if intro:
            doc += f"\n### Introduction\n{intro}\n"

        if key_takeaways:
            doc += "\n" + key_takeaways + "\n"

        if body:
            doc += "\n" + body + "\n"

        if faqs:
            doc += "\n" + faqs + "\n"

        if expert_input:
            doc += f"\n> {expert_input.strip()}"

        return doc.strip()
    except Exception as e:
        print("Error parsing article:", e)
        return ""

# === Convert All Articles ===
markdowns = [wordpress_article_to_markdown(article['acf']) for article in articles]
metadatas = [
    {'link': article['frontend_path'], 'title': article['title']['rendered']}
    for article in articles
]
ids = [str(article['id']) for article in articles]

# === Initialize ChromaDB Persistent Client ===
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="wordpress_articles")

# === Batch Indexing ===
batch_size = 64
for i in tqdm(range(0, len(markdowns), batch_size), desc="Indexing articles"):
    batch_docs = markdowns[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    batch_meta = metadatas[i:i+batch_size]

    collection.upsert(
        documents=batch_docs,
        ids=batch_ids,
        metadatas=batch_meta
    )

# === Sample Query ===
print("\n🔍 Test Query:")
results = collection.query(
    query_texts=["advice for arthritic dog"],
    n_results=2
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"📘 Title: {meta['title']}\n🔗 Link: {meta['link']}\n📝 Snippet:\n{doc[:300]}...\n---\n")
