"""Comparación O2: laboratorio Compose local, sin reset de datos ni caché."""

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, **kwargs)  # noqa: S603


def ready(url):
    for _ in range(60):
        try:
            with urlopen(f"{url}/api/v1/health/ready", timeout=2) as response:  # noqa: S310 - fixed localhost URL
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(1)
    raise RuntimeError("API no alcanzó readiness")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--duration", default="15s")
    parser.add_argument("--output", default="artifacts/benchmark")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats debe ser positivo")
    out = ROOT / args.output
    if (out / "results.json").exists():
        parser.error("Ya hay resultados; usar --output con un directorio nuevo para conservarlos")
    out.mkdir(parents=True, exist_ok=True)
    engine = os.getenv("CONTAINER_ENGINE", "podman")
    compose = [engine, "compose", "-f", "docker/docker-compose.yml"]
    api_url = "http://127.0.0.1:8000"
    metadata = {
        "started_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "commit_base": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
        "git_status": run(["git", "status", "--short"]).stdout,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "meminfo": Path("/proc/meminfo").read_text().splitlines()[:3],
        "cpu_model": next(
            (line for line in Path("/proc/cpuinfo").read_text().splitlines() if "model name" in line), "unknown"
        ),
        "engine": run([engine, "--version"]).stdout.strip(),
        "compose": run(compose + ["version"]).stdout.strip(),
        "image_ids": {
            name: run([engine, "image", "inspect", name, "--format", "{{.Id}}"]).stdout.strip()
            for name in (
                "localhost/boa-reservas:dev",
                "docker.io/library/postgres:15-alpine",
                "docker.io/valkey/valkey:8-alpine",
                "docker.io/grafana/k6:1.2.3",
            )
        },
        "cache_enabled": False,
        "workers": 2,
        "think_time_seconds": 1,
        "duration": args.duration,
        "repetitions": args.repeats,
        "generator_on_same_host": True,
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [*ROOT.glob("app/**/*.py"), ROOT / "scripts/load_test_k6.js", ROOT / "docker/docker-compose.yml"]
        },
    }
    script = (ROOT / "scripts/load_test_k6.js").read_text()
    results = []
    contract_reference = None
    try:
        for repetition in range(1, args.repeats + 1):
            modes = ("baseline", "refactored") if repetition % 2 else ("refactored", "baseline")
            for mode in modes:
                env = {**os.environ, "READ_MODE": mode, "CACHE_ENABLED": "false"}
                update = run(compose + ["up", "-d", "--no-deps", "--force-recreate", "api"], env=env)
                (out / f"compose-{repetition}-{mode}.log").write_text(update.stdout + update.stderr)
                if update.returncode:
                    raise RuntimeError("Compose falló; revisar log")
                ready(api_url)
                with urlopen(f"{api_url}/api/v1/vuelos/1/disponibilidad", timeout=5) as response:  # noqa: S310
                    contract = json.load(response)
                if contract_reference is None:
                    contract_reference = contract
                elif contract != contract_reference:
                    raise RuntimeError("El contrato o dataset cambió durante la comparación")
                (out / f"contract-{mode}-r{repetition}.json").write_text(json.dumps(contract, indent=2))
                for vus in (50, 200, 500):
                    prefix = f"{mode}-{vus}-r{repetition}"
                    command = [
                        engine,
                        "run",
                        "--rm",
                        "--network=host",
                        "-i",
                        "docker.io/grafana/k6:1.2.3",
                        "run",
                        "--quiet",
                        "--env",
                        f"API_URL={api_url}",
                        "--env",
                        f"VUS={vus}",
                    ]
                    warmup = run(command + ["--env", "DURATION=5s", "-"], input=script)
                    (out / f"{prefix}-warmup.json").write_text(warmup.stdout)
                    measured = run(command + ["--env", f"DURATION={args.duration}", "-"], input=script)
                    (out / f"{prefix}.json").write_text(measured.stdout)
                    (out / f"{prefix}.log").write_text(measured.stderr)
                    data = json.loads(measured.stdout)
                    metrics = data["metrics"]
                    result = {
                        "variant": mode,
                        "vus": vus,
                        "repetition": repetition,
                        "exit_code": measured.returncode,
                        "p50_ms": metrics["http_req_duration"]["values"]["med"],
                        "p95_ms": metrics["http_req_duration"]["values"]["p(95)"],
                        "p99_ms": metrics["http_req_duration"]["values"]["p(99)"],
                        "requests_per_second": metrics["http_reqs"]["values"]["rate"],
                        "error_rate": metrics["http_req_failed"]["values"]["rate"],
                        "checks_rate": metrics["checks"]["values"]["rate"],
                    }
                    results.append(result)
                    (out / "results.json").write_text(json.dumps(results, indent=2))
                    print(json.dumps(result), flush=True)
    finally:
        restored = run(
            compose + ["up", "-d", "--no-deps", "--force-recreate", "api"],
            env={**os.environ, "READ_MODE": "refactored", "CACHE_ENABLED": "false"},
        )
        (out / "restore.log").write_text(restored.stdout + restored.stderr)
        metadata["restore_exit_code"] = restored.returncode
        metadata["finished_utc"] = datetime.datetime.now(datetime.UTC).isoformat()
        (out / "environment.json").write_text(json.dumps(metadata, indent=2))
    if any(item["exit_code"] for item in results):
        raise SystemExit("Comparación completada con umbrales incumplidos; conservar todos los resultados")


if __name__ == "__main__":
    main()
