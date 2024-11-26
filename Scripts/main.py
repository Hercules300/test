from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sympy as sp
import openai
import schemdraw
import schemdraw.logic as logic

# Configuração da API da OpenAI
openai.api_key = "SUA_CHAVE_OPENAI_AQUI"

# Inicializa o aplicativo FastAPI
app = FastAPI()

# Modelo de dados para receber a expressão lógica
class LogicExpression(BaseModel):
    expression: str

@app.post("/generate-circuit/")
async def generate_circuit(data: LogicExpression):
    try:
        # Parte 1: Interpretar e validar a expressão lógica
        try:
            expr = sp.sympify(data.expression)  # Parse da expressão lógica
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao interpretar a expressão: {str(e)}")
        
        # Parte 2: Obter explicação via ChatGPT
        explanation = get_chatgpt_explanation(data.expression)

        # Parte 3: Gerar o circuito equivalente
        image_path = "circuit.png"
        generate_circuit_image(expr, image_path)

        return {
            "message": "Circuito gerado com sucesso!",
            "explanation": explanation,
            "image_path": image_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_chatgpt_explanation(expression: str) -> str:
    """
    Usa a API do ChatGPT para explicar a expressão lógica.
    """
    try:
        prompt = f"Explique detalhadamente a seguinte expressão lógica e como ela se relaciona com portas lógicas em circuitos: {expression}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em lógica digital."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o ChatGPT: {str(e)}")


def generate_circuit_image(expr, output_path: str):
    """
    Gera a imagem do circuito lógico correspondente à expressão.
    """
    try:
        with schemdraw.Drawing() as d:
            # Este exemplo é simplificado. Aqui, você pode mapear componentes do SymPy para portas lógicas.
            # Por exemplo: "AND", "OR", "NOT", etc.
            d += (a := logic.And())
            d += (b := logic.Or().at(a.output))
            d += logic.Not().at(b.output)
            d.save(output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar o circuito: {str(e)}")

# Endpoint inicial (opcional, apenas para verificação)
@app.get("/")
def read_root():
    return {"message": "API de Geração de Circuitos Lógicos com ChatGPT está rodando!"}
