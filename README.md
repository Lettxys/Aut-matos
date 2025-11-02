# Minimização de Autômatos Finitos Determinísticos

**Disciplina:** Linguagens Formais e Autômatos  
**Instituição:** UFC - Campus Crateús  
**Professor:** Rafael Martins Barros

---

## Descrição do Projeto

Este programa implementa um sistema completo para conversão e minimização de autômatos finitos, realizando automaticamente:

1. **AFNε → AFN**: Remoção de transições epsilon (ε)
2. **AFN → AFD**: Determinização usando construção de subconjuntos
3. **AFD → AFD Mínimo**: Minimização usando algoritmo de particionamento por equivalência

O programa **detecta automaticamente** o tipo de autômato de entrada e aplica as conversões necessárias até obter o **AFD mínimo equivalente**.

---

## Como Executar

### Requisitos
- **Python 3.6 ou superior**
- Nenhuma biblioteca externa (usa apenas módulos padrão: `json`, `sys`, `collections`)

### Modo 1: Linha de Comando

```bash
python minimizacao_automatos.py arquivo_entrada.json
```

**Exemplos:**
```bash
python minimizacao_automatos.py exemplo_afn.json
python minimizacao_automatos.py exemplo_afne.json
python minimizacao_automatos.py exemplo_afd.json
```

O resultado será salvo como `arquivo_entrada_resultado.json`

### Modo 2: Interativo

Execute sem argumentos:

```bash
python minimizacao_automatos.py
```

O programa solicitará o nome do arquivo de entrada.

---

## FORMATO DE ENTRADA E SAÍDA

### Estrutura do Arquivo JSON

Os autômatos são representados em arquivos **JSON** seguindo esta estrutura:

```json
{
  "tipo": "AFN",
  "estados": ["q0", "q1", "q2"],
  "alfabeto": ["a", "b"],
  "transicoes": {
    "q0": {
      "a": ["q0", "q1"],
      "b": ["q0"]
    },
    "q1": {
      "b": ["q2"]
    },
    "q2": {}
  },
  "estado_inicial": "q0",
  "estados_finais": ["q2"]
}
```

### Descrição dos Campos

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| **tipo** | String | Tipo do autômato | `"AFNe"`, `"AFN"` ou `"AFD"` |
| **estados** | Lista | Nomes dos estados | `["q0", "q1", "q2"]` |
| **alfabeto** | Lista | Símbolos do alfabeto | `["a", "b"]` ou `["a", "b", "ε"]` |
| **transicoes** | Objeto | Função de transição | Ver detalhes abaixo |
| **estado_inicial** | String | Estado onde começa | `"q0"` |
| **estados_finais** | Lista | Estados de aceitação | `["q2"]` |

### Formato das Transições

As transições seguem a estrutura:

```json
"transicoes": {
  "estado_origem": {
    "simbolo": ["estado_destino1", "estado_destino2", ...]
  }
}
```

**Exemplos:**

**AFN (múltiplos destinos):**
```json
"q0": {
  "a": ["q0", "q1"],  ← múltiplos destinos (não-determinismo)
  "b": ["q0"]
}
```

**AFD (único destino):**
```json
"q0": {
  "a": "q1",  ← único destino (apenas string)
  "b": "q0"
}
```

**AFNε (com epsilon):**
```json
"q0": {
  "ε": ["q1"],  ← transição vazia
  "a": ["q0"]
}
```

**Estados sem transições:**
```json
"q2": {}  ← estado sem saídas (estado final, geralmente)
```

### Tipos de Autômato Aceitos

1. **`"AFNe"`** - Autômato Finito Não Determinístico com ε-transições
   - Alfabeto deve incluir `"ε"`
   - Pode ter transições vazias
   - Pode ter não-determinismo

2. **`"AFN"`** - Autômato Finito Não Determinístico
   - Não tem transições ε
   - Pode ter não-determinismo (múltiplos destinos)

3. **`"AFD"`** - Autômato Finito Determinístico
   - Cada estado tem exatamente uma transição por símbolo
   - Sem não-determinismo

### Formato de Saída

O arquivo de saída terá o **mesmo formato** da entrada, mas com:
- `"tipo": "AFD-Minimo"`
- Número reduzido de estados
- Estados renomeados sequencialmente (q0, q1, q2, ...)
- Transições determinísticas

**Exemplo de saída:**
```json
{
  "tipo": "AFD-Minimo",
  "estados": ["q0", "q1", "q2"],
  "alfabeto": ["a", "b"],
  "transicoes": {
    "q0": {"a": "q1", "b": "q0"},
    "q1": {"a": "q2", "b": "q2"},
    "q2": {"a": "q2", "b": "q2"}
  },
  "estado_inicial": "q0",
  "estados_finais": ["q2"]
}
```

---

## ESTRUTURA DE DADOS UTILIZADA

### Representação Interna

O programa utiliza as seguintes estruturas de dados Python:

#### 1. **Estados**
```python
estados: set
# Exemplo: {'q0', 'q1', 'q2'}
```
- **Tipo:** Conjunto (set)
- **Justificativa:** Operações de união e interseção são O(1), essenciais para algoritmos

#### 2. **Alfabeto**
```python
alfabeto: set
# Exemplo: {'a', 'b'}
```
- **Tipo:** Conjunto (set)
- **Justificativa:** Verificação rápida de pertinência, evita duplicatas

#### 3. **Transições**
```python
transicoes: dict[str, dict[str, list]]
# Exemplo:
{
    'q0': {'a': ['q0', 'q1'], 'b': ['q0']},
    'q1': {'b': ['q2']},
    'q2': {}
}
```
- **Tipo:** Dicionário de dicionários de listas
- **Estrutura:** `{estado: {simbolo: [lista_destinos]}} ou {estado: {simbolo: destino}}`
- **Justificativa:**
  - **Acesso O(1):** `transicoes[estado][simbolo]` é instantâneo
  - **Flexibilidade:** Suporta AFN (múltiplos destinos) e AFD (único destino)
  - **Compatibilidade JSON:** Listas podem ser facilmente serializadas

#### 4. **Estado Inicial**
```python
estado_inicial: str
# Exemplo: 'q0'
```
- **Tipo:** String
- **Justificativa:** Único estado, referência simples

#### 5. **Estados Finais**
```python
estados_finais: list
# Exemplo: ['q2', 'q3']
```
- **Tipo:** Lista (convertida internamente para set)
- **Justificativa:** Verificação rápida se um estado é final

### Estruturas Auxiliares nos Algoritmos

#### Construção de Subconjuntos (AFN → AFD)
```python
frozenset
# Exemplo: frozenset({'q0', 'q1'})
```
- **Tipo:** Conjunto imutável
- **Uso:** Representa estados do AFD (que são conjuntos de estados do AFN)
- **Justificativa:** Imutável, pode ser chave de dicionário

#### Particionamento (Minimização)
```python
particoes: list[frozenset]
# Exemplo: [frozenset({'q0'}), frozenset({'q1', 'q2'}), frozenset({'q3', 'q4'})]
```
- **Tipo:** Lista de conjuntos imutáveis
- **Uso:** Grupos de estados equivalentes
- **Justificativa:** Fácil iteração e refinamento

---

## Algoritmos Implementados

### 1. Remoção de ε-transições (AFNε → AFN)

**Função:** `fecho_epsilon(estados, transicoes)`

**Objetivo:** Calcular o fecho-ε (epsilon-closure) de um conjunto de estados.

**Algoritmo:**
```
1. Inicializar fecho = estados de entrada
2. Usar pilha para DFS:
   - Para cada estado na pilha
   - Se tem transição ε, adicionar destinos ao fecho
   - Continuar até pilha vazia
3. Retornar fecho completo
```

**Exemplo:**
```
Estado q0 com ε → q1
fecho-ε(q0) = {q0, q1}

Estado q2 com ε → q3, q3 com ε → q4
fecho-ε(q2) = {q2, q3, q4}
```

**Função:** `remover_epsilon(dados)`

**Algoritmo:**
```
Para cada estado q:
    1. Calcular F = fecho-ε(q)
    2. Para cada símbolo a (exceto ε):
        - Para cada estado r em F:
            - Se r tem transição com 'a' para p:
                - Adicionar fecho-ε(p) aos destinos de δ'(q, a)
    3. Se F ∩ estados_finais ≠ ∅:
        - q é estado final no novo AFN
```

**Complexidade:** O(n³) onde n = número de estados

---

### 2. Determinização (AFN → AFD)

**Função:** `determinizar(dados)`

**Objetivo:** Converter AFN para AFD usando construção de subconjuntos.

**Algoritmo:**
```
1. Q₀ = {q₀}  (conjunto com estado inicial)
2. Fila = [Q₀]
3. Enquanto Fila não vazia:
   - Q = Fila.pop()
   - Para cada símbolo 'a':
       - T = ∪{δ(q, a) | q ∈ Q}
       - Se T novo, adicionar à Fila
       - δ'(Q, a) = T
4. Estados finais: Q onde Q ∩ F ≠ ∅
5. Renomear conjuntos para q0, q1, q2, ...
```

**Exemplo:**
```
AFN:
  q0 --a--> {q0, q1}
  q0 --b--> {q0}
  q1 --b--> {q2}

AFD:
  Estados: {q0}, {q0,q1}, {q0,q2}
  Renomeado: q0, q1, q2
```

**Complexidade:** O(2ⁿ × |Σ|) no pior caso (exponencial)

---

### 3. Minimização (AFD → AFD Mínimo)

**Função:** `minimizar(dados)`

**Objetivo:** Reduzir o número de estados fundindo equivalentes.

**Algoritmo:**
```
1. P = [{não-finais}, {finais}]  (partição inicial)

2. Repetir até convergir:
   Para cada partição Pᵢ:
     - Dividir estados com diferentes "assinaturas"
     - Assinatura = para onde vão com cada símbolo
   
3. Se dois estados têm mesma assinatura:
   - Estão na mesma partição (são equivalentes)

4. Cada partição final → um estado do AFD mínimo

5. Construir transições usando representantes
```

**Exemplo de assinatura:**
```
Estado q1:
  - Com 'a' vai para partição 2
  - Com 'b' vai para partição 2
  - Assinatura: (2, 2)

Estado q2:
  - Com 'a' vai para partição 2
  - Com 'b' vai para partição 2
  - Assinatura: (2, 2)

Logo q1 ≡ q2 (equivalentes, podem ser fundidos)
```

**Complexidade:** O(n² × |Σ|) onde n = número de estados

---

## Exemplos Práticos

### Exemplo 1: AFN

**Entrada:** `exemplo_afn.json`
```json
{
  "tipo": "AFN",
  "estados": ["q0", "q1", "q2"],
  "alfabeto": ["a", "b"],
  "transicoes": {
    "q0": {
      "a": ["q0", "q1"],
      "b": ["q0"]
    },
    "q1": {
      "b": ["q2"]
    },
    "q2": {}
  },
  "estado_inicial": "q0",
  "estados_finais": ["q2"]
}
```

**Comando:**
```bash
python minimizacao_automatos.py exemplo_afn.json
```

**Saída:** `exemplo_afn_resultado.json` (AFD mínimo)

**Linguagem reconhecida:** Palavras que terminam com "ab"

---

### Exemplo 2: AFNε

**Entrada:** `exemplo_afne.json`
```json
{
  "tipo": "AFNe",
  "estados": ["q0", "q1", "q2", "q3"],
  "alfabeto": ["a", "b", "ε"],
  "transicoes": {
    "q0": {
      "ε": ["q1"],
      "a": ["q0"]
    },
    "q1": {
      "b": ["q2"]
    },
    "q2": {
      "ε": ["q3"],
      "a": ["q2"]
    },
    "q3": {
      "b": ["q3"]
    }
  },
  "estado_inicial": "q0",
  "estados_finais": ["q3"]
}
```

**Comando:**
```bash
python minimizacao_automatos.py exemplo_afne.json
```

**Processo:**
1. Remove ε-transições → AFN
2. Determiniza → AFD  
3. Minimiza → AFD mínimo

---

### Exemplo 3: AFD

**Entrada:** `exemplo_afd.json`
```json
{
  "tipo": "AFD",
  "estados": ["q0", "q1", "q2", "q3", "q4"],
  "alfabeto": ["a", "b"],
  "transicoes": {
    "q0": {"a": "q1", "b": "q2"},
    "q1": {"a": "q3", "b": "q4"},
    "q2": {"a": "q3", "b": "q4"},
    "q3": {"a": "q3", "b": "q3"},
    "q4": {"a": "q4", "b": "q4"}
  },
  "estado_inicial": "q0",
  "estados_finais": ["q3", "q4"]
}
```

**Comando:**
```bash
python minimizacao_automatos.py exemplo_afd.json
```

**Resultado:**
- Estados q1 ≡ q2 (equivalentes) → fundidos
- Estados q3 ≡ q4 (equivalentes) → fundidos
- 5 estados → 3 estados (40% redução)

---

## Fundamentação Teórica

### Equivalência de Estados

Dois estados p e q são **equivalentes** se:
- Para toda palavra w, δ(p,w) e δ(q,w) levam **ambos** a estados finais ou **ambos** a não-finais

O algoritmo de minimização identifica e funde estados equivalentes.

### Teoremas Importantes

1. **Unicidade:** O AFD mínimo é único a menos de renomeação de estados
2. **Completude:** Todo AFN/AFNε pode ser convertido para AFD equivalente
3. **Otimalidade:** O AFD mínimo tem o menor número possível de estados

---

## Equipe

**Equipe:**
- Leticia Almeida Lima
- Isabelli Araujo Pinho
- Elislandia Aparecida Horlanda da Silva

**Professor:** Rafael Martins Barros  
**Instituição:** Universidade Federal do Ceará - Campus Crateús  
**Disciplina:** Linguagens Formais e Autômatos

---

## Bibliografia

1. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation*. Pearson.
2. Sipser, M. (2012). *Introduction to the Theory of Computation*. Cengage Learning.
3. Menezes, P. B. (2011). *Linguagens Formais e Autômatos*. Bookman.
