import json
import sys
from collections import deque

def fecho_epsilon(estados, transicoes):
    fecho = set(estados)
    pilha = list(estados)
    
    while pilha:
        estado = pilha.pop()
        if estado in transicoes and 'ε' in transicoes[estado]:
            for prox in transicoes[estado]['ε']:
                if prox not in fecho:
                    fecho.add(prox)
                    pilha.append(prox)
    return fecho

def remover_epsilon(dados):
    print("Removendo transições epsilon...")
    
    alfabeto = set(dados['alfabeto']) - {'ε'}
    transicoes_novas = {}
    
    for estado in dados['estados']:
        transicoes_novas[estado] = {}
        fecho = fecho_epsilon({estado}, dados['transicoes'])
        
        for simbolo in alfabeto:
            destinos = set()
            for e in fecho:
                if e in dados['transicoes'] and simbolo in dados['transicoes'][e]:
                    for dest in dados['transicoes'][e][simbolo]:
                        destinos.update(fecho_epsilon({dest}, dados['transicoes']))
            if destinos:
                transicoes_novas[estado][simbolo] = list(destinos)
    
    finais_novos = []
    for estado in dados['estados']:
        fecho = fecho_epsilon({estado}, dados['transicoes'])
        if any(f in dados['estados_finais'] for f in fecho):
            finais_novos.append(estado)
    
    return {
        'tipo': 'AFN',
        'estados': dados['estados'],
        'alfabeto': list(alfabeto),
        'transicoes': transicoes_novas,
        'estado_inicial': dados['estado_inicial'],
        'estados_finais': finais_novos
    }

def determinizar(dados):
    print("Convertendo para AFD...")
    
    inicial = frozenset([dados['estado_inicial']])
    estados_novos = {inicial}
    fila = deque([inicial])
    transicoes_novas = {}
    
    while fila:
        estado_atual = fila.popleft()
        transicoes_novas[estado_atual] = {}
        
        for simbolo in dados['alfabeto']:
            destinos = set()
            for e in estado_atual:
                if e in dados['transicoes'] and simbolo in dados['transicoes'][e]:
                    destinos.update(dados['transicoes'][e][simbolo])
            
            if destinos:
                novo = frozenset(destinos)
                transicoes_novas[estado_atual][simbolo] = novo
                if novo not in estados_novos:
                    estados_novos.add(novo)
                    fila.append(novo)
    
    finais_novos = set()
    for estado in estados_novos:
        if any(e in dados['estados_finais'] for e in estado):
            finais_novos.add(estado)
    
    mapa = {e: f'q{i}' for i, e in enumerate(sorted(estados_novos))}
    
    return {
        'tipo': 'AFD',
        'estados': list(mapa.values()),
        'alfabeto': dados['alfabeto'],
        'transicoes': {mapa[e]: {s: mapa[d] for s, d in t.items()} 
                      for e, t in transicoes_novas.items()},
        'estado_inicial': mapa[inicial],
        'estados_finais': [mapa[e] for e in finais_novos]
    }

def minimizar(dados):
    print("Minimizando...")

    finais = set(dados['estados_finais'])
    nao_finais = set(dados['estados']) - finais
    
    particoes = []
    if nao_finais:
        particoes.append(frozenset(nao_finais))
    if finais:
        particoes.append(frozenset(finais))
    
    def achar_particao(estado):
        for i, p in enumerate(particoes):
            if estado in p:
                return i
        return -1
    
    mudou = True
    while mudou:
        mudou = False
        novas = []
        
        for particao in particoes:
            grupos = {}
            for estado in particao:
                assinatura = []
                for simbolo in sorted(dados['alfabeto']):
                    if estado in dados['transicoes'] and simbolo in dados['transicoes'][estado]:
                        destino = dados['transicoes'][estado][simbolo]
                        assinatura.append(achar_particao(destino))
                    else:
                        assinatura.append(-1)
                
                chave = tuple(assinatura)
                if chave not in grupos:
                    grupos[chave] = set()
                grupos[chave].add(estado)
            
            if len(grupos) > 1:
                mudou = True
            for g in grupos.values():
                novas.append(frozenset(g))
        
        particoes = novas
    
    mapa = {}
    for i, p in enumerate(particoes):
        for e in p:
            mapa[e] = f'q{i}'
    
    trans_novas = {}
    for estado in set(mapa.values()):
        trans_novas[estado] = {}
    
    for e_orig, trans in dados['transicoes'].items():
        e_novo = mapa[e_orig]
        for simbolo, destino in trans.items():
            trans_novas[e_novo][simbolo] = mapa[destino]
    
    return {
        'tipo': 'AFD-Minimo',
        'estados': list(set(mapa.values())),
        'alfabeto': dados['alfabeto'],
        'transicoes': trans_novas,
        'estado_inicial': mapa[dados['estado_inicial']],
        'estados_finais': [mapa[e] for e in dados['estados_finais']]
    }

def processar(arquivo):
    print(f"\nProcessando: {arquivo}")
    print("-" * 40)
    
    with open(arquivo, encoding='utf-8') as f:
        dados = json.load(f)
    
    print(f"Tipo: {dados['tipo']}")
    print(f"Estados: {len(dados['estados'])}")
    
    for estado in dados['transicoes']:
        for simbolo in dados['transicoes'][estado]:
            if isinstance(dados['transicoes'][estado][simbolo], list):
                dados['transicoes'][estado][simbolo] = dados['transicoes'][estado][simbolo]
    
    if dados['tipo'] == 'AFNe':
        dados = remover_epsilon(dados)
        print(f"→ AFN: {len(dados['estados'])} estados")
    
    if dados['tipo'] == 'AFN':
        dados = determinizar(dados)
        print(f"→ AFD: {len(dados['estados'])} estados")
    
    if dados['tipo'] == 'AFD':
        dados = minimizar(dados)
        print(f"→ Mínimo: {len(dados['estados'])} estados")
    
    saida = arquivo.replace('.json', '_resultado.json')
    with open(saida, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Salvo em: {saida}")
    print("-" * 40)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        arquivo = input("Arquivo de entrada: ")
    else:
        arquivo = sys.argv[1]
    
    processar(arquivo)
