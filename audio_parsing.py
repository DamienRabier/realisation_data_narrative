# a23_transcript.py
# =================
# Objectif :
# 1) Récupérer le transcript officiel YouTube si disponible
# 2) Sinon : télécharger l'audio et transcrire avec Whisper
# 3) Écrire le texte dans un .txt (trace)

# ---- CONFIG (à modifier) ----
YOUTUBE_URL = "https://www.youtube.com/watch?v=AhWWO0EtM1c"
OUT_TXT = "bristol_transcript.txt"

# Ordre des langues tentées pour le transcript YouTube
TRANSCRIPT_LANGS = ("en", "en-GB", "en-US")

# Fallback Whisper
USE_WHISPER_FALLBACK = True
WHISPER_MODEL = "small"     # tiny/base/small/medium/large
WHISPER_LANGUAGE = "en"     # adapte si besoin
TMP_DIR = "tmp_youtube_audio"

# -----------------------------
import re
import subprocess
from pathlib import Path
import whisper
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Extrait l'ID vidéo (11 chars) depuis une URL YouTube / youtu.be."""
    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    if not m:
        raise ValueError(f"Impossible d'extraire l'ID vidéo depuis l'URL: {url}")
    return m.group(1)


def try_fetch_youtube_transcript(video_id: str, languages=TRANSCRIPT_LANGS) -> str | None:
    """
    Tente de récupérer un transcript (manuel ou auto) via youtube-transcript-api.
    Retourne le texte ou None si indisponible.
    """
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id, languages=list(languages))
        return "\n".join(seg["text"] for seg in segments).strip()
    except Exception:
        return None


def download_audio_with_ytdlp(url: str, tmp_dir: Path) -> Path:
    """
    Télécharge l'audio via yt-dlp et sort un fichier mp3.
    Nécessite yt-dlp et ffmpeg installés.
    """
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(tmp_dir / "audio.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", out_tmpl,
        url,
    ]
    subprocess.check_call(cmd)

    audio_path = tmp_dir / "audio.mp3"
    if not audio_path.exists():
        # yt-dlp peut parfois produire un autre nom/ext si config différente
        # on cherche le premier mp3 dans tmp_dir
        mp3s = list(tmp_dir.glob("*.mp3"))
        if not mp3s:
            raise FileNotFoundError("Audio mp3 introuvable après yt-dlp.")
        audio_path = mp3s[0]
    return audio_path


def transcribe_with_whisper(audio_path: Path, model_name: str, language: str) -> str:
    """
    Transcription Whisper locale.
    Nécessite openai-whisper + ffmpeg.
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path), language=language)
    return (result.get("text") or "").strip()


def write_text(out_txt: str, text: str) -> Path:
    out_path = Path(out_txt)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def main() -> None:
    video_id = extract_video_id(YOUTUBE_URL)

    # 1) Transcript officiel YouTube
    text = try_fetch_youtube_transcript(video_id, languages=TRANSCRIPT_LANGS)

    # 2) Fallback Whisper si besoin
    if (not text) and USE_WHISPER_FALLBACK:
        tmp = Path(TMP_DIR)
        audio = download_audio_with_ytdlp(YOUTUBE_URL, tmp)
        text = transcribe_with_whisper(audio, model_name=WHISPER_MODEL, language=WHISPER_LANGUAGE)

    if not text:
        raise RuntimeError(
            "Aucun transcript récupéré (pas de transcript YouTube) et fallback Whisper désactivé/échoué."
        )

    out = write_text(OUT_TXT, text)
    print(f"Transcript saved to: {out.resolve()}")


if __name__ == "__main__":
    main()
