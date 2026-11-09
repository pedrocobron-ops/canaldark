"""Efeitos sonoros sintetizados (sem direitos autorais).

whoosh  passagem de ar, para chicote e zoom
swish   whoosh curto, para flip de ícone
impact  pancada grave, para punch e revelação
thud    batida seca, para risco/X
ding    notificação de mensagem
pop     bolha curta
alarm   alarme de carro
"""
import numpy as np

SR = 44100
_rng = np.random.default_rng(11)


def _lp(x, a):
    """Passa-baixa de um polo com coeficiente variável por amostra (a em 0..1)."""
    y = np.empty_like(x)
    acc = 0.0
    a = np.broadcast_to(a, x.shape)
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def whoosh(d=0.38, peak=0.45):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    noise = _rng.normal(0, 1, n)
    # o corte sobe e desce: som de ar passando
    cut = 0.02 + 0.25 * np.sin(np.pi * np.clip(t / peak, 0, 1) * 0.5) * (1 - np.clip((t - peak) / (1 - peak), 0, 1)) ** 1.5
    x = _lp(noise, cut)
    x = x - _lp(x, 0.01)          # tira o grave embolado
    env = np.sin(np.pi * t) ** 1.6
    return x * env


def swish():
    return whoosh(0.2, 0.5)


def impact(d=0.7):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 70 * np.exp(-t * 4) + 32
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    click = _lp(_rng.normal(0, 1, n), 0.15) * np.exp(-t * 40)
    return body * 1.0 + click * 0.6


def thud():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (120 * np.exp(-t * 12) + 60) * t) * np.exp(-t * 18)
    noise = _lp(_rng.normal(0, 1, n), 0.3) * np.exp(-t * 50)
    return body + noise * 0.5


def ding():
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f, a, delay in [(1567.98, 0.6, 0.0), (2093.0, 0.5, 0.09)]:
        tt = np.clip(t - delay, 0, None)
        x += a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7) * (t >= delay)
    return x


def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 * np.exp(-t * 30) + 250) * t) * np.exp(-t * 35)


def alarm(d=1.8):
    n = int(d * SR)
    t = np.arange(n) / SR
    # sirene que sobe e desce rápido + bip alternado, típico de alarme de carro
    f = np.where((t * 4).astype(int) % 2 == 0, 1050, 780) + 120 * np.sin(2 * np.pi * 6 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.5 + np.sin(ph) * 0.5
    x = _lp(x, 0.35)
    fade = np.minimum(1, np.minimum(t / 0.02, (d - t) / 0.25))
    return x * fade


SOUNDS = {"whoosh": whoosh, "swish": swish, "impact": impact, "thud": thud,
          "ding": ding, "pop": pop, "alarm": alarm}
GAIN = {"whoosh": 0.32, "swish": 0.22, "impact": 0.55, "thud": 0.4,
        "ding": 0.22, "pop": 0.25, "alarm": 0.12}


def track(events, seconds):
    """events: lista de (tempo_s, nome). Devolve trilha estéreo float32."""
    out = np.zeros(int(seconds * SR) + SR, dtype=np.float32)
    cache = {}
    for t, name in events:
        if name not in SOUNDS:
            continue
        if name not in cache:
            s = SOUNDS[name]()
            cache[name] = (s / (np.abs(s).max() + 1e-9) * GAIN[name]).astype(np.float32)
        s = cache[name]
        i = max(0, int(t * SR))
        j = min(len(out), i + len(s))
        out[i:j] += s[: j - i]
    out = out[: int(seconds * SR)]
    return np.stack([out, out], 1)
