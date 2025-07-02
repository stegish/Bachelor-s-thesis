#!/usr/bin/env python3
"""
Unisce in un unico file di testo il contenuto di tutti i file presenti
nella cartella dello script e in tutte le sue sottocartelle.

· Ogni blocco è preceduto dal percorso relativo del file.
· Salta se stesso, il file di output e qualsiasi elemento contenuto in
  cartelle .git, img, node_modules.
· Salta specificamente il file package-lock.json.
· Segnala i file vuoti con un messaggio apposito.
"""

from pathlib import Path

# ──────────────────────────────────────────────────────────────────────
def main() -> None:
    root_dir = Path(__file__).resolve().parent          # cartella dello script
    out_path = root_dir / "merge.txt"                   # file di destinazione

    with out_path.open("w", encoding="utf-8") as out_f:  # crea/sovrascrive output
        for file_path in root_dir.rglob("*"):            # scansione ricorsiva
            if not file_path.is_file():
                continue                                 # ignora le cartelle

            # salta file dentro directory .git, img, node_modules
            if any(part in {".git", "img", "output", "node_modules"} for part in file_path.parts):
                continue

            # evita di copiare lo stesso script, il file di output e package-lock.json
            if file_path in {out_path, Path(__file__).resolve()} or file_path.name == "package-lock.json":
                continue

            rel_path = file_path.relative_to(root_dir)   # percorso relativo
            header = f"\n--- {rel_path} ---\n"
            out_f.write(header)                          # intestazione

            # copia il contenuto del file (ignora errori di decodifica)
            try:
                # controlla se il file è vuoto
                if file_path.stat().st_size == 0:
                    out_f.write("[FILE VUOTO]\n")
                else:
                    with file_path.open("r", encoding="utf-8", errors="ignore") as in_f:
                        content = in_f.read()
                        # controlla anche se il file contiene solo spazi bianchi
                        if not content.strip():
                            out_f.write("[FILE VUOTO O CONTIENE SOLO SPAZI]\n")
                        else:
                            out_f.write(content)
            except Exception as exc:
                out_f.write(f"[Impossibile leggere il file: {exc}]\n")

    print(f"Creato: {out_path.relative_to(root_dir)}")

# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
