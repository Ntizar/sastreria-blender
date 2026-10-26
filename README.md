# Sastrería en Blender — Capa española + Traje de boda

Ejemplos completos del flujo **patrón real → prenda 3D → render**, con el kit
`blender-agente` (Hermes, PC). Enfoque anti-slop del dominio moda: el render
está sostenido por el patrón DXF 1:1 y la ficha técnica con las mismas cifras.

## Traje de boda (azul marino, camisa, corbata)

| Fichero | Qué es |
|---|---|
| `generar_patron_traje.py` | Patrón paramétrico: delantero/trasero/manga/pantalón/corbata/cuello + tendedero automático sobre tela de 150 → DXF 1:1 + ficha |
| `patrones/patron_traje.dxf` + `patrones/ficha_traje.md` | Patrón 1:1 (cm) y ficha técnica (consumo chaqueta 1,25 m + pantalón y complementos 2,90 m) |
| `montar_escena_traje.py` | Escena 3D: maniquí de sastre + chaqueta con solapas y V con botón, camisa, corbata con nudo, pantalón fundido en cadera, zapatos. Geometría, NO simulación de tela |
| `traje.blend` · `renders/traje_heroe.png` | Escena lista · render Cycles OptiX 192 muestras (verificado: figura completa encuadrada, mangas, nudo conectado, zapatos visibles) |
| `renders/patron_traje_planta.png` | Tendedero del patrón en planta |

Regenerar: mismos 4 pasos del ejemplo de la capa, con estos scripts.

## Capa española clásica

Ejemplo completo del flujo **patrón real → prenda 3D → render**, con el kit
`blender-agente` (Hermes, PC). Enfoque anti-slop del dominio moda: el render
está sostenido por el patrón DXF 1:1 y la ficha técnica con las mismas cifras.

## Ficheros

| Fichero | Qué es |
|---|---|
| `generar_patron_capa.py` | Generador paramétrico: medidas del cuerpo → DXF 1:1 + ficha. Cambia las medidas de cabecera y regenera TODO |
| `patrones/patron_capa_espanola.dxf` | Patrón 1:1 (cm): cuerpo al doblez, capillo, cordón, nota de galón |
| `patrones/ficha_capa_espanola.md` | Ficha técnica: piezas, corte, consumo (2,53 m de 140) |
| `montar_escena_capa.py` | Escena 3D (bpy): maniquí de sastre + capa abierta al frente con pliegues procedurales. Geometría, NO simulación de tela |
| `capa_espanola.blend` | Escena lista para renderizar |
| `renders/capa_heroe.png` | Render Cycles OptiX 192 muestras |
| `renders/patron_planta.png` | Patrón importado del DXF, vista de planta |

## Regenerar todo

```bash
# 1. patrón + ficha (Python de Blender, trae ezdxf)
C:/Blender/blender-5.2.3-windows-x64/5.2/python/bin/python.exe generar_patron_capa.py --salida patrones

# 2. escena 3D
blender -b --factory-startup -P montar_escena_capa.py -- capa_espanola.blend

# 3. render (kit blender-agente: device OptiX)
blender -b capa_espanola.blend -P <kit>/scripts/render_cabeza.py -- renders/capa_heroe.png 192

# 4. planta del patrón (import DXF + enmarcado del kit)
blender -b --factory-startup -P <kit>/scripts/dxf_a_objetos.py -- patrones/patron_capa_espanola.dxf patrones/patron.blend
blender -b patrones/patron.blend -P <kit>/scripts/enmarcar.py -- patrones/patron_enm.blend 1.12
blender -b patrones/patron_enm.blend -P <kit>/scripts/render_cabeza.py -- renders/patron_planta.png 64
```

## Medidas base (cm)

perímetro cuello 38 · largo capa 95 · largo capillo 30 · altura maniquí 175.
De ahí salen: r cuello 6,0 · R cuerpo 101,0 · R capillo 36,0 · bajo 317 cm.

Hecho con ❤️ por David Antizar.
