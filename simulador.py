# simulador.py
# Funciones para generar y ensuciar los datos de la plataforma de cuidado animal

import random
from faker import Faker

# Objeto de Faker en espanol
faker = Faker("es_ES")

# Razas coherentes con cada especie
razas = {
    "Perro": ["Labrador", "Pastor Aleman", "Bulldog", "Poodle", "Chihuahua", "Beagle", "Criollo"],
    "Gato": ["Persa", "Siames", "Angora", "Bengali", "Criollo"],
    "Ave": ["Canario", "Periquito", "Loro", "Agapornis"],
    "Conejo": ["Belier", "Angora", "Cabeza de Leon", "Holandes"],
    "Hamster": ["Sirio", "Ruso", "Roborowski"]
}

# Rango de peso (en kilos) segun la especie
pesos = {
    "Perro": (2.0, 45.0),
    "Gato": (1.5, 9.0),
    "Ave": (0.05, 1.5),
    "Conejo": (0.8, 6.0),
    "Hamster": (0.03, 0.25)
}

# Servicios y su rango de costo
servicios = {
    "Consulta veterinaria": (40000, 120000),
    "Vacunacion": (30000, 90000),
    "Peluqueria": (25000, 70000),
    "Guarderia": (35000, 100000),
    "Paseo": (15000, 40000),
    "Desparasitacion": (20000, 60000)
}

ciudades = ["Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena",
            "Bucaramanga", "Pereira", "Manizales", "Santa Marta", "Cucuta"]

nombres_mascotas = ["Luna", "Max", "Rocky", "Bella", "Toby", "Simba", "Kira",
                    "Nala", "Milo", "Coco", "Lola", "Zeus", "Manchas", "Pelusa",
                    "Firulais", "Michi", "Bruno", "Canela", "Duque", "Nube"]


def generar_registro(numero):
    """Genera un unico registro (diccionario) con 10 atributos."""
    especie = random.choice(list(razas.keys()))
    raza = random.choice(razas[especie])

    peso_minimo, peso_maximo = pesos[especie]
    peso = round(random.uniform(peso_minimo, peso_maximo), 2)

    servicio = random.choice(list(servicios.keys()))
    costo_minimo, costo_maximo = servicios[servicio]
    costo = random.randrange(costo_minimo, costo_maximo + 1, 1000)

    registro = {
        "id_mascota": numero,
        "nombre_mascota": random.choice(nombres_mascotas),
        "especie": especie,
        "raza": raza,
        "edad": random.randint(1, 15),
        "peso": peso,
        "nombre_propietario": faker.name(),
        "ciudad": random.choice(ciudades),
        "tipo_servicio": servicio,
        "costo_servicio": costo
    }
    return registro


def generar_registros(cantidad):
    """Genera una lista con la cantidad de registros pedida."""
    lista = []
    for numero in range(1, cantidad + 1):
        lista.append(generar_registro(numero))
    return lista


def ensuciar_datos(lista, porcentaje=15):
    """Introduce errores de calidad en un porcentaje aleatorio de los registros."""
    cantidad_sucios = int(len(lista) * porcentaje / 100)
    posiciones = random.sample(range(len(lista)), cantidad_sucios)

    ciudades_malas = ["bogta", "MEDELLIN ", " cali", "barranqilla", "Cartajena", "medellin"]

    for posicion in posiciones:
        registro = lista[posicion]
        error = random.randint(1, 9)

        if error == 1:
            # 1. Valores nulos
            campo = random.choice(["raza", "ciudad", "peso", "nombre_propietario"])
            registro[campo] = None

        elif error == 2:
            # 2. Cadenas vacias
            registro["tipo_servicio"] = ""

        elif error == 3:
            # 3. Espacios innecesarios en los textos
            registro["nombre_mascota"] = "   " + registro["nombre_mascota"] + "  "

        elif error == 4:
            # 4. Diferencias entre mayusculas y minusculas
            if random.randint(1, 2) == 1:
                registro["especie"] = registro["especie"].upper()
            else:
                registro["especie"] = registro["especie"].lower()

        elif error == 5:
            # 5. Ciudades mal escritas (errores ortograficos)
            registro["ciudad"] = random.choice(ciudades_malas)

        elif error == 6:
            # 6. Valores numericos negativos
            if random.randint(1, 2) == 1:
                registro["edad"] = -registro["edad"]
            else:
                registro["peso"] = -registro["peso"]

        elif error == 7:
            # 7. Valores fuera de un rango razonable
            if random.randint(1, 2) == 1:
                registro["edad"] = random.randint(80, 200)
            else:
                registro["costo_servicio"] = random.randint(5000000, 9000000)

        elif error == 8:
            # 8. Tipos de dato incorrectos (numeros guardados como texto)
            registro["edad"] = str(registro["edad"]) + " anios"
            registro["costo_servicio"] = str(registro["costo_servicio"])

        elif error == 9:
            # 9. Datos inconsistentes entre atributos (raza que no es de la especie)
            otra_especie = random.choice(list(razas.keys()))
            registro["raza"] = random.choice(razas[otra_especie])

    # 10. Registros duplicados (se copia un registro sobre otro,
    #     asi la lista sigue teniendo exactamente 1000 registros)
    cantidad_duplicados = int(len(lista) * 0.02)
    for i in range(cantidad_duplicados):
        origen = random.randint(0, len(lista) - 1)
        destino = random.randint(0, len(lista) - 1)
        lista[destino] = dict(lista[origen])

    return lista


def mostrar_registros(lista, cantidad=5):
    """Muestra en pantalla los primeros registros de la lista."""
    for registro in lista[:cantidad]:
        print(registro)
