import numpy as np
import openpyxl

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
    """
    Lê um arquivo contendo informações sobre um mapa de cidades e retorna uma matriz de custos entre as cidades.
    
    Parâmetros:
        nome_arquivo (str): Nome do arquivo que contém os dados do mapa no formato "cidade_origem,cidade_destino,custo".
        cidades_lidas (dict): Dicionário que mapeia os nomes das cidades para seus respectivos índices na matriz.
        quantidade_cidades (int): Número total de cidades envolvidas no mapa.

    Retorna:
        numpy.ndarray: Uma matriz quadrada (quantidade_cidades x quantidade_cidades) contendo os custos de viagem entre as cidades.
                       Se uma cidade não possui conexão direta com outra, o valor será `inf` (infinito), exceto na diagonal principal,
                       que representa o custo de uma cidade para ela mesma e é sempre 0.
    """
    # Criamos uma matriz de tamanho (quantidade_cidades x quantidade_cidades) preenchida com infinito,
    # representando que, inicialmente, todas as cidades estão desconectadas.
    mapa = np.full((quantidade_cidades, quantidade_cidades), float('inf'))
    
    # Preenchemos a diagonal principal com 0, pois o custo de uma cidade para ela mesma é sempre zero.
    np.fill_diagonal(mapa, 0)
    
    try:
        # Tentamos abrir o arquivo fornecido.
        with open(nome_arquivo, "r", encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()  # Lemos todas as linhas do arquivo e armazenamos em uma lista.
            
            for linha in linhas:  # Iteramos sobre cada linha do arquivo.
                cidade_info = linha.strip().split(",")  # Removemos espaços extras e dividimos os dados por vírgula.
                
                try:
                    # Verificamos se a linha contém exatamente 3 elementos (cidade origem, destino e custo).
                    if len(cidade_info) == 3:
                        origem, destino, custo = cidade_info  # Atribuímos os valores às variáveis.
                        
                        # Atualizamos a matriz com o custo da viagem entre as cidades, convertendo o custo para inteiro.
                        mapa[cidades_lidas[origem]][cidades_lidas[destino]] = int(custo)
                except:
                    # Caso ocorra um erro ao processar a linha, informamos qual linha causou o problema.
                    print("Erro ao processar linha:", linha)
        
        return mapa  # Retornamos a matriz preenchida com os custos das viagens.
    
    except FileNotFoundError:
        # Se o arquivo não for encontrado, informamos ao usuário e retornamos uma lista vazia.
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []

def avaliar_conectividade(cidade, matriz):
    # Esta função avalia a conectividade de uma cidade específica em uma matriz de adjacência.
    # Ela retorna a quantidade de cidades conectadas à cidade especificada como:
    # (1) Conectividade de saída: Número de cidades que podem ser alcançadas a partir dela.
    # (2) Conectividade de entrada: Número de cidades que têm caminhos até ela.

    # Calcula a conectividade de saída:
    # A conectividade de saída é a quantidade de valores na linha correspondente à cidade
    # que não são infinito ('inf') e são maiores que zero.
    # Isso indica a existência de uma conexão válida de "cidade" para outra cidade.
    saidas = sum(
        1 for x in matriz[cidade] # Itera pelos valores na linha correspondente à cidade.
        if x != float('inf') and x > 0 # Verifica se o valor indica uma conexão válida
    ) 
    # Calcula a conectividade de entrada:
    # A conectividade de entrada é a quantidade de valores na coluna correspondente à cidade
    # que não são infinito ('inf') e são maiores que zero.
    # Isso indica a existência de uma conexão válida de outra cidade para "cidade".
    entradas = sum(
        1 for row in matriz # Itera pelas linhas da matriz.
        if row[cidade] != float('inf') and row[cidade] > 0) # Verifica a coluna correspondente.
    # Retorna os valores calculados de conectividade de saída e entrada como uma tupla.
    return saidas, entradas 

def encontrar_rota(matriz, cidades_obrig, dict_cidades):
    """
    Encontra a melhor rota que passa por todas as cidades obrigatórias utilizando backtracking.

    Parâmetros:
    - matriz: Matriz de adjacência representando os custos entre as cidades.
    - cidades_obrig: Lista das cidades que devem ser visitadas obrigatoriamente.
    - dict_cidades: Dicionário que mapeia o nome das cidades para seus índices na matriz.

    Retorno:
    - melhor_rota: Lista contendo os índices das cidades na melhor ordem de visitação.
    - melhor_custo: Custo total da melhor rota encontrada.
    """
    # Converte os nomes das cidades obrigatórias em seus respectivos índices na matriz.
    indices = [dict_cidades[cidade] for cidade in cidades_obrig]

    # Quantidade total de cidades obrigatórias a serem visitadas.
    n_cidades = len(indices)

    # Variáveis para armazenar a melhor rota e o menor custo encontrados.
    melhor_rota = None # Melhor rota encontrada
    melhor_custo = float('inf') # Inicializa com infinito para garantir que qualquer caminho válido seja melhor.
    
    def calcular_custo_parcial(rota):
        """
        Calcula o custo total de uma rota somando os custos entre as cidades visitadas na sequência.

        Parâmetros:
        - rota: Lista de índices das cidades na ordem de visita.

        Retorno:
        - custo: O custo total da rota.
        """
        custo = 0 # Custo total
        for i in range(len(rota) - 1): # Percorre os pares de cidades consecutivas na rota.
            custo += matriz[rota[i]][rota[i + 1]] # Adiciona o custo de viajar entre elas.
        return custo # Retorna o custo total
    
    def backtrack(rota_atual, visitadas, custo_atual):
        """
        Implementa um algoritmo de busca usando backtracking para encontrar a melhor rota.

        Parâmetros:
        - rota_atual: Lista das cidades visitadas até o momento.
        - visitadas: Conjunto das cidades que já foram visitadas.
        - custo_atual: Custo acumulado da rota até o momento.

        Essa função modifica as variáveis `melhor_rota` e `melhor_custo` caso encontre uma rota melhor.
        """
        nonlocal melhor_rota, melhor_custo # Permite modificar as variáveis globais dentro da função.
        
        # Se o custo atual já for maior que o melhor custo encontrado, não vale a pena continuar a busca.
        if custo_atual >= melhor_custo:
            return # Interrompe a execução dessa ramificação do backtracking.
            
        # Se todas as cidades obrigatórias foram visitadas, verifica se a rota atual é a melhor.
        if len(rota_atual) == n_cidades: 
            melhor_rota = rota_atual.copy() # Atualiza a melhor rota
            melhor_custo = custo_atual # Atualiza o melhor custo
            return # Interrompe essa chamada do backtracking.
            
        cidade_atual = rota_atual[-1] # Obtém a última cidade visitada na rota.
        proximas_cidades = [] # Lista para armazenar as cidades possíveis para o próximo passo.
        
        # Identifica as cidades obrigatórias que ainda não foram visitadas e que possuem conexão válida.
        for cidade in indices: # Para cada cidade obrigatória
            if cidade not in visitadas: # Se a cidade não foi visitada
                custo = matriz[cidade_atual][cidade] # Custo da viagem
                if custo != float('inf'): # Se a viagem é possível
                    saidas, _ = avaliar_conectividade(cidade, matriz) # Conectividade da cidade
                    # Calcula um score para priorizar cidades com maior conectividade e menor custo.
                    score = (1000 / (custo + 1)) * (saidas + 1) 
                    # Adiciona a cidade e seu score à lista de próximas cidades.
                    proximas_cidades.append((cidade, score))
        
        # Ordena as próximas cidades com base no score, da maior para a menor.
        # Isso melhora a eficiência da busca ao priorizar cidades mais conectadas e com menor custo.
        proximas_cidades.sort(key=lambda x: x[1], reverse=True) # Ordena as cidades por score
        
        # Tenta visitar cada uma das cidades possíveis, na ordem definida pelo score.
        for cidade, _ in proximas_cidades:
            custo = matriz[cidade_atual][cidade] # Obtém o custo de viajar para a cidade selecionada.
            nova_rota = rota_atual + [cidade]   # Cria uma nova rota incluindo a nova cidade.
            novo_custo = custo_atual + custo # Atualiza o custo total da nova rota.
            
            # Se o novo custo for menor que o melhor custo encontrado, continua a busca recursivamente.
            if novo_custo < melhor_custo:
                backtrack(nova_rota, visitadas | {cidade}, novo_custo)  # Chamada recursiva com a nova rota.
    
    # Define Buenos Aires como ponto de partida.
    inicio = dict_cidades["Buenos Aires"] # Obtém o índice de Buenos Aires no dicionário.
    # Inicia a busca pela melhor rota a partir de Buenos Aires.
    backtrack([inicio], {inicio}, 0)
    
    # Retorna a melhor rota encontrada e seu custo total.
    return melhor_rota, melhor_custo

def main():
    cidades_obrigatorias = [
        "Buenos Aires", "Cordoba", "Rosario", "La Plata", "Mar del Plata",
        "San Miguel de Tucuman", "Salta", "Santa Fe de la Vera Cruz", "Vicente Lopez",
        "Corrientes", "Pilar", "Bahia Blanca", "Resistencia", "Posadas",
        "San Salvador de Jujuy", "Santiago del Estero", "Parana", "Merlo",
        "Neuquen", "Quilmes"
    ]
    
    lista_cidades = ler_cidades_de_arquivo("Cidades.txt")
    if not lista_cidades:
        return
        
    dict_cidades = {cidade[0]: cidade[1] for cidade in lista_cidades} # Dicionário de cidades
    matriz_distancia = ler_mapa("Caminho.txt", dict_cidades, len(lista_cidades)) # Matriz de distâncias
    
    rota, custo = encontrar_rota(matriz_distancia, cidades_obrigatorias, dict_cidades) # Encontra a melhor rota
    
    if rota: # Se uma rota foi encontrada
        print("\nRota encontrada:") # Exibe a rota
        dict_reverso = {v: k for k, v in dict_cidades.items()} # Dicionário reverso
        for i, cidade_idx in enumerate(rota, 1): # Para cada cidade na rota
            print(f"{i}. {dict_reverso[cidade_idx]}") # Exibe a cidade
        print(f"\nCusto total: {custo}")    # Exibe o custo total
         
        # Save to Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Ordem", "Cidade", "Custo até próxima"])
        
        for i in range(len(rota)):
            cidade_atual = dict_reverso[rota[i]] # Cidade atual
            custo_proximo = matriz_distancia[rota[i]][rota[i+1]] if i < len(rota)-1 else 0 # Custo até a próxima cidade
            ws.append([i+1, cidade_atual, custo_proximo]) # Adiciona a linha
            
        wb.save("rota_final.xlsx")
        print("\nRota salva em rota_final.xlsx")
    else:
        print("Não foi possível encontrar uma rota válida.")

if __name__ == "__main__":
    main()