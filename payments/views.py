from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction, Escrow, AuditLog, Transaction
from .utils import verify_webhook_signature
import requests
from datetime import datetime
from django.contrib.auth import get_user_model
from ABRMS import settings
from django.shortcuts import render, redirect
from django.utils.timezone import now
from user.models import Notification
from abrmservices.models import Listing
from django.contrib import messages


User = get_user_model()

def payments(request):
    return render(request, 'payments.html')  # Path to your HTML file

# Payment initiation view
from django.shortcuts import redirect

def fund_wallet(request, amount, listing_id):
    if request.method == "POST":
        reference = f"fund_{request.user.id}_{int(datetime.now().timestamp())}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "email": request.user.email,
            "amount": int(amount * 100),
            "reference": reference,
            "callback_url": request.build_absolute_uri('/wallet/callback/'),
            "metadata": {"listing_id": listing_id}  # Include the listing_id
        }

        # Make a request to Paystack API to initialize the transaction
        response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=data)

        if response.status_code == 200:
            payment_url = response.json().get('data', {}).get('authorization_url')
            if payment_url:
                # Redirect to Paystack payment page
                return redirect(payment_url)
            else:
                messages.error(request, "Failed to generate payment URL. Please try again.")
        else:
            messages.error(request, f"Failed to initiate payment. Error: {response.text}")

    # Redirect back to wallet page in case of failure
    return redirect('housing')
# Paystack webhook callback view to verify the payment and fund wallet
from decimal import Decimal

@login_required
def wallet_callback(request):
    reference = request.GET.get("reference")
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    # Verify the transaction using Paystack API
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)

    if response.status_code == 200:
        data = response.json()["data"]
        if data["status"] == "success":
            # Retrieve the listing ID (e.g., from the reference or another source)
            listing_id = data.get("metadata", {}).get("listing_id")  # Ensure listing_id is included in metadata
            listing = get_object_or_404(Listing, id=listing_id)

            # Process the payment
            amount = Decimal(data["amount"]) / 100  # Convert back to Naira
            wallet = get_object_or_404(Wallet, user=request.user)
            wallet.balance += amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="deposit",
                amount=amount,
                reference=reference,
            )

            # Generate a unique transaction tracking ID
            tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"

            seller_user = get_object_or_404(User, email=listing.realtor)
            transaction = Transaction.objects.create(
                tracking_id=tracking_id,
                buyer=request.user,
                seller=seller_user,
                property=listing,
                amount=amount,
            )

            escrow_response = initiate_escrow(request, transaction)
            if escrow_response['status'] == 'error':
                messages.error(request, f"Failed to initiate payment. Error: {response.text}")
                return redirect('housing')  # Redirect to the wallet funding page

            # Notify both buyer and seller
            Notification.objects.create(
                user=request.user,
                message=f"Please confirm your transaction for {listing.title}. <a href='/buyer-confirm/{transaction.id}/'>Click here</a>"
            )
            Notification.objects.create(
                user=seller_user,
                message=f"Please confirm the transaction for {listing.title}. <a href='/seller-confirm/{transaction.id}/'>Click here</a>"
            )

            messages.success(request, "Transaction successful! Please confirm in notifications.")
            return redirect('housing')

    messages.error(request, "Payment verification failed. Please try again.")
    return redirect('housing')


def initiate_escrow(request, transaction):
    wallet = get_object_or_404(Wallet, user=request.user)

    # Check if the wallet has sufficient balance
    if wallet.balance < transaction.amount:
        # Notify the buyer about insufficient funds
        Notification.objects.create(
            user=request.user,
            message=f"Insufficient funds to initiate escrow for {transaction.property.title}. Please fund your wallet."
        )

        # Add an error message to the request
        messages.error(request, f"Insufficient funds to initiate escrow for {transaction.property.title}. Please fund your wallet.")

        # Return an error response
        return {"status": "error", "message": "Insufficient funds to initiate escrow. Please fund your wallet."}



    # Create escrow object
    escrow = Escrow.objects.create(
        buyer=request.user,
        seller=transaction.seller,
        amount=transaction.amount,
        transaction=transaction
    )

    transaction.status = 'escrow_initiated'
    transaction.save()

    # Create audit log for escrow initiation
    AuditLog.objects.create(
        user=request.user,
        action="Escrow Initiation",
        details=f"Escrow initiated for {transaction.amount} on property {transaction.property.title}. Escrow Hash: {escrow.transaction_hash}"
    )

    return {"status": "success", "message": "Escrow initiated successfully!"}

from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def buy_property(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    amount = listing.price

    if request.method == "POST":
        wallet = get_object_or_404(Wallet, user=request.user)

        # Check if the user has sufficient funds
        if wallet.balance < amount:
            # Redirect to fund wallet page with the required amount
            return fund_wallet(request, amount=amount, listing_id=listing_id)
        
        wallet.balance -= amount
        wallet.save()


        # # Update property status (e.g., mark it as sold)
        # listing.sold = True
        # listing.buyer = request.user  # Assuming there is a buyer field
        # listing.save()

        # Return success response or redirect to a success page
        return JsonResponse({"status": "success", "message": "Property purchased successfully."})

    # If the request method is not POST
    return JsonResponse({"status": "error", "message": "Invalid request method. Use POST to buy property."})


# Seller confirms the escrow transaction
@login_required
def seller_confirm(request, escrow_id):
    escrow = get_object_or_404(Escrow, transaction_id=escrow_id, seller=request.user, status="pending")
    escrow.status = "seller_confirmed"
    escrow.seller_confirmed_at = now()
    escrow.save()

    AuditLog.objects.create(
        user=request.user,
        action="Seller Confirmation",
        details=f"Seller confirmed receipt for escrow {escrow.transaction_hash}.",
    )

    return JsonResponse({"status": "success", "message": "Seller confirmation successful!"})

# Buyer confirms the escrow transaction and releases funds to the seller's wallet
@login_required
def buyer_confirm(request, escrow_id):
    escrow = get_object_or_404(Escrow, transaction_id=escrow_id, buyer=request.user)

    # Check if the seller has confirmed the transaction
    if escrow.status != "seller_confirmed":
        return JsonResponse({
            "status": "error",
            "message": "Seller has not confirmed the transaction. Please contact the seller to confirm."
        })

    # Confirm buyer's approval and complete the escrow
    escrow.status = "successful"
    escrow.buyer_confirmed_at = now()
    escrow.save()

    # Ensure the seller has a wallet
    seller_wallet = get_object_or_404(Wallet, user=escrow.seller)

    # Transfer the amount from the buyer to the seller
    buyer_wallet = get_object_or_404(Wallet, user=request.user)

    # Check if buyer has sufficient balance
    if buyer_wallet.balance < escrow.amount:
        return JsonResponse({"status": "error", "message": "Insufficient balance to release funds."})

    # Deduct from the buyer's wallet
    buyer_wallet.balance -= escrow.amount
    buyer_wallet.save()
    print(escrow.amount)
    # Add funds to the seller's wallet
    seller_wallet.balance += escrow.amount
    seller_wallet.save()

    # Log the wallet transactions for both the buyer and seller
    WalletTransaction.objects.update(
        wallet=buyer_wallet,
        transaction_type="escrow_release",
        amount=escrow.amount,
        reference=escrow.transaction_hash,
    )

    WalletTransaction.objects.create(
        wallet=seller_wallet,
        transaction_type="escrow_release",
        amount=escrow.amount,
        reference=escrow.transaction_hash,
    )

    # Log the action for audit purposes
    AuditLog.objects.create(
        user=request.user,
        action="Buyer Confirmation",
        details=f"Buyer confirmed service for escrow {escrow.transaction_hash}. Funds released to seller.",
    )

    return JsonResponse({"status": "success", "message": "Funds released to seller successfully!"})


# Withdraw from wallet (similar to P2P transfer out)
@login_required
def withdraw_wallet(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        bank_code = request.POST.get("bank_code")
        account_number = request.POST.get("account_number")

        wallet = get_object_or_404(Wallet, user=request.user)
        if wallet.balance >= float(amount):
            wallet.balance -= float(amount)
            wallet.save()

            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            data = {
                "source": "balance",
                "reason": "Withdrawal",
                "amount": int(float(amount) * 100),
                "recipient": {
                    "type": "nuban",
                    "name": request.user.get_full_name(),
                    "account_number": account_number,
                    "bank_code": bank_code
                }
            }
            response = requests.post(
                "https://api.paystack.co/transfer", headers=headers, json=data
            )

            if response.status_code == 200:
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="withdrawal",
                    amount=amount,
                    reference=response.json()["data"]["transfer_code"]
                )
                return JsonResponse({"status": "success", "message": "Withdrawal successful!"})

    return JsonResponse({"status": "error", "message": "Withdrawal failed."})

