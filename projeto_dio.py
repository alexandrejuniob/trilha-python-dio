"""O código asseguir é um projeto enviado ao bootcamp Santander Week - DIO.
O código visa simular uma cotação de financiamento de imóvel pelo Banco
Santander.
No corpo do código será abordado os conceitos aprendidos ao módulo Introdução
à Ciência de Dados e Python.
"""
# Passor a seguir para a relização da demanda:

# bibliotecas necessárias
import openai
import pandas as pd
import requests
import json

"""
    1 - Recuperar os dados dos usários na API do Santander
    2 - Calcular os valores da renda, sendo o financiamento no valor:
Parcela de 30% da renda X 180 meses (15 anos) = valor total + 6% x anos.
Se houver FGTS, pode ser usado para abater nos valores da prestação.
    3 - Usar uma IA generativa como especialista de marketing,
para gerar uma mensagem informando sobre o valor liberado e as condições
de pagamento.
    4 - Fazer o loading do para a API.
"""

# 1 - Recuperar os dados dos usários na API do Santander

# Recuperando os ID de 3 usuários da API Santander:
sdw2023_api_url = 'https://sdw-2023-prd.up.railway.app'
df = pd.read_csv('SDW2023.csv')  # Planilha com os ids
user_ids = df['UserID'].tolist()  # Leitura dos ids em lista
print(user_ids)


# Recuperando os dados bancáriso dos usários dos IDs acima
def get_user(id):
    response = requests.get(f'{sdw2023_api_url}/users/{id}')
    return response.json() if response.status_code == 200 else None


users = [user for id in user_ids if (user := get_user(id)) is not None]
# print(json.dumps(users[1], indent=2)) #validação

""" A API não permite a criação de variáiveis manualmente,
 como isso, será criado aqui:"""


def income_add(user, renda, fgts):
    income = {
        "id": 0,
        "icon": "string",
        "income": renda
    }
    FGTS = {
        "id": 0,
        "icon": "string",
        "FGTS": fgts
    }
    user["features"].append(income)
    user["features"].append(FGTS)


income_add(users[0], 12000, 46000)
income_add(users[1], 4000, 5000)
income_add(users[2], 18000, 0)
# print(users["features"]) # validação


"""
 3 - Calcular os valores da renda, sendo o financiamento no valor:
Parcela de 30% da renda X 180 meses (15 anos) = valor total + 6% x anos.
Se houver FGTS, pode ser usado para abater nos valores da prestação.

"""
# Chave da API do CHATGPT (A chave será escluída após a submissão do trabalho)
openai_api_key = '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'
openai.api_key = openai_api_key

"""Criando a função que irá calcular os valores do financiamento,
das parcelas.

Em seguida a função usa os produtos para criar uma mensagem de
marketing usando uma IA generativa.
"""


def financiamento(user):
    name = user["name"]
    fgts = user['features'][2]['FGTS']
    valor_total = user['features'][1]['income'] * 30 / 100 * 180 - fgts
    parcela = (
        (valor_total + (user['features'][1]['income'] * 0.06 * 20)) / 180)
    # print(f"{name}:  {fgts}   {valor_total}   {round(parcela, 2)}")
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
              "role": "system",
              "content": "Você é um especialista em markting bancário."
            },
            {
                "role": "user",
                "content": f"Crie uma mensagem para {name} oferencendo um financiamento de habitação no valor de {int(valor_total/1000)} mil e os valores {parcela} por 180 meses (máximo de 300 caracteres)"
            }
        ]
    )
    return completion.choices[0].message.content.strip('\"')


"""Passando todos os usários pela função e
armazenando a mensagem nos dados bancários"""
for user in users:
    fin = financiamento(user)
    # print(fin)
    user['news'].append({
        "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
        "description": fin
    })
    print(user['news'])

# Função para fazer upload dos useuários atualizados


def update_user(user):
    response = requests.put(
        f"{sdw2023_api_url}/users/{user['id']}", json=user)
    return True if response.status_code == 200 else False


# Passando os usuários para a função de upload
for user in users:
    success = update_user(user)
    print(f"User {user['name']} updated? {success}!")
