extends Node2D
## Debug overlay for the screenshot tour: walkable floor (green), hotspots (red), props' click areas (blue),
## characters' feet (yellow dot) with their names.


func _draw() -> void:
	var room: Node = get_parent()
	var font := ThemeDB.fallback_font
	for wa in room.get_walkable_areas():
		for poly in wa.interaction_polygon:
			var pts := PackedVector2Array()
			for p in poly:
				pts.append(wa.global_position + wa.interaction_polygon_position + p)
			if pts.size() > 2:
				pts.append(pts[0])
				draw_polyline(pts, Color(0, 1, 0, 0.9), 4)
	for group in [[room.get_props(), Color(0.2, 0.4, 1, 0.9)], [room.get_hotspots(), Color(1, 0.15, 0.15, 0.9)]]:
		for n in group[0]:
			if not n.visible or not n.has_node("InteractionPolygon") or n.script_name == "Bg":
				continue
			var cp: CollisionPolygon2D = n.get_node("InteractionPolygon")
			var pts := PackedVector2Array()
			for p in cp.polygon:
				pts.append(cp.global_transform * p)
			if pts.size() > 2:
				pts.append(pts[0])
				draw_polyline(pts, group[1], 3)
				draw_string(font, pts[0] + Vector2(4, 22), n.script_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, group[1])
			if n is PopochiuHotspot or n is PopochiuProp:
				draw_circle(n.global_position + n.walk_to_point, 7, group[1])
	for c in room.get_characters():
		if not c.visible:
			continue
		draw_circle(c.global_position, 9, Color.YELLOW)
		draw_string(font, c.global_position + Vector2(10, 30), c.script_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.YELLOW)
