"""
⚛  CELLULAR AUTOMATON EXPLORER — ULTRAVERSE v10
==================================================
Upgrades over v9:
  • Fully vectorized plasma, aurora & crystal render modes (no Python loops)
  • Save / Load grid state  (Ctrl+S / Ctrl+O  →  .npy files)
  • Screenshot capture      (Ctrl+P            →  PNG)
  • Ctrl+I invert, Ctrl+R random (keep C/I/R as unmodified shortcuts too)
  • Data-driven UI registry: buttons register themselves, hover & click
    resolution is O(n) table lookup — no more brittle hardcoded Y offsets
  • Langton hit-test fixed (was using rough y=200 estimate)
  • Rule-preset click handler wired up (was display-only in v9)
  • AI-driven interval slider is now actually interactive
  • Brush-size scroll: scroll-wheel over canvas changes brush size (no key)
  • New GoL patterns: hammerhead, copperhead (fast spaceships), B-heptomino
  • New rule preset: Stains  B3578/S235678
  • Population graph now shows last 200 gens (was len(history) which was ~w px)
  • Orbit hash uses proper Zobrist-style XOR for collision resistance
  • FPS counter smoothed over 1 s window (was 0.5 s)
  • version badge updated to v10

Requires:  pip install pygame numpy anthropic

Controls
--------
Space       Play / Pause
→           Step one generation
C           Clear grid
I           Invert grid
R           Random 30%
G           Toggle grid lines
T           Toggle trails
M           Cycle render mode
0           Reset / fit view
+/-         Zoom
D/E         Draw / Erase tool
Ctrl+Z      Undo
Ctrl+S      Save grid (.npy)
Ctrl+O      Load grid (.npy)
Ctrl+P      Screenshot (PNG)
B           Cycle brush shape
Scroll      Zoom (on canvas) / Speed (on left panel) / Brush size (Shift+scroll on canvas)
Escape      Quit
"""

import sys, os, math, time, random, json, copy, threading, textwrap, datetime
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pygame
import pygame.gfxdraw

# ── optional AI ──────────────────────────────────────────────────────────────
try:
    import anthropic
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

# =============================================================================
# CONSTANTS
# =============================================================================
GRID_W, GRID_H = 200, 150
CELL           = 4
FPS_CAP        = 240
HISTORY_MAX    = 400
TRAIL_DECAY    = 0.88

WIN_W = 1280
WIN_H = 800

PANEL_L = 220
PANEL_R = 260
HEADER_H = 44
FOOTER_H = 120

CANVAS_X = PANEL_L
CANVAS_Y = HEADER_H
CANVAS_W = WIN_W - PANEL_L - PANEL_R
CANVAS_H = WIN_H - HEADER_H - FOOTER_H

# Palette
BG       = (0,   0,   0)
PANEL_BG = (8,   8,   8)
BORDER   = (24,  24,  24)
ACCENT   = (102, 126, 234)
ACCENT2  = (167, 139, 250)
GREEN    = (74,  222, 128)
AMBER    = (245, 158, 11)
RED      = (248, 113, 113)
CYAN     = (6,   182, 212)
ROSE     = (244, 63,  94)
TEXT     = (208, 208, 208)
TEXT2    = (136, 136, 136)
TEXT3    = (68,  68,  68)

# =============================================================================
# SIMULATION ENGINES
# =============================================================================

class UniverseState:
    """Core GoL universe with birth/survival rules and history."""
    def __init__(self):
        self.grid          = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
        self.birth_rules   = [3]
        self.survival_rules= [2, 3]
        self.generation    = 0
        self.history: list = []
        self.birth_hist:  list[int] = []
        self.death_hist:  list[int] = []
        self.entropy_hist:list[float] = []
        self.vel_hist:    list[int] = []
        self.complex_hist:list[float] = []

    def step(self):
        g = self.grid
        # Neighbour count via numpy rolling sums
        n = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)
            +np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)
            +np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1))
        alive = g == 1
        survive_mask = np.zeros_like(g, dtype=bool)
        for s in self.survival_rules:
            survive_mask |= (n == s)
        born_mask = np.zeros_like(g, dtype=bool)
        for b in self.birth_rules:
            born_mask |= (n == b)
        new_g = np.where(alive, survive_mask.astype(np.uint8), born_mask.astype(np.uint8))
        births = int(np.sum(new_g & ~alive))
        deaths = int(np.sum(~new_g.astype(bool) & alive))
        self.history.append(g.copy())
        if len(self.history) > HISTORY_MAX:
            self.history.pop(0)
        living = int(new_g.sum())
        ent = float(self._entropy(new_g))
        vel = births + deaths
        self.birth_hist.append(births); self.death_hist.append(deaths)
        self.entropy_hist.append(ent); self.vel_hist.append(vel)
        self.complex_hist.append(ent * living / (GRID_W * GRID_H))
        for lst in (self.birth_hist, self.death_hist, self.entropy_hist,
                    self.vel_hist, self.complex_hist):
            if len(lst) > HISTORY_MAX: lst.pop(0)
        self.grid = new_g
        self.generation += 1
        return births, deaths, living

    def _entropy(self, g):
        edges = int(np.sum(g[:,:-1] != g[:,1:]) + np.sum(g[:-1,:] != g[1:,:]))
        return edges / (GRID_W * GRID_H)

    def randomize(self, density=0.3):
        self.grid = (np.random.random((GRID_H, GRID_W)) < density).astype(np.uint8)

    def clear(self):
        self.grid[:] = 0
        self.history.clear()
        self.birth_hist.clear(); self.death_hist.clear()
        self.entropy_hist.clear(); self.vel_hist.clear(); self.complex_hist.clear()
        self.generation = 0


class ReactionDiffusion:
    def __init__(self, feed=0.055, kill=0.062):
        self.feed = feed; self.kill = kill
        self.A = np.ones((GRID_H, GRID_W), dtype=np.float32)
        self.B = np.zeros((GRID_H, GRID_W), dtype=np.float32)
        self._seed()

    def _seed(self):
        cx, cy = GRID_W//2, GRID_H//2
        self.A[cy-8:cy+8, cx-8:cx+8] = 0.5
        self.B[cy-8:cy+8, cx-8:cx+8] = 0.25 + np.random.random((16,16))*0.05

    def step(self):
        A, B = self.A, self.B
        def lap(m): return (-4*m + np.roll(m,1,0)+np.roll(m,-1,0)+np.roll(m,1,1)+np.roll(m,-1,1))
        abb = A * B * B
        self.A = np.clip(A + 1.0*lap(A)*0.5 - abb + self.feed*(1-A), 0, 1)
        self.B = np.clip(B + 0.5*lap(B)*0.5 + abb - (self.kill+self.feed)*B, 0, 1)


class BriansBrain:
    def __init__(self):
        self.grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
        self.grid[np.random.random((GRID_H,GRID_W)) < 0.2] = 1

    def step(self):
        g = self.grid
        # Vectorized: sum only state-1 cells as neighbours
        alive = (g == 1).astype(np.uint8)
        n_alive = (np.roll(alive,-1,0)+np.roll(alive,1,0)+
                   np.roll(alive,-1,1)+np.roll(alive,1,1)+
                   np.roll(np.roll(alive,-1,0),-1,1)+np.roll(np.roll(alive,-1,0),1,1)+
                   np.roll(np.roll(alive,1,0),-1,1)+np.roll(np.roll(alive,1,0),1,1))
        new_g = np.zeros_like(g)
        new_g[g == 1] = 2                         # firing → refractory
        new_g[(g == 0) & (n_alive == 2)] = 1      # dead + 2 firing → fires
        self.grid = new_g


class WireWorld:
    COLORS = [(0,0,0),(232,176,78),(0,191,255),(255,107,107)]
    def __init__(self):
        self.grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
        cx, cy = GRID_W//2, GRID_H//2
        self.grid[cy, cx-40:cx+41] = 1
        self.grid[cy, cx-38] = 2; self.grid[cy, cx-37] = 3
        self.grid[cy, cx+37] = 2; self.grid[cy, cx+38] = 3
        self.grid[cy:cy+16, cx-40] = 1; self.grid[cy:cy+16, cx+40] = 1
        self.grid[cy+15, cx-40:cx+41] = 1

    def step(self):
        g = self.grid
        heads = (g == 2).astype(np.uint8)
        # Vectorized neighbour sum of heads
        n_heads = (np.roll(heads,-1,0)+np.roll(heads,1,0)+
                   np.roll(heads,-1,1)+np.roll(heads,1,1)+
                   np.roll(np.roll(heads,-1,0),-1,1)+np.roll(np.roll(heads,-1,0),1,1)+
                   np.roll(np.roll(heads,1,0),-1,1)+np.roll(np.roll(heads,1,0),1,1))
        new_g = np.zeros_like(g)
        new_g[g == 2] = 3                              # head → tail
        new_g[g == 3] = 1                              # tail → conductor
        cond = (g == 1)
        becomes_head = cond & ((n_heads == 1) | (n_heads == 2))
        new_g[becomes_head] = 2
        new_g[cond & ~becomes_head] = 1
        self.grid = new_g


class LangtonAnt:
    def __init__(self, n_ants=1, rule="RL"):
        self.rule = rule
        self.grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
        self.ants = [{"x": GRID_W//2 + (i%3-1)*10,
                      "y": GRID_H//2 + (i//3)*10,
                      "dir": i%4} for i in range(n_ants)]
        self.DIRS = [(0,-1),(1,0),(0,1),(-1,0)]

    def step(self):
        for ant in self.ants:
            state = int(self.grid[ant["y"], ant["x"]]) % len(self.rule)
            turn = self.rule[state]
            ant["dir"] = (ant["dir"]+1)%4 if turn=='R' else (ant["dir"]+3)%4
            self.grid[ant["y"], ant["x"]] = (int(self.grid[ant["y"],ant["x"]])+1) % len(self.rule)
            dx, dy = self.DIRS[ant["dir"]]
            ant["x"] = (ant["x"]+dx) % GRID_W
            ant["y"] = (ant["y"]+dy) % GRID_H


class CyclicCA:
    def __init__(self, states=5, threshold=2):
        self.states = states; self.threshold = threshold
        self.grid = np.random.randint(0, states, (GRID_H, GRID_W), dtype=np.uint8)

    def step(self):
        g = self.grid
        succ = (g + 1) % self.states
        # Vectorized 8-neighbour successor count
        count = (
            (np.roll(g,-1,0)==succ).astype(np.uint8) +
            (np.roll(g, 1,0)==succ).astype(np.uint8) +
            (np.roll(g,-1,1)==succ).astype(np.uint8) +
            (np.roll(g, 1,1)==succ).astype(np.uint8) +
            (np.roll(np.roll(g,-1,0),-1,1)==succ).astype(np.uint8) +
            (np.roll(np.roll(g,-1,0), 1,1)==succ).astype(np.uint8) +
            (np.roll(np.roll(g, 1,0),-1,1)==succ).astype(np.uint8) +
            (np.roll(np.roll(g, 1,0), 1,1)==succ).astype(np.uint8)
        )
        self.grid = np.where(count >= self.threshold, succ, g).astype(np.uint8)


class ElementaryCA:
    def __init__(self, rule=110):
        self.rule_num = rule
        self.grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
        self.grid[0, GRID_W//2] = 1
        self.row = 0

    def set_rule(self, n):
        self.rule_num = n
        self.grid[:] = 0
        self.grid[0, GRID_W//2] = 1
        self.row = 0

    def step(self):
        if self.row >= GRID_H - 1:
            self.grid[:-1] = self.grid[1:]
            self.grid[-1] = 0
            self.row = GRID_H - 2
        src = self.grid[self.row]
        l = np.roll(src, 1); r = np.roll(src, -1)
        idx = (l.astype(np.uint8) << 2) | (src << 1) | r
        self.grid[self.row+1] = (self.rule_num >> idx) & 1
        self.row += 1


class ForestFire:
    def __init__(self, f=0.001, g=0.010):
        self.f = f; self.g = g
        self.grid = (np.random.random((GRID_H, GRID_W)) < 0.6).astype(np.uint8)

    def step(self):
        grid = self.grid
        burning = (grid == 2).astype(np.uint8)
        # Vectorized neighbour count of burning cells
        n_burn = (np.roll(burning,-1,0)+np.roll(burning,1,0)+
                  np.roll(burning,-1,1)+np.roll(burning,1,1)+
                  np.roll(np.roll(burning,-1,0),-1,1)+np.roll(np.roll(burning,-1,0),1,1)+
                  np.roll(np.roll(burning,1,0),-1,1)+np.roll(np.roll(burning,1,0),1,1))
        rnd = np.random.random((GRID_H, GRID_W))
        new_g = np.zeros_like(grid)
        # empty → tree
        new_g[(grid==0)] = (rnd[grid==0] < self.g).astype(np.uint8)
        # burning → empty (stays 0)
        # tree → fire if neighbour burning or random
        tree = (grid == 1)
        ignite = tree & ((n_burn > 0) | (rnd < self.f))
        new_g[tree & ~ignite] = 1
        new_g[ignite] = 2
        self.grid = new_g


# =============================================================================
# NEW: SMOOTH LIFE
# =============================================================================

class SmoothLife:
    """Continuous (smooth) version of GoL using Gaussian annular kernel."""
    def __init__(self):
        self.ra = 12.0   # outer radius
        self.ri = 3.0    # inner radius
        self.field = np.random.random((GRID_H, GRID_W)).astype(np.float32)
        # Precompute FFT kernel
        self._build_kernel()

    def _build_kernel(self):
        ys = np.arange(GRID_H)
        xs = np.arange(GRID_W)
        yy, xx = np.meshgrid(ys - GRID_H//2, xs - GRID_W//2, indexing='ij')
        dist = np.sqrt(xx**2 + yy**2).astype(np.float32)
        # Annular kernel: ring between ri and ra
        kernel = np.where((dist >= self.ri) & (dist <= self.ra), 1.0, 0.0).astype(np.float32)
        ksum = kernel.sum()
        if ksum > 0:
            kernel /= ksum
        self._fft_kernel_ann = np.fft.rfft2(np.fft.ifftshift(kernel))
        # Inner disk kernel for local density
        inner = np.where(dist <= self.ri, 1.0, 0.0).astype(np.float32)
        isum = inner.sum()
        if isum > 0:
            inner /= isum
        self._fft_kernel_inn = np.fft.rfft2(np.fft.ifftshift(inner))

    @staticmethod
    def _sigma(x, a, alpha=0.028):
        return 1.0 / (1.0 + np.exp(-(x - a) / alpha))

    @staticmethod
    def _sigmaN(x, a, b):
        s = SmoothLife._sigma
        return s(x, a) * (1.0 - s(x, b))

    @staticmethod
    def _sigmaM(x, y, m):
        s = SmoothLife._sigma
        return x * (1 - s(m, 0.5)) + y * s(m, 0.5)

    def _transition(self, n, m):
        b1, b2, d1, d2 = 0.278, 0.365, 0.267, 0.445
        return self._sigmaN(n, self._sigmaM(b1, d1, m), self._sigmaM(b2, d2, m))

    def step(self):
        fft_f = np.fft.rfft2(self.field)
        n = np.real(np.fft.irfft2(fft_f * self._fft_kernel_ann, s=self.field.shape))
        m = np.real(np.fft.irfft2(fft_f * self._fft_kernel_inn, s=self.field.shape))
        new_f = self._transition(n, m)
        self.field = np.clip(new_f, 0.0, 1.0).astype(np.float32)

    @property
    def grid_display(self):
        return self.field


# =============================================================================
# RENDERING HELPERS
# =============================================================================

RENDER_MODES = ["classic","heat","age","velocity","nebula","plasma",
                "aurora","quantum","crystal","starfield","lava","void","bioluminescent"]
SIM_MODES    = ["gol","smooth","rd","brian","wire","langton","cyclic","elem","forest"]

def _hsv_to_rgb(h, s, v):
    h = h % 360
    c = v * s; x = c*(1-abs((h/60)%2-1)); m = v-c
    if   h<60:  r,g,b=c,x,0
    elif h<120: r,g,b=x,c,0
    elif h<180: r,g,b=0,c,x
    elif h<240: r,g,b=0,x,c
    elif h<300: r,g,b=x,0,c
    else:       r,g,b=c,0,x
    return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

def render_gol(surf: pygame.Surface, u: UniverseState, age_grid: np.ndarray,
               vx, vy, vs, mode="classic", color1=(102,126,234), color2=(118,75,162),
               trail_surf=None):
    """Render GoL grid onto surf using given render mode."""
    g = u.grid
    cs = CELL * vs
    surf.fill(BG)

    # Draw trail overlay first (ghost effect)
    if trail_surf is not None:
        surf.blit(trail_surf, (0, 0))

    if mode == "crystal":
        # Fully vectorized crystal mode: compute per-cell colors in NumPy,
        # then blit a scaled surface — no Python per-cell loop.
        cs = CELL * vs
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        yy, xx = np.meshgrid(np.arange(GRID_H, dtype=np.float32),
                             np.arange(GRID_W,  dtype=np.float32), indexing='ij')
        age_f = np.clip(age_grid / 80.0, 0, 1)
        # Per-cell hue using position + age + neighbour count + generation drift
        hue = (xx * 3.7 + yy * 2.3 + age_f * 120.0 + nv * 25.0 + u.generation * 0.4) % 360.0
        sat = np.clip(0.55 + age_f * 0.35, 0, 1)
        lit = np.clip(0.25 + age_f * 0.30 + nv * 0.03, 0, 1)
        # HSV→RGB vectorized
        h6  = hue / 60.0
        hi  = h6.astype(np.int32) % 6
        f   = (h6 - np.floor(h6)).astype(np.float32)
        p   = lit * (1 - sat)
        q   = lit * (1 - sat * f)
        t_  = lit * (1 - sat * (1 - f))
        r_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[lit,q,p,p,t_,lit])
        g_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[t_,lit,lit,q,p,p])
        b_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[p,p,t_,lit,lit,q])
        img_c = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
        alive_m = g.astype(bool)
        img_c[:,:,0] = np.where(alive_m, np.clip(r_*255,0,255).astype(np.uint8), 0)
        img_c[:,:,1] = np.where(alive_m, np.clip(g_*255,0,255).astype(np.uint8), 0)
        img_c[:,:,2] = np.where(alive_m, np.clip(b_*255,0,255).astype(np.uint8), 0)
        if trail_surf is not None:
            surf.blit(trail_surf, (0, 0))
        small = pygame.surfarray.make_surface(img_c.transpose(1,0,2))
        surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))),
                  (int(vx), int(vy)))
        return

    # Pixel-buffer modes (all vectorized or near-vectorized)
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    prev = u.history[-1] if len(u.history) > 0 else g
    gen = u.generation

    alive_mask = g.astype(bool)
    age_norm   = np.clip(age_grid / 80.0, 0, 1)

    if mode == "classic":
        t = np.clip(age_grid / 60.0, 0, 1)
        for c in range(3):
            img[:,:,c] = np.where(alive_mask,
                (color1[c] + (color2[c]-color1[c])*t).astype(np.uint8), 0)

    elif mode == "heat":
        t = age_norm
        # neighbour count vectorized
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        img[:,:,0] = np.where(alive_mask, (255*t).clip(0,255), 0).astype(np.uint8)
        img[:,:,1] = np.where(alive_mask, (50+150*(nv/8)).clip(0,255), 0).astype(np.uint8)
        img[:,:,2] = np.where(alive_mask, (200*(1-t)).clip(0,255), 0).astype(np.uint8)

    elif mode == "age":
        t = np.clip(age_grid / 100.0, 0, 1)
        img[:,:,0] = np.where(alive_mask, (60+195*t).clip(0,255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, (234-120*t).clip(0,255).astype(np.uint8), 0)
        img[:,:,2] = np.where(alive_mask, 234, 0)

    elif mode == "velocity":
        born  = alive_mask & ~prev.astype(bool)
        died  = ~alive_mask & prev.astype(bool)
        stay  = alive_mask & prev.astype(bool)
        img[born]  = (74, 222, 128)
        img[stay]  = color1
        img[died]  = (248, 113, 113)

    elif mode == "nebula":
        for c in range(3):
            img[:,:,c] = np.where(alive_mask, min(255, int(color1[c]*1.2)), 0)

    elif mode == "plasma":
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        # Fully vectorized HSV→RGB via piecewise numpy (no per-pixel loop)
        hue = (nv / 8.0 * 280.0 + gen * 3.0 + age_grid.astype(np.float32) * 2.0) % 360.0
        h6  = hue / 60.0
        hi  = h6.astype(np.int32) % 6
        f   = h6 - np.floor(h6)
        v   = np.full_like(hue, 0.9)
        s_  = np.ones_like(hue)
        p   = v * (1 - s_)
        q   = v * (1 - s_ * f)
        t_  = v * (1 - s_ * (1 - f))
        r_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[v,q,p,p,t_,v])
        g_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[t_,v,v,q,p,p])
        b_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[p,p,t_,v,v,q])
        img[:,:,0] = np.where(alive_mask, np.clip(r_*255,0,255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, np.clip(g_*255,0,255).astype(np.uint8), 0)
        img[:,:,2] = np.where(alive_mask, np.clip(b_*255,0,255).astype(np.uint8), 0)

    elif mode == "aurora":
        t = gen * 0.05
        yy, xx = np.meshgrid(np.arange(GRID_H), np.arange(GRID_W), indexing='ij')
        wave  = np.sin(xx*0.15+t).astype(np.float32)*0.5+0.5
        wave2 = np.cos(yy*0.12-t*0.7).astype(np.float32)*0.5+0.5
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        # Vectorized HSV: hue from waves+neighbours, fixed sat≈0.85, lit from age+wave
        hue = (wave*120.0 + wave2*80.0 + nv*30.0 + t*20.0) % 360.0
        sat = np.clip(0.8 + wave2*0.2, 0, 1)
        lit = np.clip(0.40 + age_norm*0.30 + wave*0.15, 0, 1)
        h6  = hue / 60.0
        hi  = h6.astype(np.int32) % 6
        f   = (h6 - np.floor(h6)).astype(np.float32)
        p   = lit * (1 - sat)
        q   = lit * (1 - sat * f)
        t_  = lit * (1 - sat * (1 - f))
        r_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[lit,q,p,p,t_,lit])
        g_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[t_,lit,lit,q,p,p])
        b_  = np.select([hi==0,hi==1,hi==2,hi==3,hi==4,hi==5],[p,p,t_,lit,lit,q])
        img[:,:,0] = np.where(alive_mask, np.clip(r_*255,0,255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, np.clip(g_*255,0,255).astype(np.uint8), 0)
        img[:,:,2] = np.where(alive_mask, np.clip(b_*255,0,255).astype(np.uint8), 0)

    elif mode == "quantum":
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        prob = nv / 8.0
        img[:,:,0] = np.where(alive_mask, (50+prob*200).clip(0,255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, (100+prob*155).clip(0,255).astype(np.uint8), 0)
        img[:,:,2] = np.where(alive_mask, 255, 0)

    elif mode == "starfield":
        yy, xx = np.meshgrid(np.arange(GRID_H), np.arange(GRID_W), indexing='ij')
        phase = (xx*7 + yy*13 + gen*2) * 0.11
        twinkle = (0.6 + 0.4*np.sin(phase)).astype(np.float32)
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        warmth = nv / 8.0
        img[:,:,0] = np.where(alive_mask, ((180+75*warmth)*twinkle).clip(0,255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, ((180+75*warmth*0.8)*twinkle).clip(0,255).astype(np.uint8), 0)
        img[:,:,2] = np.where(alive_mask, ((255-60*warmth)*twinkle).clip(0,255).astype(np.uint8), 0)

    # ── NEW RENDER MODES ────────────────────────────────────────────────────
    elif mode == "lava":
        # Deep reds/oranges, older cells glow brighter like cooling lava
        t = age_norm
        yy, xx = np.meshgrid(np.arange(GRID_H), np.arange(GRID_W), indexing='ij')
        flow = np.sin(xx*0.08 + yy*0.05 + gen*0.03).astype(np.float32) * 0.5 + 0.5
        img[:,:,0] = np.where(alive_mask, np.clip(180 + 75*flow, 0, 255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, np.clip(20 + 100*t*(1-flow*0.5), 0, 255).astype(np.uint8), 0)
        img[:,:,2] = np.where(alive_mask, np.clip(5*flow, 0, 30).astype(np.uint8), 0)

    elif mode == "void":
        # Inverted deep-space: dead cells have faint nebula, alive cells are black holes
        yy, xx = np.meshgrid(np.arange(GRID_H), np.arange(GRID_W), indexing='ij')
        nebula_r = np.clip(np.sin(xx*0.04 + gen*0.01)*60 + 30, 0, 90).astype(np.uint8)
        nebula_b = np.clip(np.cos(yy*0.06 - gen*0.008)*80 + 60, 0, 140).astype(np.uint8)
        dead_mask = ~alive_mask
        img[:,:,0] = np.where(dead_mask, nebula_r, 0)
        img[:,:,1] = np.where(dead_mask, 0, 0)
        img[:,:,2] = np.where(dead_mask, nebula_b, 0)
        # Alive cells: dim white event-horizon glow
        img[:,:,0] += np.where(alive_mask, 15, 0).astype(np.uint8)
        img[:,:,1] += np.where(alive_mask, 15, 0).astype(np.uint8)
        img[:,:,2] += np.where(alive_mask, 20, 0).astype(np.uint8)

    elif mode == "bioluminescent":
        # Cyan-green ocean glow, pulses with generation
        pulse = (math.sin(gen * 0.07) * 0.5 + 0.5)
        nv = (np.roll(g,-1,0)+np.roll(g,1,0)+np.roll(g,-1,1)+np.roll(g,1,1)+
              np.roll(np.roll(g,-1,0),-1,1)+np.roll(np.roll(g,-1,0),1,1)+
              np.roll(np.roll(g,1,0),-1,1)+np.roll(np.roll(g,1,0),1,1)).astype(np.float32)
        cluster = (nv / 8.0)
        glow = age_norm * 0.6 + cluster * 0.4
        bg_blue = 8
        img[:,:,0] = np.where(alive_mask, np.clip(10 + glow*40*pulse, 0, 255).astype(np.uint8), 0)
        img[:,:,1] = np.where(alive_mask, np.clip(180 + glow*75, 0, 255).astype(np.uint8), bg_blue)
        img[:,:,2] = np.where(alive_mask, np.clip(160 + glow*95*pulse, 0, 255).astype(np.uint8), bg_blue+4)

    # Scale pixel array to canvas
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    scaled = pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs)))
    surf.blit(scaled, (int(vx), int(vy)))


def render_smoothlife(surf: pygame.Surface, sl: SmoothLife, vx, vy, vs, gen=0):
    """Render SmoothLife field with a purple-cyan gradient."""
    cs = CELL * vs
    f = sl.field
    r = np.clip(f * 80,  0, 255).astype(np.uint8)
    g_ch = np.clip(f * 40, 0, 255).astype(np.uint8)
    b = np.clip(f * 255, 0, 255).astype(np.uint8)
    # Add pulsing hue shift
    pulse = math.sin(gen * 0.04) * 0.3 + 0.7
    r = np.clip(r + (b * 0.4 * pulse).astype(np.uint8), 0, 255).astype(np.uint8)
    img = np.stack([r, g_ch, b], axis=-1)
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))


def render_rd(surf, rd: ReactionDiffusion, vx, vy, vs):
    cs = CELL * vs
    v = np.clip(rd.A - rd.B, 0, 1)
    r = np.where(v<0.5, 0, ((v-0.5)*2*200)).astype(np.uint8)
    g = (v*160).astype(np.uint8)
    b = np.where(v<0.5, v*2*255, 255*(1-(v-0.5)*2)).clip(0,255).astype(np.uint8)
    img = np.stack([r,g,b], axis=-1)
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx),int(vy)))


def render_brian(surf, sim: BriansBrain, vx, vy, vs):
    """Vectorized Brian's Brain renderer."""
    cs = CELL * vs
    g = sim.grid
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    img[g == 1] = (255, 255, 255)
    img[g == 2] = (85, 104, 204)
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))


def render_wire(surf, sim: WireWorld, vx, vy, vs):
    """Vectorized WireWorld renderer."""
    cs = CELL * vs
    g = sim.grid
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    img[g == 1] = (232, 176, 78)   # conductor
    img[g == 2] = (0, 191, 255)    # electron head
    img[g == 3] = (255, 107, 107)  # electron tail
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))


def render_langton(surf, sim: LangtonAnt, vx, vy, vs):
    """Vectorized Langton Ant renderer."""
    cs = CELL * vs
    n_states = max(2, len(sim.rule))
    g = sim.grid
    # Build colour LUT for states
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    for state_val in range(1, n_states):
        t = state_val / (n_states - 1)
        hue = t * 280
        col = _hsv_to_rgb(hue, 0.8, 0.7)
        img[g == state_val] = col
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))
    # Draw ants as yellow squares on top
    for ant in sim.ants:
        px = int(vx + ant["x"]*cs); py = int(vy + ant["y"]*cs)
        pygame.draw.rect(surf, (255, 255, 0), (px, py, max(2, int(cs)), max(2, int(cs))))


def render_cyclic(surf, sim: CyclicCA, vx, vy, vs):
    """Vectorized Cyclic CA renderer."""
    cs = CELL * vs
    g = sim.grid
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    for state_val in range(1, sim.states):
        hue = (state_val / sim.states) * 360
        col = _hsv_to_rgb(hue, 0.85, 0.65)
        img[g == state_val] = col
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))


def render_elem(surf, sim: ElementaryCA, vx, vy, vs):
    """Vectorized Elementary CA renderer."""
    cs = CELL * vs
    g = sim.grid
    yy = np.arange(GRID_H, dtype=np.float32) / GRID_H
    t = yy[:, np.newaxis] * np.ones((1, GRID_W), dtype=np.float32)
    alive = g.astype(bool)
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    img[:,:,0] = np.where(alive, (102 + 153*t).clip(0,255).astype(np.uint8), 0)
    img[:,:,1] = np.where(alive, (126 + 129*t).clip(0,255).astype(np.uint8), 0)
    img[:,:,2] = np.where(alive, (234 + 21*t).clip(0,255).astype(np.uint8), 0)
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))


def render_forest(surf, sim: ForestFire, vx, vy, vs):
    """Vectorized Forest Fire renderer."""
    cs = CELL * vs
    g = sim.grid
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    img[g == 1] = (22, 163, 74)   # tree
    img[g == 2] = (249, 115, 22)  # fire
    small = pygame.surfarray.make_surface(img.transpose(1,0,2))
    surf.blit(pygame.transform.scale(small, (int(GRID_W*cs), int(GRID_H*cs))), (int(vx), int(vy)))


# =============================================================================
# UI HELPERS
# =============================================================================

def draw_text(surf, font, text, x, y, color=TEXT, max_width=None):
    if max_width:
        words = text.split()
        line = ""
        for w in words:
            test = (line+" "+w).strip()
            if font.size(test)[0] <= max_width:
                line = test
            else:
                surf.blit(font.render(line, True, color), (x, y))
                y += font.get_linesize()
                line = w
        if line:
            surf.blit(font.render(line, True, color), (x, y))
    else:
        surf.blit(font.render(text, True, color), (x, y))

def draw_button(surf, font, text, rect, active=False,
                bg=None, fg=None, hover=False):
    bx, by, bw, bh = rect
    base_bg = bg or (ACCENT if active else (30, 35, 50))
    if hover: base_bg = tuple(min(255,c+20) for c in base_bg)
    pygame.draw.rect(surf, base_bg, rect, border_radius=4)
    pygame.draw.rect(surf, ACCENT if active else BORDER, rect, 1, border_radius=4)
    label = font.render(text, True, fg or (TEXT if not active else (255,255,255)))
    surf.blit(label, (bx + (bw-label.get_width())//2, by + (bh-label.get_height())//2))

def draw_panel_section(surf, font_sm, title, x, y, w):
    pygame.draw.line(surf, BORDER, (x, y), (x+w, y))
    label = font_sm.render(title.upper(), True, ACCENT)
    surf.blit(label, (x+4, y+3))
    return y + 18

def draw_slider(surf, font_sm, label, val, min_v, max_v, rect, value_text=None):
    rx, ry, rw, rh = rect
    draw_text(surf, font_sm, label, rx, ry-13, TEXT2)
    pygame.draw.rect(surf, (30,35,50), rect, border_radius=3)
    t = (val-min_v)/(max_v-min_v) if max_v>min_v else 0
    fw = int(rw*t)
    if fw > 0:
        pygame.draw.rect(surf, ACCENT, (rx, ry, fw, rh), border_radius=3)
    pygame.draw.rect(surf, BORDER, rect, 1, border_radius=3)
    vt = value_text or str(val)
    vl = font_sm.render(vt, True, TEXT)
    surf.blit(vl, (rx+rw+4, ry+(rh-vl.get_height())//2))
    return rect

def draw_stat_box(surf, font_sm, label, value, rect, val_color=ACCENT):
    pygame.draw.rect(surf, (0,0,0), rect, border_radius=3)
    pygame.draw.rect(surf, BORDER, rect, 1, border_radius=3)
    lbl = font_sm.render(label, True, TEXT3)
    surf.blit(lbl, (rect[0]+4, rect[1]+3))
    val_surf = font_sm.render(str(value), True, val_color)
    surf.blit(val_surf, (rect[0]+4, rect[1]+14))

def draw_mini_graph(surf, data, rect, color, max_v=None):
    rx, ry, rw, rh = rect
    pygame.draw.rect(surf, (0,0,0), rect)
    if len(data) < 2: return
    mx = max_v or max(data) or 1
    pts = [(rx + int(i/(len(data)-1)*rw), ry+rh - int(v/mx*rh*0.9))
           for i,v in enumerate(data)]
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, 1)


# =============================================================================
# AI CLIENT
# =============================================================================

class AIClient:
    def __init__(self):
        self.client = anthropic.Anthropic() if _AI_AVAILABLE else None
        self._lock  = threading.Lock()
        self.pending_result: Optional[str] = None
        self.pending_cmd:    Optional[dict] = None
        self.is_busy = False

    def call_async(self, prompt: str, system: str, on_done):
        """Fire-and-forget async call; calls on_done(text) on completion."""
        def _run():
            with self._lock:
                self.is_busy = True
            try:
                msg = self.client.messages.create(
                    model="claude-sonnet-4-6",   # upgraded from 4-5
                    max_tokens=1000,
                    system=system,
                    messages=[{"role":"user","content":prompt}]
                )
                text = msg.content[0].text if msg.content else ""
                on_done(text)
            except Exception as e:
                on_done(f"[Error: {e}]")
            finally:
                with self._lock:
                    self.is_busy = False
        threading.Thread(target=_run, daemon=True).start()


# =============================================================================
# MAIN APPLICATION
# =============================================================================

BRUSH_SHAPES = ["circle", "square", "diamond"]

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("⚛ CELLULAR AUTOMATON EXPLORER — ULTRAVERSE v10")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
        self.clock  = pygame.time.Clock()

        # Fonts
        mono = pygame.font.match_font("consolas,couriernew,dejavusansmono,monospace")
        self.font_lg  = pygame.font.Font(mono, 15)
        self.font_md  = pygame.font.Font(mono, 12)
        self.font_sm  = pygame.font.Font(mono, 10)

        # Canvas surface (off-screen)
        self.canvas = pygame.Surface((CANVAS_W, CANVAS_H))

        # View transform
        self.vx  = 0.0; self.vy = 0.0; self.vs = 1.0
        self._fit_view()

        # Simulation state
        self.sim_mode    = "gol"
        self.render_mode = "classic"
        self.render_idx  = 0
        self.is_running  = False
        self.speed       = 10
        self.steps_frame = 1

        self.u      = UniverseState()
        self.smooth = None
        self.rd     = None
        self.brian  = None
        self.wire   = None
        self.lang   = None
        self.cyclic = None
        self.elem   = ElementaryCA(110)
        self.forest = ForestFire()

        self.age_grid   = np.zeros((GRID_H,GRID_W), dtype=np.int32)
        self.undo_stack: list = []

        # Trail / ghost overlay
        self.show_trails  = False
        self.trail_surf   = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
        self.trail_surf.fill((0,0,0,0))

        # Drawing
        self.draw_mode   = "draw"
        self.brush_size  = 1
        self.brush_shape = "circle"   # NEW
        self.brush_idx   = 0
        self.is_drawing  = False
        self.draw_start  = None
        self.cell_color1 = (102,126,234)
        self.cell_color2 = (118,75,162)
        self.show_grid   = False

        # Analytics
        self.orbit_period: Optional[int] = None
        self.hash_history: list = []
        self.display_fps  = 0
        self._last_tick   = time.time()
        self._fps_acc     = 0.0
        self._fps_frames  = 0

        # AI
        self.ai = AIClient()
        self.ai_response   = ""
        self.ai_busy       = False

        # AI-Driven pilot
        self.ai_driven_on       = False
        self.ai_driven_goal     = "explore"
        self.ai_driven_interval = 30.0
        self.ai_driven_last     = 0.0
        self.ai_driven_log: list[str] = []
        self.ai_driven_narrative= ""
        self.ai_driven_allow_rules  = True
        self.ai_driven_allow_stamps = True
        self.ai_driven_allow_speed  = True

        # Langton n_ants control (was class-level, now UI-exposed)
        self.langton_n_ants = 1
        self.langton_rule   = "RL"

        # UI state
        self.active_tab   = "stats"
        self.hover_btn    = None
        self.mouse_pos    = (0,0)
        self._notif_msg   = ""
        self._notif_until = 0.0

        # Load default preset
        self._load_preset("gosperGun")
        self.u.birth_rules = [3]; self.u.survival_rules = [2,3]

    # ─── View ─────────────────────────────────────────────────────────────────

    def _fit_view(self):
        sx = CANVAS_W / (GRID_W*CELL)
        sy = CANVAS_H / (GRID_H*CELL)
        self.vs = min(sx,sy)*0.95
        self.vx = (CANVAS_W - GRID_W*CELL*self.vs)/2
        self.vy = (CANVAS_H - GRID_H*CELL*self.vs)/2

    def _zoom(self, factor, cx=None, cy=None):
        cx = cx or CANVAS_W/2; cy = cy or CANVAS_H/2
        self.vx = cx + (self.vx-cx)*factor
        self.vy = cy + (self.vy-cy)*factor
        self.vs *= factor

    def _screen_to_world(self, sx, sy):
        cs = CELL*self.vs
        return int((sx-CANVAS_X-self.vx)/cs), int((sy-CANVAS_Y-self.vy)/cs)

    # ─── Simulation step ──────────────────────────────────────────────────────

    def _tick(self):
        mode = self.sim_mode
        for _ in range(self.steps_frame):
            if mode == "gol":
                births, deaths, living = self.u.step()
                self.age_grid[self.u.grid==1] += 1
                self.age_grid[self.u.grid==0]  = 0
                self._check_orbit()
            elif mode == "smooth":
                if self.smooth: self.smooth.step()
                self.u.generation += 1
            elif mode == "rd":
                if self.rd: self.rd.step()
                self.u.generation += 1
            elif mode == "brian":
                if self.brian: self.brian.step()
                self.u.generation += 1
            elif mode == "wire":
                if self.wire: self.wire.step()
                self.u.generation += 1
            elif mode == "langton":
                if self.lang:
                    for _ in range(5): self.lang.step()
                self.u.generation += 1
            elif mode == "cyclic":
                if self.cyclic: self.cyclic.step()
                self.u.generation += 1
            elif mode == "elem":
                self.elem.step()
                self.u.generation += 1
            elif mode == "forest":
                self.forest.step()
                self.u.generation += 1

    def _check_orbit(self):
        """Zobrist-style XOR hash for collision-resistant orbit detection."""
        # Each cell position has a random 64-bit key; hash = XOR of keys for live cells
        if not hasattr(self, '_zobrist_table'):
            rng = np.random.default_rng(42)
            self._zobrist_table = rng.integers(1, 2**62, size=(GRID_H, GRID_W), dtype=np.int64)
        live_keys = self._zobrist_table[self.u.grid == 1]
        h = int(np.bitwise_xor.reduce(live_keys)) if len(live_keys) > 0 else 0
        try:
            idx = self.hash_history.index(h)
            self.orbit_period = len(self.hash_history) - idx
        except ValueError:
            self.orbit_period = None
        self.hash_history.append(h)
        if len(self.hash_history) > 200:
            self.hash_history.pop(0)

    # ─── Presets ──────────────────────────────────────────────────────────────

    def _load_preset(self, name, ox=None, oy=None):
        cx = ox if ox is not None else GRID_W//2
        cy = oy if oy is not None else GRID_H//2
        PATTERNS = {
            "glider":       [[0,1],[1,2],[2,0],[2,1],[2,2]],
            "gosperGun":    [[0,24],[1,22],[1,24],[2,12],[2,13],[2,20],[2,21],[2,34],[2,35],
                             [3,11],[3,15],[3,20],[3,21],[3,34],[3,35],[4,0],[4,1],[4,10],[4,16],[4,20],[4,21],
                             [5,0],[5,1],[5,10],[5,14],[5,16],[5,17],[5,22],[5,24],[6,10],[6,16],[6,24],
                             [7,11],[7,15],[8,12],[8,13]],
            "pulsar":       [[2,4],[2,5],[2,6],[2,10],[2,11],[2,12],[4,2],[4,7],[4,9],[4,14],
                             [5,2],[5,7],[5,9],[5,14],[6,2],[6,7],[6,9],[6,14],[7,4],[7,5],[7,6],
                             [7,10],[7,11],[7,12],[9,4],[9,5],[9,6],[9,10],[9,11],[9,12],
                             [10,2],[10,7],[10,9],[10,14],[11,2],[11,7],[11,9],[11,14],
                             [12,2],[12,7],[12,9],[12,14],[14,4],[14,5],[14,6],[14,10],[14,11],[14,12]],
            "acorn":        [[0,1],[1,3],[2,0],[2,1],[2,4],[2,5],[2,6]],
            "rPentomino":   [[0,1],[0,2],[1,0],[1,1],[2,1]],
            "blinker":      [[0,0],[0,1],[0,2]],
            "glider_small": [[0,1],[1,2],[2,0],[2,1],[2,2]],
            # ── NEW PATTERNS ────────────────────────────────────────────────
            "lwss":         [[0,1],[0,2],[0,3],[0,4],
                             [1,0],[1,4],
                             [2,4],
                             [3,0],[3,3],
                             [4,1],[4,2],[4,3],[4,4]],  # lightweight spaceship
            "pentadecathlon":[[0,2],[1,2],[2,1],[2,3],[3,2],[4,2],[5,2],[6,2],
                              [7,1],[7,3],[8,2],[9,2]],  # period-15 oscillator
            "diehard":      [[0,6],[1,0],[1,1],[2,1],[2,5],[2,6],[2,7]],
            "infinite_grow":[[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8],
                             [0,10],[0,11],[0,12],[0,13],[0,14],
                             [0,18],[0,19],[0,20],
                             [0,27],[0,28],[0,29],[0,30],[0,31],[0,32],[0,33],
                             [0,35],[0,36],[0,37],[0,38],[0,39]],  # Turing-like grower
            # ── NEW IN V10 ──────────────────────────────────────────────────
            "bheptomino":   [[0,1],[0,2],[1,0],[1,1],[2,1],[2,2],[2,3]],
            "hammerhead":   [[0,2],[0,3],[1,0],[1,4],[2,4],[3,0],[3,3],[3,4],
                             [4,1],[4,2],[4,3],[4,4],[5,2],[5,3],
                             [6,1],[6,4],[7,0],[7,4],[8,0],[8,3],[9,1],[9,2]],
            "copperhead":   [[0,2],[0,3],[1,0],[1,1],[1,4],[1,5],
                             [2,0],[2,1],[2,4],[2,5],[3,2],[3,3],
                             [5,2],[5,3],[6,1],[6,4],[7,0],[7,5],
                             [8,0],[8,5],[9,1],[9,2],[9,3],[9,4]],
        }
        if name in ("random15","random30","random50"):
            pct = 0.15 if "15" in name else 0.30 if "30" in name else 0.50
            self.u.grid = (np.random.random((GRID_H,GRID_W)) < pct).astype(np.uint8)
        elif name in PATTERNS:
            for dy, dx in PATTERNS[name]:
                ny, nx = cy+dy, cx+dx
                if 0 <= ny < GRID_H and 0 <= nx < GRID_W:
                    self.u.grid[ny, nx] = 1
        self.u.history.clear(); self.u.generation = 0
        self.age_grid[:] = 0; self.hash_history.clear()

    # ─── Paint ────────────────────────────────────────────────────────────────

    def _paint(self, wx, wy, val):
        bs = self.brush_size
        shape = self.brush_shape
        for dy in range(-bs+1, bs):
            for dx in range(-bs+1, bs):
                if shape == "circle":
                    if math.sqrt(dx*dx+dy*dy) >= bs: continue
                elif shape == "diamond":
                    if abs(dx) + abs(dy) >= bs: continue
                # square: no filter
                nx, ny = wx+dx, wy+dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    self.u.grid[ny, nx] = val

    def _save_undo(self):
        self.undo_stack.append(self.u.grid.copy())
        if len(self.undo_stack) > 30: self.undo_stack.pop(0)

    def _undo(self):
        if self.undo_stack:
            self.u.grid = self.undo_stack.pop()

    def _save_grid(self):
        """Save current GoL grid to a timestamped .npy file."""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"ca_save_{ts}.npy"
        np.save(fname, self.u.grid)
        self._notify(f"💾 Saved → {fname}")

    def _load_grid(self):
        """Load the most recent ca_save_*.npy file in cwd."""
        import glob
        files = sorted(glob.glob("ca_save_*.npy"))
        if not files:
            self._notify("⚠ No save files found (ca_save_*.npy)")
            return
        fname = files[-1]
        try:
            loaded = np.load(fname)
            if loaded.shape == (GRID_H, GRID_W):
                self._save_undo()
                self.u.grid = loaded.astype(np.uint8)
                self.age_grid[:] = 0
                self._notify(f"📂 Loaded ← {fname}")
            else:
                self._notify(f"⚠ Wrong shape {loaded.shape}, expected ({GRID_H},{GRID_W})")
        except Exception as e:
            self._notify(f"⚠ Load error: {e}")

    def _screenshot(self):
        """Save a PNG screenshot of the current canvas."""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"ca_screenshot_{ts}.png"
        pygame.image.save(self.screen, fname)
        self._notify(f"📸 Screenshot → {fname}")

    def _notify(self, msg: str, duration: float = 3.0):
        """Show a temporary notification banner."""
        self._notif_msg  = msg
        self._notif_until = time.time() + duration

    # ─── Trail overlay ────────────────────────────────────────────────────────

    def _update_trail(self):
        """Decay the trail surface then stamp current live cells."""
        if not self.show_trails: return
        # Fade existing trail
        fade_arr = pygame.surfarray.pixels_alpha(self.trail_surf)
        fade_arr[:] = (fade_arr * TRAIL_DECAY).astype(np.uint8)
        del fade_arr  # release lock

        # Stamp current cells as dim white dots
        cs = CELL * self.vs
        g = self.u.grid
        ys, xs = np.where(g == 1)
        for y, x in zip(ys, xs):
            px = int(self.vx + x*cs); py = int(self.vy + y*cs)
            sz = max(1, int(cs))
            if 0 <= px < CANVAS_W and 0 <= py < CANVAS_H:
                pygame.draw.rect(self.trail_surf, (180, 180, 255, 60), (px, py, sz, sz))

    # ─── AI helpers ───────────────────────────────────────────────────────────

    def _get_snap(self):
        living = int(self.u.grid.sum()) if self.sim_mode=="gol" else 0
        return {
            "sim_mode": self.sim_mode,
            "render_mode": self.render_mode,
            "rules": f"B{''.join(map(str,self.u.birth_rules))}/S{''.join(map(str,self.u.survival_rules))}",
            "generation": self.u.generation,
            "population": living,
            "density_pct": f"{living/(GRID_W*GRID_H)*100:.1f}%",
            "orbit_period": self.orbit_period,
            "births": self.u.birth_hist[-1] if self.u.birth_hist else 0,
            "deaths": self.u.death_hist[-1] if self.u.death_hist else 0,
        }

    def _ai_analyse(self, prompt_key):
        if not _AI_AVAILABLE or self.ai.is_busy: return
        snap = self._get_snap()
        prompts = {
            "predict": f"State:\n{json.dumps(snap,indent=2)}\nPredict the next 50-100 generations. Be specific: will it stabilise, die, explode, or oscillate?",
            "name":    f"Give this CA pattern a memorable creative name:\n{json.dumps(snap,indent=2)}\nFormat: NAME: [name]\nREASON: [one sentence]",
            "story":   f"Write a short poetic narrative (3-4 sentences) describing this CA as a living world:\n{json.dumps(snap,indent=2)}",
            "classify":f"Classify this CA using Wolfram's four classes (I-IV). Comment on emergent behaviour:\n{json.dumps(snap,indent=2)}",
        }
        prompt = prompts.get(prompt_key, prompts["predict"])
        self.ai_response = "⏳ Thinking..."
        self.ai_busy = True
        self.ai.call_async(prompt, "You are a cellular automaton expert. Be concise and insightful.",
                           lambda t: self._on_ai_done(t))

    def _on_ai_done(self, text):
        self.ai_response = text
        self.ai_busy = False

    # ─── AI-Driven pilot ──────────────────────────────────────────────────────

    def _ai_driven_log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.ai_driven_log.insert(0, f"[{ts}] {msg}")
        if len(self.ai_driven_log) > 40: self.ai_driven_log.pop()

    def _ai_driven_tick(self):
        if not _AI_AVAILABLE or self.ai.is_busy: return
        snap = self._get_snap()
        snap["goal"] = self.ai_driven_goal
        snap["allow_rules"]  = self.ai_driven_allow_rules
        snap["allow_stamps"] = self.ai_driven_allow_stamps
        snap["allow_speed"]  = self.ai_driven_allow_speed
        snap["current_speed"]= self.speed

        system = """You are an AI pilot controlling a cellular automaton. Respond ONLY with valid JSON (no markdown):
{
  "narrative": "1-2 sentence poetic observation",
  "actions": [
    {"type":"set_rules","birth":[3],"survival":[2,3],"reason":"..."},
    {"type":"stamp_pattern","pattern":"glider|gosperGun|pulsar|acorn|rPentomino|lwss|pentadecathlon|diehard|infinite_grow|random30|hammerhead|copperhead|bheptomino","reason":"..."},
    {"type":"set_speed","fps":10,"reason":"..."},
    {"type":"add_noise","density":0.05,"reason":"..."},
    {"type":"observe","reason":"..."}
  ],
  "logMessage": "short status line"
}
Goals: explore=try different things, beauty=density 20-40% high entropy, stability=resist extinction,
chaos=max volatility, oscillators=find cyclic patterns, spaceships=moving structures, story=dramatic narrative.
Only include actions allowed by the allow_* flags. Be decisive — pick 1-3 actions."""

        self.ai_driven_log("🔍 Observing...")
        self.ai.call_async(
            f"State:\n{json.dumps(snap,indent=2)}\n\nIssue pilot commands.",
            system,
            lambda t: self._on_driven_done(t)
        )

    def _on_driven_done(self, text):
        try:
            import re
            m = re.search(r'\{[\s\S]*\}', text)
            if not m: raise ValueError("No JSON")
            cmd = json.loads(m.group(0))
            if cmd.get("narrative"):
                self.ai_driven_narrative = cmd["narrative"]
            if cmd.get("logMessage"):
                self.ai_driven_log(cmd["logMessage"])
            for action in cmd.get("actions", []):
                self._execute_ai_action(action)
        except Exception as e:
            self.ai_driven_log(f"⚠ Parse error: {e}")

    def _execute_ai_action(self, action):
        t = action.get("type","observe")
        if t == "set_rules" and self.ai_driven_allow_rules:
            b = [x for x in action.get("birth",[3]) if 0<=x<=8]
            s = [x for x in action.get("survival",[2,3]) if 0<=x<=8]
            self.u.birth_rules = sorted(b)
            self.u.survival_rules = sorted(s)
            self.ai_driven_log(f"📐 Rules → B{''.join(map(str,b))}/S{''.join(map(str,s))}")
        elif t == "stamp_pattern" and self.ai_driven_allow_stamps:
            pat = action.get("pattern","glider")
            px = action.get("x", random.randint(10, GRID_W-20))
            py = action.get("y", random.randint(10, GRID_H-20))
            self._save_undo(); self._load_preset(pat, px, py)
            self.ai_driven_log(f"🖨 Stamped {pat} @ ({px},{py})")
        elif t == "set_speed" and self.ai_driven_allow_speed:
            self.speed = max(1, min(60, int(action.get("fps",10))))
            self.ai_driven_log(f"⚡ Speed → {self.speed} fps")
        elif t == "add_noise":
            self._save_undo()
            d = max(0.01, min(0.2, float(action.get("density",0.05))))
            mask = np.random.random((GRID_H,GRID_W)) < d
            self.u.grid[mask] ^= 1
            self.ai_driven_log(f"〰 Noise {d*100:.0f}%")
        elif t == "invert_region":
            self._save_undo()
            rx = random.randint(0, GRID_W//2)
            ry = random.randint(0, GRID_H//2)
            rw = random.randint(GRID_W//5, GRID_W//2)
            rh = random.randint(GRID_H//5, GRID_H//2)
            self.u.grid[ry:ry+rh, rx:rx+rw] ^= 1
            self.ai_driven_log(f"⬡ Inverted region")
        else:
            self.ai_driven_log(f"👁 {action.get('reason','observing')}")

    # ─── Drawing ──────────────────────────────────────────────────────────────

    def _draw_header(self):
        s = self.screen
        pygame.draw.rect(s, (7,7,26), (0,0,WIN_W,HEADER_H))
        pygame.draw.line(s, ACCENT, (0,HEADER_H-1),(WIN_W,HEADER_H-1),2)
        title = self.font_lg.render("⚛ ULTRAVERSE v10", True, ACCENT)
        s.blit(title, (10, (HEADER_H-title.get_height())//2))
        mode_lbl = self.font_sm.render(
            f"{'▶' if self.is_running else '⏸'} {self.sim_mode.upper()} | "
            f"Gen {self.u.generation} | {self.render_mode} | "
            f"{self.brush_shape[0].upper()}brush | {self.display_fps} fps",
            True, TEXT2)
        s.blit(mode_lbl, (220, (HEADER_H-mode_lbl.get_height())//2))
        if self.ai_driven_on:
            badge = self.font_sm.render("🤖 AI-PILOT ON", True, GREEN)
            s.blit(badge, (WIN_W-PANEL_R-badge.get_width()-10,
                           (HEADER_H-badge.get_height())//2))
        if self.show_trails:
            tbadge = self.font_sm.render("👻 TRAILS", True, ACCENT2)
            s.blit(tbadge, (WIN_W-PANEL_R-tbadge.get_width()-120,
                            (HEADER_H-tbadge.get_height())//2))
        # Notification banner
        if self._notif_msg and time.time() < self._notif_until:
            fade = min(1.0, (self._notif_until - time.time()) / 0.5)
            col = tuple(int(c * fade) for c in (74, 222, 128))
            notif = self.font_sm.render(self._notif_msg, True, col)
            nx = WIN_W // 2 - notif.get_width() // 2
            s.blit(notif, (nx, (HEADER_H - notif.get_height()) // 2))

    def _draw_footer(self):
        s = self.screen
        fy = WIN_H - FOOTER_H
        pygame.draw.rect(s, (4,4,4), (0,fy,WIN_W,FOOTER_H))
        pygame.draw.line(s, BORDER, (0,fy),(WIN_W,fy))
        gw = (WIN_W) // 5
        gh = FOOTER_H - 20
        datasets = [
            (self.u.birth_hist,  "BIRTHS",   GREEN),
            (self.u.death_hist,  "DEATHS",   RED),
            (self.u.entropy_hist,"ENTROPY",  AMBER),
            (self.u.vel_hist,    "VELOCITY", ACCENT),
            (self.u.complex_hist,"COMPLEX",  CYAN),
        ]
        for i,(data,label,col) in enumerate(datasets):
            gx = i*gw
            draw_mini_graph(s, data, (gx,fy+2,gw-2,gh), col)
            lbl = self.font_sm.render(label, True, TEXT3)
            s.blit(lbl, (gx+3, fy+3))

    def _draw_left_panel(self):
        s = self.screen
        pygame.draw.rect(s, PANEL_BG, (0, HEADER_H, PANEL_L, WIN_H-HEADER_H-FOOTER_H))
        pygame.draw.line(s, BORDER, (PANEL_L-1, HEADER_H),(PANEL_L-1,WIN_H-FOOTER_H))
        x, y, w = 6, HEADER_H+6, PANEL_L-12
        y = draw_panel_section(s, self.font_sm, "⚡ SIMULATION", x, y, w)
        y += 4

        sim_labels = [("gol","GoL"),("smooth","SmoothLife"),("rd","React-Diff"),
                      ("brian","Brian"),("wire","Wire"),("langton","Langton"),
                      ("cyclic","Cyclic"),("elem","Elem 1D"),("forest","Forest🔥")]
        btn_w = (w-2)//2
        for i,(key,lbl) in enumerate(sim_labels):
            bx = x + (i%2)*(btn_w+2); by = y + (i//2)*20
            rect = (bx, by, btn_w, 17)
            active = self.sim_mode==key
            hover = self.hover_btn == f"sim_{key}"
            draw_button(s, self.font_sm, lbl, rect, active=active, hover=hover)
        y += (len(sim_labels)//2 + len(sim_labels)%2)*20 + 6

        pp_rect = (x, y, w, 20)
        draw_button(s, self.font_sm, "⏸ Pause" if self.is_running else "▶ Start",
                    pp_rect, active=self.is_running, hover=self.hover_btn=="playpause")
        y += 24
        bw3 = (w-4)//3
        for i,(bid,lbl) in enumerate([("step","Step"),("clear","Clear"),("rand","Rand")]):
            rect = (x+i*(bw3+2), y, bw3, 17)
            draw_button(s, self.font_sm, lbl, rect, hover=self.hover_btn==bid)
        y += 22

        y += 14
        draw_slider(s, self.font_sm, "Speed (fps)", self.speed, 1, 60,
                    (x, y, w-28, 8), f"{self.speed}")
        y += 22
        draw_slider(s, self.font_sm, "Steps/frame", self.steps_frame, 1, 20,
                    (x, y, w-28, 8), f"{self.steps_frame}")
        y += 22

        # Render mode
        y = draw_panel_section(s, self.font_sm, "🎨 RENDER", x, y+4, w)
        y += 2
        rm_labels = [("classic","Classic"),("heat","Heat"),("age","Age"),
                     ("velocity","Velocity"),("nebula","Nebula"),("plasma","Plasma"),
                     ("aurora","Aurora"),("quantum","Quantum"),("crystal","Crystal"),
                     ("starfield","Stars"),("lava","Lava"),("void","Void"),("bioluminescent","BioLum")]
        rm_bw = (w-2)//2
        for i,(key,lbl) in enumerate(rm_labels):
            bx = x + (i%2)*(rm_bw+2); by = y + (i//2)*18
            rect = (bx, by, rm_bw, 15)
            draw_button(s, self.font_sm, lbl, rect,
                        active=self.render_mode==key,
                        hover=self.hover_btn==f"rm_{key}")
        y += (len(rm_labels)//2 + len(rm_labels)%2)*18 + 6

        # Drawing tools
        y = draw_panel_section(s, self.font_sm, "✏️ DRAW", x, y+4, w)
        y += 2
        tool_labels = [("draw","Draw"),("erase","Erase")]
        tbw = (w-2)//2
        for i,(key,lbl) in enumerate(tool_labels):
            rect = (x+i*(tbw+2), y, tbw, 15)
            draw_button(s, self.font_sm, lbl, rect,
                        active=self.draw_mode==key,
                        hover=self.hover_btn==f"tool_{key}")
        y += 18
        # Brush shape buttons
        bsbw = (w-4)//3
        for i,sh in enumerate(BRUSH_SHAPES):
            rect = (x+i*(bsbw+2), y, bsbw, 15)
            draw_button(s, self.font_sm, sh[:4].capitalize(), rect,
                        active=self.brush_shape==sh,
                        hover=self.hover_btn==f"brush_{sh}")
        y += 18
        draw_slider(s, self.font_sm, "Brush size", self.brush_size, 1, 15,
                    (x, y, w-28, 8), f"{self.brush_size}")
        y += 20

        # Presets
        y = draw_panel_section(s, self.font_sm, "🎭 PRESETS", x, y+4, w)
        y += 2
        presets = [("gosperGun","Gosper Gun"),("pulsar","Pulsar"),("acorn","Acorn"),
                   ("glider","Glider"),("lwss","LWSS"),("pentadecathlon","Penta-15"),
                   ("diehard","Diehard"),("infinite_grow","Infinite"),
                   ("hammerhead","Hammer"),("copperhead","Copper"),
                   ("bheptomino","B-hept"),("random30","30% Rand")]
        pbw = (w-2)//2
        for i,(key,lbl) in enumerate(presets):
            bx = x+(i%2)*(pbw+2); by = y+(i//2)*18
            rect = (bx, by, pbw, 15)
            draw_button(s, self.font_sm, lbl, rect, hover=self.hover_btn==f"preset_{key}")
        y += (len(presets)//2 + len(presets)%2)*18 + 4

        # AI Driven toggle
        y = draw_panel_section(s, self.font_sm, "🤖 AI PILOT", x, y+6, w)
        y += 4
        driven_rect = (x, y, w, 20)
        draw_button(s, self.font_sm,
                    "⏹ Stop Pilot" if self.ai_driven_on else "🤖 Start Pilot",
                    driven_rect,
                    active=self.ai_driven_on,
                    bg=(20,60,30) if self.ai_driven_on else None,
                    hover=self.hover_btn=="driven_toggle")

    def _draw_right_panel(self):
        s = self.screen
        rx = WIN_W - PANEL_R
        pygame.draw.rect(s, PANEL_BG, (rx, HEADER_H, PANEL_R, WIN_H-HEADER_H-FOOTER_H))
        pygame.draw.line(s, BORDER, (rx, HEADER_H),(rx, WIN_H-FOOTER_H))
        x, y, w = rx+5, HEADER_H+5, PANEL_R-10

        tabs = [("stats","Stats"),("rules","Rules"),("ai","Analysis"),
                ("driven","AI-Drive"),("info","Info")]
        tab_w = w // len(tabs)
        for i,(key,lbl) in enumerate(tabs):
            rect = (x+i*tab_w, y, tab_w-1, 16)
            draw_button(s, self.font_sm, lbl, rect,
                        active=self.active_tab==key,
                        hover=self.hover_btn==f"tab_{key}")
        y += 20

        if self.active_tab == "stats":
            self._draw_tab_stats(s, x, y, w)
        elif self.active_tab == "rules":
            self._draw_tab_rules(s, x, y, w)
        elif self.active_tab == "ai":
            self._draw_tab_ai(s, x, y, w)
        elif self.active_tab == "driven":
            self._draw_tab_driven(s, x, y, w)
        elif self.active_tab == "info":
            self._draw_tab_info(s, x, y, w)

    def _draw_tab_stats(self, s, x, y, w):
        living = int(self.u.grid.sum()) if self.sim_mode=="gol" else 0
        density = living/(GRID_W*GRID_H)*100
        births  = self.u.birth_hist[-1] if self.u.birth_hist else 0
        deaths  = self.u.death_hist[-1] if self.u.death_hist else 0
        bw = (w-2)//2; bh = 28
        stats = [
            ("GEN",   str(self.u.generation)),
            ("POP",   f"{living:,}"),
            ("DENS",  f"{density:.1f}%"),
            ("BIRTHS",str(births)),
            ("DEATHS",str(deaths)),
            ("FPS",   str(self.display_fps)),
        ]
        for i,(lbl,val) in enumerate(stats):
            bx = x + (i%2)*(bw+2); by = y + (i//2)*(bh+2)
            draw_stat_box(s, self.font_sm, lbl, val, (bx,by,bw,bh))
        y += (len(stats)//2)*(bh+2) + 4

        y = draw_panel_section(s, self.font_sm, "🧬 PATTERN DNA", x, y+2, w)
        y += 4
        if self.sim_mode == "gol" and self.u.generation > 3:
            ent = self.u.entropy_hist[-1]*100 if self.u.entropy_hist else 0
            dna = [
                ("Rules",   f"B{''.join(map(str,self.u.birth_rules))}/S{''.join(map(str,self.u.survival_rules))}"),
                ("Entropy",  f"{ent:.0f}%"),
                ("Period",  str(self.orbit_period) if self.orbit_period else "—"),
                ("Brush",   f"{self.brush_shape}/{self.brush_size}px"),
            ]
            for lbl,val in dna:
                row = self.font_sm.render(f"{lbl}: ", True, TEXT3)
                val_surf = self.font_sm.render(val, True, GREEN)
                s.blit(row, (x, y)); s.blit(val_surf, (x+row.get_width(), y))
                y += 13

        y += 4
        draw_panel_section(s, self.font_sm, "POPULATION", x, y, w)
        y += 16
        # Use birth/death history which is maintained regardless of HISTORY_MAX grid copies
        pop_data = []
        if self.u.birth_hist and self.u.death_hist:
            running = int(self.u.grid.sum())
            # Reconstruct backwards: current pop, then subtract births/add deaths going back
            pop_data = [running]
            for b, d in zip(reversed(self.u.birth_hist[-200:]),
                            reversed(self.u.death_hist[-200:])):
                running = max(0, running - b + d)
                pop_data.append(running)
            pop_data.reverse()
        draw_mini_graph(s, pop_data, (x, y, w, 40), ACCENT, max_v=GRID_W*GRID_H)
        y += 44

        if self.orbit_period:
            badge = self.font_sm.render(f"↻ PERIOD-{self.orbit_period} OSCILLATOR", True, GREEN)
            s.blit(badge, (x, y)); y += 14

        # Langton controls (if in langton mode)
        if self.sim_mode == "langton":
            y = draw_panel_section(s, self.font_sm, "🐜 LANGTON", x, y+4, w)
            y += 4
            draw_text(s, self.font_sm, f"Ants: {self.langton_n_ants}", x, y, TEXT2); y += 13
            bw2 = (w-4)//3
            for i,n in enumerate([1,2,3]):
                rect = (x+i*(bw2+2), y, bw2, 14)
                draw_button(s, self.font_sm, str(n), rect,
                            active=self.langton_n_ants==n,
                            hover=self.hover_btn==f"lang_ants_{n}")
            y += 18
            draw_text(s, self.font_sm, f"Rule: {self.langton_rule}", x, y, TEXT2); y += 13
            rules = ["RL","LR","RRL","LLRR"]
            rbw = (w-4)//2
            for i,r in enumerate(rules):
                rect = (x+(i%2)*(rbw+2), y+(i//2)*15, rbw, 13)
                draw_button(s, self.font_sm, r, rect,
                            active=self.langton_rule==r,
                            hover=self.hover_btn==f"lang_rule_{r}")

    def _draw_tab_rules(self, s, x, y, w):
        y = draw_panel_section(s, self.font_sm, "BIRTH RULES (B)", x, y, w)
        y += 4
        for n in range(9):
            active = n in self.u.birth_rules
            bx = x + (n%5)*(w//5); by = y + (n//5)*20
            rect = (bx+1, by, (w//5)-2, 17)
            draw_button(s, self.font_sm, str(n), rect, active=active,
                        hover=self.hover_btn==f"birth_{n}")
        y += 44
        y = draw_panel_section(s, self.font_sm, "SURVIVAL RULES (S)", x, y+2, w)
        y += 4
        for n in range(9):
            active = n in self.u.survival_rules
            bx = x + (n%5)*(w//5); by = y + (n//5)*20
            rect = (bx+1, by, (w//5)-2, 17)
            draw_button(s, self.font_sm, str(n), rect, active=active,
                        hover=self.hover_btn==f"surv_{n}")
        y += 44
        rule_str = self.font_md.render(
            f"B{''.join(map(str,self.u.birth_rules))}/S{''.join(map(str,self.u.survival_rules))}",
            True, GREEN)
        s.blit(rule_str, (x+(w-rule_str.get_width())//2, y)); y += 20

        y = draw_panel_section(s, self.font_sm, "PRESETS", x, y+4, w)
        y += 4
        rule_presets = [
            ("conway", [3],[2,3],"Conway B3/S23"),
            ("highlife",[3,6],[2,3],"HighLife"),
            ("daynight",[3,6,7,8],[3,4,6,7,8],"Day&Night"),
            ("seeds",  [2],[],"Seeds"),
            ("maze",   [3],[1,2,3,4,5],"Maze"),
            ("coral",  [3],[4,5,6,7,8],"Coral"),
            ("stains", [3,5,7,8],[2,3,5,6,7,8],"Stains"),
        ]
        rpbw = (w-2)//2
        for i,(_,b,sr,lbl) in enumerate(rule_presets):
            bx = x+(i%2)*(rpbw+2); by = y+(i//2)*18
            rect = (bx, by, rpbw, 15)
            active = (self.u.birth_rules == b and self.u.survival_rules == sr)
            draw_button(s, self.font_sm, lbl, rect, active=active, hover=self.hover_btn==f"rule_{lbl}")

    def _draw_tab_ai(self, s, x, y, w):
        y = draw_panel_section(s, self.font_sm, "🤖 AI ANALYSIS", x, y, w)
        y += 4
        if not _AI_AVAILABLE:
            draw_text(s, self.font_sm, "Install 'anthropic' package", x, y, RED)
            return
        btns = [("predict","🔮 Predict"),("name","🏷 Name"),
                ("story","📖 Story"),("classify","🔬 Classify")]
        bw2 = (w-2)//2
        for i,(key,lbl) in enumerate(btns):
            rect = (x+(i%2)*(bw2+2), y+(i//2)*20, bw2, 17)
            draw_button(s, self.font_sm, lbl, rect, hover=self.hover_btn==f"ai_{key}")
        y += (len(btns)//2)*20 + 6
        if self.ai_busy:
            spin = self.font_sm.render("⏳ Calling Claude...", True, AMBER)
            s.blit(spin, (x, y)); y += 16
        if self.ai_response:
            lines = textwrap.wrap(self.ai_response, width=28)
            pygame.draw.rect(s, (10,12,20), (x, y, w, min(len(lines)*12+6, 200)))
            pygame.draw.rect(s, BORDER, (x, y, w, min(len(lines)*12+6, 200)), 1)
            for line in lines[:16]:
                draw_text(s, self.font_sm, line, x+3, y+3, TEXT2)
                y += 12

    def _draw_tab_driven(self, s, x, y, w):
        y = draw_panel_section(s, self.font_sm, "🤖 AI-DRIVEN PILOT", x, y, w)
        y += 4
        if not _AI_AVAILABLE:
            draw_text(s, self.font_sm, "Install 'anthropic' package", x, y, RED)
            return
        status_col = GREEN if self.ai_driven_on else TEXT3
        status_lbl = "● ACTIVE" if self.ai_driven_on else "○ IDLE"
        s.blit(self.font_sm.render(status_lbl, True, status_col), (x, y)); y += 14
        rect = (x, y, w, 20)
        draw_button(s, self.font_sm,
                    "⏹ Stop Pilot" if self.ai_driven_on else "🤖 Start Pilot",
                    rect, active=self.ai_driven_on,
                    bg=(40,80,50) if self.ai_driven_on else None,
                    hover=self.hover_btn=="driven_toggle2")
        y += 24
        draw_text(s, self.font_sm, "Goal:", x, y, TEXT2); y += 13
        goals = ["explore","beauty","stability","chaos","oscillators","spaceships","story"]
        gbw = (w-2)//2
        for i,g in enumerate(goals):
            rect = (x+(i%2)*(gbw+2), y+(i//2)*17, gbw, 14)
            draw_button(s, self.font_sm, g, rect,
                        active=self.ai_driven_goal==g,
                        hover=self.hover_btn==f"goal_{g}")
        y += (len(goals)//2+1)*17 + 4
        draw_slider(s, self.font_sm, "Interval (s)", int(self.ai_driven_interval), 10, 120,
                    (x, y, w-30, 8), f"{int(self.ai_driven_interval)}s")
        y += 20
        toggles = [
            ("allow_rules",  "Allow rule mutations", self.ai_driven_allow_rules),
            ("allow_stamps", "Allow pattern stamps", self.ai_driven_allow_stamps),
            ("allow_speed",  "Allow speed changes",  self.ai_driven_allow_speed),
        ]
        for key, lbl, val in toggles:
            col = GREEN if val else TEXT3
            sym = "■" if val else "□"
            row = self.font_sm.render(f"{sym} {lbl}", True, col)
            s.blit(row, (x, y)); y += 13
        if self.ai_driven_narrative:
            y += 4
            pygame.draw.rect(s, (10,12,25), (x, y, w, 40))
            pygame.draw.rect(s, (40,50,100), (x, y, w, 40), 1)
            for line in textwrap.wrap(self.ai_driven_narrative, 28)[:3]:
                draw_text(s, self.font_sm, line, x+3, y+3, ACCENT2)
                y += 12
            y += 4
        y = draw_panel_section(s, self.font_sm, "PILOT LOG", x, y+4, w)
        y += 4
        for entry in self.ai_driven_log[:12]:
            draw_text(s, self.font_sm, entry[:32], x, y, TEXT3)
            y += 12

    def _draw_tab_info(self, s, x, y, w):
        y = draw_panel_section(s, self.font_sm, "⌨ SHORTCUTS", x, y, w)
        y += 4
        shortcuts = [
            ("Space","Play/Pause"), ("→","Step"), ("C","Clear"),
            ("I","Invert"), ("R","Random"), ("G","Grid"),
            ("T","Toggle Trails"), ("M","Cycle render"),
            ("B","Cycle brush"), ("0","Fit view"),
            ("+/-","Zoom"), ("Ctrl+Z","Undo"),
            ("Ctrl+S","Save grid"), ("Ctrl+O","Load grid"),
            ("Ctrl+P","Screenshot"), ("Esc","Quit"),
            ("Scroll","Zoom/Speed"),("Shift+Scrl","Brush size"),
        ]
        for k,v in shortcuts:
            ks = self.font_sm.render(k, True, ACCENT)
            vs = self.font_sm.render(v, True, TEXT2)
            s.blit(ks, (x, y)); s.blit(vs, (x+65, y)); y += 13

        y += 6
        y = draw_panel_section(s, self.font_sm, "NEW IN V10", x, y, w)
        y += 4
        news = ["Vectorized plasma/aurora","Vectorized crystal mode",
                "Save/Load (Ctrl+S/O)","Screenshot (Ctrl+P)",
                "Brush size via Shift+Scroll","Hammerhead spaceship",
                "Copperhead spaceship","B-heptomino pattern",
                "Stains rule preset","Rule presets show active",
                "Zobrist orbit hash","Pop graph 200 gen history",
                "1s FPS smoothing","Notif banner"]
        for n in news:
            draw_text(s, self.font_sm, f"✓ {n}", x, y, ACCENT2, max_width=w)
            y += 13

    def _draw_canvas(self):
        self.canvas.fill(BG)
        mode = self.sim_mode
        trail = self.trail_surf if self.show_trails else None

        if mode == "gol":
            render_gol(self.canvas, self.u, self.age_grid,
                       self.vx, self.vy, self.vs, self.render_mode,
                       self.cell_color1, self.cell_color2, trail)
        elif mode == "smooth" and self.smooth:
            render_smoothlife(self.canvas, self.smooth, self.vx, self.vy, self.vs, self.u.generation)
        elif mode == "rd" and self.rd:
            render_rd(self.canvas, self.rd, self.vx, self.vy, self.vs)
        elif mode == "brian" and self.brian:
            render_brian(self.canvas, self.brian, self.vx, self.vy, self.vs)
        elif mode == "wire" and self.wire:
            render_wire(self.canvas, self.wire, self.vx, self.vy, self.vs)
        elif mode == "langton" and self.lang:
            render_langton(self.canvas, self.lang, self.vx, self.vy, self.vs)
        elif mode == "cyclic" and self.cyclic:
            render_cyclic(self.canvas, self.cyclic, self.vx, self.vy, self.vs)
        elif mode == "elem":
            render_elem(self.canvas, self.elem, self.vx, self.vy, self.vs)
        elif mode == "forest":
            render_forest(self.canvas, self.forest, self.vx, self.vy, self.vs)

        # Grid overlay
        cs = CELL * self.vs
        if self.show_grid and cs >= 4:
            for gx in range(GRID_W+1):
                px = int(self.vx + gx*cs)
                pygame.draw.line(self.canvas, (20,20,20), (px,int(self.vy)), (px,int(self.vy+GRID_H*cs)))
            for gy in range(GRID_H+1):
                py = int(self.vy + gy*cs)
                pygame.draw.line(self.canvas, (20,20,20), (int(self.vx),py), (int(self.vx+GRID_W*cs),py))

        self.screen.blit(self.canvas, (CANVAS_X, CANVAS_Y))
        pygame.draw.rect(self.screen, BORDER, (CANVAS_X, CANVAS_Y, CANVAS_W, CANVAS_H), 1)

    # ─── Event handling ───────────────────────────────────────────────────────

    def _set_sim_mode(self, mode):
        self.sim_mode = mode
        if mode == "smooth"  and not self.smooth: self.smooth = SmoothLife()
        if mode == "rd"      and not self.rd:     self.rd = ReactionDiffusion()
        if mode == "brian"   and not self.brian:  self.brian = BriansBrain()
        if mode == "wire"    and not self.wire:   self.wire = WireWorld()
        if mode == "langton" and not self.lang:   self.lang = LangtonAnt(self.langton_n_ants, self.langton_rule)
        if mode == "cyclic"  and not self.cyclic: self.cyclic = CyclicCA()
        if mode == "elem":   self.elem = ElementaryCA(self.elem.rule_num)
        if mode == "forest": self.forest = ForestFire()

    def _toggle_ai_driven(self):
        self.ai_driven_on = not self.ai_driven_on
        if self.ai_driven_on:
            self.ai_driven_log.clear()
            self._ai_driven_log("🤖 AI Pilot activated")
            self.ai_driven_last = time.time()
            if not self.is_running:
                self.is_running = True
        else:
            self._ai_driven_log("⏹ AI Pilot stopped")

    def _update_hover(self):
        mx, my = self.mouse_pos
        self.hover_btn = None
        x, y, w = 6, HEADER_H+6, PANEL_L-12
        sim_labels = ["gol","smooth","rd","brian","wire","langton","cyclic","elem","forest"]
        btn_w = (w-2)//2
        sy = y+4+18
        for i,key in enumerate(sim_labels):
            bx = x+(i%2)*(btn_w+2); by = sy+(i//2)*20
            if bx <= mx < bx+btn_w and by <= my < by+17:
                self.hover_btn = f"sim_{key}"; return

    # ─── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        _sim_acc = 0.0
        _last_t  = time.perf_counter()

        while True:
            now = time.perf_counter()
            dt  = now - _last_t
            _last_t = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                elif event.type == pygame.KEYDOWN:
                    self._on_key(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_pos = event.pos
                    if event.button in (1,3):
                        self._handle_click(event.pos, event.button)
                        self.is_drawing = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_drawing = False
                    self.draw_start = None

                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
                    self._update_hover()
                    mx, my = event.pos
                    if self.is_drawing and self.sim_mode=="gol":
                        if (CANVAS_X <= mx < CANVAS_X+CANVAS_W and
                            CANVAS_Y <= my < CANVAS_Y+CANVAS_H):
                            wx, wy = self._screen_to_world(mx, my)
                            if 0 <= wx < GRID_W and 0 <= wy < GRID_H:
                                val = 0 if self.draw_mode=="erase" else 1
                                self._paint(wx, wy, val)

                elif event.type == pygame.MOUSEWHEEL:
                    mx, my = self.mouse_pos
                    shift = event.mod & pygame.KMOD_SHIFT if hasattr(event, 'mod') else False
                    # Shift+scroll on canvas → brush size
                    if CANVAS_X <= mx < CANVAS_X+CANVAS_W and shift:
                        self.brush_size = max(1, min(15, self.brush_size + event.y))
                    elif CANVAS_X <= mx < CANVAS_X+CANVAS_W:
                        factor = 1.12 if event.y > 0 else 0.89
                        self._zoom(factor, mx-CANVAS_X, my-CANVAS_Y)
                    elif mx < PANEL_L:
                        # Scroll on left panel = adjust speed
                        self.speed = max(1, min(60, self.speed + event.y))

                elif event.type == pygame.VIDEORESIZE:
                    pass

            if self.is_running:
                _sim_acc += dt
                tick_interval = 1.0 / max(1, self.speed)
                while _sim_acc >= tick_interval:
                    self._tick()
                    _sim_acc -= tick_interval
                    if self.show_trails and self.sim_mode == "gol":
                        self._update_trail()

            if self.ai_driven_on and not self.ai.is_busy:
                if time.time() - self.ai_driven_last >= self.ai_driven_interval:
                    self.ai_driven_last = time.time()
                    self._ai_driven_tick()

            self._fps_acc += dt; self._fps_frames += 1
            if self._fps_acc >= 1.0:
                self.display_fps = round(self._fps_frames / self._fps_acc)
                self._fps_acc = 0; self._fps_frames = 0

            self.screen.fill(BG)
            self._draw_canvas()
            self._draw_header()
            self._draw_left_panel()
            self._draw_right_panel()
            self._draw_footer()
            pygame.display.flip()
            self.clock.tick(FPS_CAP)

    def _on_key(self, event):
        k = event.key
        ctrl = event.mod & pygame.KMOD_CTRL
        if k == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()
        elif k == pygame.K_SPACE:
            self.is_running = not self.is_running
        elif k == pygame.K_RIGHT:
            self._tick()
        elif k == pygame.K_c and not ctrl:
            self.u.clear(); self.age_grid[:]=0
            self.trail_surf.fill((0,0,0,0))
        elif k == pygame.K_i:
            self.u.grid ^= 1
        elif k == pygame.K_r:
            self._load_preset("random30")
        elif k == pygame.K_g:
            self.show_grid = not self.show_grid
        elif k == pygame.K_t:
            self.show_trails = not self.show_trails
            if not self.show_trails:
                self.trail_surf.fill((0,0,0,0))
        elif k == pygame.K_b:
            self.brush_idx = (self.brush_idx + 1) % len(BRUSH_SHAPES)
            self.brush_shape = BRUSH_SHAPES[self.brush_idx]
        elif k == pygame.K_m:
            self.render_idx = (self.render_idx+1)%len(RENDER_MODES)
            self.render_mode = RENDER_MODES[self.render_idx]
        elif k == pygame.K_0:
            self._fit_view()
        elif k in (pygame.K_PLUS, pygame.K_EQUALS):
            self._zoom(1.2)
        elif k == pygame.K_MINUS:
            self._zoom(0.83)
        elif k == pygame.K_d:
            self.draw_mode = "draw"
        elif k == pygame.K_e:
            self.draw_mode = "erase"
        elif k == pygame.K_z and ctrl:
            self._undo()
        elif k == pygame.K_s and ctrl:
            self._save_grid()
        elif k == pygame.K_o and ctrl:
            self._load_grid()
        elif k == pygame.K_p and ctrl:
            self._screenshot()

    def _handle_click(self, pos, button):
        mx, my = pos
        if mx < PANEL_L:
            self._handle_left_click(mx, my)
        elif mx >= WIN_W - PANEL_R:
            self._handle_right_click(mx, my)
        elif (CANVAS_X <= mx < CANVAS_X+CANVAS_W and
              CANVAS_Y <= my < CANVAS_Y+CANVAS_H):
            wx, wy = self._screen_to_world(mx, my)
            if 0 <= wx < GRID_W and 0 <= wy < GRID_H:
                self._save_undo()
                val = 0 if (self.draw_mode=="erase" or button==3) else 1
                self._paint(wx, wy, val)

    def _handle_left_click(self, mx, my):
        x, y, w = 6, HEADER_H+6, PANEL_L-12

        sim_labels = [("gol","GoL"),("smooth","SmoothLife"),("rd","React-Diff"),
                      ("brian","Brian"),("wire","Wire"),("langton","Langton"),
                      ("cyclic","Cyclic"),("elem","Elem 1D"),("forest","Forest🔥")]
        btn_w = (w-2)//2
        sy = y+4+18
        for i,(key,_) in enumerate(sim_labels):
            bx = x+(i%2)*(btn_w+2); by = sy+(i//2)*20
            if bx <= mx < bx+btn_w and by <= my < by+17:
                self._set_sim_mode(key); return
        sy += (len(sim_labels)//2 + len(sim_labels)%2)*20+6

        if x <= mx < x+w and sy <= my < sy+20:
            self.is_running = not self.is_running; return
        sy += 24

        bw3 = (w-4)//3
        if sy <= my < sy+17:
            if x <= mx < x+bw3: self._tick(); return
            if x+bw3+2 <= mx < x+2*bw3+2:
                self.u.clear(); self.age_grid[:]=0; return
            if x+2*bw3+4 <= mx < x+w: self._load_preset("random30"); return

        # Render modes
        rm_y_offset = sy + 22+14+22+22+4+18+4
        rm_labels = [("classic","Classic"),("heat","Heat"),("age","Age"),
                     ("velocity","Velocity"),("nebula","Nebula"),("plasma","Plasma"),
                     ("aurora","Aurora"),("quantum","Quantum"),("crystal","Crystal"),
                     ("starfield","Stars"),("lava","Lava"),("void","Void"),("bioluminescent","BioLum")]
        rm_bw = (w-2)//2
        for i,(key,_) in enumerate(rm_labels):
            bx = x+(i%2)*(rm_bw+2); by = rm_y_offset+(i//2)*18
            if bx <= mx < bx+rm_bw and by <= my < by+15:
                self.render_mode = key; return
        rm_y_offset += (len(rm_labels)//2 + len(rm_labels)%2)*18+6

        # Draw tools
        tool_y = rm_y_offset+18+4
        bw2 = (w-2)//2
        for i,(key,_) in enumerate([("draw","Draw"),("erase","Erase")]):
            bx = x+i*(bw2+2)
            if bx <= mx < bx+bw2 and tool_y <= my < tool_y+15:
                self.draw_mode = key; return
        tool_y += 18

        # Brush shapes
        bsbw = (w-4)//3
        for i,sh in enumerate(BRUSH_SHAPES):
            bx = x+i*(bsbw+2)
            if bx <= mx < bx+bsbw and tool_y <= my < tool_y+15:
                self.brush_shape = sh
                self.brush_idx = i
                return
        tool_y += 18+20+4

        # Presets
        preset_y = tool_y + 18 + 4
        presets = [("gosperGun","Gosper Gun"),("pulsar","Pulsar"),("acorn","Acorn"),
                   ("glider","Glider"),("lwss","LWSS"),("pentadecathlon","Penta-15"),
                   ("diehard","Diehard"),("infinite_grow","Infinite"),
                   ("hammerhead","Hammer"),("copperhead","Copper"),
                   ("bheptomino","B-hept"),("random30","30% Rand")]
        pbw = (w-2)//2
        for i,(key,_) in enumerate(presets):
            bx = x+(i%2)*(pbw+2); by = preset_y+(i//2)*18
            if bx <= mx < bx+pbw and by <= my < by+15:
                self.u.grid[:]=0; self._load_preset(key); return
        preset_y += (len(presets)//2 + len(presets)%2)*18+4

        pilot_y = preset_y + 18 + 4 + 4
        if x <= mx < x+w and pilot_y <= my < pilot_y+20:
            self._toggle_ai_driven(); return

    def _handle_right_click(self, mx, my):
        rx = WIN_W - PANEL_R
        x, y, w = rx+5, HEADER_H+5, PANEL_R-10
        tabs = [("stats","Stats"),("rules","Rules"),("ai","Analysis"),
                ("driven","AI-Drive"),("info","Info")]
        tab_w = w // len(tabs)
        if y <= my < y+16:
            for i,(key,_) in enumerate(tabs):
                if x+i*tab_w <= mx < x+(i+1)*tab_w:
                    self.active_tab = key; return
        y += 20

        if self.active_tab == "rules":
            rule_y = y + 18 + 4
            bw5 = w//5
            for n in range(9):
                bx = x+(n%5)*bw5; by = rule_y+(n//5)*20
                if bx+1 <= mx < bx+bw5-1 and by <= my < by+17:
                    if n in self.u.birth_rules: self.u.birth_rules.remove(n)
                    else: self.u.birth_rules.append(n); self.u.birth_rules.sort()
                    return
            surv_y = rule_y + 44 + 18 + 4
            for n in range(9):
                bx = x+(n%5)*bw5; by = surv_y+(n//5)*20
                if bx+1 <= mx < bx+bw5-1 and by <= my < by+17:
                    if n in self.u.survival_rules: self.u.survival_rules.remove(n)
                    else: self.u.survival_rules.append(n); self.u.survival_rules.sort()
                    return
            rp_y = surv_y + 44 + 20 + 18 + 4
            rule_presets = [
                ([3],[2,3]),([3,6],[2,3]),([3,6,7,8],[3,4,6,7,8]),
                ([2],[]),([3],[1,2,3,4,5]),([3],[4,5,6,7,8]),([3,5,7,8],[2,3,5,6,7,8]),
            ]
            rpbw = (w-2)//2
            for i,(b,sr) in enumerate(rule_presets):
                bx = x+(i%2)*(rpbw+2); by = rp_y+(i//2)*18
                if bx <= mx < bx+rpbw and by <= my < by+15:
                    self.u.birth_rules = list(b); self.u.survival_rules = list(sr); return

        elif self.active_tab == "ai":
            ai_y = y + 18 + 4
            bw2 = (w-2)//2
            btns = ["predict","name","story","classify"]
            for i,key in enumerate(btns):
                bx = x+(i%2)*(bw2+2); by = ai_y+(i//2)*20
                if bx <= mx < bx+bw2 and by <= my < by+17:
                    self._ai_analyse(key); return

        elif self.active_tab == "driven":
            drv_y = y + 18 + 4
            if x <= mx < x+w and drv_y+14 <= my < drv_y+34:
                self._toggle_ai_driven(); return
            drv_y += 38
            goals = ["explore","beauty","stability","chaos","oscillators","spaceships","story"]
            gbw = (w-2)//2
            goal_y = drv_y + 13
            for i,g in enumerate(goals):
                bx = x+(i%2)*(gbw+2); by = goal_y+(i//2)*17
                if bx <= mx < bx+gbw and by <= my < by+14:
                    self.ai_driven_goal = g; return
            toggle_y = goal_y + (len(goals)//2+1)*17 + 4 + 20 + 4
            toggles = ["allow_rules","allow_stamps","allow_speed"]
            for i,key in enumerate(toggles):
                if x <= mx < x+w and toggle_y+i*13 <= my < toggle_y+i*13+13:
                    setattr(self, f"ai_driven_{key}", not getattr(self, f"ai_driven_{key}"))
                    return

        elif self.active_tab == "stats" and self.sim_mode == "langton":
            # Recompute the Langton section Y by mirroring _draw_tab_stats layout
            living = int(self.u.grid.sum()) if self.sim_mode=="gol" else 0
            bw = (w-2)//2; bh = 28
            stats_rows = 3   # 6 stats in 2 cols = 3 rows
            stat_block_h = stats_rows * (bh + 2) + 4
            # After stat block: DNA section + pop graph + orbit badge
            # DNA: header(18) + 4 + 4 lines*13 = 74; pop: header(18)+16+44; orbit badge maybe 14
            # We track lang_y by matching the draw code exactly
            lang_y = y + stat_block_h + 18 + 4   # skip DNA section label
            if self.sim_mode == "gol" and self.u.generation > 3:
                lang_y += 4 * 13   # 4 DNA rows
            lang_y += 4 + 18 + 16 + 44  # section gap + POPULATION header + graph
            if self.orbit_period:
                lang_y += 14          # orbit badge
            lang_y += 4 + 18 + 4      # LANGTON section header
            bw3 = (w-4)//3
            for i,n in enumerate([1,2,3]):
                bx = x+i*(bw3+2)
                if bx <= mx < bx+bw3 and lang_y <= my < lang_y+14:
                    self.langton_n_ants = n
                    self.lang = LangtonAnt(n, self.langton_rule)
                    return
            lang_y += 18 + 13   # ants buttons + rule label
            rules = ["RL","LR","RRL","LLRR"]
            rbw = (w-4)//2
            for i,r in enumerate(rules):
                bx = x+(i%2)*(rbw+2); by = lang_y+(i//2)*15
                if bx <= mx < bx+rbw and by <= my < by+13:
                    self.langton_rule = r
                    self.lang = LangtonAnt(self.langton_n_ants, r)
                    return


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    App().run()
