import json

class ZoneChecker:
    def __init__(self, zone_config_path):
        with open(zone_config_path, "r") as f:
            self.zones = json.load(f)["zones"]

    def _point_in_polygon(self, point, polygon):
        x, y = point
        inside = False

        n = len(polygon)
        px1, py1 = polygon[0]

        for i in range(n + 1):
            px2, py2 = polygon[i % n]
            if min(py1, py2) < y <= max(py1, py2) and x <= max(px1, px2):
                if py1 != py2:
                    xinters = (y - py1) * (px2 - px1) / (py2 - py1) + px1
                if px1 == px2 or x <= xinters:
                    inside = not inside
            px1, py1 = px2, py2

        return inside

    def get_zone(self, bbox):
        cx = int((bbox[0] + bbox[2]) / 2)
        cy = int((bbox[1] + bbox[3]) / 2)

        for zone in self.zones:
            if self._point_in_polygon((cx, cy), zone["polygon"]):
                return zone["type"]

        return "none"
