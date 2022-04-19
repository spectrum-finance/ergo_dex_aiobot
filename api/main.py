import requests

def get_markets():
    res = requests.get('https://api.ergodex.io/v1/amm/markets').json()
    
    return res

def get_pretty_markets():
    res=""
    for item in get_markets():
        for key in item:
            res+=str(key)+'\t\t'+str(item[key])
        res+='\n\n'

    return res

def get_important_data_merkets():
    response = get_markets()
    data=[]
    for coin in response:
        print(coin)
        print('baseSymbol:',coin['quoteSymbol'])
        print('lastPrice:', coin['lastPrice'])
        print()


if __name__ == "__main__":
    get_markets()
    #get_important_data_merkets()
