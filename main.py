import numpy as np

def ler_cidades_de_arquivo(nome_arquivo):
    try:
        lista_cidades = []
        i = 0
        with open(nome_arquivo, "r", encoding='utf-8') as arquivo:
            for linha in arquivo:
                cidade = (linha.strip(), i)
                lista_cidades.append(cidade)
                i+=1
        return lista_cidades
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []

def ler_mapa(nome_arquivo, cidades_lidas, quantidade_cidades):
    mapa = np.zeros((quantidade_cidades, quantidade_cidades))
    try:
        with open(nome_arquivo, "r", encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas:
                cidade_info = linha.strip().split(",")
                try:
                    if len(cidade_info) == 3:
                        origem, destino, custo = cidade_info
                        mapa[cidades_lidas[origem]][cidades_lidas[destino]] = int(custo)
                        mapa[cidades_lidas[destino]][cidades_lidas[origem]] = int(custo)
                except:
                    print("")
        return mapa
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []

def vizinho_mais_proximo(indices_a_percorrer, matriz_distancia):
    # Essa parte do código procura pela rota mais curta usando uma abordagem heuristica, buscando reduzir a complexidade do código
    # A função recebe dois parâmetros, required_indices e distance_matrix, required_indices é uma lista de índices representando os locais que serão visitados, já distance_matrix é uma matriz de distâncias entre os locais i e j
    # A ideia dessa função é começar por um ponto e ir buscando o ponto mais próximo ainda não visitado, até que todos os pontos sejam visitados
    
    # Nessa parte a gente copia a lista dos índices para evitar modificarmos a lista original
    nao_visitado = indices_a_percorrer.copy()

    # Aqui nós começamos pelo primeiro ponto da lista e depois removemos ele dos não visitados
    rota = [nao_visitado.pop(0)] 

    # Também iniciamos com o custo zerado
    custo_total = 0
    
    # Enquanto houverem cidades não visitadas esse loop vai rodar
    while nao_visitado:
        # Pegamos a última cidade visitada pois sempre partimos a partir do último local
        cidade_atual = rota[-1]

        # Inicializamos cidade_mais_proxima como None e distancia_minima como infinito (float('inf')) para encontrar a cidade mais próxima.
        cidade_mais_proxima = None
        distancia_minima = float('inf')
        
        # Neste loop, para cada cidade não visitada, pegamos a distância entre a cidade atual e a cidade candidata (cidade). Se essa distância for menor que distancia_minima e maior que 0, atualizamos distancia_minima e cidade_mais_proxima. distance > 0 evita escolher um caminho inválido.
        for cidade in nao_visitado:
            distancia = matriz_distancia[cidade_atual][cidade]
            if distancia < distancia_minima and distancia > 0:
                distancia_minima = distancia
                cidade_mais_proxima = cidade
        

        # Se nenhuma cidade foi encontrada, escolhemos a primeira cidade não visitada e atribuímos a distância correspondente.
        if cidade_mais_proxima is None:
            cidade_mais_proxima = nao_visitado[0]
            distancia_minima = matriz_distancia[cidade_atual][cidade_mais_proxima]
            
        # Adicionamos a cidade encontrada à rota.    
        rota.append(cidade_mais_proxima)

        # Removemos essa cidade da lista de não visitadas.
        nao_visitado.remove(cidade_mais_proxima)

        # Adicionamos a distância mínima ao custo total.
        custo_total += distancia_minima
    
    return rota, custo_total

def caminho_mais_curto(cidades_obrigatorias, dicionario_cidades, matriz_distancia):  
    # Convertendo os nomes das cidades de cidades_obrigatorias para seus índices correspondentes na matriz_distancia. Isso facilita a busca na matriz de distâncias, pois as funções trabalham com índices numéricos
    indices_obrigatorios = [dicionario_cidades[city] for city in cidades_obrigatorias]
    
    melhor_rota = None # armazenará a melhor rota encontrada.
    custo_minimo = float('inf') # armazenará o menor custo encontrado, inicializado com infinito (float('inf')), garantindo que qualquer rota válida será menor.
    
    # Testamos todas as cidades como ponto de partida, percorrendo a lista indices_obrigatorios
    for indice_partida in range(len(indices_obrigatorios)):
        # A ideia aqui é rotacionar a lista de cidades obrigatórias: por exemplo, se indices_obrigatorios = [A, B, C, D], e indice_partida = 1, teremos
        # indices_rotacionados = [B, C, D, A]
        # Isso simula o caso de começar por B em vez de A, e assim por diante.
        indices_rotacionados = indices_obrigatorios[indice_partida:] + indices_obrigatorios[:indice_partida]
        
        # Chamamos a função find_nearest_neighbor_route, que encontra um caminho usando o algoritmo do vizinho mais próximo a partir da cidade inicial escolhida.
        rota, custo = vizinho_mais_proximo(indices_rotacionados, matriz_distancia)
        

        # Se o custo da nova rota (cost) for menor que min_cost, atualizamos

        if custo < custo_minimo:
            custo_minimo = custo # menor custo encontrado.
            melhor_rota = rota # melhor rota correspondente.
    
    return melhor_rota, custo_minimo

def main():
    # Lista de cidades obrigatórias
    cidades_obrigatorias = [
        "Buenos Aires", "Cordoba", "Rosario", "La Plata", "Mar del Plata",
        "San Miguel de Tucuman", "Salta", "Santa Fe de la Vera Cruz", "Vicente Lopez",
        "Corrientes", "Pilar", "Bahia Blanca", "Resistencia", "Posadas",
        "San Salvador de Jujuy", "Santiago del Estero", "Parana", "Merlo",
        "Neuquen", "Quilmes"
    ]
    
    print("Lendo as cidades dos arquivos...")
    lista_cidades = ler_cidades_de_arquivo("Cidades.txt")
    
    if not lista_cidades:
        print("Nenhuma cidade foi encontrada no arquivo.")
        return
    
    print(f"\nEncontrado {len(lista_cidades)} cidades no arquivo.")
    
    # Converte a lista de cidades em um dicionário de mapeamento {nome: índice}, facilitando buscas rápidas.
    dicionario_cidades = {cidade[0]: cidade[1] for cidade in lista_cidades}
    
    print("\nLendo o arquivo Caminho.txt...")
    # A função ler_mapa precisa converter os dados corretamente para formar a distance_matrix
    matriz_distancia = ler_mapa("Caminho.txt", dicionario_cidades, len(lista_cidades))
    
    try:
        # A função caminho_mais_curto encontra a melhor rota testando diferentes cidades como ponto de partida. Retorna a melhor sequência de cidades e o custo total da viagem.
        melhor_rota, custo_minimo = caminho_mais_curto(cidades_obrigatorias, dicionario_cidades, matriz_distancia)
        
        # Como caminho_mais_curto retorna os índices das cidades, precisamos converter os índices de volta para os nomes das cidades.
        # melhor_rota = [2, 0, 3, 1] 
        # indice_ate_cidade = {0: "Buenos Aires", 1: "Cordoba", 2: "Rosario", 3: "La Plata"}
        # rotas = ["Rosario", "Buenos Aires", "La Plata", "Cordoba"]
        indice_ate_cidade = {v: k for k, v in dicionario_cidades.items()}
        rotas = [indice_ate_cidade[i] for i in melhor_rota]
        
        # Resultados
        print("\nRota encontratada:")
        for i, cidade in enumerate(rotas, 1):
            print(f"{i}. {cidade}")
        print(f"\nCusto total: {custo_minimo}")
        
    except ValueError as e:
        print(f"\Erro: {e}")

if __name__ == "__main__":
    main()