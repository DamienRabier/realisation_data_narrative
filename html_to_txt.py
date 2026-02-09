import re
from pathlib import Path
from typing import Union
from bs4 import BeautifulSoup
from bs4.element import Comment


def extract_visible_text_from_html(path: Union[str, Path]) -> str:
    """
    Extrait le texte visible d'un fichier HTML :
    - supprime <script>, <style>
    - supprime les commentaires HTML
    - récupère le texte rendu
    - nettoie les lignes vides
    """
    path = Path(path)
    html = path.read_text(encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")

    # Retirer scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Retirer commentaires HTML
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Texte brut
    text = soup.get_text("\n")

    # Nettoyage de lignes vides
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def dump_extracted_text(html_path: Union[str, Path], out_txt: Union[str, Path]) -> Path:
    """
    Extrait le texte visible et l'écrit dans un fichier .txt UTF-8.
    """
    out_txt = Path(out_txt)
    out_txt.parent.mkdir(parents=True, exist_ok=True)

    text = extract_visible_text_from_html(html_path)
    out_txt.write_text(text, encoding="utf-8")
    return out_txt


if __name__ == "__main__":
    html_path = "sam_kerr.html"
    out_txt = "sam_kerr_extracted_text.txt"
    out_path = dump_extracted_text(html_path, out_txt)
    print(f"Extracted text saved to: {out_path}")
