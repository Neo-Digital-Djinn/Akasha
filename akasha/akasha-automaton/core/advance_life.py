#!/usr/bin/env python3
"""
advance_life.py — Reads the current Game of Life grid from README.md,
computes one generation of B3/S23, and writes it back.

Grid is stored between <!-- LIFE_START --> and <!-- LIFE_END --> markers.
⬜ = alive, ⬛ = dead
"""

import re
import sys

README = "README.md"
ALIVE = "⬜"
DEAD  = "⬛"

START_TAG = "<!-- LIFE_START -->"
END_TAG   = "<!-- LIFE_END -->"
STAT_RE   = re.compile(r"Generation: (\d+) · Population: (\d+) · Rule: B3/S23")


def parse_grid(lines):
    grid = []
    for line in lines:
        row = []
        # Each emoji is one cell
        i = 0
        chars = list(line)
        # Walk by character but emoji are multi-byte — work on the string directly
        # Split on known cell chars
        pos = 0
        s = line
        while pos < len(s):
            if s[pos:pos+3] == ALIVE:
                row.append(1)
                pos += 3
            elif s[pos:pos+3] == DEAD:
                row.append(0)
                pos += 3
            else:
                pos += 1
        if row:
            grid.append(row)
    return grid


def next_gen(grid):
    if not grid:
        return grid
    H = len(grid)
    W = len(grid[0])
    new = [[0]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            neighbors = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = (y + dy) % H
                    nx = (x + dx) % W
                    neighbors += grid[ny][nx]
            alive = grid[y][x]
            if alive and neighbors in (2, 3):
                new[y][x] = 1
            elif not alive and neighbors == 3:
                new[y][x] = 1
    return new


def grid_to_lines(grid):
    lines = []
    for row in grid:
        lines.append("".join(ALIVE if c else DEAD for c in row))
    return lines


def count_population(grid):
    return sum(sum(row) for row in grid)


def main():
    with open(README, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the block between markers
    start_idx = content.find(START_TAG)
    end_idx   = content.find(END_TAG)

    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find LIFE_START / LIFE_END markers in README.md")
        sys.exit(1)

    before  = content[:start_idx + len(START_TAG)]
    between = content[start_idx + len(START_TAG):end_idx]
    after   = content[end_idx:]

    # Parse grid lines (non-empty lines inside the block)
    raw_lines = [l for l in between.split("\n") if l.strip()]
    grid = parse_grid(raw_lines)

    if not grid:
        print("ERROR: No grid data found between markers.")
        sys.exit(1)

    # Advance one generation
    new_grid = next_gen(grid)
    new_lines = grid_to_lines(new_grid)
    population = count_population(new_grid)

    new_between = "\n" + "\n".join(new_lines) + "\n"

    new_content = before + new_between + after

    # Update the stats line below the closing marker
    # Pattern: "Generation: N · Population: N · Rule: B3/S23"
    match = STAT_RE.search(new_content)
    if match:
        old_gen = int(match.group(1))
        new_gen = old_gen + 1
        new_stat = f"Generation: {new_gen} · Population: {population} · Rule: B3/S23"
        new_content = new_content[:match.start()] + new_stat + new_content[match.end():]

    with open(README, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Advanced to generation {new_gen} — population: {population}")


if __name__ == "__main__":
    main()
