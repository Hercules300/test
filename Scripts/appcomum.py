from flask import Flask, render_template, request, send_from_directory
from sympy.logic.boolalg import And, Or, Not
import sympy
from graphviz import Digraph
import os

app = Flask(__name__)

# Caminho para a pasta de imagens geradas
IMAGES_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Função para gerar o circuito
def gerar_circuito(expressao_logica):
    expressao = sympy.sympify(expressao_logica)
    dot = Digraph(comment='Circuito Lógico')
    dot.attr(rankdir='LR')  # Define a direção do gráfico

    ultima_saida = None

    def criar_nodos(expr, parent=None):
        nonlocal ultima_saida
        if isinstance(expr, sympy.Symbol):  # Caso seja uma variável booleana
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

    return ultima_saida, output_image_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        expressao_logica = request.form["expressao"]

        try:
            # Chama a função para gerar o circuito e retorna a última saída e o caminho da imagem
            ultima_saida, image_path = gerar_circuito(expressao_logica)
            # Envia para o template o caminho da imagem e a última saída
            return render_template("index.html", image_path=image_path, ultima_saida=ultima_saida)
        except Exception as e:
            return render_template("index.html", error=f"Erro ao processar a expressão: {e}")
    
    return render_template("index.html", image_path=None, ultima_saida=None)

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
