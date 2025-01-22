from django.urls import path
from . import views

urlpatterns = [
    path('buy-property/<int:listing_id>/', views.buy_property, name='buy_property'),

    # Payment and wallet-related paths
    path('payments/', views.payments, name='payments'), 
    path('fund-wallet/', views.fund_wallet, name="fund_wallet"),
    path('wallet/callback/', views.wallet_callback, name="wallet_callback"),
    
    # Escrow-related paths
    path('initiate-escrow/', views.initiate_escrow, name="initiate_escrow"),
    
    # Buyer and Seller confirmation related to escrow
    path('buyer-confirm/<int:escrow_id>/', views.buyer_confirm, name="buyer_confirm"),
    path('seller-confirm/<int:escrow_id>/', views.seller_confirm, name="seller_confirm"),
    
    # Withdrawal-related paths
    path('withdraw-wallet/', views.withdraw_wallet, name="withdraw_wallet"),
]
