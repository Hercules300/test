from sympy.logic.boolalg import And, Or, Not
from graphviz import Digraph
import sympy

# Função para criar um circuito lógico a partir de uma expressão booleana
def gerar_circuito(expressao_logica):
    # Converte a expressão booleana para um objeto do sympy
    expressao = sympy.sympify(expressao_logica)
    
    # Cria o grafo
    dot = Digraph(comment='Circuito Lógico')
    dot.attr(rankdir='LR')  # Define a direção do gráfico (da esquerda para a direita)
    
    # Função recursiva para percorrer a expressão booleana e criar o circuito
    def criar_nodos(expr, parent=None):
        if isinstance(expr, sympy.Symbol):  # Caso seja uma variável booleana
            node_id = str(expr)
            dot.node(node_id, label=str(expr), shape='circle', color='lightblue', style='filled')
            if parent:
                dot.edge(node_id, parent)
            return node_id
        
        if isinstance(expr, Not):  # Porta NOT
            child = criar_nodos(expr.args[0])
            node_id = f"NOT_{id(expr)}"
            dot.node(node_id, label='NOT', shape='triangle', color='red', style='filled')
            dot.edge(child, node_id)
            if parent:
                dot.edge(node_id, parent)
            return node_id
        
        if isinstance(expr, And):  # Porta AND
            left = criar_nodos(expr.args[0])
            right = criar_nodos(expr.args[1])
            node_id = f"AND_{id(expr)}"
            dot.node(node_id, label='AND', shape='box', color='green', style='filled')
            dot.edge(left, node_id)
            dot.edge(right, node_id)
            if parent:
                dot.edge(node_id, parent)
            return node_id
        
        if isinstance(expr, Or):  # Porta OR
            left = criar_nodos(expr.args[0])
            right = criar_nodos(expr.args[1])
            node_id = f"OR_{id(expr)}"
            dot.node(node_id, label='OR', shape='box', color='yellow', style='filled')
            dot.edge(left, node_id)
            dot.edge(right, node_id)
            if parent:
                dot.edge(node_id, parent)
            return node_id

    # Inicia a criação do circuito
    criar_nodos(expressao)
    
    # Renderiza o grafo em formato de imagem
    dot.render('circuito_logico', format='png', cleanup=True)
    print("Circuito gerado com sucesso! A imagem foi salva como 'circuito_logico.png'.")

# Solicita a expressão booleana do usuário
print("Bem-vindo ao gerador de circuito lógico!")
print("Digite uma expressão booleana válida usando '&', '|', e '~'.")
print("Exemplo: ((C|D)&(~(A&B)))")
expressao_logica = input("Sua expressão: ")

try:
    gerar_circuito(expressao_logica)
except Exception as e:
    print("Erro ao processar a expressão booleana. Certifique-se de que ela está correta.")
    print(f"Detalhes do erro: {e}")
