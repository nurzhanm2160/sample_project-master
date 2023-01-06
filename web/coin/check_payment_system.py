from paykassa.struct import System

def check_payment_system(system):
    if system == "PERFECTMONEY":
        return System.PERFECTMONEY
    elif system == "BERTY":
        return System.BERTY
    elif system == "BITCOIN":
        return System.BITCOIN
    elif system == "ETHEREUM":
        return System.ETHEREUM
    elif system == "LITECOIN":
        return System.LITECOIN
    elif system == "DOGECOIN":
        print("попала в elif sytem == DOGECOIN")
        return System.DOGECOIN
    elif system == "DASH":
        return System.DASH
    elif system == "BITCOINCASH":
        return System.BITCOINCASH
    elif system == "ZCASH":
        return System.ZCASH
    elif system == "ETHEREUMCLASSIC":
        return System.ETHEREUMCLASSIC
    elif system == "RIPPLE":
        return System.RIPPLE
    elif system == "TRON":
        return System.TRON
    elif system == "STELLAR":
        return System.STELLAR
    elif system == "BINANCECOIN":
        return System.BINANCECOIN
    elif system == "TRON_TRC20":
        return System.TRON_TRC20
    elif system == "BINANCESMARTCHAIN_BEP20":
        return System.BINANCESMARTCHAIN_BEP20
    elif system == "ETHEREUM_ERC20":
        return System.ETHEREUM_ERC20   