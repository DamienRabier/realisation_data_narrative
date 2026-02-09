import re
from pathlib import Path
from typing import List, Tuple, Union, Optional
from bs4 import BeautifulSoup


def extract_ncase_words_text(html_path: Union[str, Path]) -> str:
    """
    Extrait le texte narratif de projets Nicky Case (Crowds) :
    - prend uniquement les balises <words id="...">
    - exclut preloader_* et translations_* (UI non-narrative)
    """
    html_path = Path(html_path)
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    parts = []
    for w in soup.find_all("words"):
        wid = w.get("id") or ""
        if wid.startswith("preloader_") or wid.startswith("translations_") or wid == "translations_original":
            continue

        t = w.get_text("\n")
        lines = [ln.strip() for ln in t.splitlines()]
        lines = [ln for ln in lines if ln]
        if lines:
            parts.append("\n".join(lines))

    return "\n".join(parts)


def tokenize_basic(text: str) -> List[str]:
    # mêmes conventions que tes autres scripts
    text = text.lower().replace("→", " ")
    text = re.sub(r"[^a-z0-9']+", " ", text)  # conserve lettres/chiffres/apostrophes
    tokens = [tok for tok in text.split() if tok.strip("'")]
    return tokens


def lexical_diversity(tokens: List[str]) -> float:
    N = len(tokens)
    return (len(set(tokens)) / N) if N else 0.0


def trigram_repetition(tokens: List[str]) -> float:
    N = len(tokens)
    if N < 3:
        return 0.0
    trigrams = list(zip(tokens, tokens[1:], tokens[2:]))
    return 1 - (len(set(trigrams)) / len(trigrams))


def compute_text_metrics_from_html(html_path: Union[str, Path]) -> Tuple[int, int, float, float]:
    text = extract_ncase_words_text(html_path)
    tokens = tokenize_basic(text)
    N = len(tokens)
    V = len(set(tokens))
    return N, V, lexical_diversity(tokens), trigram_repetition(tokens)


def main(path: Union[str, Path], out_name: str, out_dir: Optional[Union[str, Path]] = None):
    path = Path(path)
    N, V, ld, tr = compute_text_metrics_from_html(path)

    out_base = Path(out_dir) if out_dir else Path.cwd()
    out_base.mkdir(parents=True, exist_ok=True)
    out_path = out_base / out_name

    out_path.write_text(
        f"input_file={path.name}\n"
        f"N_words={N}\n"
        f"V_unique={V}\n"
        f"lexical_diversity={ld:.10f}\n"
        f"trigram_repetition={tr:.10f}\n",
        encoding="utf-8",
    )

    return N, V, ld, tr, out_path


if __name__ == "__main__":
    in_file = "crowds.html"
    out_file = "crowds_text_metrics.txt"
    N, V, ld, tr, out = main(in_file, out_name=out_file)
    print("Wrote:", out)
