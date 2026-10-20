#!/usr/bin/env python3
"""Render a smoothly colored Mandelbrot set to a 24-bit BMP image."""

import argparse
import colorsys
import math
import struct
from pathlib import Path


def positive_int(value: str) -> int:
    """Parse a positive integer for image dimensions and iteration limits."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def resolution(value: str) -> tuple[int, int]:
    """Parse an image resolution written as WIDTHxHEIGHT."""
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width = positive_int(width_text)
        height = positive_int(height_text)
    except (ValueError, argparse.ArgumentTypeError) as error:
        raise argparse.ArgumentTypeError(
            "resolution must be WIDTHxHEIGHT with positive integers"
        ) from error
    return width, height


def mandelbrot_color(real: float, imaginary: float, max_iterations: int) -> tuple[int, int, int]:
    """Return the RGB color for one point in the complex plane."""
    z_real = 0.0
    z_imaginary = 0.0

    for iteration in range(max_iterations):
        z_real_squared = z_real * z_real
        z_imaginary_squared = z_imaginary * z_imaginary
        if z_real_squared + z_imaginary_squared > 4.0:
            magnitude = (z_real_squared + z_imaginary_squared) ** 0.5
            smooth_iteration = iteration + 1 - (
                math.log(math.log(magnitude)) / math.log(2.0)
            )
            hue = (smooth_iteration * 0.035) % 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            return round(red * 255), round(green * 255), round(blue * 255)

        z_imaginary = 2.0 * z_real * z_imaginary + imaginary
        z_real = z_real_squared - z_imaginary_squared + real

    return 0, 0, 0


def write_bitmap(
    output: Path, width: int, height: int, max_iterations: int
) -> None:
    """Render the set and write it as an uncompressed 24-bit BMP."""
    row_size = (width * 3 + 3) & ~3
    image_size = row_size * height
    pixel_offset = 14 + 40

    with output.open("wb") as bitmap:
        bitmap.write(struct.pack("<2sIHHI", b"BM", pixel_offset + image_size, 0, 0, pixel_offset))
        bitmap.write(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                height,
                1,
                24,
                0,
                image_size,
                2835,
                2835,
                0,
                0,
            )
        )

        real_min, real_max = -2.5, 1.0
        imaginary_span = (real_max - real_min) * height / width
        imaginary_max = imaginary_span / 2

        for row in range(height - 1, -1, -1):
            imaginary = imaginary_max - (row + 0.5) * imaginary_span / height
            pixels = bytearray()
            for column in range(width):
                real = real_min + (column + 0.5) * (real_max - real_min) / width
                red, green, blue = mandelbrot_color(real, imaginary, max_iterations)
                pixels.extend((blue, green, red))
            pixels.extend(b"\0" * (row_size - width * 3))
            bitmap.write(pixels)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a smoothly colored Mandelbrot set bitmap."
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path("mandelbrot.bmp"),
        help="output BMP path (default: mandelbrot.bmp)",
    )
    parser.add_argument(
        "--resolution",
        type=resolution,
        default=(800, 600),
        metavar="WIDTHxHEIGHT",
        help="image resolution in pixels (default: 800x600)",
    )
    parser.add_argument("--width", type=positive_int, help="override image width in pixels")
    parser.add_argument("--height", type=positive_int, help="override image height in pixels")
    parser.add_argument(
        "--max-iterations",
        type=positive_int,
        default=256,
        help="maximum iterations per point",
    )
    args = parser.parse_args()

    width = args.width if args.width is not None else args.resolution[0]
    height = args.height if args.height is not None else args.resolution[1]
    write_bitmap(args.output, width, height, args.max_iterations)
    print(f"Saved {width}x{height} Mandelbrot bitmap to {args.output}")


if __name__ == "__main__":
    main()
