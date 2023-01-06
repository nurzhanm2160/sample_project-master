from paykassa.struct import Currency

 # USD = "USD"
    #RUB = "RUB"
    #BTC = "BTC"
    #DOGE = "DOGE"
    #ETH = "ETH"
    #LTC = "LTC"
    #DASH = "DASH"
    #BCH = "BCH"
    #ZEC = "ZEC"
    #XRP = "XRP"
    #TRX = "TRX"
    #XLM = "XLM"
    #BNB = "BNB"
    #USDT = "USDT"
    #BUSD = "BUSD"
    #USDC = "USDC"
    #ADA = "ADA"
    #EOS = "EOS"
    #SHIB = "SHIB"
    #ETC = "ETC"

def check_payment_currency(currency):
    if currency == "USD":
        return Currency.USD
    elif currency == "RUB":
        return Currency.RUB
    elif currency == "BTC":
        return Currency.BTC
    elif currency == "DOGE":
        return Currency.DOGE
    elif currency == "ETH":
        return Currency.ETH
    elif currency == "LTC":
        return Currency.LTC
    elif currency == "DASH":
        return Currency.DASH
    elif currency == "BCH":
        return Currency.BCH
    elif currency == "ZEC":
        return Currency.ZEC
    elif currency == "XRP":
        return Currency.XRP
    elif currency == "TRX":
        return Currency.TRX
    elif currency == "XLM":
        return Currency.XLM
    elif currency == "BNB":
        return Currency.BNB
    elif currency == "USDT":
        return Currency.USDT
    elif currency == "BUSD":
        return Currency.BUSD
    elif currency == "USDC":
        return Currency.USDC
    elif currency == "ADA":
        return Currency.ADA  
    elif currency == "EOS":
        return Currency.EOS  
    elif currency == "SHIB":
        return Currency.SHIB  
    elif currency == "ETC":
        return Currency.ETC