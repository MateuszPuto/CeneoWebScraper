
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import functools
import _thread
from dateutil import parser


def get_charts(productId):
    _thread.start_new_thread(chart, (productId,))

def chart(productId):
    with open(f"app/downloads/{productId}/{productId}.json", encoding="UTF-8") as f:
        opinions = pd.read_json(f)

    os.mkdir(f'app/static/{productId}')

    opinionCount = len(opinions)
    prosCount = opinions.pros.astype(bool).sum()
    consCount = opinions.cons.astype(bool).sum()
    averageScore = opinions.stars.mean()
    firstBought = min([parser.parse(p) for p in opinions.purchaseDate.values.tolist() if p]).date()
    lastBought =  max([parser.parse(p) for p in opinions.purchaseDate.values.tolist() if p]).date()
    confirmedByPurchase = round(100 * opinions.purchased.count() / opinionCount, 2)
    sumOfPros = sum(map(lambda x: len(x), opinions.pros.values))
    sumOfCons = sum(map(lambda x: len(x), opinions.cons.values)) 

    overview = f'''\nO produkcie dostępnych jest {opinionCount} opinii.
    W {prosCount} opiniach podana została lista zalet produkty, a w {consCount} lista wad. 
    Średnia ocena produktu wyznaczona na podstawie liczby gwiazdek w opiniach wynosi {averageScore:.1f}.
    Produkt zakupiony pierwszy raz {firstBought}. Ostatni dokonany zakup miał miejsce {lastBought}.
    Procent opinii potwierdzonych zakupem wynosi {confirmedByPurchase}%.
    Liczba wymienionych zalet przez wszystkich użytkowników to {sumOfPros}, natomiast wad {sumOfCons}.\n'''

    with open(f'app/static/{productId}/{productId}_overview.txt', 'w', encoding="UTF-8") as f:
        f.write(overview)

    stars = opinions.stars.value_counts().reindex(np.arange(0,5.5,0.5), fill_value=0)
    stars.plot.barh(color = 'lightskyblue')
    plt.title("Częstość występowania poszczególnych ocen produktu w opiniach")
    plt.xlabel("Liczba opinii")
    plt.ylabel("Liczba gwiazdek")
    plt.savefig(f"app/static/{productId}/{productId}_stars.png", bbox_inches="tight")

    print(opinions.rcmd)

    recommendations = opinions.rcmd.value_counts(ascending=True)
    recommendations.plot.pie(
        colors = ['lightskyblue', 'crimson']
    )
    plt.title('Udział poszczególnych rekomendacji w ogólnej liczbie opinii')
    plt.legend(['Nie polecam', 'Polecam'], bbox_to_anchor = (0.5, 0.5))
    plt.savefig(f"app/static/{productId}/{productId}_rcmd.png", bbox_inches="tight")

    allPros = functools.reduce(lambda x, y: x + y, list(opinions.pros))
    allCons = functools.reduce(lambda x, y: x + y, list(opinions.cons))

    def reduce(lst):
        d = {}

        for pros in lst:
            if pros in d:
                d[pros] += 1
            else:
                d[pros] = 1

        return d

    sumPros, sumCons = reduce(allPros), reduce(allCons)
    colors = ['bisque', 'tan', 'orange', 'linen', 'gold', 'papayawhip', 'darkorange']

    fig = plt.figure(figsize=(8/20*len(sumPros.keys()), 6))
    fig.canvas.draw_idle() 
    plt.xticks(rotation=90)
    plt.title('Zalety produktu')
    plt.bar(sumPros.keys(), sumPros.values(), color=colors)
    plt.savefig(f"app/static/{productId}/{productId}_pros.png", bbox_inches="tight")

    fig = plt.figure(figsize=(8/20*len(sumCons.keys()), 6))
    fig.canvas.draw_idle() 
    plt.xticks(rotation=90)
    plt.title('Wady produktu')
    plt.bar(sumCons.keys(), sumCons.values(), color=colors)
    plt.savefig(f"app/static/{productId}/{productId}_cons.png", bbox_inches="tight")
