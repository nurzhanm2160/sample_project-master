from paykassa.dto import CheckPaymentRequest
from paykassa.merchant import MerchantApi

def get_payment_details(hash):
    client = MerchantApi(20132, "8x6GobG05RMhUTwwLNEU879oNZNTeWz6")

    request = CheckPaymentRequest()\
        .set_private_hash(hash)

    return client.check_payment(request)

