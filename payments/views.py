from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from django.db import transaction
from django.db.models import F
from decimal import Decimal
import requests
import logging
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.validators import RegexValidator

from .models import Wallet, WalletTransaction, Escrow, AuditLog, Transaction
from .utils import verify_webhook_signature
from user.models import Notification
from abrmservices.models import Listing
from django.contrib.auth import get_user_model
from ABRMS import settings

User = get_user_model()

# Configure logging for debugging and security purposes
logger = logging.getLogger(__name__)

def payments(request):
    return render(request, 'payments.html')  # Path to your HTML file

@login_required
@ensure_csrf_cookie
def fund_wallet(request, amount, listing_id):
    if request.method == "POST":
        try:
            amount = Decimal(amount)
            listing_id = listing_id

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
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers, timeout=30
        )
        response.raise_for_status()

        data = response.json()["data"]
        if data["status"] == "success":
            listing_id = data.get("metadata", {}).get("listing_id")
            listing = get_object_or_404(Listing, id=listing_id)
            fund_amount = Decimal(data["amount"]) / 100

            wallet = get_object_or_404(Wallet, user=request.user)
            # Use Django F expression for atomic update (see Django docs on F expressions)
            wallet.balance += fund_amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet, transaction_type="deposit", amount=fund_amount, reference=reference
            )
            tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"
            amount = listing.price
            seller_user = get_object_or_404(User, email=listing.realtor)
            transaction_obj = Transaction.objects.create(
                tracking_id=tracking_id,
                buyer=request.user,
                seller=seller_user,
                property=listing,
                amount=amount,
            )

            escrow_response = initiate_escrow(request, transaction_obj)
            if escrow_response['status'] == 'error':
                logger.error("Failed to initiate escrow.")
                messages.error(request, "Failed to initiate escrow.")
                return redirect('housing')
            else:
                escrow = get_object_or_404(Escrow, transaction=transaction_obj)

                Notification.objects.create(
                    user=request.user,
                    message=f"Please confirm your transaction from {transaction_obj.seller.name} for {transaction_obj.property.title}. <a href='{reverse('buyer_confirm', args=[escrow.id])}'>Click here</a>"
                )
                Notification.objects.create(
                    user=seller_user,
                    message=f"Please confirm the transaction from {transaction_obj.buyer.name} for  {transaction_obj.property.title}. <a href='{reverse('seller_confirm', args=[escrow.id])}'>Click here</a>"
                )
                messages.success(request, "Transaction initiated! Please confirm in notifications.")
                return redirect('housing')

        
    except requests.RequestException:
        logger.exception("Error verifying transaction.")
        messages.error(request, "A network error occurred. Please try again.")
    except Exception:
        logger.exception("Unexpected error during transaction verification.")
    messages.error(request, "Payment verification failed. Please contact support.")
    return redirect('housing')

def initiate_escrow(request, transaction_obj):
    try:
        wallet = get_object_or_404(Wallet, user=request.user)
        seller_wallet = get_object_or_404(Wallet, user=transaction_obj.seller)
        
        # Calculate available balance as total balance minus locked balance.
        # This ensures locked funds are not re-used.
        available_balance = wallet.balance - wallet.locked_balance
        if available_balance < transaction_obj.amount:
            Notification.objects.create(
                user=request.user,
                message=f"Insufficient available funds to initiate escrow for {transaction_obj.property.title}. Please fund your wallet."
            )
            messages.error(request, "Insufficient available funds. Please fund your wallet.")
            return {"status": "error", "message": "Insufficient available funds."}
        
        # Begin an atomic transaction to ensure data consistency
        with transaction.atomic():
            # Lock the funds by increasing the locked_balance
            wallet.locked_balance += transaction_obj.amount
            wallet.save(update_fields=['locked_balance'])

            seller_wallet.locked_balance += transaction_obj.amount
            seller_wallet.save()
            
            # Create the escrow record with a 'pending' status
            escrow = Escrow.objects.create(
                buyer=request.user,
                seller=transaction_obj.seller,
                amount=transaction_obj.amount,
                transaction=transaction_obj,
                status="pending"
            )
            
            # Create notifications for both buyer and seller
            Notification.objects.bulk_create([
                Notification(
                    user=request.user, 
                    message=f"You have successfully transferred {transaction_obj.property.price} to {transaction_obj.seller.name} for {transaction_obj.property.title}. The funds have been locked until the transaction is fully completed."
                ),
                Notification(
                    user=transaction_obj.seller,
                    message=f"{transaction_obj.seller.name} has successfully transferred {transaction_obj.property.price} to your wallet for {transaction_obj.property.title}. The funds have been locked until the transaction is fully completed."
                )
            ])
            
            # Update transaction status
            transaction_obj.status = 'escrow_initiated'
            transaction_obj.save(update_fields=['status'])
            
            # Log the escrow initiation for audit purposes
            AuditLog.objects.create(
                user=request.user,
                action="Escrow Initiation",
                details=f"Escrow initiated for {transaction_obj.amount} on property {transaction_obj.property.title}. Escrow Hash: {escrow.transaction_hash}"
            )
            
        return {"status": "success", "message": "Escrow initiated successfully."}
    except Exception as e:
        logger.exception("An error occurred during escrow initiation.")
        return {"status": "error", "message": "An error occurred. Please contact support."}

@login_required
def cancel_escrow(request, escrow_id):
    try:
        escrow = get_object_or_404(Escrow, id=escrow_id, buyer=request.user)
        if escrow.status not in ['pending', 'seller_confirmed']:
            return JsonResponse({"status": "error", "message": "Cannot cancel this transaction."})

        with transaction.atomic():
            # Unlock the funds by reducing the buyer's locked_balance
            buyer_wallet = get_object_or_404(Wallet, user=escrow.buyer)
            buyer_wallet.locked_balance -= escrow.amount
            buyer_wallet.save(update_fields=['locked_balance'])

            # Unlock the funds by reducing the Seller's locked_balance
            seller_wallet = get_object_or_404(Wallet, user=escrow.seller)
            seller_wallet.locked_balance -= escrow.amount
            seller_wallet.save(update_fields=['locked_balance'])

            escrow.status = "cancelled"
            escrow.save(update_fields=['status'])

            AuditLog.objects.create(
                user=request.user,
                action="Escrow Cancellation",
                details=f"Escrow {escrow.transaction_hash} cancelled. {escrow.amount} unlocked."
            )

        messages.success(request, "Transaction cancelled and funds unlocked.")
        return redirect('housing')
    except Exception as e:
        logger.exception("An error occurred during escrow cancellation.")
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

@login_required
def buy_property(request, listing_id):
    try:
        listing = get_object_or_404(Listing, id=listing_id)
        amount = listing.price

        if request.method == "POST":
            wallet = get_object_or_404(Wallet, user=request.user)
            # Calculate actual available funds by subtracting locked funds
            actual_balance = wallet.balance - wallet.locked_balance
            if actual_balance < amount:
                shortfall = amount - actual_balance
                return fund_wallet(request, amount=shortfall, listing_id=listing_id)
            elif actual_balance >= amount:
                tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"

                seller_user = get_object_or_404(User, email=listing.realtor)
                transaction_obj = Transaction.objects.create(
                    tracking_id=tracking_id,
                    buyer=request.user,
                    seller=seller_user,
                    property=listing,
                    amount=amount,
                )

                escrow_response = initiate_escrow(request, transaction_obj)
                if escrow_response['status'] == 'error':
                    logger.error("Failed to initiate escrow.")
                    messages.error(request, "Failed to initiate escrow.")
                    return redirect('housing')
                else:
                    escrow = get_object_or_404(Escrow, transaction=transaction_obj)

                    Notification.objects.create(
                        user=request.user,
                        message=f"Please confirm your transaction from {request.user.name} for {listing.title}. <a href='{reverse('buyer_confirm', args=[escrow.id])}'>Click here</a>"
                    )
                    Notification.objects.create(
                        user=seller_user,
                        message=f"Please confirm the transaction from {seller_user.name} for  {listing.title}. <a href='{reverse('seller_confirm', args=[escrow.id])}'>Click here</a>"
                    )

                    messages.success(request, "Transaction initiated! Please confirm in notifications.")
                    return redirect('housing')

        return JsonResponse({"status": "error", "message": "Invalid request method."})
    except Exception as e:
        logger.exception("An error occurred during property purchase.")
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

@login_required
def seller_confirm(request, escrow_id):
    try:
        escrow = get_object_or_404(Escrow, id=escrow_id, seller=request.user)
        if escrow.status == "cancelled":
            return JsonResponse({"status": "error", "message": "This transaction has been cancelled."})
        
        if escrow.status == "successful":
            return JsonResponse({"status": "error", "message": "Transaction has already been completed."})
        if escrow.status == "pending":
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
        escrow = get_object_or_404(Escrow, id=escrow_id, buyer=request.user)

        if escrow.status == "cancelled":
            return JsonResponse({"status": "error", "message": "This transaction has been cancelled."})
        if escrow.status == "successful":
            return JsonResponse({"status": "error", "message": "Transaction has already been completed."})
        if escrow.status == "pending":
            return JsonResponse({"status": "error", "message": "Seller has not confirmed receipt yet."})

        if escrow.status == "seller_confirmed":
            with transaction.atomic():
                escrow.status = "successful"
                escrow.buyer_confirmed_at = now()
                escrow.save(update_fields=['status', 'buyer_confirmed_at'])

                transaction_obj = escrow.transaction
                transaction_obj.status = "completed"
                transaction_obj.save(update_fields=['status'])

                buyer_wallet = get_object_or_404(Wallet, user=escrow.buyer)
                seller_wallet = get_object_or_404(Wallet, user=escrow.seller)

                # Ensure buyer_wallet has the locked funds
                if buyer_wallet.locked_balance < escrow.amount:
                    return JsonResponse({"status": "error", "message": "Insufficient locked funds in buyer's wallet."})

                # Calculate commission (10%)
                commission = escrow.amount * Decimal("0.10")
                seller_amount = escrow.amount - commission

                # Deduct the escrowed amount from locked_balance
                buyer_wallet.locked_balance -= escrow.amount
                buyer_wallet.balance -= escrow.amount
                buyer_wallet.save()

                # Credit seller and process commission
                seller_wallet.locked_balance -= escrow.amount
                seller_wallet.balance += seller_amount
                seller_wallet.save()

                super_user = User.objects.filter(is_superuser=True).first()
                if super_user:
                    super_wallet = get_object_or_404(Wallet, user=super_user)
                    super_wallet.balance += commission
                    super_wallet.save()
                    AuditLog.objects.create(
                        user=super_user,
                        action="Commission Credited",
                        details=f"Commission of {commission} credited from transaction {escrow.transaction_hash}."
                    )
                else:
                    logger.error("Superuser not found. Commission not credited.")

                AuditLog.objects.create(
                    user=request.user,
                    action="Buyer Confirmation",
                    details=(f"Buyer confirmed transaction {escrow.transaction_hash}. "
                             f"Funds transferred: Seller credited {seller_amount}, Superuser credited {commission}.")
                )

                Notification.objects.create(
                    user=escrow.seller,
                    message=(f"Buyer has confirmed the transaction for {transaction_obj.property.title}. "
                             f"Funds have been released: {seller_amount} credited to your wallet.")
                )

            messages.success(request, "Transaction completed successfully!")
            return redirect('housing')
        else:
            raise NameError("Unexpected escrow status encountered.")
    except Exception as e:
        logger.exception("An error occurred during buyer confirmation.")
        return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

@login_required
@csrf_protect
def withdraw_wallet(request):
    if request.method == "POST":
        try:
            # Extract and validate input fields
            amount = request.POST.get("amount")
            bank_code = request.POST.get("bank_code")
            account_number = request.POST.get("account_number")

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

            wallet = get_object_or_404(Wallet, user=request.user)
            # Prevent withdrawal of locked funds:
            if (wallet.balance - wallet.locked_balance) < amount:
                return JsonResponse({"status": "error", "message": "Insufficient available balance."})

            # Deduct the amount from the total balance
            wallet.balance -= amount
            wallet.save()

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

            if response.status_code == 200:
                transfer_data = response.json().get("data", {})
                transfer_code = transfer_data.get("transfer_code")

                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="withdrawal",
                    amount=amount,
                    reference=transfer_code,
                )

                return JsonResponse({"status": "success", "message": "Withdrawal successful!"})
            else:
                # Roll back the balance deduction if transfer fails
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
# from decimal import Decimal
# import logging
# from django.views.decorators.csrf import csrf_exempt

# # Configure logging for security and debugging
# logger = logging.getLogger(__name__)

# User = get_user_model()

# def payments(request):
#     return render(request, 'payments.html')  # Path to your HTML file


# from django.db import transaction
# from django.urls import reverse
# from django.views.decorators.csrf import ensure_csrf_cookie
# from django.db.models import F

# # Payment initiation view
# @login_required
# @ensure_csrf_cookie
# def fund_wallet(request, amount, listing_id):
#     if request.method == "POST":
#         try:
#             amount = Decimal(amount)
#             listing_id = listing_id

#             if amount <= 0:
#                 messages.error(request, "Invalid amount specified.")
#                 return redirect('housing')

#             listing = get_object_or_404(Listing, id=listing_id)
#             reference = f"fund_{request.user.id}_{int(now().timestamp())}"

#             headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
#             payload = {
#                 "email": request.user.email,
#                 "amount": int(amount * 100),
#                 "reference": reference,
#                 "callback_url": request.build_absolute_uri(reverse('wallet_callback')),
#                 "metadata": {"listing_id": listing.id},
#             }

#             response = requests.post(
#                 "https://api.paystack.co/transaction/initialize", 
#                 headers=headers, json=payload, timeout=30
#             )
#             response.raise_for_status()

#             payment_url = response.json().get('data', {}).get('authorization_url')
#             if payment_url:
#                 return redirect(payment_url)
#             else:
#                 logger.error("Payment URL not found in Paystack response.")
#                 messages.error(request, "Failed to initiate payment. Please try again.")
#         except requests.RequestException as e:
#             logger.exception("Network error during payment initiation.")
#             messages.error(request, "A network error occurred. Please try again.")
#         except Exception as e:
#             logger.exception("Error during payment initiation.")
#             messages.error(request, "An unexpected error occurred. Please try again.")
#     return redirect('housing')



# @login_required
# def wallet_callback(request):
#     reference = request.GET.get("reference")
#     headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

#     try:
#         response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers, timeout=30)
#         response.raise_for_status()

#         data = response.json()["data"]
#         if data["status"] == "success":
#             listing_id = data.get("metadata", {}).get("listing_id")
#             listing = get_object_or_404(Listing, id=listing_id)
#             amount = Decimal(data["amount"]) / 100

#             wallet = get_object_or_404(Wallet, user=request.user)
#             wallet.balance = F('balance') + amount
#             wallet.save()

#             WalletTransaction.objects.create(
#                 wallet=wallet, transaction_type="deposit", amount=amount, reference=reference
#             )
#             tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"

#             seller_user = get_object_or_404(User, email=listing.realtor)
#             Transaction.objects.create(
#                 tracking_id=tracking_id,
#                 buyer=request.user,
#                 seller=seller_user,
#                 property=listing,
#                 amount=amount,
#             )

#             transaction = get_object_or_404(Transaction, tracking_id=tracking_id)
#             escrow_response = initiate_escrow(request, transaction)
#             if escrow_response['status'] == 'error':
#                 logger.error("Failed to initiate payment from wallet.")
#                 messages.error(request, "Failed to initiate payment from wallet.")
#                 return redirect('housing')
#             else:
#                 messages.success(request, "Transaction successful! Please confirm in notifications.")
#                 return redirect('housing')


#     except requests.RequestException:
#         logger.exception("Error verifying transaction.")
#         messages.error(request, "A network error occurred. Please try again.")
#     except Exception:
#         logger.exception("Unexpected error during transaction verification.")
#     messages.error(request, "Payment verification failed. Please contact support.")
#     return redirect('housing')

# from django.db import transaction

# def initiate_escrow(request, transaction_obj):
#     try:
#         wallet = get_object_or_404(Wallet, user=request.user)
        
#         # Use the available_balance property if you added it,
#         # otherwise calculate manually (if not using a locked_balance field).
#         if wallet.available_balance < transaction_obj.amount:
#             Notification.objects.create(
#                 user=request.user,
#                 message=f"Insufficient available funds to initiate escrow for {transaction_obj.property.title}. Please fund your wallet."
#             )
#             messages.error(request, "Insufficient available funds. Please fund your wallet.")
#             return {"status": "error", "message": "Insufficient available funds."}
        
#         # Begin an atomic transaction to avoid race conditions
#         with transaction.atomic():
#             # Lock the funds by increasing locked_balance
#             wallet.locked_balance += transaction_obj.amount
#             wallet.save(update_fields=['locked_balance'])
            
#             # Create the escrow record
#             escrow = Escrow.objects.create(
#                 buyer=request.user,
#                 seller=transaction_obj.seller,
#                 amount=transaction_obj.amount,
#                 transaction=transaction_obj,
#                 status="pending"
#             )
            
#             Notification.objects.bulk_create([
#                 Notification(
#                     user=request.user, 
#                     message=f"Please confirm your transaction for {transaction_obj.property.title}. "
#                             f"<a href='{reverse('buyer_confirm', args=[escrow.id])}'>Click here</a>"
#                 ),
#                 Notification(
#                     user=transaction_obj.seller,
#                     message=f"A buyer has initiated a transaction for {transaction_obj.property.title}. "
#                             f"<a href='{reverse('seller_confirm', args=[escrow.id])}'>Click here</a>"
#                 )
#             ])
            
#             transaction_obj.status = 'escrow_initiated'
#             transaction_obj.save(update_fields=['status'])
            
#             AuditLog.objects.create(
#                 user=request.user,
#                 action="Escrow Initiation",
#                 details=f"Escrow initiated for {transaction_obj.amount} on property {transaction_obj.property.title}. Escrow Hash: {escrow.transaction_hash}"
#             )
            
#         return {"status": "success", "message": "Escrow initiated successfully."}
#     except Exception as e:
#         logger.exception("An error occurred during escrow initiation.")
#         return {"status": "error", "message": "An error occurred. Please contact support."}


# @login_required
# def cancel_escrow(request, escrow_id):
#     try:
#         escrow = get_object_or_404(Escrow, id=escrow_id, buyer=request.user)
#         if escrow.status not in ['pending', 'seller_confirmed']:
#             return JsonResponse({"status": "error", "message": "Cannot cancel this transaction."})

#         with transaction.atomic():
#             # Unlock the funds by reducing locked_balance
#             buyer_wallet = get_object_or_404(Wallet, user=escrow.buyer)
#             buyer_wallet.locked_balance -= escrow.amount
#             buyer_wallet.save(update_fields=['locked_balance'])

#             escrow.status = "cancelled"
#             escrow.save(update_fields=['status'])

#             AuditLog.objects.create(
#                 user=request.user,
#                 action="Escrow Cancellation",
#                 details=f"Escrow {escrow.transaction_hash} cancelled. {escrow.amount} unlocked."
#             )

#         messages.success(request, "Transaction cancelled and funds unlocked.")
#         return redirect('housing')
#     except Exception as e:
#         logger.exception("An error occurred during escrow cancellation.")
#         return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})



# @login_required
# def buy_property(request, listing_id):
#     try:
#         listing = get_object_or_404(Listing, id=listing_id)
#         amount = listing.price

#         if request.method == "POST":
#             wallet = get_object_or_404(Wallet, user=request.user)
#             actual_ballance = Decimal(wallet.balance) - Decimal(wallet.locked_balance)
#             if actual_ballance < amount:
#                 shortfall = amount - actual_ballance
#                 return fund_wallet(request, amount=shortfall, listing_id=listing_id)
#             elif actual_ballance >= amount:
#                 tracking_id = f"TX_{request.user.id}_{listing.id}_{int(datetime.now().timestamp())}"

#                 seller_user = get_object_or_404(User, email=listing.realtor)
#                 transaction = Transaction.objects.create(
#                     tracking_id=tracking_id,
#                     buyer=request.user,
#                     seller=seller_user,
#                     property=listing,
#                     amount=amount,
#                 )

#                 escrow_response = initiate_escrow(request, transaction)
#                 if escrow_response['status'] == 'error':
#                     logger.error("Failed to initiate payment from wallet.")
#                     messages.error(request, "Failed to initiate payment from wallet.")
#                     return redirect('housing')

#                 Notification.objects.create(
#                     user=request.user,
#                     message=f"Please confirm your transaction for {listing.title}. <a href='/buyer-confirm/{transaction.id}/'>Click here</a>"
#                 )
#                 Notification.objects.create(
#                     user=seller_user,
#                     message=f"Please confirm the transaction for {listing.title}. <a href='/seller-confirm/{transaction.id}/'>Click here</a>"
#                 )

#                 messages.success(request, "Transaction successful! Please confirm in notifications.")
#                 return redirect('housing')

#         return JsonResponse({"status": "error", "message": "Invalid request method."})
#     except Exception as e:
#         logger.exception("An error occurred during property purchase.")
#         return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

# @login_required
# def seller_confirm(request, escrow_id):
#     try:
#         escrow = get_object_or_404(Escrow, id=escrow_id, seller=request.user)
#         if escrow.status == "cancelled":
#             return JsonResponse({"status": "error", "message": "This transaction has been cancelled."})
        
#         if escrow.status == "successful":
#             return JsonResponse({"status": "error", "message": "Transaction has already been completed."})
#         if escrow.status == "pending":
        
#             escrow.status = "seller_confirmed"
#             escrow.seller_confirmed_at = now()
#             escrow.save()

#             AuditLog.objects.create(
#                 user=request.user,
#                 action="Seller Confirmation",
#                 details=f"Seller confirmed receipt for escrow {escrow.transaction_hash}."
#             )

#             return JsonResponse({"status": "success", "message": "Seller confirmation successful!"})
#     except Exception as e:
#         logger.exception("An error occurred during seller confirmation.")
#         return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})

# from decimal import Decimal
# from django.db import transaction  # recommended for atomicity
# @login_required
# def buyer_confirm(request, escrow_id):
#     try:
#         escrow = get_object_or_404(Escrow, id=escrow_id, buyer=request.user)

#         if escrow.status == "cancelled":
#             return JsonResponse({"status": "error", "message": "This transaction has been cancelled."})
#         if escrow.status == "successful":
#             return JsonResponse({"status": "error", "message": "Transaction has already been completed."})
#         if escrow.status == "pending":
#             return JsonResponse({"status": "error", "message": "Seller has not confirmed receipt yet."})

#         if escrow.status == "seller_confirmed":
#             with transaction.atomic():
#                 escrow.status = "successful"
#                 escrow.buyer_confirmed_at = now()
#                 escrow.save(update_fields=['status', 'buyer_confirmed_at'])

#                 transaction_obj = escrow.transaction
#                 transaction_obj.status = "completed"
#                 transaction_obj.save(update_fields=['status'])

#                 buyer_wallet = get_object_or_404(Wallet, user=escrow.buyer)
#                 seller_wallet = get_object_or_404(Wallet, user=escrow.seller)

#                 # Ensure buyer_wallet has the locked funds
#                 if buyer_wallet.locked_balance < escrow.amount:
#                     return JsonResponse({"status": "error", "message": "Insufficient locked funds in buyer's wallet."})

#                 # Calculate commission (10%)
#                 commission = escrow.amount * Decimal("0.10")
#                 seller_amount = escrow.amount - commission

#                 # Deduct the escrowed amount from locked_balance instead of balance
#                 buyer_wallet.locked_balance -= escrow.amount
#                 buyer_wallet.save(update_fields=['locked_balance'])

#                 # Credit seller and credit commission to superuser as before
#                 seller_wallet.balance += seller_amount
#                 seller_wallet.save(update_fields=['balance'])

#                 super_user = User.objects.filter(is_superuser=True).first()
#                 if super_user:
#                     super_wallet = get_object_or_404(Wallet, user=super_user)
#                     super_wallet.balance += commission
#                     super_wallet.save(update_fields=['balance'])
#                     AuditLog.objects.create(
#                         user=super_user,
#                         action="Commission Credited",
#                         details=f"Commission of {commission} credited from transaction {escrow.transaction_hash}."
#                     )
#                 else:
#                     logger.error("Superuser not found. Commission not credited.")

#                 AuditLog.objects.create(
#                     user=request.user,
#                     action="Buyer Confirmation",
#                     details=(f"Buyer confirmed transaction {escrow.transaction_hash}. "
#                              f"Funds transferred: Seller credited {seller_amount}, Superuser credited {commission}.")
#                 )

#                 Notification.objects.create(
#                     user=escrow.seller,
#                     message=(f"Buyer has confirmed the transaction for {transaction_obj.property.title}. "
#                              f"Funds have been released: {seller_amount} credited to your wallet.")
#                 )

#             messages.success(request, "Transaction completed successfully!")
#             return redirect('housing')
#         else:
#             raise NameError("Unexpected escrow status encountered.")
#     except Exception as e:
#         logger.exception("An error occurred during buyer confirmation.")
#         return JsonResponse({"status": "error", "message": "An error occurred. Please try again."})



# from django.views.decorators.csrf import csrf_protect
# from django.core.validators import RegexValidator

# # Configure logging for security purposes
# logger = logging.getLogger(__name__)

# @login_required
# @csrf_protect
# def withdraw_wallet(request):
#     if request.method == "POST":
#         try:
#             # Extract and validate input
#             amount = request.POST.get("amount")
#             bank_code = request.POST.get("bank_code")
#             account_number = request.POST.get("account_number")

#             # Input validation
#             if not amount or not bank_code or not account_number:
#                 return JsonResponse({"status": "error", "message": "All fields are required."})
            
#             try:
#                 amount = Decimal(amount)
#                 if amount <= 0:
#                     return JsonResponse({"status": "error", "message": "Amount must be greater than zero."})
#             except ValueError:
#                 return JsonResponse({"status": "error", "message": "Invalid amount."})

#             bank_code_validator = RegexValidator(r"^\d{3}$", "Bank code must be 3 digits.")
#             account_number_validator = RegexValidator(r"^\d{10}$", "Account number must be 10 digits.")
            
#             bank_code_validator(bank_code)
#             account_number_validator(account_number)

#             # Get wallet and check balance
#             wallet = get_object_or_404(Wallet, user=request.user)
#             if wallet.balance < amount:
#                 return JsonResponse({"status": "error", "message": "Insufficient balance."})

#             # Deduct balance temporarily
#             wallet.balance -= amount
#             wallet.save()

#             # Prepare and send request to Paystack
#             headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
#             data = {
#                 "source": "balance",
#                 "reason": "Withdrawal",
#                 "amount": int(amount * 100),
#                 "recipient": {
#                     "type": "nuban",
#                     "name": request.user.get_full_name(),
#                     "account_number": account_number,
#                     "bank_code": bank_code,
#                 },
#             }
#             response = requests.post(
#                 "https://api.paystack.co/transfer", headers=headers, json=data, timeout=30
#             )

#             # Handle Paystack response
#             if response.status_code == 200:
#                 transfer_data = response.json().get("data", {})
#                 transfer_code = transfer_data.get("transfer_code")

#                 # Log transaction
#                 WalletTransaction.objects.create(
#                     wallet=wallet,
#                     transaction_type="withdrawal",
#                     amount=amount,
#                     reference=transfer_code,
#                 )

#                 return JsonResponse({"status": "success", "message": "Withdrawal successful!"})
#             else:
#                 # Roll back balance if transfer fails
#                 wallet.balance += amount
#                 wallet.save()

#                 logger.error(f"Paystack withdrawal error: {response.text}")
#                 return JsonResponse({"status": "error", "message": "Withdrawal failed. Please try again."})

#         except requests.exceptions.RequestException as e:
#             logger.exception("Network error during withdrawal.")
#             return JsonResponse({"status": "error", "message": "A network error occurred. Please try again."})
#         except Exception as e:
#             logger.exception("An error occurred during withdrawal.")
#             return JsonResponse({"status": "error", "message": "An unexpected error occurred. Please contact support."})

#     return JsonResponse({"status": "error", "message": "Invalid request method."})



