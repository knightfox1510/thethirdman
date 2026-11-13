"""Spike: render a broadcast-cam delivery with real 3D lighting in Blender (bpy), using the SAME rig, camera and ball path as broadcast.py.
    python3 render3d.py specs/henry_cam_test.json <scene index> <out_dir> t1 t2 ...      # stills at those scene times
Illustrative figures only."""
import sys, json, math, time, types
import bpy
import rig3d as R, broadcast as B

W0 = 1080
def bl(p): return (p[0], p[2], p[1])                       # world (x, up, toward batter) -> Blender (x, y forward, z up)

def mat(col, rough=.6, emit=0):
    m = bpy.data.materials.new("m"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*[(v / 255) ** 2.2 for v in col], 1); b.inputs["Roughness"].default_value = rough
    return m
MC = {}
def M(col, rough=.6):
    k = (tuple(col), rough)
    if k not in MC: MC[k] = mat(col, rough)
    return MC[k]

def box(name, loc, size, col, rough=.8):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.data.materials.append(M(col, rough)); return o

POOL = {}
def cyl(key):
    if key not in POOL:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=.5, depth=1); POOL[key] = bpy.context.object
    return POOL[key]
def sph(key):
    if key not in POOL:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=1); POOL[key] = bpy.context.object
    return POOL[key]

def place_seg(o, p0, p1, w, col):
    a, b = (bl(p0)), (bl(p1)); import mathutils
    A, Bv = mathutils.Vector(a), mathutils.Vector(b); d = Bv - A; L = max(d.length, 1e-4)
    o.location = (A + Bv) / 2; o.scale = (w, w, L); o.rotation_mode = "QUATERNION"; o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.clear(); o.data.materials.append(M(col)); o.hide_render = False
def place_dot(o, p, rad, col):
    o.location = bl(p); o.scale = (rad, rad, rad); o.data.materials.clear(); o.data.materials.append(M(col)); o.hide_render = False

def draw_figure(fid, x, z, P, kit, **kw):
    sink = []; R.figure(None, None, x, z, P, kit, sink=sink, **kw); ci = si = 0
    for it in sink:
        if it[0] == "seg":
            place_seg(cyl((fid, "c", ci)), it[1], it[2], it[3], it[4]); ci += 1
            # rounded joints
            place_dot(sph((fid, "j", ci)), it[1], it[3] * .5, it[4])
        else:
            place_dot(sph((fid, "d", si)), it[1], it[2], it[3]); si += 1

def setup_scene(res):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.film_transparent = False
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (.38, .6, .9, 1); bg.inputs[1].default_value = 1.1
    bpy.ops.object.light_add(type="SUN", location=(-20, -30, 40)); s = bpy.context.object; s.rotation_euler = (math.radians(52), 0, math.radians(-35)); s.data.energy = 4.0; s.data.angle = math.radians(3)
    for i, z in enumerate(range(-30, 130, 6)):                                         # mown stripes
        box("g%d" % i, (0, z + 3, -.01), (240, 6, .02), (46, 128, 54) if i % 2 == 0 else (60, 150, 68), .95)
    box("pitch", (0, B.PL / 2, .0), (3.05, B.PL + 2.8, .03), (206, 178, 120), .95)
    for zz in (0, 1.22, B.PL - 1.22, B.PL): box("crease", (0, zz, .02), (2.64, .05, .01), (245, 240, 225), .5)
    box("stand", (0, 118, 14), (260, 3, 28), (46, 50, 74), .9)                         # backdrop stand
    box("board", (0, 114, 1.0), (260, 1, 2), (230, 230, 230), .6)
    import random; rnd = random.Random(3)
    for i in range(160):                                                                # crowd blobs
        box("f", (rnd.uniform(-110, 110), 116.5, rnd.uniform(3, 24)), (1.6, .4, 1.6), rnd.choice([(200, 70, 70), (60, 120, 200), (230, 230, 230), (230, 190, 60)]), .9)
    bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.sensor_fit = "HORIZONTAL"; cam.data.sensor_width = 36; cam.data.clip_end = 400
    return sc, cam

def set_cam(cam, c3, res):
    cam.location = (0, c3.zc, c3.h); cam.rotation_euler = (math.pi / 2 - c3.th, 0, 0); cam.data.lens = c3.f / W0 * 36
    cam.data.shift_y = -(0.5 - c3.cy / (W0 * res[1] / res[0]))

def stumps3d(t, tc, res_, hit):
    u = max(0.0, t - tc) if hit else 0.0
    for i, sx in enumerate((-B.STUMP_DX, 0, B.STUMP_DX)):
        base = (sx, 0.0, B.PL); L = B.STUMP_H
        if hit:
            q = min(1.0, u / .9); phi = q * (.9 + .35 * i) * (1 if i != 1 else -.6)
            base = (sx + (i - 1) * .9 * q, max(0, .9 * q * (1 - q) * (1 + i * .3)), B.PL + 1.6 * q * (1 + .25 * i))
            tip = (base[0] + .12 * math.sin(phi * 2) * (i - 1), base[1] + L * math.cos(phi), base[2] + L * math.sin(phi))
        else: tip = (sx, L, B.PL)
        place_seg(cyl(("st", i)), base, tip, .04, (248, 244, 228))
    for k, sg in enumerate((-1, 1)):
        if hit:
            f = min(1.0, u / 1.1); p = (sg * B.STUMP_DX * .5 + sg * 1.1 * f, max(0, B.STUMP_H + 1.3 * f - 2.6 * f * f + .05), B.PL + 1.8 * f)
        else: p = (sg * B.STUMP_DX * .5, B.STUMP_H + .01, B.PL)
        place_seg(cyl(("bail", k)), (p[0] - .05, p[1], p[2]), (p[0] + .05, p[1], p[2]), .025, (255, 214, 90))
    for i, sx in enumerate((-B.STUMP_DX, 0, B.STUMP_DX)):                               # bowler-end stumps
        place_seg(cyl(("st0", i)), (sx, 0, 0), (sx, B.STUMP_H, 0), .04, (248, 244, 228))

def render_at(spec_path, idx, t, out, res):
    s = json.load(open(spec_path))["short"][idx]["scene"]; D = 6.3
    s.setdefault("ball", {}); s["ball"]["_t"] = D * s["ball"].get("at", .62)
    g = types.SimpleNamespace(W=W0, H=int(W0 * res[1] / res[0]))
    c3, tR, tc = B._plan(s, D, g, t); hand, off, zb, xb, T = B._geom(s); res_ = s.get("result", "dot")
    set_cam(CAM, c3, res)
    bz = -.5 - 8.5 * (1 - R.smooth(min(1, t / tR))) if t < tR else B.lerp(-.5, 3.0, 1 - (1 - min(1, (t - tR) / 1.0)) ** 3)
    bx = 0 if t < tR else B.lerp(0, -off * 1.0, 1 - (1 - min(1, (t - tR) / 1.0)) ** 3)
    draw_figure("bowler", bx, bz, B._bowler_pose(t, tR), "NZ", cap=True)
    draw_figure("ump", -off * 2.6, .6, R.STAND, "UMP", brim=True)
    draw_figure("keeper", 0, B.PL + 8.0, R.KEEP, "NZ", cap=True)
    bp = R.STANCE
    if t >= tc:
        u_ = R.smooth((t - tc) / .5)
        if res_ == "bowled": bp = R.blend(R.STANCE, R.DEJECT, u_)
    draw_figure("batter", 0, B.PL - 1.0, bp, "IND", bat=True, pads=True)
    stumps3d(t, tc, res, res_ == "bowled" and t >= tc)
    bs = B.ball_state(s, t, tR, tc); bo = sph("ball")
    if bs: place_dot(bo, bs, .13, (250, 248, 240))
    else: bo.hide_render = True
    bpy.context.scene.render.filepath = out; bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    spec, idx, od = sys.argv[1], int(sys.argv[2]), sys.argv[3]; ts = [float(x) for x in sys.argv[4:]]
    if ts and ts[0] < 0: ts = [i / 25 for i in range(int(-ts[0] * 25))]          # negative = every frame for that many seconds
    RES = (540, 960); SC, CAM = setup_scene(RES)
    for t in ts:
        t0 = time.time(); render_at(spec, idx, t, (f"{od}/f_{int(round(t*25)):04d}.png" if len(ts) > 20 else f"{od}/f_{t:.2f}.png"), RES); print("t=%.2f %.1fs" % (t, time.time() - t0), flush=True)
