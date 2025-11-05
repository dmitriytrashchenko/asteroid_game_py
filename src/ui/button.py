#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Button UI component.
"""

import pygame
from typing import Optional, Callable
from ..constants import WHITE, YELLOW


class Button:
    """
    Interactive button UI element.

    Attributes:
        rect (pygame.Rect): Button rectangle
        text (str): Button label text
        action (Callable): Function to call when clicked
        hovered (bool): Whether mouse is over button
        enabled (bool): Whether button is clickable
    """

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, action: Optional[Callable] = None):
        """
        Initialize button.

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button label
            action: Callback function when clicked
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.enabled = True
        self.font = pygame.font.Font(None, 32)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.

        Args:
            event: Pygame event to handle

        Returns:
            True if button was clicked and action executed
        """
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos) and self.action:
                    self.action()
                    return True
        return False

    def draw(self, screen: pygame.Surface):
        """
        Draw button.

        Args:
            screen: Pygame surface to draw on
        """
        # Choose color based on state
        if not self.enabled:
            color = (100, 100, 100)
        elif self.hovered:
            color = YELLOW
        else:
            color = WHITE

        # Draw border
        pygame.draw.rect(screen, color, self.rect, 2)

        # Draw text
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def set_enabled(self, enabled: bool):
        """
        Enable or disable button.

        Args:
            enabled: Whether button should be enabled
        """
        self.enabled = enabled

    def set_text(self, text: str):
        """
        Change button text.

        Args:
            text: New button label
        """
        self.text = text
