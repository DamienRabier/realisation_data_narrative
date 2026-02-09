import re
from pathlib import Path
from typing import List, Tuple, Union, Optional


def tokenize_basic(text: str) -> List[str]:
    """
    Pré-traitement (à documenter dans le rapport) :
    - minuscules
    - remplace certains symboles (ex: flèche) par des espaces
    - supprime la ponctuation/caractères spéciaux
    - conserve lettres, chiffres et apostrophes (pour "don't", "they're", etc.)
    - tokenisation par espaces
    """
    text = text.lower().replace("→", " ")
    # Conserver [a-z], [0-9] et apostrophes, remplacer le reste par des espaces
    text = re.sub(r"[^a-z0-9']+", " ", text)
    tokens = [tok for tok in text.split() if tok.strip("'")]
    return tokens


def lexical_diversity(tokens: List[str]) -> float:
    """lexical_diversity = V / N"""
    N = len(tokens)
    if N == 0:
        return 0.0
    V = len(set(tokens))
    return V / N


def trigram_repetition(tokens: List[str]) -> float:
    """
    trigram_repetition = 1 - U / (N-2)
    Convention : si N < 3, retourner 0.
    """
    N = len(tokens)
    if N < 3:
        return 0.0
    trigrams = list(zip(tokens, tokens[1:], tokens[2:]))
    total = len(trigrams)  # = N - 2
    unique = len(set(trigrams))
    return 1 - (unique / total)


def compute_text_metrics(text: str) -> Tuple[int, int, float, float]:
    tokens = tokenize_basic(text)
    N = len(tokens)
    V = len(set(tokens))
    ld = lexical_diversity(tokens)
    tr = trigram_repetition(tokens)
    return N, V, ld, tr


def main(
    path: Union[str, Path],
    out_name: str,
    out_dir: Optional[Union[str, Path]] = None
) -> Tuple[int, int, float, float, Path]:
    """
    Calcule les métriques sur le contenu d'un fichier texte UTF-8
    et écrit les résultats dans un fichier .txt.

    Args:
        path: chemin vers le fichier texte d'entrée (str ou Path)
        out_name: nom du fichier de sortie (ex: "A01_metrics.txt")
        out_dir: dossier de sortie (par défaut: dossier du script)

    Returns:
        (N_words, V_unique, lexical_diversity, trigram_repetition, out_path)
    """
    in_path = Path(path)
    if not in_path.exists():
        raise FileNotFoundError(f"File not found: {in_path}")
    if not in_path.is_file():
        raise ValueError(f"Not a file: {in_path}")

    text = in_path.read_text(encoding="utf-8")
    N, V, ld, tr = compute_text_metrics(text)

    out_base = Path(out_dir) if out_dir is not None else Path.cwd()
    out_base.mkdir(parents=True, exist_ok=True)
    out_path = out_base / out_name

    content = (
        f"input_file={in_path.name}\n"
        f"N_words={N}\n"
        f"V_unique={V}\n"
        f"lexical_diversity={ld:.10f}\n"
        f"trigram_repetition={tr:.10f}\n"
    )
    out_path.write_text(content, encoding="utf-8")

    return N, V, ld, tr, out_path


if __name__ == "__main__":
    in_file = "bowling.txt"
    out_file = "bowling_text_metrics.txt"
    N, V, ld, tr, out_path = main(in_file, out_name=out_file)
    print(f"Wrote results to: {out_path}")
