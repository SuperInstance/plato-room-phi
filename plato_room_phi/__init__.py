"""
PLATO Room PRII — PLATO Room Integration Index

Inspired by Integrated Information Theory (Tononi) but using computable heuristics:
- PRII measures how much a room's whole exceeds the sum of its tiles
- High PRII = highly integrated, coherent knowledge
- Low PRII = fragmented, uncertain, or disorganized

The PRII computation uses three components:
1. **Size**: log-scaled tile count (small rooms penalized)
2. **Integration**: word-overlap cross-references between tiles
3. **Confidence diversity**: entropy of confidence distribution

NOTE: This is NOT literal IIT. Aaronson (2014) proved trivial systems can achieve
arbitrarily high Φ. We use heuristic proxies (size, cross-refs, entropy) that capture
architectural coherence, not consciousness. See IIT critique in flux-research.

Usage:
    from plato_room_phi import RoomPRII
    prii = RoomPRII(plato_url="http://localhost:8847")
    result = prii.compute_for_room("fleet_orchestration")
    print(f"PRII: {result['prii']:.3f} — {result['level']}")
"""

import math
import requests
from typing import List, Dict, Any


def _get_significant_words(text: str) -> set:
    """Extract significant words (3+ chars) from text."""
    return {w for w in text.lower().split() if len(w) >= 3}


def _compute_cross_refs(tiles: List[Dict[str, Any]]) -> float:
    """Count cross-references between tiles using word overlap."""
    n = len(tiles)
    if n < 2:
        return 0.0
    
    tile_words = []
    for t in tiles:
        text = str(t.get("answer", "")) + " " + str(t.get("question", ""))
        tile_words.append(_get_significant_words(text))
    
    cross_refs = 0
    max_refs = n * (n - 1) / 2  # undirected pairs
    
    for i in range(n):
        for j in range(i + 1, n):
            # Tiles are cross-referenced if they share 3+ significant words
            if len(tile_words[i] & tile_words[j]) >= 3:
                cross_refs += 1
    
    return cross_refs / max_refs if max_refs > 0 else 0.0


def _compute_confidence_entropy(tiles: List[Dict[str, Any]]) -> float:
    """Compute normalized entropy of confidence distribution."""
    n = len(tiles)
    if n < 2:
        return 0.5  # default neutral
    
    confidences = [t.get("confidence", 0.5) for t in tiles]
    total = sum(confidences)
    
    entropy = 0.0
    if total > 0:
        for c in confidences:
            p = c / total
            if p > 0:
                entropy -= p * math.log2(p)
    
    max_entropy = math.log2(n)
    return entropy / max_entropy if max_entropy > 0 else 0.5


class RoomPRII:
    """
    Compute PLATO Room Integration Index (PRII) for rooms.
    
    PRII is computed from three components:
    - Size (log-scaled tile count)
    - Integration (word-overlap cross-references)
    - Confidence diversity (entropy)
    
    NOTE: This is NOT literal IIT Phi. See module docstring.
    """
    
    # Backward compatibility alias
    RoomPhi = None  # set below
    
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
    
    def compute_prii(self, tiles: List[Dict[str, Any]]) -> float:
        """
        Compute PRII = f(size, integration, confidence_entropy).
        
        PRII is the weighted combination of three room properties:
        - Size: log-scaled, penalizes tiny rooms
        - Integration: word-overlap cross-references
        - Confidence diversity: entropy of confidence scores
        
        Args:
            tiles: list of tile dicts with question, answer, confidence
        
        Returns:
            float: PRII value from 0.0 (no integration) to 1.0 (fully integrated)
        """
        n = len(tiles)
        if n < 2:
            return 0.0
        
        # 1. Size component (log-scaled, 0-1)
        # 1 tile -> 0, 10 tiles -> ~0.33, 100 -> ~0.5, 1000 -> ~0.67
        size_component = math.log(n) / math.log(1000)
        size_component = min(size_component, 1.0)
        
        # 2. Integration component (cross-ref density)
        integration = _compute_cross_refs(tiles)
        
        # 3. Confidence entropy component
        confidence_factor = _compute_confidence_entropy(tiles)
        
        # PRII = size-weighted blend of components
        # Size is primary limiter for small rooms
        prii = size_component * (0.4 + 0.3 * integration + 0.3 * confidence_factor)
        
        return round(min(prii, 1.0), 4)
    
    def compute_for_room(self, room: str) -> Dict[str, Any]:
        """Compute PRII for a PLATO room with full breakdown."""
        tiles = self.get_room_tiles(room)
        prii = self.compute_prii(tiles)
        
        level = self.prii_to_level(prii)
        
        return {
            "room": room,
            "prii": prii,
            "level": level,
            "tile_count": len(tiles),
            "status": "healthy" if prii > 0.1 else "fragmented" if prii > 0 else "empty"
        }
    
    def prii_to_level(self, prii: float) -> str:
        """Map PRII value to coherence level."""
        if prii < 0.05:
            return "empty"
        elif prii < 0.15:
            return "fragmented"
        elif prii < 0.30:
            return "basic"
        elif prii < 0.50:
            return "connected"
        elif prii < 0.70:
            return "integrated"
        else:
            return "coherent"
    
    def scan_all_rooms(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Scan top rooms by tile count, compute PRII for each."""
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
        
        return sorted(results, key=lambda x: x["prii"], reverse=True)


# Backward compatibility alias
RoomPhi = RoomPRII

# Demo
if __name__ == "__main__":
    prii = RoomPRII()
    
    print("=== Room PRII Demo ===")
    
    # Test with empty
    print(f"Empty room: {prii.compute_prii([])}")
    
    # Test with two unrelated tiles
    unrelated = [
        {"question": "What is PLATO?", "answer": "A knowledge system.", "confidence": 0.8},
        {"question": "How fast is Rust?", "answer": "Rust is very fast.", "confidence": 0.9},
    ]
    print(f"Unrelated tiles (2): PRII={prii.compute_prii(unrelated)}")
    
    # Test with two related tiles (3+ shared words)
    related = [
        {"question": "What is the DMN?", "answer": "The DMN generates creative options.", "confidence": 0.9},
        {"question": "What is the ECN?", "answer": "The ECN evaluates the DMN options.", "confidence": 0.8},
    ]
    print(f"Related tiles (2): PRII={prii.compute_prii(related)}")
    
    # Test against live PLATO
    print("\n=== Live PLATO Rooms ===")
    for room in ["oracle1_history", "fleet_orchestration", "dmn-ecm"]:
        r = prii.compute_for_room(room)
        print(f"{room}: PRII={r['prii']:.3f} Level={r['level']} Tiles={r['tile_count']}")
