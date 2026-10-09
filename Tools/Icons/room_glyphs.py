import os
import struct
import sys
import zlib

SCALE = 4
SIZE = 16

GLYPHS = {
    "RoomGlyph_Skull1": [
        "................",
        "................",
        "................",
        "................",
        ".....######.....",
        "...##########...",
        "..############..",
        "..##..####..##..",
        "..#.#..##.#..#..",
        "..#....##....#..",
        "..##..####..##..",
        "..#####..#####..",
        "...##########...",
        "....##.##.##....",
        ".....######.....",
        "................",
    ],
    "RoomGlyph_Skull2": [
        "................",
        "................",
        "..#..........#..",
        "..##........##..",
        "..##.###.##.##..",
        "...######.###...",
        "..######.#####..",
        "..#..######..#..",
        "..#...####...#..",
        "..#....##....#..",
        "..##..####..##..",
        "..#####..#####..",
        "...##########...",
        "...#.#.##.#.#...",
        "....########....",
        "................",
    ],
    "RoomGlyph_Skull3": [
        "................",
        ".##..........##.",
        ".###........###.",
        "..###......###..",
        "...##.##.#.##...",
        "...#####.####...",
        "..#####.#.###...",
        "..#.###.####.#..",
        "..#..######..#..",
        "..##...##...##..",
        "..#####..#####..",
        "..############..",
        "..##.##..##.##..",
        "..#..#....#..#..",
        "...##########...",
        "................",
    ],
    "RoomGlyph_Mineral": [
        "................",
        "................",
        "..........##....",
        ".........###....",
        "........####....",
        ".......#####....",
        ".......#.###....",
        ".#....#.###.....",
        ".##...#.###...#.",
        ".###..#.###..##.",
        ".####.#.###.###.",
        ".####.#####.###.",
        ".####.#####.###.",
        ".####.#####.###.",
        ".##############.",
        "................",
    ],
    "RoomGlyph_Heal": [
        "................",
        "................",
        "................",
        "..####....####..",
        ".######..######.",
        ".##############.",
        ".######..######.",
        ".######..######.",
        ".####......####.",
        "..###......###..",
        "...####..####...",
        "....###..###....",
        ".....######.....",
        "......####......",
        ".......##.......",
        "................",
    ],
}


def chunk(tag, data):
    body = tag + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def encode_png(rows):
    size = SIZE * SCALE
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        line = rows[y // SCALE]
        for x in range(size):
            if line[x // SCALE] == "#":
                raw += b"\xff\xff\xff\xff"
            else:
                raw += b"\x00\x00\x00\x00"
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def validate(name, rows):
    if len(rows) != SIZE:
        raise ValueError(f"{name}: {len(rows)} filas")
    for i, line in enumerate(rows):
        if len(line) != SIZE or set(line) - {"#", "."}:
            raise ValueError(f"{name}: fila {i} invalida")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_out = os.path.join(here, "..", "..", "Assets", "RunRunSimulator", "Resources", "Sprites", "Brawl")
    out_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else default_out)
    os.makedirs(out_dir, exist_ok=True)
    for name, rows in GLYPHS.items():
        validate(name, rows)
        path = os.path.join(out_dir, name + ".png")
        with open(path, "wb") as f:
            f.write(encode_png(rows))
        print(path)


if __name__ == "__main__":
    main()
