#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound manager with procedural sound generation.
"""

import pygame
import numpy as np
from typing import Dict
from ..utils.settings import Settings


class SoundManager:
    """
    Manages game sound effects using procedural generation.

    Attributes:
        settings (Settings): Game settings
        sounds (Dict[str, pygame.mixer.Sound]): Cache of generated sounds
        enabled (bool): Whether sound is enabled
    """

    def __init__(self, settings: Settings):
        """
        Initialize sound manager.

        Args:
            settings: Game settings instance
        """
        self.settings = settings
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.enabled = True

        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._generate_sounds()
        except pygame.error as e:
            print(f"Не удалось инициализировать звук: {e}")
            self.enabled = False

    def _generate_sounds(self):
        """Generate all sound effects procedurally."""
        if not self.enabled:
            return

        try:
            # Generate sounds
            self.sounds['shoot'] = self._generate_shoot_sound()
            self.sounds['explosion'] = self._generate_explosion_sound()
            self.sounds['explosion_small'] = self._generate_small_explosion_sound()
            self.sounds['powerup'] = self._generate_powerup_sound()
            self.sounds['ship_hit'] = self._generate_ship_hit_sound()
            self.sounds['thrust'] = self._generate_thrust_sound()

        except Exception as e:
            print(f"Ошибка генерации звуков: {e}")
            self.enabled = False

    def _generate_shoot_sound(self) -> pygame.mixer.Sound:
        """
        Generate laser shoot sound.

        Returns:
            Pygame Sound object
        """
        sample_rate = 22050
        duration = 0.1
        frequency = 800

        # Generate descending tone
        samples = int(sample_rate * duration)
        wave = np.zeros(samples)

        for i in range(samples):
            # Frequency sweeps down
            freq = frequency - (frequency * 0.5 * i / samples)
            wave[i] = np.sin(2 * np.pi * freq * i / sample_rate) * 32767

        # Add envelope
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope

        # Convert to stereo
        stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_explosion_sound(self) -> pygame.mixer.Sound:
        """
        Generate explosion sound.

        Returns:
            Pygame Sound object
        """
        sample_rate = 22050
        duration = 0.5

        # Generate noise-based explosion
        samples = int(sample_rate * duration)
        wave = np.random.uniform(-1, 1, samples) * 32767

        # Add low-frequency rumble
        rumble = np.sin(2 * np.pi * 100 * np.arange(samples) / sample_rate) * 16384
        wave = wave * 0.7 + rumble * 0.3

        # Envelope (sharp attack, exponential decay)
        envelope = np.exp(-3 * np.arange(samples) / samples)
        wave = wave * envelope

        # Convert to stereo
        stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_small_explosion_sound(self) -> pygame.mixer.Sound:
        """
        Generate small explosion sound.

        Returns:
            Pygame Sound object
        """
        sample_rate = 22050
        duration = 0.3

        samples = int(sample_rate * duration)
        wave = np.random.uniform(-1, 1, samples) * 24576

        # Higher frequency rumble
        rumble = np.sin(2 * np.pi * 200 * np.arange(samples) / sample_rate) * 12288
        wave = wave * 0.6 + rumble * 0.4

        # Faster decay
        envelope = np.exp(-5 * np.arange(samples) / samples)
        wave = wave * envelope

        stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_powerup_sound(self) -> pygame.mixer.Sound:
        """
        Generate power-up collection sound.

        Returns:
            Pygame Sound object
        """
        sample_rate = 22050
        duration = 0.3

        samples = int(sample_rate * duration)
        wave = np.zeros(samples)

        # Ascending arpeggio
        frequencies = [523, 659, 784]  # C, E, G

        segment_length = samples // len(frequencies)
        for i, freq in enumerate(frequencies):
            start = i * segment_length
            end = start + segment_length
            segment_samples = end - start

            for j in range(segment_samples):
                wave[start + j] = np.sin(2 * np.pi * freq * j / sample_rate) * 32767

        # Envelope
        envelope = np.linspace(0.3, 1.0, samples)
        wave = wave * envelope

        stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_ship_hit_sound(self) -> pygame.mixer.Sound:
        """
        Generate ship hit/death sound.

        Returns:
            Pygame Sound object
        """
        sample_rate = 22050
        duration = 0.8

        samples = int(sample_rate * duration)
        wave = np.random.uniform(-1, 1, samples) * 32767

        # Low rumble
        rumble = np.sin(2 * np.pi * 60 * np.arange(samples) / sample_rate) * 20000
        wave = wave * 0.5 + rumble * 0.5

        # Long decay
        envelope = np.exp(-2 * np.arange(samples) / samples)
        wave = wave * envelope

        stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

        return pygame.sndarray.make_sound(stereo_wave)

    def _generate_thrust_sound(self) -> pygame.mixer.Sound:
        """
        Generate thrust/engine sound.

        Returns:
            Pygame Sound object
        """
        sample_rate = 22050
        duration = 0.2

        samples = int(sample_rate * duration)
        # Low rumbling noise
        wave = np.random.uniform(-1, 1, samples) * 16384

        # Add low frequency
        rumble = np.sin(2 * np.pi * 150 * np.arange(samples) / sample_rate) * 16384
        wave = wave * 0.7 + rumble * 0.3

        # Gentle envelope
        envelope = np.hanning(samples)
        wave = wave * envelope

        stereo_wave = np.column_stack((wave, wave)).astype(np.int16)

        return pygame.sndarray.make_sound(stereo_wave)

    def play_sound(self, sound_name: str):
        """
        Play a sound effect.

        Args:
            sound_name: Name of the sound to play
        """
        if not self.enabled or sound_name not in self.sounds:
            return

        try:
            sound = self.sounds[sound_name]
            sound.set_volume(self.settings.sound_volume)
            sound.play()
        except pygame.error as e:
            print(f"Ошибка воспроизведения звука {sound_name}: {e}")

    def play_shoot(self):
        """Play shoot sound."""
        self.play_sound('shoot')

    def play_explosion(self, large: bool = True):
        """
        Play explosion sound.

        Args:
            large: Whether to play large explosion sound
        """
        sound_name = 'explosion' if large else 'explosion_small'
        self.play_sound(sound_name)

    def play_powerup(self):
        """Play power-up collection sound."""
        self.play_sound('powerup')

    def play_ship_hit(self):
        """Play ship hit/death sound."""
        self.play_sound('ship_hit')

    def play_thrust(self):
        """Play thrust sound."""
        self.play_sound('thrust')

    def update_volume(self):
        """Update volume for all sounds based on settings."""
        if not self.enabled:
            return

        for sound in self.sounds.values():
            sound.set_volume(self.settings.sound_volume)

    def stop_all(self):
        """Stop all playing sounds."""
        if self.enabled:
            pygame.mixer.stop()
