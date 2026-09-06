#!/usr/bin/env python3
"""🧪 EL EXPERIMENTO DEL GATITO INFINITO.

El gato NO se elige. SE CONSTRUYE.

Cada corrida toma 64 bits reales de entropía del SO y los reparte en
8 bytes independientes, uno por parte del gato. Solo byte == 0 produce
la pieza canónica para esa parte:

    P(TRUE_CAT) = (1/256)^8 = 1 / 2^64  ≈  5.4e-20  por corrida.

Cuencas de fallo:
    8/8 hits  -> CAT         (jackpot absoluto)
    7/8 hits  -> DOG         (fallo estructurado A: un solo fallo)
    <=1 hit   -> CUP         (fallo estructurado B: nada coincide)
    resto     -> ABOMINATION (mutante inclasificable)

REGLA SAGRADA: THE CI MUST NEVER GUARANTEE THAT THE CAT WILL APPEAR.
Ni la fecha, ni el contador de días, ni el número de commits condicionan
el resultado. Cada corrida publica su roll en cat_log.jsonl (entropía,
bytes por parte, hits, verdict) para que nadie pueda decir que el gato
salió a convenio.
"""
import json
import secrets
import time

# 8 partes. Ningún pool de abominaciones incluye la pieza canónica:
# eso es lo que hace que hits==8 implique gato canónico y nada más.
PARTS = [
    ("ears",   "/\\_/\\", ["<~_~>", "~,_,~", "(oYo)", "_____", "|-\\_/-|", "?.?.?"]),
    ("face_l", "(",       ["[", "{", "<", "¿", "¡", "ε"]),
    ("eye_l",  "o",       ["O", "0", "-", "x", "@", "°"]),
    ("eye_r",  "o",       ["O", "0", "-", "x", "@", "°"]),
    ("face_r", ")",       ["]", "}", ">", "!", "?", "ж"]),
    ("jaw",    ">",       ["w", "u", "~", "_", "?", "¯"]),
    ("nose",   "^",       ["v", "w", "3", "?", "Δ", "≈"]),
    ("chin",   "<",       [">", "«", "-", ".", "!", "¿"]),
]
# El gato canónico que emerge SOLO si las 8 piezas son canónicas:
#       /\_/\
#      ( o.o )
#       > ^ <

VERDICTS = ("CAT", "DOG", "CUP", "ABOMINATION")
LOG_PATH = "cat_log.jsonl"


def build_cat(byte_values):
    """Construye la criatura a partir de 8 bytes. Determinista dado bytes.

    Solo byte == 0 produce la pieza canónica. Las abominaciones derivan del
    mismo byte (auditables), nunca coinciden con lo canónico.
    """
    glyphs = {}
    for (name, canonical, abominations), b in zip(PARTS, byte_values):
        glyphs[name] = canonical if b == 0 else abominations[b % len(abominations)]
    hits = sum(1 for b in byte_values if b == 0)
    cat = (f" {glyphs['ears']}\n"
           f"{glyphs['face_l']} {glyphs['eye_l']}.{glyphs['eye_r']} {glyphs['face_r']}\n"
           f" {glyphs['jaw']} {glyphs['nose']} {glyphs['chin']}")
    if hits == len(PARTS):
        verdict = "CAT"
    elif hits == len(PARTS) - 1:
        verdict = "DOG"
    elif hits <= 1:
        verdict = "CUP"
    else:
        verdict = "ABOMINATION"
    return cat, hits, verdict


def main():
    # consola Windows puede ser cp1252; el log y cat.txt siempre son UTF-8
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    roll = secrets.randbits(64)
    byte_values = [(roll >> (8 * i)) & 0xFF for i in range(8)]
    cat, hits, verdict = build_cat(byte_values)

    with open("cat.txt", "w", encoding="utf-8") as f:
        f.write(cat)

    record = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entropy_source": "secrets.randbits(64) -> os.urandom (SystemRandom)",
        "roll_hex": f"{roll:016x}",
        "bytes": byte_values,
        "hits": hits,
        "parts_canonical": [PARTS[i][0] for i, b in enumerate(byte_values) if b == 0],
        "verdict": verdict,
        "cat": cat,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(cat)
    print(f"\nroll={record['roll_hex']} hits={hits}/8 verdict={verdict}")


if __name__ == "__main__":
    main()
