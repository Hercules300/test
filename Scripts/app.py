from flask import Flask, render_template, request, send_from_directory
from sympy.logic.boolalg import And, Or, Not
import sympy
import openai  # Certifique-se de instalar o openai
import os

app = Flask(__name__)

# Caminho para a pasta de imagens geradas
IMAGES_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Chave da API do OpenAI
openai.api_key = "CHAVE"  # Insira sua chave de API aqui

# Função para gerar a explicação usando o ChatGPT
def gerar_explicacao_chatgpt(expressao_logica):
    prompt = f"Explique detalhadamente a seguinte expressão lógica e como ela se relaciona com portas lógicas em circuitos: {expressao_logica}"
    
    # Chamando a API corretamente
    response = openai.chat.completions.create(
        model="gpt-4",  # Use "gpt-4" ou "gpt-3.5-turbo" dependendo do modelo disponível
        messages=[
            {"role": "system", "content": "Você é um especialista em lógica booleana."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )

    # Extraindo a explicação do resultado retornado
    explicacao = response['choices'][0]['message']['content'].strip()

    return explicacao

# Função para gerar o circuito
def gerar_circuito(expressao_logica):
    expressao = sympy.sympify(expressao_logica)
    from graphviz import Digraph
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
    output_image_path = os.path.join(IMAGES_FOLDER, 'circuito_logico.png')
    dot.render(output_image_path, format='png', cleanup=True)

    return output_image_path, ultima_saida

@app.route("/", methods=["GET", "POST"])
def index():
    explicacao = None
    image_path = None
    ultima_saida = None
    if request.method == "POST":
        expressao_logica = request.form["expressao"]

        try:
            # Gerar o circuito
            image_path, ultima_saida = gerar_circuito(expressao_logica)
            
            # Gerar explicação da expressão lógica usando o ChatGPT
            explicacao = gerar_explicacao_chatgpt(expressao_logica)
            
            # Passar para o template
            return render_template("index.html", image_path=image_path, ultima_saida=ultima_saida, explicacao=explicacao)
        except Exception as e:
            return render_template("index.html", error=f"Erro ao processar a expressão: {e}")

    return render_template("index.html", image_path=None, ultima_saida=None, explicacao=None)

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
