# main.py
# Programa principal: simulacion de datos de una plataforma de cuidado animal

import simulador

def main():
    print("SIMULADOR DE DATOS - PLATAFORMA DE CUIDADO ANIMAL")
    print("-" * 55)

    # 1. Generar los 1000 registros limpios
    mascotas = simulador.generar_registros(1000)
    print("Registros generados:", len(mascotas))

    print("\nEjemplo de datos limpios:")
    simulador.mostrar_registros(mascotas, 5)

    # 2. Ensuciar los datos
    mascotas = simulador.ensuciar_datos(mascotas, 15)
    print("\nDatos ensuciados correctamente.")
    print("Total de registros despues del ensuciamiento:", len(mascotas))

    print("\nEjemplo de datos despues del ensuciamiento:")
    simulador.mostrar_registros(mascotas, 5)

    # 3. Revision rapida de la estructura
    print("\nCantidad de atributos del primer registro:", len(mascotas[0]))
    print("Atributos:", list(mascotas[0].keys()))


main()
