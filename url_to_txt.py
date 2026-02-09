import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

def extract_visible_text_from_url(url: str) -> str:
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    # Retirer scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Retirer commentaires HTML
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Essayer de cibler le contenu principal (fallback si non trouvé)
    main = soup.find("article") or soup.find("main") or soup.body
    text = main.get_text("\n") if main else soup.get_text("\n")

    # Nettoyage basique des lignes vides
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)

def save_text(text: str, out_txt: str) -> Path:
    out_path = Path(out_txt)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path

if __name__ == "__main__":
    URL = "https://www.gapminder.org/dollar-street"
    txt = extract_visible_text_from_url(URL)
    out = save_text(txt, "dollar_street_extracted_text.txt")
    print(f"Saved: {out}  ({len(txt)} characters)")
    print("--- preview ---")
    print(txt[:400])
