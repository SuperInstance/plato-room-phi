"""Tests for PLATO Room Phi."""

import pytest
from plato_room_phi import RoomPhi


class TestComputePhi:
    """Test Phi computation with mock tile data."""
    
    def test_empty_room(self):
        """Empty room has phi = 0."""
        phi = RoomPhi()
        assert phi.compute_phi([]) == 0.0
    
    def test_single_tile(self):
        """Single tile returns phi = 0 (needs 2+ for integration)."""
        phi = RoomPhi()
        tiles = [{"answer": "Only one tile", "question": "?"}]
        assert phi.compute_phi(tiles) == 0.0
    
    def test_unrelated_tiles(self):
        """Two completely unrelated tiles have low phi."""
        phi = RoomPhi()
        tiles = [
            {"answer": "Apples are red fruit", "question": "What color are apples?"},
            {"answer": "The sky is blue above us", "question": "What color is the sky?"},
        ]
        phi_val = phi.compute_phi(tiles)
        assert phi_val < 0.15  # Low phi - no cross-references
    
    def test_referencing_tiles(self):
        """Two tiles with shared opener text have detectable cross-reference."""
        phi = RoomPhi()
        # Both tiles start with identical text — "Plato is the fleet knowledge system"
        # so each tile's first-50-char prefix appears in the other's body.
        tiles = [
            {"answer": "Plato is the fleet knowledge system. Ships carry cargo.", "question": "What is Plato?"},
            {"answer": "Plato is the fleet knowledge system. Ships navigate seas.", "question": "How does Plato work?"},
        ]
        phi_val = phi.compute_phi(tiles)
        # cross_refs=2, integration=2/(2*1)=1.0, phi=1.0*1.0*10=1.0
        assert phi_val > 0.0, f"Expected phi > 0, got {phi_val}"
    
    def test_high_integration_room(self):
        """A room with 4 tiles all sharing the same opener has phi > 0.3."""
        phi = RoomPhi()
        # All tiles start with identical "Plato is the fleet knowledge system"
        # (50 chars), ensuring mutual prefix containment across all pairs.
        tiles = [
            {"answer": "Plato is the fleet knowledge system. Ships carry cargo.", "question": "What is Plato?"},
            {"answer": "Plato is the fleet knowledge system. Ships navigate seas.", "question": "How does Plato work?"},
            {"answer": "Plato is the fleet knowledge system. Ports process goods.", "question": "What are ports?"},
            {"answer": "Plato is the fleet knowledge system. Crews operate vessels.", "question": "Who operates the fleet?"},
        ]
        phi_val = phi.compute_phi(tiles)
        # 4 tiles → max_refs=12, cross_refs=12 (all pairs share the same opener)
        # integration=1.0, entropy_norm=1.0, phi=1.0*1.0*10=1.0
        assert phi_val > 0.3, f"Expected phi > 0.3, got {phi_val}"


class TestPhiLevels:
    """Test level classification."""
    
    def test_levels(self):
        phi = RoomPhi()
        assert phi.phi_to_level(0.01) == "unconscious"
        assert phi.phi_to_level(0.10) == "threshold"
        assert phi.phi_to_level(0.20) == "basic"
        assert phi.phi_to_level(0.40) == "rich"
        assert phi.phi_to_level(0.60) == "complex"
        assert phi.phi_to_level(0.85) == "transcendent"


class TestComputeForRoom:
    """Test room-level computation."""
    
    def test_phi_to_level_method(self):
        phi = RoomPhi()
        # Test boundary cases
        assert phi.phi_to_level(0.05) == "threshold"
        assert phi.phi_to_level(0.04) == "unconscious"
        assert phi.phi_to_level(0.15) == "basic"
        assert phi.phi_to_level(0.30) == "rich"
        assert phi.phi_to_level(0.50) == "complex"
        assert phi.phi_to_level(0.70) == "transcendent"
    
    def test_compute_returns_dict(self):
        """compute_for_room returns properly shaped dict (mock unavailable room)."""
        phi = RoomPhi(plato_url="http://localhost:9999")
        result = phi.compute_for_room("nonexistent_room")
        assert "room" in result
        assert "phi" in result
        assert "level" in result
        assert "tile_count" in result
        assert "status" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
