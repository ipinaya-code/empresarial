"""Tabla y gráfico de evidencia real. Requiere matplotlib para el SVG."""

import argparse
import json
import statistics
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    directory = Path(args.directory)
    rows = json.loads((directory / "results.json").read_text())
    expected = {
        (mode, vus, repeat) for mode in ("baseline", "refactored") for vus in (50, 200, 500) for repeat in (1, 2, 3)
    }
    actual = {(r["variant"], r["vus"], r["repetition"]) for r in rows}
    if expected != actual:
        raise SystemExit("Se requieren las 18 ejecuciones del protocolo para emitir el informe final")
    lines = [
        "# Resultados medidos",
        "",
        "Cada fila es una ejecución; valores de latencia en ms.",
        "",
        "| Variante | VU | Repetición | p50 | p95 | p99 | req/s | Errores | Checks | Salida k6 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant']} | {row['vus']} | {row['repetition']} | "
            f"{row['p50_ms']:.2f} | {row['p95_ms']:.2f} | {row['p99_ms']:.2f} | "
            f"{row['requests_per_second']:.2f} | {row['error_rate']:.2%} | "
            f"{row['checks_rate']:.2%} | {row['exit_code']} |"
        )
    lines.extend(
        [
            "",
            "Medianas de p95 entre repeticiones (no percentil agregado de todas las solicitudes):",
            "",
            "| VU | Baseline p95 | Refactor p95 | Cambio relativo |",
            "|---|---:|---:|---:|",
        ]
    )
    grouped = {}
    for vus in (50, 200, 500):
        values = {
            mode: statistics.median(r["p95_ms"] for r in rows if r["variant"] == mode and r["vus"] == vus)
            for mode in ("baseline", "refactored")
        }
        grouped[vus] = values
        improvement = 100 * (values["baseline"] - values["refactored"]) / values["baseline"]
        lines.append(f"| {vus} | {values['baseline']:.2f} | {values['refactored']:.2f} | {improvement:.1f}% |")
    lines += [
        "",
        "Salida 99 significa umbral incumplido; 0 indica todos los umbrales satisfechos.",
        "Un porcentaje positivo representa reducción de la mediana de p95 en este experimento.",
        "Generador y servicio comparten host. No extrapolar a tráfico institucional o disponibilidad mensual.",
        "",
    ]
    (directory / "report.md").write_text("\n".join(lines))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for mode, color in (("baseline", "#b45309"), ("refactored", "#0369a1")):
        ax.plot(list(grouped), [grouped[v][mode] for v in grouped], marker="o", color=color, label=mode)
        for row in rows:
            if row["variant"] == mode:
                ax.scatter(row["vus"], row["p95_ms"], color=color, alpha=0.4, s=18)
    ax.axhline(200, color="#991b1b", linestyle="--", label="Meta de laboratorio: 200 ms")
    ax.set(
        xlabel="Usuarios virtuales (pausa 1 s)",
        ylabel="p95 por ejecución (ms)",
        title="Disponibilidad sin caché · 3 repeticiones · 15 s",
    )
    ax.set_xticks([50, 200, 500])
    ax.set_ylim(bottom=0)
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(directory / "latencia.svg")
    plt.close(fig)


if __name__ == "__main__":
    main()
