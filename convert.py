#!/usr/bin/env python3
from pathlib import Path
from subprocess import run, check_call, DEVNULL, PIPE

import click


def convert(src: Path, dest: Path, size: int, subset=None) -> None:
    otf_command = ["otf2bdf", "-p", f"{size}", "-r", "72", f"{src}"]
    if subset:
        otf_command.extend(['-l', subset])

    otf_process = run(otf_command, stdin=DEVNULL, stdout=PIPE
    )
    bdf_content = otf_process.stdout
    if otf_process.returncode != 8:
        print(f"Note: End of bdf_content: {bdf_content[-32:]!r}")
        raise RuntimeError(
            f"otf2bdf failed: exit status was {otf_process.returncode}, not 8"
        )
    if not bdf_content.endswith(b"ENDFONT\n"):
        print(f"Note: End of bdf_content: {bdf_content[-32:]!r}")
        raise RuntimeError(f"otf2bdf failed: output did not end with ENDFONT")
    bdf_process = run(["bdftopcf", "-o", f"{dest}", "/dev/stdin"], input=bdf_content)
    bdf_process.check_returncode()


@click.command
@click.option("--source", type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "--destination", type=click.Path(exists=False, path_type=Path), required=True
)
@click.option("--size", type=int, required=True)
def main(source, destination, size):
    destination.parent.mkdir(parents=True, exist_ok=True)
    convert(source, destination, size)


if __name__ == "__main__":
    main()
