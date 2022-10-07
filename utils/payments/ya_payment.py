from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay


async def create_link_for_payment(receiver, label, summa):
    quick_pay = Quickpay(
        receiver=receiver,
        quickpay_form="shop",
        targets="Оплата покупки",
        paymentType="SB",
        sum=summa,
        label=label
    )
    # print(quick_pay.redirected_url)
    return quick_pay.base_url


async def check_payment(label, token, value):
    #return True
    client = Client(token)
    history = client.operation_history(label=label)
    try:
        if history.operations[0].status == 'success' and history.operations[0].amount >= value * 0.97:
            return True
        else:
            return False
    except:
        return False


def get_token(client_id, redirect_uri):
    Authorize(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop",
               ]
    )


def get_client_info(token):
    client = Client(token)
    user = client.account_info()
    print("Account number:", user.account)
    print("Account balance:", user.balance)
    print("Account currency code in ISO 4217 format:", user.currency)
    print("Account status:", user.account_status)
    print("Account type:", user.account_type)
    print("Extended balance information:")
    for pair in vars(user.balance_details):
        print("\t-->", pair, ":", vars(user.balance_details).get(pair))
    print("Information about linked bank cards:")
    cards = user.cards_linked
    if len(cards) != 0:
        for card in cards:
            print(card.pan_fragment, " - ", card.type)
    else:
        print("No card is linked to the account")


