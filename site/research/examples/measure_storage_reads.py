"""Compare reading selected chunks from separate files and a single bundle.

This is a small I/O example. Timings depend on the machine and filesystem cache.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter


def timed_read(read):
    start = perf_counter()
    data = read()
    return sum(map(len, data)), perf_counter() - start


def compare_reads(folder, chunk_size, indices):
    def read_files():
        return [(folder / f"{i}.bin").read_bytes() for i in indices]

    def read_bundle():
        chunks = []
        with (folder / "bundle.bin").open("rb") as stream:
            for index in indices:
                stream.seek(index * chunk_size)
                chunks.append(stream.read(chunk_size))
        return chunks

    return timed_read(read_files), timed_read(read_bundle)


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        folder = Path(directory)
        chunks = [bytes([i]) * 4096 for i in range(20)]
        for index, chunk in enumerate(chunks):
            (folder / f"{index}.bin").write_bytes(chunk)
        (folder / "bundle.bin").write_bytes(b"".join(chunks))
        for name, (size, seconds) in zip(("files", "bundle"), compare_reads(folder, 4096, [2, 5, 9])):
            print(f"{name}: {size} bytes in {seconds * 1000:.3f} ms")
