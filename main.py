import numpy as np
import openpyxl
def ler_cidades_de_arquivo(nome_arquivo):
    try:
        lista_cidades = []
        i = 0
        with open(nome_arquivo, "r", encoding='utf-8') as arquivo: # Abre o arquivo para leitura
            for linha in arquivo: # Lê cada linha do arquivo
                cidade = (linha.strip(), i) # Remove espaços em branco e atribui um índice para a cidade
                lista_cidades.append(cidade) # Adiciona a cidade à lista de cidades
                i+=1 # Incrementa o índice
        return lista_cidades
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []

def ler_mapa(nome_arquivo, cidades_lidas, quantidade_cidades):
    mapa = np.full((quantidade_cidades, quantidade_cidades), float('inf'))  # Usar infinito ao invés de zero
    np.fill_diagonal(mapa, 0)  # Distância de uma cidade para ela mesma é zero
    try:
        with open(nome_arquivo, "r", encoding='utf-8') as arquivo:  # Abre o arquivo para leitura
            linhas = arquivo.readlines()  # Lê todas as linhas do arquivo
            for linha in linhas:  # Para cada linha do arquivo
                cidade_info = linha.strip().split(",")  # Remove espaços em branco e divide a linha em uma lista
                print(cidade_info)
                try:
                    if len(cidade_info) == 3:  # Se a lista tiver 3 elementos
                        origem, destino, custo = cidade_info  # Atribui os elementos a origem, destino e custo
                        if mapa[cidades_lidas[origem]][cidades_lidas[destino]] == float('inf'):
                            mapa[cidades_lidas[origem]][cidades_lidas[destino]] = int(custo)  # Adiciona o custo à matriz
                except:
                    print("Erro ao processar linha:", linha)
        return mapa
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []
    

def salvar_escolhas_excel(escolhas, nome_arquivo="escolhas.xlsx"):
    # Cria uma nova planilha Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Escolhas"

    # Adiciona os cabeçalhos
    ws.append(["Cidade Atual", "Cidade Mais Próxima", "Distância"])

    # Adiciona os dados das escolhas
    print(f"Total de escolhas: {len(escolhas)}")  # Debugging line
    for escolha in escolhas:
        ws.append(escolha)

    # Salva o arquivo Excel
    wb.save(nome_arquivo)
    print(f"Escolhas salvas em {nome_arquivo}")


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
    escolhas = []
    # Enquanto houverem cidades não visitadas esse loop vai rodar
    while nao_visitado:
        # Pegamos a última cidade visitada pois sempre partimos a partir do último local
        cidade_atual = rota[-1]

        # Inicializamos cidade_mais_proxima como None e distancia_minima como infinito (float('inf')) para encontrar a cidade mais próxima.
        cidade_mais_proxima = None
        distancia_minima = float('inf')
        
        # Neste loop, para cada cidade não visitada, pegamos a distância entre a cidade atual e a cidade candidata (cidade). Se essa distância for menor que distancia_minima e maior que 0, atualizamos distancia_minima e cidade_mais_proxima. distance > 0 evita escolher um caminho inválido.
        for cidade in nao_visitado: 
            distancia = matriz_distancia[cidade_atual][cidade] # Calcula a distância entre a cidade atual e a cidade candidata
            if distancia != float('inf') and distancia > 0:
                print(f"Valid path found: {cidade_atual} -> {cidade}, Distance: {distancia}")
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    cidade_mais_proxima = cidade
                    print(f"New best choice: {cidade_atual} -> {cidade_mais_proxima}, Distance: {distancia}")

        # Se nenhuma cidade foi encontrada, escolhemos a primeira cidade não visitada e atribuímos a distância correspondente.
        if cidade_mais_proxima is None:
            print(f"No direct path found from city {cidade_atual}. Looking for any valid connection...")
            for cidade in nao_visitado:
                # Check all remaining unvisited cities for ANY valid connection
                distancia = matriz_distancia[cidade_atual][cidade]
                if distancia != float('inf') and distancia > 0:
                    cidade_mais_proxima = cidade
                    distancia_minima = distancia
                    print(f"Found alternative path: {cidade_atual} -> {cidade_mais_proxima}, Distance: {distancia}")
                    break
        
        if cidade_mais_proxima is None:
            print(f"Warning: No valid path found from city {cidade_atual} to any remaining city")
            # Choose the first unvisited city and check if there's a path in either direction
            cidade_mais_proxima = nao_visitado[0]
            distancia_direta = matriz_distancia[cidade_atual][cidade_mais_proxima]
            if distancia_direta == float('inf') or distancia_direta <= 0:
                print(f"Using fallback path to continue route")
                distancia_minima = float('inf')

        # Adicionamos a cidade encontrada à rota.    
        rota.append(cidade_mais_proxima)

        # Removemos essa cidade da lista de não visitadas.
        nao_visitado.remove(cidade_mais_proxima)

        # Adicionamos a distância mínima ao custo total.
        if distancia_minima != float('inf'):
            custo_total += distancia_minima
            escolhas.append((cidade_atual, cidade_mais_proxima, distancia_minima))
    salvar_escolhas_excel(escolhas)
    return rota, custo_total # Retorna a rota e o custo total

def caminho_mais_curto(cidades_obrigatorias, dicionario_cidades, matriz_distancia):  
    # Convertendo os nomes das cidades de cidades_obrigatorias para seus índices correspondentes na matriz_distancia. Isso facilita a busca na matriz de distâncias, pois as funções trabalham com índices numéricos
    indices_obrigatorios = [dicionario_cidades[cidade] for cidade in cidades_obrigatorias]
    
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
        

        # Se o custo da nova rota (custo) for menor que min_cost, atualizamos
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
    
    lista_cidades = ler_cidades_de_arquivo("Cidades.txt")
    if not lista_cidades:
        print("Nenhuma cidade foi encontrada no arquivo.")
        return
    
    # Converte a lista de cidades em um dicionário de mapeamento {nome: índice}, facilitando buscas rápidas.
    dicionario_cidades = {cidade[0]: cidade[1] for cidade in lista_cidades}
    print(dicionario_cidades)
    print("quantidade de cidades: ", len(lista_cidades))
    # A função ler_mapa precisa converter os dados corretamente para formar a distance_matrix
    matriz_distancia = ler_mapa("Caminho.txt", dicionario_cidades, len(lista_cidades)) # Lê o mapa e retorna a matriz de distâncias
     
    try:
        # A função caminho_mais_curto encontra a melhor rota testando diferentes cidades como ponto de partida. Retorna a melhor sequência de cidades e o custo total da viagem.
        melhor_rota, custo_minimo = caminho_mais_curto(cidades_obrigatorias, dicionario_cidades, matriz_distancia) # Encontra a melhor rota e o custo total
        
        # Como caminho_mais_curto retorna os índices das cidades, precisamos converter os índices de volta para os nomes das cidades.
        # melhor_rota = [2, 0, 3, 1] 
        # indice_ate_cidade = {0: "Buenos Aires", 1: "Cordoba", 2: "Rosario", 3: "La Plata"}
        # rotas = ["Rosario", "Buenos Aires", "La Plata", "Cordoba"]

        if melhor_rota is None:  # Check if no route was found
            print("Não foi possível encontrar uma rota válida.")
        else:
            indice_ate_cidade = {v: k for k, v in dicionario_cidades.items()}
            rotas = [indice_ate_cidade[i] for i in melhor_rota]
            
            # Resultados
            print("\nRota encontrada:")
            for i, cidade in enumerate(rotas, 1):
                print(f"{i}. {cidade}")
            print(f"\nCusto total: {custo_minimo}")
        
    except ValueError as e:
        print(f"\Erro: {e}")

if __name__ == "__main__":
    main()