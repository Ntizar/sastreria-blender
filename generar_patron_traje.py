# -*- coding: utf-8 -*-
"""Patrón 1:1 (cm) de un traje de boda/oficina: chaqueta + pantalón.
Salida: patrones/patron_traje.dxf + patrones/ficha_traje.md
Uso: <python-de-blender> generar_patron_traje.py
Medidas del cuerpo de cabecera → cambia y regenera todo."""
import ezdxf, os, math

BASE = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(BASE, "patrones"); os.makedirs(SALIDA, exist_ok=True)

# ---------------- medidas del cuerpo (cm) ----------------
PECHO, CINTURA, CADERA, ALTURA = 96.0, 78.0, 100.0, 175.0
LARGO_CHAQUETA, LARGO_MANGA = 74.0, 62.0
LARGO_PANTALON, TIRO = 104.0, 27.0
CUELLO = 40.0
ANCHO_TELA = 150.0
COSTURA = 1.5  # incluida en las piezas

doc = ezdxf.new("R2010", setup=True)
msp = doc.modelspace()

def bezier(p0, p1, p2, n=22):
    """Puntos interiores de una bezier cuadrática."""
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])
            for t in (i/n for i in range(1, n))]

def pieza(nombre, puntos, notas=()):
    xs = [p[0] for p in puntos]; ys = [p[1] for p in puntos]
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    msp.add_lwpolyline(puntos, close=True, dxfattribs={"layer": "PIEZAS"})
    # piezas pequeñas: etiqueta DEBAJO de la pieza (dentro no cabe)
    if (max(ys)-min(ys)) < 16:
        y0 = min(ys)
        t = msp.add_text(nombre, dxfattribs={"height": 8.5, "layer": "ETIQUETAS"})
        t.set_placement((cx - len(nombre)*2.9, y0 - 11.0))
        for i, nota in enumerate(notas):
            n = msp.add_text(nota, dxfattribs={"height": 4.5, "layer": "ETIQUETAS"})
            n.set_placement((cx - len(nota)*1.6, y0 - 18.0 - i*5.5))
        return
    t = msp.add_text(nombre, dxfattribs={"height": 8.5, "layer": "ETIQUETAS"})
    t.set_placement((cx - len(nombre)*2.9, cy))
    for i, nota in enumerate(notas):
        n = msp.add_text(nota, dxfattribs={"height": 4.5, "layer": "ETIQUETAS"})
        n.set_placement((cx - len(nota)*1.6, cy - 11.0 - i*5.5))

def linea(p0, p1, capa="MOLDE"):
    msp.add_line(p0, p1, dxfattribs={"layer": capa})

# ---------------- piezas (coordenadas locales, y hacia arriba) ----------------
PIEZAS = []

# 0: DELANTERO x2 — del centro-frontal (x=0) a la sisa
p = [(0, 0), (27.0, 0)]
p += bezier((27, 0), (29.2, 26), (28.2, 57))          # costado
p += bezier((28.2, 57), (26.5, 68), (20.0, 74.5))     # sisa
p += [(8.0, 76.0)]                                    # hombro
p += bezier((8.0, 76.0), (3.0, 75.0), (0.0, 71.5))    # escote
p += [(0.0, 60.0)]                                    # canto frontal (ojal a botón)
PIEZAS.append(("DELANTERO", p, ["CORTE 2 (izq/der)", "solapa hacia x-"]))

# 1: TRASERO x2
p = [(0, 0), (26.5, 0)]
p += bezier((26.5, 0), (28.6, 26), (27.6, 57))        # costado
p += bezier((27.6, 57), (25.8, 68), (19.5, 73.8))     # sisa
p += [(7.0, 74.8)]                                    # hombro (más alto)
p += bezier((7.0, 74.8), (3.0, 74.2), (0.0, 73.0))    # escote poco profundo
PIEZAS.append(("TRASERO", p, ["CORTE 2", "el hombro lleva pinza"]))

# 2: MANGA x2
p = [(-22.0, 52.0)]
p += bezier((-22, 52), (-19, 62), (-8, 63.4))
p += bezier((-8, 63.4), (0, 63.6), (8, 63.4))
p += bezier((8, 63.4), (19, 62), (22.0, 52.0))        # copa
p += bezier((22, 52), (20, 30), (12.5, 0))            # costura exterior
p += [(-12.5, 0)]
p += bezier((-12.5, 0), (-20, 30), (-22, 52))
PIEZAS.append(("MANGA", p, ["CORTE 2", f"largo {LARGO_MANGA+2:.0f} con puño"]))

# 3: PANTALON (pierna) x2
p = [(-17.0, LARGO_PANTALON), (17.0, LARGO_PANTALON)]
p += bezier((17, LARGO_PANTALON), (15.0, 62), (12.0, 1.0))    # costura exterior
p += [(-8.0, 1.0)]
p += bezier((-8, 1), (-6.0, 14), (-4.0, TIRO))                # entrepierna
p += bezier((-4, TIRO), (-8.0, 62), (-17.0, LARGO_PANTALON))  # silla
PIEZAS.append(("PANTALON", p, ["CORTE 2 (espejo)", "cinturilla aparte"]))

# 4: CUELLO CAMISA (al doblez)
w = CUELLO / 2 + 22
PIEZAS.append(("CUELLO", [(0, 0), (w, 0), (w, 7.5), (0, 7.5)], ["CORTE 1 AL DOBLEZ"]))

# 5: CORBATA
p = [(0, 0), (4.6, 10), (4.6, 112), (2.6, 128), (2.6, 141), (0, 147),
     (-2.6, 141), (-2.6, 128), (-4.6, 112), (-4.6, 10)]
PIEZAS.append(("CORBATA", p, ["CORTE 1 AL DOBLEZ", "forro de corbata aparte"]))

# 6: PAÑUELO (triángulo)
PIEZAS.append(("PANUELO", [(0, 0), (22, 0), (0, 22)], ["CORTE 1"]))

# 7: BOLSILLO lateral
PIEZAS.append(("BOLSILLO LATERAL", [(0, 0), (15, 0), (15, 5.5), (0, 5.5)], ["CORTE 2"]))

# 8: BOLSILLO pecho
PIEZAS.append(("BOLSILLO PECHO", [(0, 0), (11, 0), (11, 4.5), (0, 4.5)], ["CORTE 1"]))

# 9: CINTURILLA
PIEZAS.append(("CINTURILLA", [(0, 0), (CINTURA + 8, 0), (CINTURA + 8, 5), (0, 5)],
               ["CORTE 1", f"largo {CINTURA+8:.0f}"]))

# ---------------- tendedero + consumo ----------------
def tender(grupo, x0=0.0, y0=0.0, sep=6.0):
    """Coloca las piezas en filas sobre la tela; devuelve (alto_total, offsets).
    Crece hacia arriba si y0>=0, hacia abajo si y0<0."""
    signo = 1.0 if y0 >= 0 else -1.0
    x, y, alto_fila, offs = x0, y0, 0.0, []
    for nombre, pts, notas in grupo:
        xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
        w, h = max(xs)-min(xs), max(ys)-min(ys)
        if x + w + sep > x0 + ANCHO_TELA:
            x = x0
            y += signo * (alto_fila + 16.0)  # aire extra para etiquetas bajo piezas
            alto_fila = 0.0
        dy = (y - min(ys)) if signo > 0 else (y - max(ys))
        offs.append((nombre, pts, notas, x - min(xs), dy))
        x += w + sep
        alto_fila = max(alto_fila, h)
    return abs(y - y0) + alto_fila, offs

alto_ch, offs_ch = tender([PIEZAS[0], PIEZAS[1], PIEZAS[2], PIEZAS[8], PIEZAS[6]])
alto_pt, offs_pt = tender([PIEZAS[3], PIEZAS[4], PIEZAS[7], PIEZAS[9], PIEZAS[5]], y0=-(alto_ch + 40))

def consumo(alto):  # + 8% de margen de embolsado, redondeo a 5 cm
    return math.ceil(alto * 1.08 / 5.0) * 5.0 / 100.0

cons_ch, cons_pt = consumo(alto_ch), consumo(alto_pt)

for nombre, pts, notas, dx, dy in offs_ch + offs_pt:
    pieza(nombre, [(x + dx, y + dy) for x, y in pts], notas)
    if nombre == "DELANTERO":  # línea de solapa (molde)
        linea((0 + dx, 60 + dy), (7 + dx, 74 + dy))

msp.add_text(f"TELA {ANCHO_TELA:.0f} cm — CHAQUETA",
             dxfattribs={"height": 12.0, "layer": "TITULOS"}).set_placement((-30, alto_ch + 14))
msp.add_text(f"TELA {ANCHO_TELA:.0f} cm — PANTALON",
             dxfattribs={"height": 12.0, "layer": "TITULOS"}).set_placement((-30, -(alto_ch + 28)))

ruta_dxf = os.path.join(SALIDA, "patron_traje.dxf")
doc.saveas(ruta_dxf)

# ---------------- ficha técnica ----------------
ficha = f"""# Ficha técnica — Traje de boda (azul marino)

**Honestidad:** geometría paramétrica 1:1, no simulador de tela. El patrón y
la escena 3D comparten estas mismas medidas.

## Medidas del cuerpo (cm)
| Cota | Valor |
|---|---|
| Pecho | {PECHO:.0f} |
| Cintura | {CINTURA:.0f} |
| Cadera | {CADERA:.0f} |
| Altura | {ALTURA:.0f} |
| Largo chaqueta | {LARGO_CHAQUETA:.0f} |
| Largo manga | {LARGO_MANGA:.0f} |
| Largo pantalón | {LARGO_PANTALON:.0f} |
| Tiro | {TIRO:.0f} |
| Contorno cuello | {CUELLO:.0f} |

## Piezas
- DELANTERO ×2 · TRASERO ×2 · MANGA ×2 (costura 1,5 cm incluida)
- PANTALON ×2 (espejo) + CINTURILLA (largo {CINTURA+8:.0f})
- CUELLO camisa ×1 al doblez · CORBATA ×1 al doblez · PAÑUELO ×1
- BOLSILLO lateral ×2 + pecho ×1

## Consumo estimado (tela de {ANCHO_TELA:.0f} cm, +8% margen)
| Prenda | Consumo |
|---|---|
| Chaqueta (+pañuelo, bolsillo pecho) | {cons_ch:.2f} m |
| Pantalón y complementos (corbata, cuello, cinturilla) | {cons_pt:.2f} m |
| **Total** | **{cons_ch+cons_pt:.2f} m** |

Entretela de solapas y ojales: 0,90 m. Forro opcional (mismas piezas -0,5 cm).

Hecho con ❤️ por David Antizar.
"""
ruta_md = os.path.join(SALIDA, "ficha_traje.md")
with open(ruta_md, "w", encoding="utf-8") as f:
    f.write(ficha)

print("PATRON_OK", ruta_dxf, f"chaqueta={cons_ch:.2f}m pantalon={cons_pt:.2f}m")
