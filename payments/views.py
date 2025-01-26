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
from decimal import Decimal
import logging
from django.views.decorators.csrf import csrf_exempt

# Configure logging for security and debugging
logger = logging.getLogger(__name__)

User = get_user_model()

def payments(request):
    return render(request, 'payments.html')  # Path to your HTML file


from django.db import transaction
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import F

# Payment initiation view
@login_required
@ensure_csrf_cookie
def fund_wallet(request):
    if request.method == "POST":
        try:
            data = request.POST
            amount = Decimal(data.get("amount", "0"))
            listing_id = data.get("listing_id")

            if amount <= 0:
                messages.error(request, "Invalid amount specified.")
                return redirect('housing')

            listing = get_object_or_404(Listing, id=listing_id)
            reference = f"fund_{request.user.id}_{int(now().timestamp())}"

            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            payload = {
                "email": request.user.email,
                "amount": int(amount * 100),
                "reference": reference,
                "callback_url": request.build_absolute_uri(reverse('wallet_callback')),
                "metadata": {"listing_id": listing.id},
            }

            response = requests.post(
                "https://api.paystack.co/transaction/initialize", 
                headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            payment_url = response.json().get('data', {}).get('authorization_url')
            if payment_url:
                return redirect(payment_url)
            else:
                logger.error("Payment URL not found in Paystack response.")
                messages.error(request, "Failed to initiate payment. Please try again.")
        except requests.RequestException as e:
            logger.exception("Network error during payment initiation.")
            messages.error(request, "A network error occurred. Please try again.")
        except Exception as e:
            logger.exception("Error during payment initiation.")
            messages.error(request, "An unexpected error occurred. Please try again.")
    return redirect('housing')

@login_required
def wallet_callback(request):
    reference = request.GET.get("reference")
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()["data"]
        if data["status"] == "success":
            with transaction.atomic():
                listing_id = data.get("metadata", {}).get("listing_id")
                listing = get_object_or_404(Listing, id=listing_id)
                amount = Decimal(data["amount"]) / 100

                wallet = get_object_or_404(Wallet, user=request.user)
                wallet.balance = F('balance') + amount
                wallet.save()

                WalletTransaction.objects.create(
                    wallet=wallet, transaction_type="deposit", amount=amount, reference=reference
                )

                Notification.objects.bulk_create([
                    Notification(
                        user=request.user, 
                        message=f"Please confirm your transaction for {listing.title}. "
                                f"<a href='{reverse('buyer_confirm', args=[listing.id])}'>Click here</a>"
                    ),
                    Notification(
                        user=listing.realtor,
                        message=f"A buyer has initiated a transaction for {listing.title}. "
                                f"<a href='{reverse('seller_confirm', args=[listing.id])}'>Click here</a>"
                    )
                ])
                messages.success(request, "Transaction successful! Check notifications for details.")
                return redirect('housing')
        else:
            logger.error(f"Transaction verification failed: {response.json()}")
    except requests.RequestException:
        logger.exception("Error verifying transaction.")
        messages.error(request, "A network error occurred. Please try again.")
    except Exception:
        logger.exception("Unexpected error during transaction verification.")
    messages.error(request, "Payment verification failed. Please contact support.")
    return redirect('housing')

def initiate_escrow(request, transaction):
    try:
        wallet = get_object_or_404(Wallet, user=request.user)

        if wallet.balance < transaction.amount:
            Notification.objects.create(
                user=request.user,
                message=f"Insufficient funds to initiate escrow for {transaction.property.title}. Please fund your wallet."
            )
            messages.error(request, "Insufficient funds. Please fund your wallet.")
            return {"status": "error", "message": "Insufficient funds."}

        escrow = Escrow.objects.create(
            buyer=request.user,
            seller=transaction.seller,
            amount=transaction.amount,
            transaction=transaction
        )

        transaction.status = 'escrow_initiated'
        transaction.save()

        AuditLog.objects.create(
            user=request.user,
            action="Escrow Initiation",
            details=f"Escrow initiated for {transaction.amount} on property {transaction.property.title}. Escrow Hash: {escrow.transaction_hash}"
        )

        return {"status": "success", "message": "Escrow initiated successfully."}
    except Exception as e:
        logger.exception("An error occurred during escrow initiation.")
        return {"status": "error", "message": "An error occurred. Please contact support."}

@login_required
def buy_property(request, listing_id):
    try:
        listing = get_object_or_404(Listing, id=listing_id)
        amount = listing.price

        if request.method == "POST":
            wallet = get_object_or_404(Wallet, user=request.user)

            if wallet.balance < amount:
                shortfall = amount - wallet.balance
                return fund_wallet(request, amount=shortfall, listing_id=listing_id)

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
                logger.error("Failed to initiate payment from wallet.")
                messages.error(request, "Failed to initiate payment from wallet.")
                return redirect('housing')

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

        return JsonResponse({"status": "error", "message": "Invalid request method."})
    except Exception as e:
        logger.exception("An error occurred during property purchase.")
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

@login_required
def seller_confirm(request, escrow_id):
    try:
        escrow = get_object_or_404(Escrow, transaction_id=escrow_id, seller=request.user, status="pending")
        escrow.status = "seller_confirmed"
        escrow.seller_confirmed_at = now()
        escrow.save()

        AuditLog.objects.create(
            user=request.user,
            action="Seller Confirmation",
            details=f"Seller confirmed receipt for escrow {escrow.transaction_hash}."
        )

        return JsonResponse({"status": "success", "message": "Seller confirmation successful!"})
    except Exception as e:
        logger.exception("An error occurred during seller confirmation.")
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

@login_required
def buyer_confirm(request, escrow_id):
    try:
        escrow = get_object_or_404(Escrow, transaction_id=escrow_id, buyer=request.user)

        if escrow.status != "seller_confirmed":
            return JsonResponse({"status": "error", "message": "Seller has not confirmed the transaction."})

        escrow.status = "successful"
        escrow.buyer_confirmed_at = now()
        escrow.save()

        transaction = escrow.transaction
        transaction.status = "completed"
        transaction.save()

        buyer_wallet = get_object_or_404(Wallet, user=escrow.buyer)
        seller_wallet = get_object_or_404(Wallet, user=escrow.seller)

        buyer_wallet.balance -= escrow.amount
        seller_wallet.balance += escrow.amount

        buyer_wallet.save()
        seller_wallet.save()

        AuditLog.objects.create(
            user=request.user,
            action="Buyer Confirmation",
            details=f"Buyer confirmed transaction {escrow.transaction_hash}. Funds transferred."
        )

        Notification.objects.create(
            user=escrow.seller,
            message=f"Buyer has confirmed the transaction for {transaction.property.title}. Funds have been released."
        )

        messages.success(request, "Transaction completed successfully!")
        return redirect('housing')
    except Exception as e:
        logger.exception("An error occurred during buyer confirmation.")
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})



# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .models import Wallet, WalletTransaction, Escrow, AuditLog, Transaction
# from .utils import verify_webhook_signature
# import requests
# from datetime import datetime
# from django.contrib.auth import get_user_model
# from ABRMS import settings
# from django.shortcuts import render, redirect
# from django.utils.timezone import now
# from user.models import Notification
# from abrmservices.models import Listing
# from django.contrib import messages


# User = get_user_model()

# def payments(request):
#     return render(request, 'payments.html')  # Path to your HTML file

# # Payment initiation view
# from django.shortcuts import redirect

# def fund_wallet(request, amount, listing_id):
#     if request.method == "POST":
#         reference = f"fund_{request.user.id}_{int(datetime.now().timestamp())}"
#         headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
#         data = {
#             "email": request.user.email,
#             "amount": int(amount * 100),
#             "reference": reference,
#             "callback_url": request.build_absolute_uri('/wallet/callback/'),
#             "metadata": {"listing_id": listing_id}  # Include the listing_id
#         }

#         # Make a request to Paystack API to initialize the transaction
#         response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=data)

#         if response.status_code == 200:
#             payment_url = response.json().get('data', {}).get('authorization_url')
#             if payment_url:
#                 # Redirect to Paystack payment page
#                 return redirect(payment_url)
#             else:
#                 messages.error(request, "Failed to generate payment URL. Please try again.")
#         else:
#             messages.error(request, f"Failed to initiate payment. Error: {response.text}")

#     # Redirect back to wallet page in case of failure
#     return redirect('housing')
# # Paystack webhook callback view to verify the payment and fund wallet
# from decimal import Decimal

# @login_required
# def wallet_callback(request):
#     reference = request.GET.get("reference")
#     headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

#     # Verify the transaction using Paystack API
#     response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)

#     if response.status_code == 200:
#         data = response.json()["data"]
#         if data["status"] == "success":
#             # Retrieve the listing ID (e.g., from the reference or another source)
#             listing_id = data.get("metadata", {}).get("listing_id")  # Ensure listing_id is included in metadata
#             listing = get_object_or_404(Listing, id=listing_id)

#             # Process the payment
#             amount = Decimal(data["amount"]) / 100  # Convert back to Naira
#             wallet = get_object_or_404(Wallet, user=request.user)
#             wallet.balance += amount
#             wallet.save()

#             WalletTransaction.objects.create(
#                 wallet=wallet,
#                 transaction_type="deposit",
#                 amount=amount,
#                 reference=reference,
#             )

#             # Generate a unique transaction tracking ID
#             tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"

#             seller_user = get_object_or_404(User, email=listing.realtor)
#             transaction = Transaction.objects.create(
#                 tracking_id=tracking_id,
#                 buyer=request.user,
#                 seller=seller_user,
#                 property=listing,
#                 amount=amount,
#             )

#             escrow_response = initiate_escrow(request, transaction)
#             if escrow_response['status'] == 'error':
#                 messages.error(request, f"Failed to initiate payment. Error: {response.text}")
#                 return redirect('housing')  # Redirect to the wallet funding page

#             # Notify both buyer and seller
#             Notification.objects.create(
#                 user=request.user,
#                 message=f"Please confirm your transaction for {listing.title}. <a href='/buyer-confirm/{transaction.id}/'>Click here</a>"
#             )
#             Notification.objects.create(
#                 user=seller_user,
#                 message=f"Please confirm the transaction for {listing.title}. <a href='/seller-confirm/{transaction.id}/'>Click here</a>"
#             )

#             messages.success(request, "Transaction successful! Please confirm in notifications.")
#             return redirect('housing')

#     messages.error(request, "Payment verification failed. Please try again.")
#     return redirect('housing')


# def initiate_escrow(request, transaction):
#     wallet = get_object_or_404(Wallet, user=request.user)

#     # Check if the wallet has sufficient balance
#     if wallet.balance < transaction.amount:
#         # Notify the buyer about insufficient funds
#         Notification.objects.create(
#             user=request.user,
#             message=f"Insufficient funds to initiate escrow for {transaction.property.title}. Please fund your wallet."
#         )

#         # Add an error message to the request
#         messages.error(request, f"Insufficient funds to initiate escrow for {transaction.property.title}. Please fund your wallet.")

#         # Return an error response
#         return {"status": "error", "message": "Insufficient funds to initiate escrow. Please fund your wallet."}



#     # Create escrow object
#     escrow = Escrow.objects.create(
#         buyer=request.user,
#         seller=transaction.seller,
#         amount=transaction.amount,
#         transaction=transaction
#     )

#     transaction.status = 'escrow_initiated'
#     transaction.save()

#     # Create audit log for escrow initiation
#     AuditLog.objects.create(
#         user=request.user,
#         action="Escrow Initiation",
#         details=f"Escrow initiated for {transaction.amount} on property {transaction.property.title}. Escrow Hash: {escrow.transaction_hash}"
#     )

#     return {"status": "success", "message": "Escrow initiated successfully!"}

# from django.shortcuts import redirect, render
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404

# @login_required
# def buy_property(request, listing_id):
#     listing = get_object_or_404(Listing, id=listing_id)
#     amount = listing.price

#     if request.method == "POST":
#         wallet = get_object_or_404(Wallet, user=request.user)

#         # Check if the user has sufficient funds
#         if wallet.balance < amount:
#             amount-= wallet.balance
#             # Redirect to fund wallet page with the required amount
#             return fund_wallet(request, amount=amount, listing_id=listing_id)
        
#         # Generate a unique transaction tracking ID
#         tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"

#         seller_user = get_object_or_404(User, email=listing.realtor)
#         transaction = Transaction.objects.create(
#             tracking_id=tracking_id,
#             buyer=request.user,
#             seller=seller_user,
#             property=listing,
#             amount=amount,
#         )

#         escrow_response = initiate_escrow(request, transaction)
#         if escrow_response['status'] == 'error':
#             messages.error(request, f"Failed to initiate payment from wallet")
#             return redirect('housing')  # Redirect to the wallet funding page

#         # Notify both buyer and seller
#         Notification.objects.create(
#             user=request.user,
#             message=f"Please confirm your transaction for {listing.title}. <a href='/buyer-confirm/{transaction.id}/'>Click here</a>"
#         )
#         Notification.objects.create(
#             user=seller_user,
#             message=f"Please confirm the transaction for {listing.title}. <a href='/seller-confirm/{transaction.id}/'>Click here</a>"
#         )

#         messages.success(request, "Transaction successful! Please confirm in notifications.")
#         return redirect('housing')


#         # # Update property status (e.g., mark it as sold)
#         # listing.sold = True
#         # listing.buyer = request.user  # Assuming there is a buyer field
#         # listing.save()

#         # Return success response or redirect to a success page
#         return JsonResponse({"status": "success", "message": "Property purchased successfully."})

#     # If the request method is not POST
#     return JsonResponse({"status": "error", "message": "Invalid request method. Use POST to buy property."})


# # Seller confirms the escrow transaction
# @login_required
# def seller_confirm(request, escrow_id):
#     escrow = get_object_or_404(Escrow, transaction_id=escrow_id, seller=request.user, status="pending")
#     escrow.status = "seller_confirmed"
#     escrow.seller_confirmed_at = now()
#     escrow.save()

#     AuditLog.objects.create(
#         user=request.user,
#         action="Seller Confirmation",
#         details=f"Seller confirmed receipt for escrow {escrow.transaction_hash}.",
#     )

#     return JsonResponse({"status": "success", "message": "Seller confirmation successful!"})

# # Buyer confirms the escrow transaction and releases funds to the seller's wallet
# @login_required
# def buyer_confirm(request, escrow_id):
#     escrow = get_object_or_404(Escrow, transaction_id=escrow_id, buyer=request.user)

#     # Check if the seller has confirmed the transaction
#     if escrow.status != "seller_confirmed":
#         return JsonResponse({
#             "status": "error",
#             "message": "Seller has not confirmed the transaction. Please contact the seller to confirm."
#         })

#     # Confirm buyer's approval and complete the escrow
#     escrow.status = "successful"
#     escrow.buyer_confirmed_at = now()
#     escrow.save()

#     # Ensure the seller has a wallet
#     seller_wallet = get_object_or_404(Wallet, user=escrow.seller)

#     # Transfer the amount from the buyer to the seller
#     buyer_wallet = get_object_or_404(Wallet, user=request.user)

#     # Check if buyer has sufficient balance
#     if buyer_wallet.balance < escrow.amount:
#         return JsonResponse({"status": "error", "message": "Insufficient balance to release funds."})

#     # Deduct from the buyer's wallet
#     buyer_wallet.balance -= escrow.amount
#     buyer_wallet.save()
#     print(escrow.amount)
#     # Add funds to the seller's wallet
#     seller_wallet.balance += escrow.amount
#     seller_wallet.save()

#     # Log the wallet transactions for both the buyer and seller
#     WalletTransaction.objects.update(
#         wallet=buyer_wallet,
#         transaction_type="escrow_release",
#         amount=escrow.amount,
#         reference=escrow.transaction_hash,
#     )

#     WalletTransaction.objects.create(
#         wallet=seller_wallet,
#         transaction_type="escrow_release",
#         amount=escrow.amount,
#         reference=escrow.transaction_hash,
#     )

#     # Log the action for audit purposes
#     AuditLog.objects.create(
#         user=request.user,
#         action="Buyer Confirmation",
#         details=f"Buyer confirmed service for escrow {escrow.transaction_hash}. Funds released to seller.",
#     )

#     return JsonResponse({"status": "success", "message": "Funds released to seller successfully!"})

from django.views.decorators.csrf import csrf_protect
from django.core.validators import RegexValidator

# Configure logging for security purposes
logger = logging.getLogger(__name__)

@login_required
@csrf_protect
def withdraw_wallet(request):
    if request.method == "POST":
        try:
            # Extract and validate input
            amount = request.POST.get("amount")
            bank_code = request.POST.get("bank_code")
            account_number = request.POST.get("account_number")

            # Input validation
            if not amount or not bank_code or not account_number:
                return JsonResponse({"status": "error", "message": "All fields are required."})
            
            try:
                amount = Decimal(amount)
                if amount <= 0:
                    return JsonResponse({"status": "error", "message": "Amount must be greater than zero."})
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid amount."})

            bank_code_validator = RegexValidator(r"^\d{3}$", "Bank code must be 3 digits.")
            account_number_validator = RegexValidator(r"^\d{10}$", "Account number must be 10 digits.")
            
            bank_code_validator(bank_code)
            account_number_validator(account_number)

            # Get wallet and check balance
            wallet = get_object_or_404(Wallet, user=request.user)
            if wallet.balance < amount:
                return JsonResponse({"status": "error", "message": "Insufficient balance."})

            # Deduct balance temporarily
            wallet.balance -= amount
            wallet.save()

            # Prepare and send request to Paystack
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            data = {
                "source": "balance",
                "reason": "Withdrawal",
                "amount": int(amount * 100),
                "recipient": {
                    "type": "nuban",
                    "name": request.user.get_full_name(),
                    "account_number": account_number,
                    "bank_code": bank_code,
                },
            }
            response = requests.post(
                "https://api.paystack.co/transfer", headers=headers, json=data, timeout=30
            )

            # Handle Paystack response
            if response.status_code == 200:
                transfer_data = response.json().get("data", {})
                transfer_code = transfer_data.get("transfer_code")

                # Log transaction
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="withdrawal",
                    amount=amount,
                    reference=transfer_code,
                )

                return JsonResponse({"status": "success", "message": "Withdrawal successful!"})
            else:
                # Roll back balance if transfer fails
                wallet.balance += amount
                wallet.save()

                logger.error(f"Paystack withdrawal error: {response.text}")
                return JsonResponse({"status": "error", "message": "Withdrawal failed. Please try again."})

        except requests.exceptions.RequestException as e:
            logger.exception("Network error during withdrawal.")
            return JsonResponse({"status": "error", "message": "A network error occurred. Please try again."})
        except Exception as e:
            logger.exception("An error occurred during withdrawal.")
            return JsonResponse({"status": "error", "message": "An unexpected error occurred. Please contact support."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})



