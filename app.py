import os
from flask import Flask, render_template, request, send_from_directory
from sympy.logic.boolalg import And, Or, Not
from sympy import symbols, sympify
from graphviz import Digraph

app = Flask(__name__)

# Caminho absoluto para evitar erros de permissão
IMAGES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'images'))

# Garante que o diretório exista
if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

# Função para validar a expressão
def validar_expressao(expressao):
    stack = []
    for char in expressao:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

# Função para formatar a expressão lógica
def formatar_expressao(expressao_logica):
    # Substituir operadores para o formato desejado
    expressao_formatada = expressao_logica.replace("&", "^").replace("|", "v").replace("~", "¬")
    return expressao_formatada

# Função para avaliar a expressão lógica com SymPy
def avaliar_expressao(expressao_logica):
    # Criar símbolos genéricos
    variaveis = {char: symbols(char) for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    # Avaliar a expressão lógica usando SymPy
    expressao_avaliada = sympify(
        expressao_logica,
        locals=variaveis
    )
    return expressao_avaliada

# Função para gerar o circuito
def gerar_circuito(expressao_logica):
    expressao = avaliar_expressao(expressao_logica)
    dot = Digraph(comment='Circuito Lógico')
    dot.attr(rankdir='LR')  # Define a direção do gráfico

    ultima_saida = None

    def criar_nodos(expr, parent=None):
        nonlocal ultima_saida
        if expr.is_Symbol:  # Verifica se é um símbolo
            node_id = str(expr)
            dot.node(node_id, label=str(expr), shape='circle', color='lightblue', style='filled')
            if parent:
                dot.edge(node_id, parent)
            ultima_saida = node_id
            return node_id

        if isinstance(expr, Not):  # Porta NOT
            child = criar_nodos(expr.args[0])
            node_id = f"NOT_{id(expr)}"
            dot.node(node_id, label='NOT', shape='triangle', color='red', style='filled')
            dot.edge(child, node_id)
            if parent:
                dot.edge(node_id, parent)
            ultima_saida = node_id
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
            ultima_saida = node_id
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
            ultima_saida = node_id
            return node_id

    # Criação do circuito
    criar_nodos(expressao)

    # Salva a imagem no diretório de imagens
    output_image_path = os.path.join(IMAGES_FOLDER, 'circuito_logico')
    dot.render(output_image_path, format='png', cleanup=True)

    return ultima_saida, f"{output_image_path}.png"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        expressao_logica = request.form["expressao"]

        # Validar a expressão antes de processar
        if not validar_expressao(expressao_logica):
            return render_template("index.html", error="Expressão inválida: Parênteses desbalanceados ou operadores incorretos.")

        try:
            # Formatar a expressão
            expressao_formatada = formatar_expressao(expressao_logica)
            
            # Gerar o circuito
            ultima_saida, image_path = gerar_circuito(expressao_logica)
            
            # Retornar a expressão formatada, imagem e última saída
            return render_template(
                "index.html", 
                image_path=image_path, 
                ultima_saida=ultima_saida, 
                expressao_formatada=expressao_formatada
            )
        except Exception as e:
            return render_template("index.html", error=f"Erro ao processar a expressão: {e}")
    
    return render_template("index.html", image_path=None, ultima_saida=None, expressao_formatada=None)

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
