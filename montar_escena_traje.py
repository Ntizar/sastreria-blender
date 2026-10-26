# -*- coding: utf-8 -*-
"""Escena 3D: traje de boda (chaqueta azul + camisa + corbata + pantalón)
sobre maniquí de sastre, en cm. Geometría paramétrica — NO simulación de tela.
Uso: blender -b --factory-startup -P montar_escena_traje.py -- salida.blend"""
import bpy, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SALIDA = argv[0] if argv else "traje.blend"
SEG = 64

# ---------------- perfil del maniquí (cotas reales, cm) ----------------
PERFIL = [(86, 16.8, 14.6), (98, 17.2, 14.4), (106, 13.6, 11.2), (116, 16.6, 13.0),
          (128, 17.0, 12.2), (140, 16.0, 10.8), (147, 14.2, 9.8)]

def torso(z):
    if z <= PERFIL[0][0]:
        return PERFIL[0][1], PERFIL[0][2]
    for (z0, a0, b0), (z1, a1, b1) in zip(PERFIL, PERFIL[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
    return PERFIL[-1][1], PERFIL[-1][2]

def limpiar():
    for n in ("Cube", "Camera", "Light"):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

def mat(nombre, color, rough=0.8, metal=0.0, sheen=0.0):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if sheen and "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = sheen
    return m

def superficie(nombre, anillos, cerrada=True, material=None, grosor=0.12):
    n = len(anillos[0])
    verts = [p for a in anillos for p in a]
    caras = []
    for i in range(len(anillos) - 1):
        jmax = n if cerrada else n - 1
        for j in range(jmax):
            j2 = (j + 1) % n
            caras.append((i * n + j, i * n + j2, (i + 1) * n + j2, (i + 1) * n + j))
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(verts, [], caras)
    me.update()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(o)
    if material:
        o.data.materials.append(material)
    if not cerrada:
        mod = o.modifiers.new("Solidez", "SOLIDIFY")
        mod.thickness = grosor
    return o

limpiar()
LANA   = mat("LANA_AZUL",  (0.045, 0.085, 0.20), rough=0.85, sheen=0.30)
CAMISA = mat("CAMISA",     (0.95, 0.95, 0.93),   rough=0.55)
CORB   = mat("CORBATA",    (0.30, 0.035, 0.075), rough=0.45, sheen=0.15)
PIEL   = mat("LINEN",      (0.75, 0.64, 0.50),   rough=0.8)
MADERA = mat("MADERA",     (0.36, 0.22, 0.11),   rough=0.55)
SUELO  = mat("SUELO",      (0.55, 0.55, 0.56),   rough=0.9)
CUERO  = mat("CUERO",      (0.05, 0.045, 0.04),  rough=0.35)
METAL  = mat("BOTON",      (0.03, 0.05, 0.12),   rough=0.4)

# ---------------- maniquí + pedestal ----------------
zs = [86 + i * (147 - 86) / 16 for i in range(17)]
superficie("Torso", [[Vector((torso(z)[0] * math.cos(t), torso(z)[1] * math.sin(t), z))
                      for t in [2 * math.pi * j / SEG for j in range(SEG)]] for z in zs],
           cerrada=True, material=PIEL)
bpy.ops.mesh.primitive_cylinder_add(radius=6.2, depth=10, location=(0, 0, 149.5))
bpy.context.object.data.materials.append(PIEL); bpy.context.object.name = "Cuello"
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=6.4, location=(0, 0, 156))
bpy.context.object.scale = (1, 1, 0.55)
bpy.context.object.data.materials.append(MADERA); bpy.context.object.name = "Remate"
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=84, location=(0, 8, 46))
bpy.context.object.data.materials.append(MADERA); bpy.context.object.name = "Poste"
bpy.ops.mesh.primitive_cylinder_add(radius=26, depth=5, location=(0, 0, 2.5))
bpy.context.object.data.materials.append(MADERA); bpy.context.object.name = "Pedestal"

# ---------------- chaqueta ----------------
ANILLOS = 13
def gap(z):  # abertura frontal (rad), nace en el botón (z=100)
    return math.radians(2 + 38 * max(0.0, min(1.0, (z - 100) / 47)))

anillos = []
for i in range(ANILLOS):
    z = 84 + (147 - 84) * i / (ANILLOS - 1)  # bajo de chaqueta cubre la silla
    A, B = torso(z)[0] + 2.2, torso(z)[1] + 2.2
    g = gap(z)
    th0, th1 = -math.pi / 2 + g / 2, 3 * math.pi / 2 - g / 2
    anillos.append([Vector((A * math.cos(th0 + (th1 - th0) * j / (SEG - 1)),
                            B * math.sin(th0 + (th1 - th0) * j / (SEG - 1)), z))
                    for j in range(SEG)])
superficie("Chaqueta", anillos, cerrada=False, material=LANA, grosor=0.25)

# solapas: cinta desde el canto de la V hacia fuera, engordando arriba
for lado in (1, -1):
    cols_e, cols_o = [], []
    for i in range(10):
        z = 100 + 47 * i / 9
        A, B = torso(z)[0] + 2.2, torso(z)[1] + 2.2
        th = -math.pi / 2 + lado * gap(z) / 2
        e = Vector((A * math.cos(th), B * math.sin(th), z))
        u = Vector((math.cos(th), math.sin(th), 0))
        cols_e.append(e)
        cols_o.append(e + u * (0.6 + 5.6 * i / 9) + Vector((0, 0, -1.1 * i / 9)))
    superficie(f"Solapa{lado}", [cols_e, cols_o], cerrada=False, material=LANA, grosor=0.22)

# cuello de la chaqueta
an = []
for z, dA in ((147.4, 2.6), (150.8, 1.6)):
    A, B = torso(147)[0] + dA, torso(147)[1] + dA
    th0 = -math.pi / 2 + math.radians(13)
    an.append([Vector((A * math.cos(th0 + (2 * math.pi - math.radians(26)) * j / (SEG - 1)),
                       B * math.sin(th0 + (2 * math.pi - math.radians(26)) * j / (SEG - 1)), z))
               for j in range(SEG)])
superficie("CuelloChaqueta", an, cerrada=False, material=LANA, grosor=0.22)

# camisa (se ve por la V y bajo el cuello)
anillos = []
for i in range(11):
    z = 92 + (149 - 92) * i / 10
    A, B = torso(min(z, 147))[0] + 0.9, torso(min(z, 147))[1] + 0.9
    anillos.append([Vector((A * math.cos(2 * math.pi * j / SEG), B * math.sin(2 * math.pi * j / SEG), z))
                    for j in range(SEG)])
superficie("Camisa", anillos, cerrada=True, material=CAMISA)

# corbata: cinta frontal que se ensancha hacia abajo con punta + nudo
col_iz, col_de = [], []
for i in range(15):
    z = 104 + 44 * i / 14
    A, B = torso(min(z, 147))
    if z > 140:
        w = 4.6
    else:
        w = 8.8 - 0.30 * (140 - z)
    if z < 108:
        w = max(2.2, w * (z - 104) / 4)  # punta
    y = -(B + 1.7) * (1 - 0.5 * (w / 2 / (A + 1.5)) ** 2)
    col_iz.append(Vector((-w / 2, y, z)))
    col_de.append(Vector((w / 2, y, z)))
superficie("Corbata", [col_iz, col_de], cerrada=False, material=CORB, grosor=0.15)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=3.4, location=(0, -(torso(147)[1] + 2.8), 148.2))
bpy.context.object.scale = (1.5, 0.9, 1.25)
bpy.context.object.data.materials.append(CORB); bpy.context.object.name = "Nudo"

# cuello de la camisa: dos alas blancas junto al nudo
for lado in (1, -1):
    bpy.ops.mesh.primitive_cube_add(location=(lado * 4.8, -(torso(147)[1] + 1.6), 150.4),
                                    rotation=(0, 0, lado * 0.35))
    bpy.context.object.scale = (4.4, 0.5, 3.4)
    bpy.context.object.data.materials.append(CAMISA); bpy.context.object.name = f"CuelloCamisa{lado}"

# mangas: tubos casi verticales pegados al cuerpo + hombrera
for lado in (1, -1):
    S = Vector((lado * 17.0, 0, 143))
    d = Vector((lado * 0.12, 0.06, -0.99)).normalized()
    L = 62.0
    u = d.cross(Vector((0, 0, 1))).normalized()
    v = d.cross(u).normalized()
    anillos = []
    for i in range(9):
        t = i / 8
        c = S + d * (t * L)
        rx, ry = 7.0 - 2.8 * t, 6.6 - 2.4 * t
        anillos.append([c + u * (rx * math.cos(2 * math.pi * j / SEG)) + v * (ry * math.sin(2 * math.pi * j / SEG))
                        for j in range(SEG)])
    superficie(f"Manga{lado}", anillos, cerrada=True, material=LANA)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1,
                                         location=(lado * 15.5, 0, 141.5))
    bpy.context.object.scale = (9.5, 7.5, 5.5)
    bpy.context.object.data.materials.append(LANA); bpy.context.object.name = f"Hombrera{lado}"

# botones, bolsillos, pañuelo
for z in (97.5, 91.5):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=0.7, location=(0, -(torso(z)[1] + 2.6), z),
                                        rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(METAL); bpy.context.object.name = f"Boton{z}"
for lado in (1, -1):
    th = -math.pi / 2 + lado * 0.62
    A, B = torso(103)[0] + 2.4, torso(103)[1] + 2.4
    bpy.ops.mesh.primitive_cube_add(location=(A * math.cos(th), B * math.sin(th), 103),
                                    rotation=(0, 0, th + math.pi / 2))
    bpy.context.object.scale = (6.75, 0.35, 2.1)
    bpy.context.object.data.materials.append(LANA); bpy.context.object.name = f"Bolsillo{lado}"
th = -math.pi / 2 + 0.34
A, B = torso(128)[0] + 2.2, torso(128)[1] + 2.2
bpy.ops.mesh.primitive_cube_add(location=(A * math.cos(th), B * math.sin(th), 128.0),
                                rotation=(0.18, 0, th + math.pi / 2))
bpy.context.object.scale = (3.2, 0.4, 2.8)
bpy.context.object.data.materials.append(CAMISA); bpy.context.object.name = "Panuelo"

# ---------------- pantalón + zapatos ----------------
for lado in (1, -1):
    zs = [90 - i * (90 - 8) / 8 for i in range(9)]
    anillos = []
    for z in zs:
        t = (90 - z) / 82
        cx = lado * (8.86 - 0.9 * t)         # fundidas en la cadera, separadas al tobillo
        rx, ry = 10.0 - 4.6 * t, 9.4 - 4.0 * t
        anillos.append([Vector((cx + rx * math.cos(2 * math.pi * j / SEG), ry * math.sin(2 * math.pi * j / SEG), z))
                        for j in range(SEG)])
    superficie(f"Pantalon{lado}", anillos, cerrada=True, material=LANA)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1, location=(lado * 9.0, -3.5, 4.2))
    bpy.context.object.scale = (10.5, 4.8, 4.2)
    bpy.context.object.data.materials.append(CUERO); bpy.context.object.name = f"Zapato{lado}"

# ---------------- suelo, luces, cámara ----------------
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, 0))
bpy.context.object.data.materials.append(SUELO); bpy.context.object.name = "Suelo"

def sol(energy, rot):
    bpy.ops.object.light_add(type='SUN', location=(0, -100, 200))
    o = bpy.context.object
    o.data.energy = energy
    o.rotation_euler = rot
    return o
sol(3.0, (math.radians(55), 0, math.radians(35)))
sol(0.7, (math.radians(45), 0, math.radians(-120)))

cam = bpy.data.cameras.new("Cam"); cam.lens = 50
o = bpy.data.objects.new("Camera", cam)
bpy.context.collection.objects.link(o)
o.location = Vector((22, -462, 94))
o.rotation_euler = (Vector((0, 0, 82)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = o

mundo = bpy.context.scene.world or bpy.data.worlds.new("W")
bpy.context.scene.world = mundo
mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.86, 0.88, 0.92, 1)
bg.inputs[1].default_value = 0.5

bpy.ops.wm.save_as_mainfile(filepath=SALIDA)
print("ESCENA_OK", SALIDA)
