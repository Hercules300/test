def obter_explicacao_chatgpt(expressao_logica):
    try:
        prompt = f"Explique detalhadamente a seguinte expressão lógica e como ela se relaciona com portas lógicas em circuitos: {expressao_logica}"
        response = openai.Completion.create(
            model="gpt-4",  # Usando GPT-4
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        
        # Adicionando um print para verificar o conteúdo da resposta
        print("Resposta completa da API:", response)  # Isso imprimirá a resposta completa no terminal
        
        explicacao = response.choices[0].text.strip()
        print(f"Explicação do ChatGPT: {explicacao}")  # Imprime a explicação no console
        return explicacao
    except Exception as e:
        print(f"Erro ao chamar a API: {str(e)}")  # Isso vai mostrar se houver algum erro na chamada
        return f"Erro ao obter explicação do ChatGPT: {str(e)}"
