#!/usr/bin/env python3
"""Writes Popochiu rooms and inventory items from a short Python description, so a new story
doesn't need hours of clicking in the editor.

A room gets: room_<name>.tscn (background, props, hotspots, markers, one walkable area, all inline),
room_<name>_state.gd + .tres, and room_<name>.gd **only if it doesn't exist yet** (the story logic
lives there and is written by hand). Props and hotspots use the shared delegating scripts in
game/game/shared/, which pass clicks to the room script:
    on_click(node) / on_look(node) / on_item(node, item)
Everything is registered in game/game/popochiu_data.cfg and the R / I autoloads.

Coordinates are Godot pixels (rooms are 1920 x 1080, y down).
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game", "game")
CFG = os.path.join(GAME, "popochiu_data.cfg")


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _vec(pts):
    return "PackedVector2Array(" + ", ".join(f"{x:g}, {y:g}" for x, y in pts) + ")"


def _rect(cx, cy, w, h):
    return [(cx - w/2, cy - h/2), (cx + w/2, cy - h/2), (cx + w/2, cy + h/2), (cx - w/2, cy + h/2)]


def _register(section, key, value):
    txt = open(CFG, encoding="utf-8").read()
    line = f'{key}="{value}"'
    if line in txt:
        return
    m = re.search(rf"\[{section}\]\n\n?((?:[^\[\n].*\n)*)", txt)
    block = m.group(0).rstrip("\n") + "\n" + line + "\n"
    txt = txt[:m.start()] + block + ("\n" if not txt[m.end():].startswith("\n") else "") + txt[m.end():]
    open(CFG, "w", encoding="utf-8").write(txt)


def _autoload(file, prefix, name, path, getter):
    p = os.path.join(GAME, "autoloads", file)
    s = open(p, encoding="utf-8").read()
    if f"const {prefix}{name} " in s:
        return
    s = s.replace("# ---- classes", f'const {prefix}{name} := preload("{path}")\n# ---- classes', 1)
    s = s.replace("# ---- nodes", f"var {name}: {prefix}{name} : get = get_{name}\n# ---- nodes", 1)
    s = s.replace("# ---- functions", f'func get_{name}() -> {prefix}{name}: return {getter}("{name}")\n# ---- functions', 1)
    open(p, "w", encoding="utf-8").write(s)


STATE_GD = """# @popochiu-docs-ignore-class
extends {base}


func _on_save() -> Dictionary:
	return {{}}


func _on_load(_data: Dictionary) -> void:
	pass
"""


def make_room(name, bg, walk, props=(), hotspots=(), markers=()):
    """props: dicts name, tex, pos, desc, [scale, baseline, poly (local), visible, clickable]
    hotspots: dicts name, poly (room coords), desc, walk_to
    markers: {name: (x, y)}"""
    sn = snake(name)
    d = os.path.join(GAME, "rooms", sn)
    os.makedirs(d, exist_ok=True)
    res = f"res://game/rooms/{sn}"
    ext, ids = [], {}

    def ext_res(kind, path):
        if path not in ids:
            ids[path] = f"{len(ids) + 1}_r"
            ext.append(f'[ext_resource type="{kind}" path="{path}" id="{ids[path]}"]')
        return ids[path]

    room_script = ext_res("Script", f"{res}/room_{sn}.gd")
    prop_script = ext_res("Script", "res://game/shared/story_prop.gd")
    hot_script = ext_res("Script", "res://game/shared/story_hotspot.gd")
    walk_script = ext_res("Script", "res://game/shared/story_walkable.gd")
    nodes = [f'[node name="Room{name}" type="Node2D"]\nscript = ExtResource("{room_script}")\n'
             f'script_name = "{name}"\nwidth = 1920\nheight = 1080\n']

    wv = _vec(walk)
    nodes.append('[node name="WalkableAreas" type="Node2D" parent="."]\n')
    nodes.append(f'[node name="Podlaha" type="Node2D" parent="WalkableAreas"]\nscript = ExtResource("{walk_script}")\n'
                 f'script_name = "Podlaha"\ndescription = "Podlaha"\n'
                 f'interaction_polygon = Array[PackedVector2Array]([{wv}])\n')
    nodes.append(f'[node name="Perimeter" type="NavigationRegion2D" parent="WalkableAreas/Podlaha"]\n'
                 f'navigation_polygon = SubResource("nav")\n')

    nodes.append('[node name="Props" type="Node2D" parent="."]\n')
    all_props = [dict(name="Bg", tex=f"res://assets/rooms/{bg}.png", pos=(960, 540), desc="Bg", clickable=False,
                      baseline=-540, poly=_rect(0, 0, 1920, 1080), z=-1)] + list(props)
    for pr in all_props:
        tex = ext_res("Texture2D", pr["tex"])
        poly = pr.get("poly") or _rect(0, 0, *pr.get("size", (200, 200)))
        lines = [f'[node name="{pr["name"]}" type="Area2D" parent="Props"]']
        if pr.get("z"):
            lines.append(f"z_index = {pr['z']}")
        lines.append(f'position = Vector2({pr["pos"][0]:g}, {pr["pos"][1]:g})')
        if pr.get("scale"):
            lines.append(f'scale = Vector2({pr["scale"]:g}, {pr["scale"]:g})')
        if pr.get("visible") is False:
            lines.append("visible = false")
        if pr.get("clickable") is False:
            lines.append("input_pickable = false")
        lines += [f'script = ExtResource("{prop_script}")', f'script_name = "{pr["name"]}"',
                  f'texture = ExtResource("{tex}")', f'description = "{pr["desc"]}"']
        if pr.get("clickable") is False:
            lines.append("clickable = false")
        lines += [f"baseline = {pr.get('baseline', 0)}", "cursor = 1", f"interaction_polygon = {_vec(poly)}"]
        nodes.append("\n".join(lines) + "\n")
        base = f'Props/{pr["name"]}'
        nodes.append(f'[node name="Sprite2D" type="Sprite2D" parent="{base}"]\ntexture_filter = 1\ntexture = ExtResource("{tex}")\n')
        nodes.append(f'[node name="AnimationPlayer" type="AnimationPlayer" parent="{base}"]\n')
        nodes.append(f'[node name="InteractionPolygon" type="CollisionPolygon2D" parent="{base}"]\nvisible = false\n'
                     f'polygon = {_vec(poly)}\n')

    nodes.append('[node name="Hotspots" type="Node2D" parent="."]\n')
    for h in hotspots:
        wt = h.get("walk_to", (960, 960))
        nodes.append(f'[node name="{h["name"]}" type="Area2D" parent="Hotspots"]\nscript = ExtResource("{hot_script}")\n'
                     f'script_name = "{h["name"]}"\ndescription = "{h["desc"]}"\ncursor = 1\n'
                     f'walk_to_point = Vector2({wt[0]:g}, {wt[1]:g})\ninteraction_polygon = {_vec(h["poly"])}\n')
        nodes.append(f'[node name="InteractionPolygon" type="CollisionPolygon2D" parent="Hotspots/{h["name"]}"]\n'
                     f'visible = false\npolygon = {_vec(h["poly"])}\n')

    nodes.append('[node name="Regions" type="Node2D" parent="."]\n')
    nodes.append('[node name="Markers" type="Node2D" parent="."]\n')
    for m, (x, y) in dict(markers).items():
        nodes.append(f'[node name="{m}" type="Marker2D" parent="Markers"]\nvisible = false\nposition = Vector2({x:g}, {y:g})\n')
    nodes.append('[node name="Characters" type="Node2D" parent="."]\n')

    nav = (f'[sub_resource type="NavigationPolygon" id="nav"]\nvertices = {wv}\n'
           f'polygons = Array[PackedInt32Array]([PackedInt32Array({", ".join(str(i) for i in range(len(walk)))})])\n'
           f'outlines = Array[PackedVector2Array]([{wv}])\nagent_radius = 0.0\n')
    tscn = f'[gd_scene load_steps={len(ext) + 2} format=3]\n\n' + "\n".join(ext) + "\n\n" + nav + "\n" + "\n".join(nodes)
    open(os.path.join(d, f"room_{sn}.tscn"), "w", encoding="utf-8").write(tscn)

    open(os.path.join(d, f"room_{sn}_state.gd"), "w", encoding="utf-8").write(STATE_GD.format(base="PopochiuRoomData"))
    open(os.path.join(d, f"room_{sn}.tres"), "w", encoding="utf-8").write(
        f'[gd_resource type="Resource" format=3]\n\n[ext_resource type="Script" path="{res}/room_{sn}_state.gd" id="1_s"]\n\n'
        f'[resource]\nresource_name = "{name}"\nscript = ExtResource("1_s")\nscript_name = "{name}"\nscene = "{res}/room_{sn}.tscn"\n')
    gd = os.path.join(d, f"room_{sn}.gd")
    if not os.path.exists(gd):
        open(gd, "w", encoding="utf-8").write(
            f"@tool\nextends \"res://game/shared/story_room.gd\"\n\nconst Data := preload('room_{sn}_state.gd')\n\n"
            f'var state: Data = load("{res}/room_{sn}.tres")\n')
    _register("rooms", name, f"{res}/room_{sn}.tres")
    _autoload("r.gd", "PR", name, f"{res}/room_{sn}.gd", "get_runtime_room")
    print("room", name)


def make_item(name, tex, desc):
    sn = snake(name)
    d = os.path.join(GAME, "inventory_items", sn)
    os.makedirs(d, exist_ok=True)
    res = f"res://game/inventory_items/{sn}"
    open(os.path.join(d, f"inventory_item_{sn}.tscn"), "w", encoding="utf-8").write(
        f'[gd_scene format=3]\n\n[ext_resource type="Texture2D" path="{tex}" id="1_t"]\n'
        f'[ext_resource type="Script" path="{res}/inventory_item_{sn}.gd" id="2_s"]\n\n'
        f'[node name="Item{name}" type="TextureRect"]\ntexture_filter = 1\nsize_flags_horizontal = 3\n'
        f'size_flags_vertical = 4\nmouse_filter = 0\ntexture = ExtResource("1_t")\nstretch_mode = 5\n'
        f'script = ExtResource("2_s")\nscript_name = "{name}"\ndescription = "{desc}"\n\n'
        f'[node name="AnimationPlayer" type="AnimationPlayer" parent="."]\n')
    gd = os.path.join(d, f"inventory_item_{sn}.gd")
    if not os.path.exists(gd):
        open(gd, "w", encoding="utf-8").write(
            f"extends \"res://game/shared/story_item.gd\"\n\nconst Data := preload('inventory_item_{sn}_state.gd')\n\n"
            f'var state: Data = load("{res}/inventory_item_{sn}.tres")\n')
    open(os.path.join(d, f"inventory_item_{sn}_state.gd"), "w", encoding="utf-8").write(STATE_GD.format(base="PopochiuInventoryItemData"))
    open(os.path.join(d, f"inventory_item_{sn}.tres"), "w", encoding="utf-8").write(
        f'[gd_resource type="Resource" format=3]\n\n[ext_resource type="Script" path="{res}/inventory_item_{sn}_state.gd" id="1_s"]\n\n'
        f'[resource]\nresource_name = "{name}"\nscript = ExtResource("1_s")\nscript_name = "{name}"\nscene = "{res}/inventory_item_{sn}.tscn"\n')
    _register("inventory_items", name, f"{res}/inventory_item_{sn}.tres")
    _autoload("i.gd", "PII", name, f"{res}/inventory_item_{sn}.gd", "get_item_instance")
    print("item", name)


CHAR_GD = """@tool
extends "res://game/characters/animated_character.gd"
## Made by tools/popochiu_gen.py: the room script decides what clicking this character does.

const Data := preload('character_{sn}_state.gd')

var state: Data = load("res://game/characters/{sn}/character_{sn}.tres")


func _on_click() -> void:
	if R.current.has_method("on_character") and await R.current.on_character(self, "click"):
		return
	await C.player.face_clicked()


func _on_right_click() -> void:
	if R.current.has_method("on_character") and await R.current.on_character(self, "look"):
		return
	await C.player.say(description)


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if R.current.has_method("on_character") and await R.current.on_character(self, "item", item):
		return
	E.command_fallback()
"""


def make_character(name, prefix, desc, height, color):
    """height = sprite height in px (feet at the bottom); color = subtitle colour "r, g, b" (0..1)"""
    sn = snake(name)
    d = os.path.join(GAME, "characters", sn)
    os.makedirs(d, exist_ok=True)
    res = f"res://game/characters/{sn}"
    poly = _vec([(-130, -height), (130, -height), (130, 0), (-130, 0)])
    open(os.path.join(d, f"character_{sn}.tscn"), "w", encoding="utf-8").write(
        f'[gd_scene format=3]\n\n[ext_resource type="Script" path="{res}/character_{sn}.gd" id="1_s"]\n'
        f'[ext_resource type="Texture2D" path="res://assets/characters/{prefix}_happy.png" id="2_t"]\n\n'
        f'[node name="Character{name}" type="Area2D"]\nscript = ExtResource("1_s")\ntext_color = Color({color}, 1)\n'
        f'walk_speed = 400.0\ndialog_pos = Vector2(0, {-height - 30})\nsprite_prefix = "{prefix}"\ndefault_mood = "happy"\n'
        f'script_name = "{name}"\ndescription = "{desc}"\ncursor = 8\ninteraction_polygon = {poly}\n\n'
        f'[node name="ScalingPolygon" type="CollisionPolygon2D" parent="."]\npolygon = PackedVector2Array(0, 0, 0, 0, 0, 0, 0, 0)\n\n'
        f'[node name="AnimationPlayer" type="AnimationPlayer" parent="."]\n\n'
        f'[node name="Sprite2D" type="Sprite2D" parent="."]\ntexture = ExtResource("2_t")\noffset = Vector2(0, {-height // 2})\n\n'
        f'[node name="InteractionPolygon" type="CollisionPolygon2D" parent="."]\nvisible = false\npolygon = {poly}\n')
    gd = os.path.join(d, f"character_{sn}.gd")
    if not os.path.exists(gd):
        open(gd, "w", encoding="utf-8").write(CHAR_GD.format(sn=sn))
    open(os.path.join(d, f"character_{sn}_state.gd"), "w", encoding="utf-8").write(STATE_GD.format(base="PopochiuCharacterData"))
    open(os.path.join(d, f"character_{sn}.tres"), "w", encoding="utf-8").write(
        f'[gd_resource type="Resource" format=3]\n\n[ext_resource type="Script" path="{res}/character_{sn}_state.gd" id="1_s"]\n\n'
        f'[resource]\nresource_name = "{name}"\nscript = ExtResource("1_s")\nscript_name = "{name}"\nscene = "{res}/character_{sn}.tscn"\n')
    _register("characters", name, f"{res}/character_{sn}.tres")
    _autoload("c.gd", "PC", name, f"{res}/character_{sn}.gd", "get_runtime_character")
    print("character", name)
