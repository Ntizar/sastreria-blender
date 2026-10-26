# Bibliografía de sastrería — por dónde aprender

Mapeado a nuestro pipeline: cada libro cubre el hueco que el ejemplo del traje
deja abierto (el traje de Blender es geometría paramétrica; el sastre además
moldea, pinza y da caída).

## Orden recomendado

1. **«Construcción de prendas» — Anette Fischer** (Gustavo Gili, en español)
   El mejor primer libro: patronaje base, mangas, cuellos, bolsillos, una
   sección específica de **sastrería** y otra de **drapear sobre maniquí**.
   Cubre exactamente lo que al traje 3D le falta.
2. **«Metric Pattern Cutting for Menswear» — Winifred Aldrich**
   El estándar del patrón base masculino: tablas de tallas reales y sistemas
   de trazado para chaqueta y pantalón. Es la fuente para mejorar nuestras
   medidas de cabecera.
3. **«Classic Tailoring Techniques for Menswear» — Roberto Cabrera**
   Sastrería a medida clásica: hombro, entretela, solapa, tirada de manga.
   El nivel «hecho a mano».

## Complementos

- **«Patternmaking for Fashion Design» — Helen Joseph Armstrong**: la biblia
  general del patronaje (mujer+homme), referencia de consulta.
- **Sistema Martí, tomo IV «Sastrería»** (sistemamarti.com): sistema español
  clásico con tratado en PDF — muy útil para trajes españoles.
- **Manual gratuito «Corte y Confección»** (PDF libre, guao.org): bases de
  máquina, medidas y ensamblaje sin coste.

## Qué aplicar al pipeline (idea viva)

| Concepto del libro | Traducción a nuestro código |
|---|---|
| Tirada de manga (copa = sisa + 2-3 cm) | `rx, ry` de `Manga` en `montar_escena_traje.py` + curva de copa en `generar_patron_traje.py` |
| Pinzas de pecho y hombro | Añadir a DELANTERO/TRASERO como líneas de molde |
| Roll line de la solapa | Recalcular `Solapa` siguiendo el busto, no el plano |
| Caída real de la tela | Simulación de cloth de Blender o Marvelous Designer (fase 2) |

Hecho con ❤️ por David Antizar.
