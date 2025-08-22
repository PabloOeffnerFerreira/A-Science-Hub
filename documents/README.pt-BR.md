# A Science Hub (ASH)

## Visão Geral

A Science Hub é um aplicativo de desktop com ferramentas para física, química, biologia, geologia e matemática. Inclui calculadoras, conversores, simuladores e utilitários de referência. A interface é feita com PyQt6.

## Funcionalidades

* **Biologia**: busca de códons, conteúdo GC, tradução de quadros de leitura, transcrição/tradução, ferramentas de sequência, crescimento populacional, cálculo de pH, tonicidade osmótica
* **Química**: explorador de elementos, gráfico de propriedades, notação isotópica, massa molar, biblioteca de moléculas com visualizador 3D, preditor de fases, balanceador de reações, visualizador de camadas eletrônicas
* **Eletricidade**: força de Coulomb, calculadoras/visualizadores de campo elétrico e magnético, ajudante de circuito RC, Lei de Ohm, ferramentas de indução
* **Mecânica**: velocidade, aceleração, energia cinética, força de arrasto, movimento de projétil, velocidade terminal, equação de lentes/espelhos
* **Geologia**: explorador de minerais, identificador de minerais, datação radioativa, calculadora de meia-vida, designer de limites de placas, velocidade das placas
* **Matemática**: calculadora algébrica, plotador de funções, solucionador quadrático, solucionador de triângulos, calculadora vetorial
* **Ferramentas de Painel**: conversor de unidades, combinador/divisor de prefixos SI, algarismos significativos, conversor de notação, consulta de constantes, verificador de grandezas, calculadora científica, visualizador de log, busca rápida, gerenciador de janelas

## Estrutura

```
core/        # Lógica central, dados, bancos de dados, funções
UI/          # Painéis, janelas, assets
tools/       # Ferramentas por categoria
storage/     # Dados do usuário: logs, resultados, imagens, fórmulas, favoritos
documents/   # Documentação e notas de versão
misc/        # Testes, ajudantes, modelos
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```
