import pandas as pd
from itertools import combinations
from collections import defaultdict

def leer_datos(archivo):
    return pd.read_excel(archivo, index_col=0)

def generar_conjuntos_frecuentes(transacciones, k, soporte_minimo):
    conteo = defaultdict(int)
    for transaccion in transacciones:
        for itemset in combinations(transaccion, k):
            conteo[itemset] += 1
    
    return {itemset: count for itemset, count in conteo.items() if count >= soporte_minimo}

def apriori(datos, soporte_minimo):
    transacciones = [tuple(datos.columns[datos.loc[i] == 1].tolist()) for i in datos.index]
    n_transacciones = len(transacciones)
    soporte_minimo_count = soporte_minimo * n_transacciones
    
    L1 = generar_conjuntos_frecuentes(transacciones, 1, soporte_minimo_count)
    L = [L1]
    k = 2
    
    max_iterations = 10  # Límite de iteraciones para evitar bucle infinito
    for _ in range(max_iterations):
        Ck = generar_conjuntos_frecuentes(transacciones, k, soporte_minimo_count)
        if not Ck:
            break
        L.append(Ck)
        k += 1
    
    return L

def generar_reglas(conjuntos_frecuentes, soporte_minimo, confianza_minima):
    reglas = []
    for k in range(2, len(conjuntos_frecuentes)):
        for itemset, soporte in conjuntos_frecuentes[k].items():
            for i in range(1, len(itemset)):
                for antecedente in combinations(itemset, i):
                    consecuente = tuple(item for item in itemset if item not in antecedente)
                    confianza = soporte / conjuntos_frecuentes[len(antecedente) - 1][antecedente]
                    if confianza >= confianza_minima:
                        reglas.append((antecedente, consecuente, soporte, confianza))
    return reglas

def obtener_recomendaciones(datos, id_compra, reglas):
    productos_comprados = set(datos.columns[datos.loc[id_compra] == 1])
    recomendaciones = []
    
    for antecedente, consecuente, soporte, confianza in reglas:
        if set(antecedente).issubset(productos_comprados):
            for producto in consecuente:
                if producto not in productos_comprados:
                    recomendaciones.append((producto, confianza))
    
    return sorted(recomendaciones, key=lambda x: x[1], reverse=True)

def mostrar_productos_mas_vendidos_juntos(conjuntos_frecuentes, n=5):
    productos_juntos = []
    for k in range(2, len(conjuntos_frecuentes)):
        for itemset, count in conjuntos_frecuentes[k].items():
            productos_juntos.append((itemset, count))
    
    productos_juntos.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTop {n} productos más vendidos juntos:")
    for i, (itemset, count) in enumerate(productos_juntos[:n], 1):
        print(f"{i}. {' + '.join(itemset)} (Frecuencia: {count})")

def main():
    archivo = 'Datos.xlsx'
    soporte_minimo = 0.02  # 2% de las transacciones
    confianza_minima = 0.5  # 50% de confianza

    datos = leer_datos(archivo)
    conjuntos_frecuentes = apriori(datos, soporte_minimo)
    reglas = generar_reglas(conjuntos_frecuentes, soporte_minimo, confianza_minima)

    while True:
        print("\nOpciones:")
        print("1. Obtener los objetos de una sola compra")
        print("2. Ver productos más vendidos juntos")
        print("3. Salir")
        opcion = input("Seleccione una opción (1-3): ")

        if opcion == '1':
            id_compra = input("Ingrese el ID de la compra: ")
            try:
                id_compra = int(id_compra)
                if id_compra not in datos.index:
                    print("ID de compra no encontrado.")
                    continue
                
                recomendaciones = obtener_recomendaciones(datos, id_compra, reglas)
                
                print(f"\nproductos en la compra numero {id_compra}:")
                productos_comprados = datos.columns[datos.loc[id_compra] == 1].tolist()
                print(", ".join(productos_comprados))               
                
                if not recomendaciones:
                    print("No se encontraron recomendaciones para esta compra.")
            
            except ValueError:
                print("Por favor, ingrese un número válido para el ID de compra.")

        elif opcion == '2':
            mostrar_productos_mas_vendidos_juntos(conjuntos_frecuentes)

        elif opcion == '3':
            print("Gracias por usar el sistema. ¡Hasta luego!")
            break

        else:
            print("Opción no válida. Por favor, seleccione 1, 2 o 3.")

if __name__ == "__main__":
    main()