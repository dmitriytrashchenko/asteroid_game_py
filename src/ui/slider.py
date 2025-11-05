#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slider UI component.
"""

import pygame
from ..constants import WHITE, YELLOW


class Slider:
    """
    Interactive slider UI element.

    Attributes:
        rect (pygame.Rect): Slider track rectangle
        min_val (float): Minimum value
        max_val (float): Maximum value
        val (float): Current value
        label (str): Slider label
        dragging (bool): Whether slider is being dragged
    """

    def __init__(self, x: int, y: int, width: int,
                 min_val: float, max_val: float,
                 initial_val: float, label: str):
        """
        Initialize slider.

        Args:
            x: X position
            y: Y position
            width: Slider width
            min_val: Minimum value
            max_val: Maximum value
            initial_val: Initial value
            label: Slider label
        """
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = max(min_val, min(max_val, initial_val))
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame event.

        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on slider track or handle
                handle_x = self._get_handle_x()
                handle_rect = pygame.Rect(handle_x - 8, self.rect.centery - 8, 16, 16)

                if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self._update_value(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value(event.pos[0])

    def _update_value(self, mouse_x: int):
        """
        Update slider value based on mouse position.

        Args:
            mouse_x: Mouse X coordinate
        """
        # Clamp to slider bounds
        rel_x = mouse_x - self.rect.x
        rel_x = max(0, min(rel_x, self.rect.width))

        # Calculate value
        ratio = rel_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)

    def _get_handle_x(self) -> int:
        """
        Get X position of slider handle.

        Returns:
            Handle X coordinate
        """
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def draw(self, screen: pygame.Surface):
        """
        Draw slider.

        Args:
            screen: Pygame surface to draw on
        """
        # Draw track
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Draw handle
        handle_x = self._get_handle_x()
        pygame.draw.circle(screen, YELLOW, (handle_x, self.rect.centery), 8)

        # Draw label and value
        label_text = f"{self.label}: {self.val:.2f}"
        text_surface = self.font.render(label_text, True, WHITE)
        screen.blit(text_surface, (self.rect.x, self.rect.y - 30))

    def get_value(self) -> float:
        """
        Get current slider value.

        Returns:
            Current value
        """
        return self.val

    def set_value(self, value: float):
        """
        Set slider value.

        Args:
            value: New value (will be clamped to range)
        """
        self.val = max(self.min_val, min(self.max_val, value))
