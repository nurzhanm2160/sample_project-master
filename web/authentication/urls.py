from django.urls import path
from .views import RegisterView, SetNewPasswordAPIView, VerifyEmail, LoginAPIView, PasswordTokenCheckAPI, RequestPasswordResetEmail, LogoutAPIView, AuthUserDetailAPIView, ChangePasswordView, UpdateProfileView, UserCoinWalletAPIView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    path('my-profile/', AuthUserDetailAPIView.as_view(), name='auth-user'),
    path('update_password/', ChangePasswordView.as_view(), name='auth_update_password'),
    path('update_profile/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('my_wallets/', UserCoinWalletAPIView.as_view(), name='my_wallets'),

]
