from flask import Flask, render_template_string
import re
import json

app = Flask(__name__)

# HTML para a página inicial
main = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
    background: linear-gradient(to bottom, white, rgba(0, 0, 0, 0.5));
    height: 100vh; /* Faz o body ocupar toda a altura da tela */
    margin: 0; /* Remove margens padrão */
    position: relative; /* Necessário para o posicionamento absoluto */
}


.project_c{
    position: absolute;
    right: 10px;
    bottom: 2px;
    display: flex;
    background: linear-gradient(to right, rgba(0, 0, 0), #2c5e5f); /* Degradê de cores */
    -webkit-background-clip: text; /* Clip para o texto */
    -webkit-text-fill-color: transparent; /* Faz o texto transparente para mostrar o fundo */
}

h3{
    margin-right: 5px;
    background: linear-gradient(to right, rgba(0, 0, 0, 0.7), #2c5e5f); /* Degradê de cores */
    -webkit-background-clip: text; /* Clip para o texto */
    -webkit-text-fill-color: transparent; /* Faz o texto transparente para mostrar o fundo */
}
.container {
    display: flex;
    flex-direction: column; /* Coloca os itens em coluna */
    justify-content: center; /* Centraliza horizontalmente */
    align-items: center; /* Centraliza verticalmente */
    height: 100%; /* Faz o contêiner ocupar toda a altura do body */
}

h1 {
    text-align: center;
    font-size: 100px;
    font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background-color: #007BFF;
    color: white;
    text-decoration: none;
    border-radius: 5px;
}
</style>
    <title>PLC_TP1</title>
</head>
<body>
    <div class="container">
        <h1>TP1 Exercício 2</h1>
        <a href="{{ url_for('results') }}" class="btn">Ir para Resultados</a>
    </div>
    <div class="project_c">
        <h3>Projeto realizado por: </h3>
        <h5> Gabriel Antunes - A101101<p>
             Guilherme Pinho - A105533<p>
             Oliver Teixeira - A102506
        </h5>
    </div>
</body>
</html>

"""

# HTML para a página de resultados
index = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        h1 {
            text-align: center;
            font-size: 100px;
            font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
        }

        body {
            background: linear-gradient(to bottom, white, rgba(0, 0, 0, 0.6));
        }

        p {
            text-align: center;
        }

        h2 {
            text-align: center;
        }

        pre {
            font-size: 15px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        th {
            background-color: #f2f2f2;
        }

        .container {
            margin: 20px 0;
        }

        .texto {
            text-align: left; /* Alinha o texto à esquerda */
        }
    </style>
    <title>PLC_TP1</title>
</head>
<body>
    <h1>PLC_TP1</h1>
    <div class="top-right">   
    </div>
    <table>
        <thead>
            <tr>
                <th>Menor idade</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{{ menor }}</td>
            </tr>
        </tbody>
    </table>

    <table>
        <thead>
            <tr>
                <th>Maior idade</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{{ maior }}</td>
            </tr>
        </tbody>
    </table>
    <br>
    <table>
        <thead>
            <tr>
                <th>Masculinos</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{{ masculino }}</td>
            </tr>
        </tbody>
    </table>
    <br>
    <table>
        <thead>
            <tr>
                <th>Femininos</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{{ feminino }}</td>
            </tr>
        </tbody>
    </table>
    <br>

    <div class="container">
        <div class="texto">
            <h2>Modalidades por Ano:</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ano</th>
                        <th>Modalidade</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for ano, modalidades in lista_anos.items() %}
                        {% for modalidade, total in modalidades.items() %}
                            <tr>
                                <td>{{ ano }}</td>  
                                <td>{{ modalidade }}</td>
                                <td>{{ total }}</td>
                            </tr>
                        {% endfor %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="container">
        <div class="texto">
            <h2>Total de Praticantes por Modalidade:</h2>
            <table>
                <thead>
                    <tr>
                        <th>Modalidade</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for modalidade, total in conta_numeros.items() %}
                    <tr>
                        <td>{{ modalidade }}</td>
                        <td>{{ total }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="container">
        <div class="texto">
            <h2>Percentagem de Aprovação anual:</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ano</th>
                        <th>Percentagem Aptos</th>
                        <th>Percentagem não Aptos</th>
                    </tr>
                </thead>
                <tbody>
                    {% for ano, percentagem in media.items() %}
                    <tr>
                        <td>{{ ano }}</td>
                        <td>{{ percentagem }}</td>
                        <td>{{ 100 - percentagem }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
</body>
</html>

"""


@app.route('/')
def index1():
    return render_template_string(main)

# A função results vai calcular todos os objetivos pedidos no exercício
@app.route('/index')
def results():
    # Variáveis para guardar o atleta mais novo e mais velho respetivamente
    menor = float('inf')
    maior = float('-inf')

    # Variáveis para contar o número de atletas masculinos e femininos
    masculino = 0
    feminino = 0

    # Dicionário que vai agrupar os desportos praticados num determinado ano
    lista_anos = {}

    # Dicionário para guardar o nº de atletas aptos a competir em cada ano
    lista_aptos = {}

    # Dicionário que vai guardar a média de aptos e não aptos por ano em percentagem
    media = {}

    # Lista onde vão ser guardadas as sugestões de nomes a trocar, juntamente com a sua normalização
    sugestao_nomes = []

    # Objetivo da alínea c) ii) 
    # Função auxiliar que vai contar o número de atletas por cada desporto
    def conta_desportos(lista_anos):
        modalidade_total = {}
        for ano in lista_anos:
            for desporto, total in lista_anos[ano].items():
                modalidade_total[desporto] = modalidade_total.get(desporto, 0) + total
        return modalidade_total

    try:
        with open("emd.csv", 'r') as file:
            content = file.read()
            res = re.split(r"\n", content)
            res.pop(0)

            for linha in res:
                info = re.split(r",", linha)

                # Objetivo da alínea a) Calcular as Idades extremas dos registos 
                menor = min(int(info[5]), menor)
                maior = max(int(info[5]), maior)

                #  Objetivo da alínea b) Calcular a distribuição por Género no total
                if info[6] == "M":
                    masculino += 1
                elif info[6] == "F":
                    feminino += 1
                
                #  Objetivo da alínea c) i) Calcular a distribuição por Modalidade em cada ano
                ano = re.match(r'[0-9]{4}', info[2])
                if ano:
                    ano = ano.group(0)
                    desporto = info[8]
                    
                    if ano not in lista_anos:
                        lista_anos[ano] = {}
                    if desporto not in lista_anos[ano]:
                        lista_anos[ano][desporto] = 0
                    
                    lista_anos[ano][desporto] += 1

                # Objetivo da alínea d) Calcular a pertentagem de atletas aptos e não aptos por cada ano
                apto = info[12]
                if ano not in lista_aptos:
                    lista_aptos[ano] = {0: 0, 1: 0}
                if apto == "true":
                    lista_aptos[ano][0] += 1
                lista_aptos[ano][1] += 1      

                # Objetivo da alínea e) Normalizar as colunas do Nome
                if info[6] != "F":
                    sugestao_nomes.append(f">> Sugestao: Alterar o nome do atleta com o Id {info[0]}, {info[3]} {info[4]} --> {info[4]} {info[3]}")

        # Organizar lista_anos e calcular percentagens
        lista_anos = dict(sorted(lista_anos.items()))
        for ano in lista_anos:
            lista_anos[ano] = dict(sorted(lista_anos[ano].items(), key=lambda t: t[0]))
            media[ano] = round(lista_aptos[ano][0] * 100 / lista_aptos[ano][1], 2)

        with open('mensagem.json', 'w') as json_file:
            json.dump(sugestao_nomes, json_file, indent=4)

    except FileNotFoundError:
        print("O arquivo emd.csv não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    conta_numeros = conta_desportos(lista_anos)

    # Esta função vai registar o código html para depois registar todos os resultados no ficheiro index.html
    def gerar_html(menor, maior, masculino, feminino, lista_anos, conta_numeros, media):  

        html = "<html>\n<head></head>\n<body>\n"
        
        # Adicionar um título
        html += "<h2>Valores finais</h2>\n"

        # Adicionar parágrafos com as idades
        html += f"<p>Menor Idade: {menor} anos</p>\n"
        html += f"<p>Maior Idade: {maior} anos</p>\n"
        html += "<br>\n"
        html += f"<p>Masculinos: {masculino}</p>\n"
        html += f"<p>Femininos: {feminino}</p>\n"
        html += "<br>\n"
        html += "<h2>Modalidades por Ano:</h2>\n"
        html += "<table>\n"
        html += "<thead>\n"
        html += "<tr>\n"
        html += "<th>Ano</th>\n"
        html += "<th>Modalidade</th>\n"
        html += "<th>Total</th>\n"
        html += "</tr>\n"
        html += "</thead>\n"
        html += "<tbody>\n"

        for ano, modalidades in lista_anos.items():
            for modalidade, total in modalidades.items():
                html += "<tr>\n"
                html += f"<td>{ano}</td>\n"
                html += f"<td>{modalidade}</td>\n"
                html += f"<td>{total}</td>\n"
                html += "</tr>\n"

        html += "</tbody>\n"
        html += "</table>\n"
        html += "<br>\n"
        html += "<h2>Total de Praticantes por Modalidade:</h2>\n"
        html += "<table>\n"
        html += "<thead>\n"
        html += "<tr>\n"
        html += "<th>Modalidade</th>\n"
        html += "<th>Total</th>\n"
        html += "</tr>\n"
        html += "</thead>\n"
        html += "<tbody>\n"

        for modalidade, total in conta_numeros.items():
            html += "<tr>\n"
            html += f"<td>{modalidade}</td>\n"
            html += f"<td>{total}</td>\n"
            html += "</tr>\n"

        html += "</tbody>\n"
        html += "</table>\n"
        html += "<br>\n"
        html += "<h2>Percentagem de Aprovação anual:</h2>\n"
        html += "<table>\n"
        html += "<thead>\n"
        html += "<tr>\n"
        html += "<th>Ano</th>\n"
        html += "<th>Percentagem Aptos</th>\n"
        html += "<th>Percentagem não Aptos</th>\n"
        html += "</tr>\n"
        html += "</thead>\n"
        html += "<tbody>\n"

        for ano, percentagem in media.items():
            html += "<tr>\n"
            html += f"<td>{ano}</td>\n"
            html += f"<td>{percentagem}</td>\n"
            html += f"<td>{100 - percentagem}</td>\n"
            html += "</tr>\n"

        html += "</tbody>\n"
        html += "</table>\n"
        html += "</body>\n</html>"

        return html

    html= gerar_html(menor, maior, masculino, feminino, lista_anos, conta_numeros, media)

    # Escrever a string HTML no ficheiro idades.html
    with open("index.html", "w") as file:
        file.write(html)

    return render_template_string(index, menor=menor, maior=maior, masculino=masculino, feminino=feminino, lista_anos=lista_anos, conta_numeros=conta_desportos(lista_anos), media=media)

if __name__ == '__main__':
    app.run(debug=True)