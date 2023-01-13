import jwt

from pprint import pprint

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status, views, permissions

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from coin.models import Plan
from coin.serializers import PlanSerializer
# from .renderers import UserRenderer
from .serializers import RegisterSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LoginSerializer, LogoutSerializer, UserDetailSerializer, UpdateUserSerializer, UpdatePasswordSerializer, UserCoinWalletSerializer
from .utils import Util
from coin.models import CoinWallet, Coin


class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    # renderer_classes = (UserRenderer,)

    inviter_referral_code = openapi.Parameter(
        'code', in_=openapi.IN_QUERY, description='User Referral code', type=openapi.TYPE_STRING)

    source_name_code = openapi.Parameter(
        'source', in_=openapi.IN_QUERY, description='Marketing Source code', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[inviter_referral_code, source_name_code])
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        code = request.GET.get('code')
        marketing_source_name = request.GET.get('source')
        if code:
            inviter = User.objects.filter(referral_code=code)[0]
            user.recommended_by = inviter
            user.save()
        else:
            pass

        if marketing_source_name:
            user.sourse_name = marketing_source_name
            user.save()
        else:
            pass

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'Hi '+user.email+' Use link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

        # Util.send_email(data)
        # TODO Переделать на нормальное отправление подтверждения почты
        new_user_data = {'email_data': data, 'email': user.email, 'username': user.username, 'token': str(token)}
        return Response(new_user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                for coin in Coin.objects.all():
                    CoinWallet.objects.create(
                        owner=user,
                        coin=coin
                    )

            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            # Util.send_email(data)
        return Response(
            {
                'data':
                 {
                     'email_data':data,
                     'uidb64':uidb64,
                     'token':token,
                  },
             'success': 'We have sent you a link to reset your password'
            }, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status.HTTP_204_NO_CONTENT)


class AuthUserDetailAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)

        return Response(serializer.data, status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdatePasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        old_password_status = user.check_password(old_password)
        if old_password_status:
            user.set_password(new_password)
            user.save()
            return Response({'success': True, 'message': 'Password reset successfull'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Old password is not correct'},
                            status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        user = request.user

        user.some_data = request.data.get('some_data')
        user.save()

        return Response({'success': True, 'message': 'Update successfull'}, status=status.HTTP_200_OK)


class UserCoinWalletAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserCoinWalletSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        returned_data = user.my_wallets

        return Response(returned_data, status.HTTP_200_OK)


# class AuthUserDetailAPIView(generics.GenericAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = UserDetailSerializer

#     def get(self, request):
#         user = request.user
#         serializer = self.serializer_class(user)

#         return Response(serializer.data, status.HTTP_200_OK)

class UserReferallAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def post(self, request):
        user = request.data
        # user_object = User.objects.get(id=user['user_id'])
        user_object = get_object_or_404(User, id=user['user_id'])
        first_level_referrals = UserDetailSerializer(user_object.first_level_referrals, many=True)
        second_level_referrals = UserDetailSerializer(user_object.second_level_referrals, many=True)


        return Response({
            "first_level_referrals": first_level_referrals.data, 
            "second_level_referrals": second_level_referrals.data
            })

class UserPlanAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def post(self, request):
        user = request.data
        user_object = get_object_or_404(User, id=user['user_id'])
        my_plan = PlanSerializer(user_object.my_plan)

        return Response({
            "my_plan": my_plan.data
        })