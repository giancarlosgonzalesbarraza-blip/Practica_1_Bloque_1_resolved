import json
import xml.etree.ElementTree as ET
from pathlib import Path

    # Carpetas base del proyecto
BASE_DIR = Path(__file__).resolve().parent
FUENTE = BASE_DIR / "data" / "Analisis_Academico"       
DESTINO = BASE_DIR / "data" / "raw"               

TABLAS = {
        "alumnos.xml": {
            "registro": "alumno",
            "campos": {"NIA": "NIA", "curso": "Curso", "turno": "Turno", "grupo": "Grupo"},
        },
        "cursos.xml": {
            "registro": "curso",
            "campos": {"codigo": "Codigo", "nombre_cas": "Nombre_Cas",
                    "nombre_val": "Nombre_Val", "padre": "Padre"},
        },
        "calificaciones.xml": {
            "registro": "calificacion",
            "campos": {"alumno": "NIA", "curso": "Curso", "contenido": "Modulo",
                    "nota_numerica": "Nota", "evaluacion": "Evaluacion"},
        },
        "contenidos.xml": {
            "registro": "contenido",
            "campos": {"curso": "Curso", "codigo": "Modulo", "nombre_cas": "Nombre_Modulo"},
        },
    }


def parsear_xml(ruta_xml: Path, config: dict) -> list:
        """Lee un XML y devuelve una lista de registros (dicts) listos para JSON."""
        arbol = ET.parse(ruta_xml)
        raiz = arbol.getroot()

        
        anyo = raiz.get("curso")

        
        registros = []
        for registro in raiz.findall(f".//{config['registro']}"):
           
            fila = {"Anyo": anyo}
            for atributo, campo in config["campos"].items():
               
                fila[campo] = registro.get(atributo)
            registros.append(fila)
        return registros


def main():
        total_registros = 0

        
        for carpeta in sorted(FUENTE.iterdir()):
            if not carpeta.is_dir():
                continue  

            salida_curso = DESTINO / carpeta.name
            salida_curso.mkdir(parents=True, exist_ok=True)  

            for nombre_xml, config in TABLAS.items():
                ruta_xml = carpeta / nombre_xml
                if not ruta_xml.exists():
                    print(f"  ! falta {ruta_xml}, lo salto")
                    continue

                registros = parsear_xml(ruta_xml, config)

                
                tabla = nombre_xml.removesuffix(".xml")
                ruta_json = salida_curso / f"{tabla}.json"
                ruta_json.write_text(
                    json.dumps(registros, ensure_ascii=False),
                    encoding="utf-8",
                )
                total_registros += len(registros)
                print(f"  {carpeta.name}/{nombre_xml} -> {ruta_json.relative_to(BASE_DIR)}  ({len(registros)} registros)")

        print(f"Total registros ingestados: {total_registros}")


if __name__ == "__main__":
        main()
