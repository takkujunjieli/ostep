from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from core import endpoint
from . import repository, services


def transfer_json(transfer, wallet):
    return {"id": transfer.pk, "sender": transfer.sender.user.username, "recipient": transfer.recipient.user.username,
            "amount_cents": transfer.amount_cents, "direction": "outgoing" if transfer.sender_id == wallet.pk else "incoming",
            "memo": transfer.memo}


@login_required
def home(request):
    panels = '''<section><h2>Send money</h2><form data-api="/api/transfers/">
    <label>Recipient username</label><input name="recipient" value="bob" required>
    <label>Amount in cents</label><input name="amount_cents" data-type="number" type="number" min="1" value="250" required>
    <label>Memo</label><input name="memo" value="Lunch"><button>Transfer</button></form>
    <p>Balances and history update after a successful transfer. Sign in as the recipient to inspect incoming transfers.</p>
    <hr><h2>History</h2><form data-api="/api/history/" data-method="GET"><button>Load history</button></form></section>'''
    return render(request, "dashboard.html", {"title": "Wallet", "description": "A local ledger with integer-cent balances and transfers. Demo funds only.", "panels": panels})


@endpoint("GET")
def state(request, data):
    wallet = repository.wallet_for_user(request.user)
    return JsonResponse({"username": request.user.username, "balance_cents": wallet.balance_cents,
                         "history": [transfer_json(row, wallet) for row in repository.history_for_wallet(wallet)]})


@endpoint("GET")
def history(request, data):
    wallet = repository.wallet_for_user(request.user)
    return JsonResponse({"transfers": [transfer_json(row, wallet) for row in repository.history_for_wallet(wallet)]})


@endpoint("POST")
def transfer(request, data):
    result = services.transfer_money(request.user, data.get("recipient"), data.get("amount_cents"), data.get("memo", ""))
    return JsonResponse(transfer_json(result, result.sender), status=201)
