# PLATO Room Phi

**Integrated Information (Phi) computation for PLATO rooms.**

Based on Integrated Information Theory (IIT), originally developed by neuroscientist Giulio Tononi. Phi measures how much a system's whole exceeds the sum of its parts.

## What is Phi?

Phi answers a deceptively simple question: **does this room know more as a whole than its tiles do separately?**

A room with high Phi has tiles that cross-reference each other, share coherent confidence distributions, and form an integrated knowledge structure. A room with low Phi is fragmented — tiles that don't connect, uncertainty that doesn't resolve.

## Why It Matters for PLATO

PLATO stores knowledge as tiles in rooms. Tile count is vanity. Phi is the signal:

| Level | Phi Range | Meaning |
|-------|----------|---------|
| **Unconscious** | 0.00 – 0.05 | Empty or completely disconnected |
| **Threshold** | 0.05 – 0.15 | Barely integrated, early-stage room |
| **Basic** | 0.15 – 0.30 | Coherent but simple knowledge |
| **Rich** | 0.30 – 0.50 | Well-integrated, useful knowledge |
| **Complex** | 0.50 – 0.70 | Deeply interconnected expertise |
| **Transcendent** | 0.70+ | Maximum integration |

## Installation

```bash
pip install plato-room-phi
```

## Quick Start

```python
from plato_room_phi import RoomPhi

phi = RoomPhi(plato_url="http://localhost:8847")

# Compute Phi for a specific room
result = phi.compute_for_room("fleet_orchestration")
print(f"Phi: {result['phi']:.3f} — {result['level']}")
print(f"Tiles: {result['tile_count']}, Status: {result['status']}")

# Scan all rooms
rooms = phi.scan_all_rooms(limit=50)
for r in rooms:
    print(f"{r['room']}: Φ={r['phi']:.4f} ({r['level']})")
```

## API

### `RoomPhi(plato_url: str = "http://localhost:8847")`

Create a RoomPhi instance pointing at your PLATO gateway.

### `compute_phi(tiles: List[Dict]) -> float`

Compute Phi from a list of tile dicts. Each tile should have `answer`, `question`, and optionally `confidence` (default 0.5).

### `compute_for_room(room: str) -> Dict`

Fetch tiles from a room and compute its full Phi profile:

```python
{
    "room": "fleet_orchestration",
    "phi": 0.342,
    "level": "rich",
    "tile_count": 12,
    "status": "healthy"
}
```

### `scan_all_rooms(limit: int = 50) -> List[Dict]`

Scan the top N rooms by tile count, compute Phi for each, return sorted by highest Phi.

### `phi_to_level(phi: float) -> str`

Convert a Phi value to its level label.

## How Phi is Calculated

1. **Integration** — Count how many tiles reference each other (first 50 chars of body text). Higher cross-reference density = higher integration.

2. **Distinct Information** — Shannon entropy of the confidence distribution. Diverse confidence levels = more distinct information.

3. **Phi = integration × normalized_entropy × 10** (capped at 1.0)

## License

MIT
