"""Resume a single-worker experiment after an interrupted chunk.

The checkpoint commits completed results together. A retry recomputes only
chunks whose results were never committed.
"""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory


def resume_chunks(checkpoint, chunks, compute):
    chunks = list(chunks)
    encoded = json.dumps(chunks, sort_keys=True, separators=(",", ":"), allow_nan=False)
    fingerprint = sha256(encoded.encode("utf-8")).hexdigest()
    results = []
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text(encoding="utf-8"))
        if saved.get("plan") != fingerprint:
            raise ValueError("The checkpoint belongs to a different chunk plan")
        results = saved.get("results")
        if not isinstance(results, list) or len(results) > len(chunks):
            raise ValueError("Invalid checkpoint results")

    for chunk in chunks[len(results):]:
        results.append(compute(chunk))
        state = json.dumps({"plan": fingerprint, "results": results}, allow_nan=False)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=checkpoint.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(state)
        try:
            temporary.replace(checkpoint)
        finally:
            temporary.unlink(missing_ok=True)
    return results


if __name__ == "__main__":
    def run_first_chunk(chunk):
        if chunk == 3:
            raise InterruptedError("Demonstration interruption")
        return chunk**2

    with TemporaryDirectory() as folder:
        checkpoint = Path(folder) / "checkpoint.json"
        try:
            resume_chunks(checkpoint, [2, 3, 4], run_first_chunk)
        except InterruptedError:
            print("Interrupted after the first committed chunk")
        print("Resumed results:", resume_chunks(checkpoint, [2, 3, 4], lambda chunk: chunk**2))
