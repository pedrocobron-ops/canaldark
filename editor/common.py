from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30

FONT_CAPTION = ROOT / "assets/fonts/LuckiestGuy-Regular.ttf"
FONT_EMOJI = Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
FONT_UI = Path("/usr/share/fonts/opentype/inter/Inter-Regular.otf")
FONT_UI_BOLD = Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf")

MODEL_DIR = ROOT / "models"
KOKORO_MODEL = MODEL_DIR / "kokoro-v1.0.int8.onnx"
KOKORO_VOICES = MODEL_DIR / "voices-v1.0.bin"

# cores das palavras-chave: {y:palavra}
COLORS = {
    "y": (255, 230, 0),     # destaque
    "r": (255, 43, 43),     # perigo, impacto
    "g": (60, 224, 90),     # apps verdes
    "b": (47, 139, 255),    # apps azuis
    "o": (255, 138, 0),
    "p": (255, 95, 210),
    "w": (255, 255, 255),
    "v": (178, 102, 255),   # roxo (Barney)
}
