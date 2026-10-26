#!/usr/bin/env python3
"""Patrón paramétrico 1:1 de una capa española clásica (DXF + ficha técnica).

Sastrería real: piezas con cotas derivadas de las medidas del cuerpo, etiquetas
de corte y consumo de tela calculado desde la marcada. Correrlo con el Python
de Blender (tiene ezdxf) o cualquier intérprete con ezdxf:

  python generar_patron_capa.py --salida DIR

Salidas en DIR:
  patron_capa_espanola.dxf   patrón 1:1 (unidades cm) para plotter/impresión
  ficha_capa_espanola.md     ficha técnica con las mismas cifras

Piezas (sastrería clásica de capa):
  1. CUERPO  — semicírculo al doblez con hueco de cuello (annulus semicircular)
  2. CAPILLO — semicírculo corto al doblez que cubre hombros
  3. CORDÓN  — cinta de cierre
  4. GALÓN   — ribete del bajo (se corta a la medida del perímetro)
"""
import argparse
import json
import math
import os

import ezdxf

# --- Medidas del cuerpo (cm) — cambiar aqui para tallas distintas ---
ALTURA = 175
PERIM_CUELLO = 38.0
LARGO_CAPA = 95.0      # hombro -> bajo
LARGO_CAPILLO = 30.0   # hombro -> punta del capillo
ANCHO_CORDON = 3.0
ANCHO_GALON = 4.0
ANCHO_TELA = 140.0     # paño estándar

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=".")
    args = ap.parse_args()
    os.makedirs(args.salida, exist_ok=True)

    r_cuello = PERIM_CUELLO / (2 * math.pi)          # R = c/2pi
    R_cuerpo = LARGO_CAPA + r_cuello                 # el largo sale del hueco
    R_capillo = LARGO_CAPILLO + r_cuello
    perim_bajo = math.pi * R_cuerpo                  # semicírculo al doblez
    perim_capillo = math.pi * R_capillo

    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4  # cm
    doc.header["$MEASUREMENT"] = 1
    msp = doc.modelspace()
    desplaz = {"x": 0.0}

    def pieza_anular(nombre, nota, R_out, R_in, y):
        """Semicírculo anular al doblez, con etiqueta."""
        msp.add_lwpolyline([(0, y - R_in), (0, y - R_out)], dxfattribs={"layer": nombre})
        msp.add_arc((0, y), R_out, 270, 90, dxfattribs={"layer": nombre})
        msp.add_lwpolyline([(0, y + R_out), (0, y + R_in)], dxfattribs={"layer": nombre})
        msp.add_arc((0, y), R_in, 90, 270, dxfattribs={"layer": nombre})
        t = msp.add_text(nombre, dxfattribs={"height": 6, "layer": "ETIQUETAS"})
        t.set_placement((R_out * 0.18, y - 4))
        t2 = msp.add_text(nota, dxfattribs={"height": 3.5, "layer": "ETIQUETAS"})
        t2.set_placement((R_out * 0.18, y - 11))

    # Pieza 1: cuerpo (colocada a la derecha)
    pieza_anular("CUERPO", "CORTE 1 AL DOBLEZ - paño guinda", R_cuerpo, r_cuello, 0)
    desplaz["x"] = R_cuerpo * 2 + 30
    # Pieza 2: capillo, dibujada desplazada a la derecha del cuerpo
    x0 = desplaz["x"]
    msp.add_lwpolyline([(x0, -r_cuello), (x0, -R_capillo)], dxfattribs={"layer": "CAPILLO"})
    msp.add_arc((x0, 0), R_capillo, 270, 90, dxfattribs={"layer": "CAPILLO"})
    msp.add_lwpolyline([(x0, R_capillo), (x0, r_cuello)], dxfattribs={"layer": "CAPILLO"})
    msp.add_arc((x0, 0), r_cuello, 90, 270, dxfattribs={"layer": "CAPILLO"})
    t = msp.add_text("CAPILLO", dxfattribs={"height": 6, "layer": "ETIQUETAS"})
    t.set_placement((x0 + R_capillo * 0.15, -12))
    t2 = msp.add_text("CORTE 1 AL DOBLEZ", dxfattribs={"height": 3.5, "layer": "ETIQUETAS"})
    t2.set_placement((x0 + R_capillo * 0.15, -19))

    # Pieza 3: cordón — rectángulo debajo del capillo
    x1 = x0 + R_capillo + 25
    msp.add_lwpolyline([(x1, -ANCHO_CORDON), (x1 + 95, -ANCHO_CORDON),
                        (x1 + 95, 0), (x1, 0)], close=True,
                       dxfattribs={"layer": "CORDON"})
    t = msp.add_text("CORDON  95x3", dxfattribs={"height": 4, "layer": "ETIQUETAS"})
    t.set_placement((x1, 6))

    # Pieza 4: galón — cinta a la medida del bajo (indicación, no se corta de paño)
    t = msp.add_text("GALON DORADO: %.0f cm (perimetro del bajo) x %d cm"
                     % (perim_bajo, ANCHO_GALON),
                     dxfattribs={"height": 4, "layer": "ETIQUETAS"})
    t.set_placement((-R_cuerpo, -R_cuerpo - 18))

    # Capas visibles y colores
    for capa, color in [("CUERPO", 1), ("CAPILLO", 5), ("CORDON", 3),
                        ("ETIQUETAS", 7)]:
        doc.layers.add(capa, color=color)

    dxf_path = os.path.join(args.salida, "patron_capa_espanola.dxf")
    doc.saveas(dxf_path)

    # --- Marcada y consumo (paño de 140, pieza al doblez) ---
    # Cuerpo al doblez: paño plegado, aprovecha R_cuerpo de largo por capa
    consumo = 2 * R_cuerpo / 100 + R_capillo / 100 + 0.15  # +15 cm de margen/rollos
    ficha = {
        "prenda": "Capa española clásica",
        "talla": "base %.0f cm de altura" % ALTURA,
        "medidas": {"perimetro_cuello": PERIM_CUELLO, "largo_capa": LARGO_CAPA,
                     "largo_capillo": LARGO_CAPILLO},
        "radios_derivados_cm": {"r_cuello": round(r_cuello, 1),
                                 "R_cuerpo": round(R_cuerpo, 1),
                                 "R_capillo": round(R_capillo, 1)},
        "perimetro_bajo_cm": round(perim_bajo, 0),
        "piezas": [
            ["CUERPO", "1 al doblez", "paño guinda 500 g/m2"],
            ["CAPILLO", "1 al doblez", "paño guinda"],
            ["CORDON", "1", "terciopelo guinda 95x3"],
            ["GALON", "a medida", "cinta dorada %.0f x %d cm" % (perim_bajo, ANCHO_GALON)],
        ],
        "consumo_tela_m": round(consumo, 2),
        "ancho_tela_cm": ANCHO_TELA,
    }
    with open(os.path.join(args.salida, "ficha_capa_espanola.json"), "w",
              encoding="utf-8") as f:
        json.dump(ficha, f, ensure_ascii=False, indent=2)

    md = """# Ficha técnica — Capa española clásica

**Talla base:** altura %.0f cm · **Tejido:** paño de pura lana 500 g/m², guinda
**Consumo calculado por marcada:** **%.2f m** de %.0f cm de ancho

## Medidas del cuerpo

| Medida | Valor |
|---|---|
| Perímetro de cuello | %.0f cm |
| Largo de capa (hombro → bajo) | %.0f cm |
| Largo del capillo | %.0f cm |

## Piezas y corte

| Pieza | Corte | Notas |
|---|---|---|
| CUERPO | 1 al doblez | semicírculo R=%.1f con hueco de cuello r=%.1f |
| CAPILLO | 1 al doblez | semicírculo R=%.1f |
| CORDÓN | 1 | terciopelo, 95×%d cm |
| GALÓN | a medida | cinta dorada %.0f×%d cm en el bajo |

## Construcción

1. Cerrar hombros del cuerpo y capillo (costura de 1 cm, pegadas al doblez).
2. Montar el capillo sobre el cuerpo en la sisa del cuello.
3. Dobladillar el bajo a 4 cm y coser el galón dorado a vivo.
4. Forrar el cuello con cinta y practicar ojales para el cordón.

*Patrón generado paramétricamente (DXF 1:1, unidades cm): `patron_capa_espanola.dxf`.*
*Cambiar las medidas de cabecera del generador regenera patrón y ficha.*
""" % (ALTURA, consumo, ANCHO_TELA, PERIM_CUELLO, LARGO_CAPA, LARGO_CAPILLO,
       R_cuerpo, r_cuello, R_capillo, ANCHO_CORDON, perim_bajo, ANCHO_GALON)
    with open(os.path.join(args.salida, "ficha_capa_espanola.md"), "w",
              encoding="utf-8") as f:
        f.write(md)

    print("PATRON_OK R_cuerpo=%.1f r_cuello=%.1f R_capillo=%.1f bajo=%.0fcm consumo=%.2fm" % (
        R_cuerpo, r_cuello, R_capillo, perim_bajo, consumo))

if __name__ == "__main__":
    main()
