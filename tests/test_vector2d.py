#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Vector2D class.
"""

import unittest
import math
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.vector2d import Vector2D


class TestVector2D(unittest.TestCase):
    """Test cases for Vector2D class."""

    def test_initialization(self):
        """Test vector initialization."""
        v = Vector2D(3, 4)
        self.assertEqual(v.x, 3)
        self.assertEqual(v.y, 4)

        # Default initialization
        v_default = Vector2D()
        self.assertEqual(v_default.x, 0)
        self.assertEqual(v_default.y, 0)

    def test_addition(self):
        """Test vector addition."""
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        result = v1 + v2
        self.assertEqual(result.x, 4)
        self.assertEqual(result.y, 6)

    def test_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector2D(5, 7)
        v2 = Vector2D(2, 3)
        result = v1 - v2
        self.assertEqual(result.x, 3)
        self.assertEqual(result.y, 4)

    def test_multiplication(self):
        """Test scalar multiplication."""
        v = Vector2D(2, 3)
        result = v * 3
        self.assertEqual(result.x, 6)
        self.assertEqual(result.y, 9)

    def test_division(self):
        """Test scalar division."""
        v = Vector2D(6, 9)
        result = v / 3
        self.assertEqual(result.x, 2)
        self.assertEqual(result.y, 3)

        # Test division by zero
        with self.assertRaises(ZeroDivisionError):
            v / 0

    def test_magnitude(self):
        """Test magnitude calculation."""
        v = Vector2D(3, 4)
        self.assertEqual(v.magnitude(), 5.0)

        v_zero = Vector2D(0, 0)
        self.assertEqual(v_zero.magnitude(), 0.0)

    def test_magnitude_squared(self):
        """Test squared magnitude calculation."""
        v = Vector2D(3, 4)
        self.assertEqual(v.magnitude_squared(), 25)

    def test_normalize(self):
        """Test vector normalization."""
        v = Vector2D(3, 4)
        normalized = v.normalize()
        self.assertAlmostEqual(normalized.magnitude(), 1.0)
        self.assertAlmostEqual(normalized.x, 0.6)
        self.assertAlmostEqual(normalized.y, 0.8)

        # Zero vector normalization
        v_zero = Vector2D(0, 0)
        normalized_zero = v_zero.normalize()
        self.assertEqual(normalized_zero.x, 0)
        self.assertEqual(normalized_zero.y, 0)

    def test_rotate(self):
        """Test vector rotation."""
        v = Vector2D(1, 0)
        # Rotate 90 degrees (pi/2 radians)
        rotated = v.rotate(math.pi / 2)
        self.assertAlmostEqual(rotated.x, 0, places=10)
        self.assertAlmostEqual(rotated.y, 1, places=10)

    def test_dot_product(self):
        """Test dot product calculation."""
        v1 = Vector2D(2, 3)
        v2 = Vector2D(4, 5)
        dot = v1.dot(v2)
        self.assertEqual(dot, 23)  # 2*4 + 3*5 = 23

    def test_distance_to(self):
        """Test distance calculation."""
        v1 = Vector2D(0, 0)
        v2 = Vector2D(3, 4)
        distance = v1.distance_to(v2)
        self.assertEqual(distance, 5.0)

    def test_distance_squared_to(self):
        """Test squared distance calculation."""
        v1 = Vector2D(0, 0)
        v2 = Vector2D(3, 4)
        distance_sq = v1.distance_squared_to(v2)
        self.assertEqual(distance_sq, 25)

    def test_from_angle(self):
        """Test creating vector from angle."""
        # 0 degrees
        v = Vector2D.from_angle(0, 1.0)
        self.assertAlmostEqual(v.x, 1.0)
        self.assertAlmostEqual(v.y, 0.0)

        # 90 degrees
        v = Vector2D.from_angle(math.pi / 2, 1.0)
        self.assertAlmostEqual(v.x, 0.0, places=10)
        self.assertAlmostEqual(v.y, 1.0)

    def test_limit(self):
        """Test magnitude limiting."""
        v = Vector2D(10, 0)
        limited = v.limit(5)
        self.assertEqual(limited.magnitude(), 5.0)

        # Vector already within limit
        v_small = Vector2D(2, 0)
        limited_small = v_small.limit(5)
        self.assertEqual(limited_small.magnitude(), 2.0)

    def test_equality(self):
        """Test vector equality."""
        v1 = Vector2D(1.0, 2.0)
        v2 = Vector2D(1.0, 2.0)
        v3 = Vector2D(2.0, 3.0)

        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)

    def test_repr(self):
        """Test string representation."""
        v = Vector2D(1.23456, 2.34567)
        repr_str = repr(v)
        self.assertIn("1.23", repr_str)
        self.assertIn("2.35", repr_str)


if __name__ == '__main__':
    unittest.main()
