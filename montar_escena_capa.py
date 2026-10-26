#!/usr/bin/env python3
"""Escena 3D: maniquí de sastre con la capa española montada.

Geometría por perfiles de anillos (cm): el mismo validador del visor three.js
del dominio moda, aquí en bpy. La capa va ABIERTA al frente (arco ~300°) para
dejar ver el maniquí, con pliegues procedurales que crecen hacia el bajo.
NO es simulación de tela — es la prenda caída sobre el maniquí (así se declara
también en la ficha).

  blender -b --factory-startup -P montar_escena_capa.py -- salida.blend
"""
import math
import sys

import bpy
import bmesh
from mathutils import Vector

SEG = 64
GAP_FRONTAL = math.radians(72)   # abertura de la capa, mirando a cámara
INICIO = -math.pi / 2            # el frente mira a -Y (donde está la cámara)

# ---------------------------------------------------------------- materiales
def material(nombre, color, rough=0.85, metal=0.0, sheen=0.0):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if sheen:
        bsdf.inputs["Sheen Weight"].default_value = sheen
    return mat


PAÑO = material("paño_guinda", (0.14, 0.018, 0.045), rough=0.96)
ORO = material("galón_oro", (0.72, 0.55, 0.13), rough=0.38, metal=1.0)
LINEN = material("lino_maniquí", (0.74, 0.68, 0.58), rough=0.95)
MADERA = material("madera_nogal", (0.20, 0.13, 0.08), rough=0.6)
SUELO_M = material("suelo", (0.15, 0.13, 0.12), rough=0.98)

# ------------------------------------------- malla por anillos (arco parcial)
def malla_por_anillos(nombre, perfil, mat, ondula=None, arco=2 * math.pi,
                      inicio=INICIO, cerrar=False):
    """perfil: [(z, rx, rz)]. ondula(t, th) -> multiplicador de radio."""
    me = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    anillos = []
    n_fila = SEG + (0 if arco >= 2 * math.pi else 1)
    for i, (z, rx, rz) in enumerate(perfil):
        t = i / (len(perfil) - 1)
        fila = []
        for j in range(n_fila):
            th = inicio + arco * (j / SEG)
            w = ondula(t, th) if ondula else 1.0
            fila.append(bm.verts.new((math.cos(th) * rx * w,
                                      math.sin(th) * rz * w, z)))
        anillos.append(fila)
    for a, b in zip(anillos, anillos[1:]):
        for j in range(n_fila - 1):
            bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
    if cerrar and n_fila == SEG:
        bm.faces.new(anillos[-1][::-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    obj.data.materials.append(mat)
    return obj


# ------------------------------------------------------------ maniquí (cm)
A = 175.0
C = {"tobillo": .06 * A, "rodilla": .285 * A, "cadera": .525 * A,
     "cintura": .625 * A, "pecho": .725 * A, "hombro": .815 * A,
     "cuello": .865 * A}
R = {"cuello": 38 / (2 * math.pi), "pecho": 96 / (2 * math.pi),
     "cintura": 78 / (2 * math.pi), "cadera": 100 / (2 * math.pi),
     "hombro": (96 / (2 * math.pi)) * 1.44}

perfil_torso = [
    (85, 14.8, 10.6),
    (C["cadera"], R["cadera"], R["cadera"] * .72),
    (C["cintura"], R["cintura"], R["cintura"] * .72),
    (C["pecho"], R["pecho"], R["pecho"] * .72),
    (136, 14.6, 10.8),
    (C["hombro"], R["hombro"], R["hombro"] * .60),
    (148, 7.0, 5.6),
    (C["cuello"], 6.2, 5.2),
]
malla_por_anillos("maniquí", perfil_torso, LINEN, cerrar=True)

# Pedestal de sastre
bpy.ops.mesh.primitive_cylinder_add(radius=3.2, depth=85, location=(0, 0, 42.5))
bpy.context.object.data.materials.append(MADERA)
bpy.ops.mesh.primitive_cylinder_add(radius=24, depth=4.5, location=(0, 0, 2.25))
bpy.context.object.data.materials.append(MADERA)

# ------------------------------------------------- capa: vuelo + pliegues
def ondula_capa(t, th):
    """Pliegues verticales que crecen hacia el bajo + leve vaivén."""
    amp = 0.012 + 0.055 * t ** 1.6
    return 1.0 + amp * math.sin(9 * th + 1.3) * math.sin(t * 2.4)


def vuelo(z_arriba, z_abajo, r_arriba, r_abajo, n=10, curva=1.35):
    """Caída de capa: el vuelo acelera hacia el bajo (paño que pesa)."""
    perfil = []
    for i in range(n + 1):
        t = i / n
        z = z_arriba + (z_abajo - z_arriba) * t
        r = r_arriba + (r_abajo - r_arriba) * (t ** (1 / curva))
        perfil.append((z, r, r * .78))
    return perfil


ARCO_CAPA = 2 * math.pi - GAP_FRONTAL
malla_por_anillos("capa_cuerpo", vuelo(143, 48, 27, 78), PAÑO,
                  ondula=ondula_capa, arco=ARCO_CAPA)

# Capillo SOBRE el cuerpo de la capa: mismo vuelo + 2.5 cm de holgura
perfil_capillo = []
for i in range(11):
    t = i / 10
    z = 143 + (115 - 143) * t
    r = 27 + 51 * t ** (1 / 1.35) + 2.5
    perfil_capillo.append((z, r, r * .78))
malla_por_anillos("capillo", perfil_capillo, PAÑO,
                  ondula=lambda t, th: 1.0 + 0.02 * math.sin(9 * th + 1.3),
                  arco=ARCO_CAPA)

# Galón dorado: banda que sigue EXACTAMENTE el pliegue del bajo
# (el ondula de la capa en t=1: 1 + 0.067*sin(t*2.4)*sin(9θ+1.3) = 1 + 0.0453*sin(9θ+1.3))
malla_por_anillos("galón_bajo",
                  [(47.2, 79.4, 79.4 * .78), (48.8, 79.4, 79.4 * .78)], ORO,
                  ondula=lambda t, th: 1.0 + 0.0453 * math.sin(9 * th + 1.3),
                  arco=ARCO_CAPA)
# Cordón dorado en el cuello
malla_por_anillos("cordón_cuello",
                  [(142.2, 7.6, 7.6), (143.8, 7.6, 7.6)], ORO, arco=ARCO_CAPA)

# ------------------------------------------------------------------ entorno
bpy.ops.mesh.primitive_plane_add(size=900, location=(0, 0, 0))
bpy.context.object.data.materials.append(SUELO_M)

mundo = bpy.context.scene.world or bpy.data.worlds.new("Mundo")
bpy.context.scene.world = mundo
mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[0].default_value = (0.10, 0.09, 0.085, 1)
mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.5

sol_data = bpy.data.lights.new("sol", type="SUN")
sol_data.energy = 2.6
sol_data.angle = math.radians(4)
sol = bpy.data.objects.new("sol", sol_data)
bpy.context.scene.collection.objects.link(sol)
sol.rotation_euler = (math.radians(52), math.radians(14), math.radians(-22))

reldata = bpy.data.lights.new("relleno", type="AREA")
reldata.energy = 2600
reldata.size = 180
relleno = bpy.data.objects.new("relleno", reldata)
bpy.context.scene.collection.objects.link(relleno)
relleno.location = (-130, -150, 140)
relleno.rotation_euler = (math.radians(55), 0, math.radians(-40))

# ------------------------------------------------------------------- cámara
datos_cam = bpy.data.cameras.new("CamHeroe")
datos_cam.lens = 45
cam = bpy.data.objects.new("CamHeroe", datos_cam)
bpy.context.scene.collection.objects.link(cam)
cam.location = (120, -380, 170)
objetivo = Vector((0, 0, 80))
cam.rotation_euler = (objetivo - cam.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = cam

# ------------------------------------------------------------------- salida
salida = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.save_as_mainfile(filepath=salida)
print("ESCENA_OK objetos=%d salida=%s" % (len(bpy.data.objects), salida))
