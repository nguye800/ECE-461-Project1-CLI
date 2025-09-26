import sys, os
import pytest

# Ensure src is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.classes.Size import Size


def test_size_small_project():
    m = Size()
    # Small project: total < 1 GB (e.g., 500 MB = 500*1024^2 bytes)
    m.setSize([500 * 1024 * 1024])  
    score = m.getSize()
    size_gb = m.getModelSizeGB()
    print("Small project size (GB):", size_gb, "score:", score)
    assert score == 1.0
    assert size_gb < 1.0


def test_size_large_project():
    m = Size()
    # Large project: e.g., 5 GB total
    m.setSize([5 * 1024 * 1024 * 1024])  
    score = m.getSize()
    size_gb = m.getModelSizeGB()
    print("Large project size (GB):", size_gb, "score:", score)
    assert score == 0.5
    assert 1.0 <= size_gb < 10.0


def test_size_huge_project():
    m = Size()
    # Very large project: e.g., 20 GB
    m.setSize([20 * 1024 * 1024 * 1024])  
    score = m.getSize()
    size_gb = m.getModelSizeGB()
    print("Huge project size (GB):", size_gb, "score:", score)
    assert score == 0.0
    assert size_gb >= 10.0