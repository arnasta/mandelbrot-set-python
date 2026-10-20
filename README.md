# Mandelbrot Set Plotter

A dependency-free Python 3 script that generates a smoothly colored
Mandelbrot set image in the bitmap (BMP) format.

## Usage

```bash
python3 mandelbrot.py
```

This creates `mandelbrot.bmp` at the default resolution of 800×600 pixels.
To choose the output path and resolution:

```bash
python3 mandelbrot.py output.bmp --resolution 1920x1080
```

You can also set width and height separately. These options override the
corresponding dimensions from `--resolution`:

```bash
python3 mandelbrot.py output.bmp --width 1200 --height 800
```

Use `--max-iterations` to change the maximum number of iterations per point;
higher values can reveal more detail around the set's boundary:

```bash
python3 mandelbrot.py output.bmp --resolution 1200x800 --max-iterations 512
```

Run `python3 mandelbrot.py --help` to see all available options.
