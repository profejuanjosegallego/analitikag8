# limpieza.py
# Funciones para limpiar los datos sucios generados por simulador.py
# Cada funcion corrige uno de los 10 tipos de error que introduce ensuciar_datos()

import difflib
import statistics
import unicodedata

from simulador import razas, pesos, servicios, ciudades

# Rango razonable de edad (en anios) para cualquier mascota
EDAD_MINIMA = 0
EDAD_MAXIMA = 30

# Valor que se usa para rellenar textos nulos que no se pueden recuperar
DESCONOCIDO = "Desconocido"

# Campos de texto que deben limpiarse de espacios
CAMPOS_TEXTO = ["nombre_mascota", "especie", "raza", "nombre_propietario",
                "ciudad", "tipo_servicio"]


# ---------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------

def quitar_acentos(texto):
    """Devuelve el texto sin tildes ni caracteres especiales."""
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def normalizar_texto(texto):
    """Quita espacios, acentos y pasa a minusculas para poder comparar."""
    return quitar_acentos(texto).strip().lower()


def buscar_parecido(valor, opciones, umbral=0.6):
    """Busca en 'opciones' el valor mas parecido al texto dado.
    Sirve para corregir errores ortograficos (ej: 'bogta' -> 'Bogota')."""
    if valor is None:
        return None
    valor_normalizado = normalizar_texto(valor)
    opciones_normalizadas = {normalizar_texto(op): op for op in opciones}

    # Coincidencia exacta despues de normalizar
    if valor_normalizado in opciones_normalizadas:
        return opciones_normalizadas[valor_normalizado]

    # Coincidencia aproximada
    parecidos = difflib.get_close_matches(valor_normalizado,
                                          list(opciones_normalizadas.keys()),
                                          n=1, cutoff=umbral)
    if parecidos:
        return opciones_normalizadas[parecidos[0]]
    return None


# ---------------------------------------------------------------
# Correccion de cada tipo de error
# ---------------------------------------------------------------

def limpiar_espacios(registro):
    """Error 3: quita espacios innecesarios al inicio y al final de los textos."""
    for campo in CAMPOS_TEXTO:
        valor = registro.get(campo)
        if isinstance(valor, str):
            registro[campo] = valor.strip()
    return registro


def limpiar_cadenas_vacias(registro):
    """Error 2: convierte las cadenas vacias en None para tratarlas como nulos."""
    for campo in CAMPOS_TEXTO:
        if registro.get(campo) == "":
            registro[campo] = None
    return registro


def corregir_especie(registro):
    """Error 4: unifica mayusculas/minusculas de la especie (ej: 'PERRO' -> 'Perro')."""
    especie = buscar_parecido(registro.get("especie"), list(razas.keys()))
    if especie is not None:
        registro["especie"] = especie
    return registro


def corregir_ciudad(registro):
    """Error 5: corrige ciudades mal escritas usando la lista oficial de ciudades."""
    ciudad = registro.get("ciudad")
    if ciudad is not None:
        registro["ciudad"] = buscar_parecido(ciudad, ciudades)
    return registro


def corregir_servicio(registro):
    """Normaliza el nombre del servicio contra la lista oficial."""
    servicio = registro.get("tipo_servicio")
    if servicio is not None:
        registro["tipo_servicio"] = buscar_parecido(servicio, list(servicios.keys()))
    return registro


def convertir_a_numero(valor, tipo=float):
    """Error 8: convierte textos como '12 anios' o '45000' a numero.
    Si no se puede convertir devuelve None."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return valor
    # Nos quedamos solo con digitos, signo y punto decimal
    limpio = "".join(c for c in str(valor) if c.isdigit() or c in "-.")
    if limpio in ("", "-", ".", "-."):
        return None
    try:
        return tipo(float(limpio))
    except ValueError:
        return None


def corregir_tipos(registro):
    """Error 8: se asegura de que edad, peso y costo sean numeros."""
    registro["edad"] = convertir_a_numero(registro.get("edad"), int)
    registro["peso"] = convertir_a_numero(registro.get("peso"), float)
    registro["costo_servicio"] = convertir_a_numero(registro.get("costo_servicio"), int)
    return registro


def corregir_negativos(registro):
    """Error 6: los valores negativos se interpretan como error de signo."""
    for campo in ["edad", "peso", "costo_servicio"]:
        valor = registro.get(campo)
        if isinstance(valor, (int, float)) and valor < 0:
            registro[campo] = abs(valor)
    return registro


def corregir_fuera_de_rango(registro):
    """Error 7: los valores fuera de un rango razonable se marcan como None
    para luego imputarlos."""
    edad = registro.get("edad")
    if isinstance(edad, (int, float)) and not (EDAD_MINIMA <= edad <= EDAD_MAXIMA):
        registro["edad"] = None

    especie = registro.get("especie")
    peso = registro.get("peso")
    if especie in pesos and isinstance(peso, (int, float)):
        peso_minimo, peso_maximo = pesos[especie]
        if not (peso_minimo <= peso <= peso_maximo):
            registro["peso"] = None

    servicio = registro.get("tipo_servicio")
    costo = registro.get("costo_servicio")
    if servicio in servicios and isinstance(costo, (int, float)):
        costo_minimo, costo_maximo = servicios[servicio]
        if not (costo_minimo <= costo <= costo_maximo):
            registro["costo_servicio"] = None

    return registro


def corregir_raza(registro):
    """Error 9: si la raza no corresponde a la especie se marca como desconocida."""
    especie = registro.get("especie")
    raza = registro.get("raza")
    if especie in razas and raza is not None:
        raza_valida = buscar_parecido(raza, razas[especie])
        registro["raza"] = raza_valida  # None si no pertenece a la especie
    return registro


def eliminar_duplicados(lista):
    """Error 10: elimina registros duplicados conservando la primera aparicion.
    Dos registros son duplicados si tienen el mismo id_mascota."""
    vistos = set()
    resultado = []
    for registro in lista:
        clave = registro["id_mascota"]
        if clave not in vistos:
            vistos.add(clave)
            resultado.append(registro)
    return resultado


# ---------------------------------------------------------------
# Imputacion de valores nulos (Error 1 y los None generados arriba)
# ---------------------------------------------------------------

def calcular_medianas(lista):
    """Calcula la mediana de edad, y de peso y costo por especie/servicio,
    usando solo los valores validos."""
    edades = [r["edad"] for r in lista if isinstance(r["edad"], (int, float))]
    mediana_edad = int(statistics.median(edades)) if edades else None

    mediana_peso = {}
    for especie in pesos:
        valores = [r["peso"] for r in lista
                   if r["especie"] == especie and isinstance(r["peso"], (int, float))]
        if valores:
            mediana_peso[especie] = round(statistics.median(valores), 2)

    mediana_costo = {}
    for servicio in servicios:
        valores = [r["costo_servicio"] for r in lista
                   if r["tipo_servicio"] == servicio
                   and isinstance(r["costo_servicio"], (int, float))]
        if valores:
            mediana_costo[servicio] = int(statistics.median(valores))

    return mediana_edad, mediana_peso, mediana_costo


def imputar_nulos(lista):
    """Rellena los valores None:
    - numericos: con la mediana (por especie o por servicio cuando aplica)
    - textos: con 'Desconocido'."""
    mediana_edad, mediana_peso, mediana_costo = calcular_medianas(lista)

    for registro in lista:
        if registro["edad"] is None:
            registro["edad"] = mediana_edad

        if registro["peso"] is None:
            registro["peso"] = mediana_peso.get(registro["especie"])

        if registro["costo_servicio"] is None:
            registro["costo_servicio"] = mediana_costo.get(registro["tipo_servicio"])

        for campo in ["raza", "ciudad", "nombre_propietario", "tipo_servicio",
                      "nombre_mascota", "especie"]:
            if registro[campo] is None:
                registro[campo] = DESCONOCIDO

    return lista


# ---------------------------------------------------------------
# Funcion principal de limpieza
# ---------------------------------------------------------------

def limpiar_registro(registro):
    """Aplica todas las correcciones a un solo registro (en orden)."""
    registro = dict(registro)  # copia para no modificar el original
    registro = limpiar_espacios(registro)
    registro = limpiar_cadenas_vacias(registro)
    registro = corregir_especie(registro)
    registro = corregir_ciudad(registro)
    registro = corregir_servicio(registro)
    registro = corregir_tipos(registro)
    registro = corregir_negativos(registro)
    registro = corregir_fuera_de_rango(registro)
    registro = corregir_raza(registro)
    return registro


def limpiar_datos(lista):
    """Limpia toda la lista de registros y devuelve una lista nueva."""
    limpios = [limpiar_registro(registro) for registro in lista]
    limpios = eliminar_duplicados(limpios)
    limpios = imputar_nulos(limpios)
    return limpios


# ---------------------------------------------------------------
# Reporte de calidad
# ---------------------------------------------------------------

def contar_problemas(lista):
    """Cuenta cuantos registros tienen cada tipo de problema. Sirve para
    comparar antes y despues de la limpieza."""
    conteo = {
        "nulos_o_vacios": 0,
        "espacios_extra": 0,
        "especie_mal_escrita": 0,
        "ciudad_mal_escrita": 0,
        "tipos_incorrectos": 0,
        "valores_negativos": 0,
        "fuera_de_rango": 0,
        "raza_inconsistente": 0,
        "duplicados": 0,
    }
    ids = []

    for r in lista:
        if any(r[c] is None or r[c] == "" for c in r):
            conteo["nulos_o_vacios"] += 1
        if any(isinstance(r[c], str) and r[c] != r[c].strip() for c in CAMPOS_TEXTO):
            conteo["espacios_extra"] += 1
        # 'Desconocido' es el marcador que deja la limpieza cuando el valor
        # original era nulo, asi que no se cuenta como error
        if r["especie"] not in razas and r["especie"] != DESCONOCIDO:
            conteo["especie_mal_escrita"] += 1
        if r["ciudad"] not in ciudades and r["ciudad"] != DESCONOCIDO:
            conteo["ciudad_mal_escrita"] += 1
        if any(isinstance(r[c], str) for c in ["edad", "peso", "costo_servicio"]):
            conteo["tipos_incorrectos"] += 1
        if any(isinstance(r[c], (int, float)) and r[c] < 0
               for c in ["edad", "peso", "costo_servicio"]):
            conteo["valores_negativos"] += 1
        if isinstance(r["edad"], (int, float)) and r["edad"] > EDAD_MAXIMA:
            conteo["fuera_de_rango"] += 1
        elif (r["tipo_servicio"] in servicios
              and isinstance(r["costo_servicio"], (int, float))
              and r["costo_servicio"] > servicios[r["tipo_servicio"]][1]):
            conteo["fuera_de_rango"] += 1
        if (r["especie"] in razas and r["raza"] not in razas[r["especie"]]
                and r["raza"] != DESCONOCIDO):
            conteo["raza_inconsistente"] += 1
        ids.append(r["id_mascota"])

    conteo["duplicados"] = len(ids) - len(set(ids))
    return conteo


def mostrar_reporte(antes, despues):
    """Imprime una tabla comparando los problemas antes y despues de limpiar."""
    conteo_antes = contar_problemas(antes)
    conteo_despues = contar_problemas(despues)

    print(f"{'Problema':<22}{'Antes':>8}{'Despues':>10}")
    print("-" * 40)
    for problema in conteo_antes:
        print(f"{problema:<22}{conteo_antes[problema]:>8}{conteo_despues[problema]:>10}")
    print("-" * 40)
    print(f"{'Total registros':<22}{len(antes):>8}{len(despues):>10}")
