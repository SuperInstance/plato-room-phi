"""
PLATO Room Phi — Integrated Information for PLATO rooms

Based on Integrated Information Theory (Tononi):
- Phi measures how much a room's whole exceeds the sum of its tiles
- High Phi = highly integrated, coherent knowledge
- Low Phi = fragmented, uncertain, or unconscious

Usage:
    from plato_room_phi import RoomPhi
    phi = RoomPhi(plato_url="http://localhost:8847")
    result = phi.compute("fleet_orchestration")
    print(f"Phi: {result['phi']:.3f} — {result['level']}")
"""

import math
import requests
from typing import List, Dict, Any, Optional

class RoomPhi:
    def __init__(self, plato_url: str = "http://localhost:8847"):
        self.plato_url = plato_url.rstrip("/")
    
    def get_room_tiles(self, room: str) -> List[Dict[str, Any]]:
        """Fetch all tiles from a PLATO room."""
        try:
            resp = requests.get(f"{self.plato_url}/room/{room}", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("tiles", [])
        except:
            pass
        return []
    
    def compute_phi(self, tiles: List[Dict[str, Any]]) -> float:
        """
        Compute Phi = integration × distinct information.
        
        Integration: cross-reference density between tiles
        Distinct information: entropy of confidence distribution
        """
        if len(tiles) < 2:
            return 0.0
        
        # Build full body text for each tile (answer + question)
        tile_bodies = [str(t.get("answer", "")) + " " + str(t.get("question", "")) for t in tiles]
        
        # Count cross-references: shared significant words between tiles.
        # Integration via shared concept overlap rather than fragile substring matching.
        cross_refs = 0
        stop_words = set(['the', 'a', 'an', 'is', 'are', 'in', 'on', 'at', 'to', 'of', 'for', 'and', 'or', 'but', 'with', 'by', 'as', 'it', 'its', 'this', 'that', 'what', 'how', 'where', 'when', 'who', 'do', 'does', '?'])
        def get_words(text):
            return set(w.lower().strip('.,!?') for w in text.split() if w.lower().strip('.,!?') not in stop_words)
        tile_words = [get_words(b) for b in tile_bodies]
        for i, words_i in enumerate(tile_words):
            for j, words_j in enumerate(tile_words):
                if i != j:
                    shared = words_i & words_j
                    if len(shared) >= 3:  # 3+ shared significant words = cross-reference
                        cross_refs += 1
        
        max_refs = len(tiles) * (len(tiles) - 1)
        integration = cross_refs / max_refs if max_refs > 0 else 0.0
        
        # Entropy of confidences
        confidences = [t.get("confidence", 0.5) for t in tiles]
        total = sum(confidences)
        entropy = 0.0
        if total > 0:
            for c in confidences:
                p = c / total
                if p > 0:
                    entropy -= p * math.log2(p)
        
        max_entropy = math.log2(len(tiles)) if len(tiles) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        phi = min(integration * normalized_entropy * 10, 1.0)
        return round(phi, 4)
    
    def compute_for_room(self, room: str) -> Dict[str, Any]:
        """Compute Phi for a PLATO room with full breakdown."""
        tiles = self.get_room_tiles(room)
        phi = self.compute_phi(tiles)
        
        level = self.phi_to_level(phi)
        
        return {
            "room": room,
            "phi": phi,
            "level": level,
            "tile_count": len(tiles),
            "status": "healthy" if phi > 0.1 else "fragmented" if phi > 0 else "empty"
        }
    
    def phi_to_level(self, phi: float) -> str:
        if phi < 0.05: return "unconscious"
        elif phi < 0.15: return "threshold"
        elif phi < 0.30: return "basic"
        elif phi < 0.50: return "rich"
        elif phi < 0.70: return "complex"
        else: return "transcendent"
    
    def scan_all_rooms(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Scan top rooms by tile count, compute Phi for each."""
        try:
            resp = requests.get(f"{self.plato_url}/rooms?limit={limit}", timeout=5)
            if resp.status_code == 200:
                rooms = resp.json().get("rooms", [])
            else:
                rooms = []
        except:
            rooms = []
        
        results = []
        for room in rooms[:limit]:
            room_name = room.get("name", room.get("room", ""))
            if room_name:
                r = self.compute_for_room(room_name)
                results.append(r)
        
        return sorted(results, key=lambda x: x["phi"], reverse=True)
