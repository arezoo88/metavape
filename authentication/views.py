from django.contrib.auth import get_user_model
from rest_framework import generics, serializers, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from .serializers import (
    RegisterSerializer,
    EmailverificationSerializer,
    LoginSerializer,
    LogoutSerializer,
    RelationSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
)
from django.urls import reverse
from .utils import Utils
from django.conf import settings
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.http import HttpResponsePermanentRedirect
import os
from rest_framework.generics import get_object_or_404
from authentication.models import Relation
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get("APP_SCHEME"), "http", "https"]


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data["email"])

        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse("email-verify")
        absurl = "http://" + current_site + relativeLink + "?token=" + str(token)
        email_body = "Hi " + "Use link below to verify your email \n" + absurl
        data = {
            "email_body": email_body,
            "email_subject": "Verify your email",
            "to": user_data["email"],
        }
        Utils.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailverificationSerializer
    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        print(11, token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response(
                {"email": "Successfully activated"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"error": "invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get("email", "")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )

            redirect_url = request.data.get("redirect_url", "")
            absurl = "http://" + current_site + relativeLink
            email_body = (
                "Hello, \n Use link below to reset your password  \n"
                + absurl
                + "?redirect_url="
                + redirect_url
            )
            data = {
                "email_body": email_body,
                "to": user.email,
                "email_subject": "Reset your passsword",
            }
            Utils.send_email(data)
        return Response(
            {"success": "We have sent you a link to reset your password"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get("redirect_url")

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + "?token_valid=False")
                else:
                    return CustomRedirect("http://10.0.2.2:8000" + "?token_valid=False")

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url
                    + "?token_valid=True&message=Credentials Valid&uidb64="
                    + uidb64
                    + "&token="
                    + token
                )
            else:
                # return Response({'success':True})
                # print(55,os.environ.get('FRONTEND_URL', ''))
                return CustomRedirect("http://10.0.2.2:8000" + "?token_valid=False")

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + "?token_valid=False")

            except UnboundLocalError as e:
                return Response(
                    {"error": "Token is not valid, please request a new one"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset success"},
            status=status.HTTP_200_OK,
        )


class RelationApiView(generics.ListCreateAPIView, generics.UpdateAPIView):
    serializer_class = RelationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        following = get_object_or_404(User, pk=user_id)
        check_relation = Relation.objects.filter(
            from_user=request.user, to_user=following
        )
        if check_relation.exists():
            return Response({"success": False}, status=status.HTTP_200_OK)
        else:
            obj = Relation.objects.create(from_user=request.user, to_user=following)
            serializer = self.serializer_class(obj)
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )

    def list(self, request, *args, **kwargs):
        type = self.request.query_params.get("type")
        if type and type == "follower":
            relations = Relation.objects.filter(to_user=request.user)
        elif type and type == "following":
            relations = Relation.objects.filter(from_user=request.user)
        else:
            relations = Relation.objects.filter(
                Q(from_user=request.user) | Q(to_user=request.user)
            )
        serializer = self.serializer_class(relations, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unfollow(request):
    user_id = request.data.get("user_id")
    following = get_object_or_404(User, pk=user_id)
    check_relation = Relation.objects.filter(from_user=request.user, to_user=following)
    if check_relation.exists():
        check_relation.delete()
        return Response({"success": True})
    else:
        return Response({"success": False, "error": "not exists"})
