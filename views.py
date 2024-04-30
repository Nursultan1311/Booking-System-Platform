import random
from datetime import datetime, timedelta

import jwt
from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from users.forms import CreateUserRequestForm
from users.models import User, Application, Document, UserCreateRequest
from users.serializers import UserSerializer, DocumentSerializer, ApplicationSerializer, UserLoginSerializer


class CheckUserView(APIView):
    def post(self, request):
        phone_number = request.data['phone_number']
        email = request.data['email']

        if len(User.objects.filter(phone_number=phone_number)) + len(User.objects.filter(email=email)) == 0:
            return Response({}, status=200)
        return Response({}, status=400)


class RegisterRequestView(APIView):
    def post(self, request):
        form = CreateUserRequestForm(data=request.data)
        if form.is_valid():
            try:
                userCreateRequest = form.save()
            except:
                return Response({'message': 'Пользователь с такой почтой или номером уже существует!'})
            sms_code = str(random.randint(100000, 999999))
            userCreateRequest.sms_code = sms_code
            userCreateRequest.save()

            return Response({'message': 'SMS code sent. Please verify to complete registration.', 'sms_code': sms_code},
                            status=200)

        return Response(form.errors, status=400)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if len(UserCreateRequest.objects.filter(sms_code=request.data['sms_code'])) == 0:
                return Response({'message': 'Wrong sms code'}, status=400)

            userCreateRequest = UserCreateRequest.objects.filter(sms_code=request.data['sms_code']).first()

            user = User(
                first_name=userCreateRequest.phone_number,
                last_name=userCreateRequest.last_name,
                email=userCreateRequest.email,
                phone_number=userCreateRequest.phone_number,
                username=userCreateRequest.username,
                password=userCreateRequest.password,
            )
            user.save()

            token = jwt.encode(
                {'id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24), 'iat': datetime.utcnow()}, 'sercet',
                algorithm='HS256').encode('utf-8')

            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {'token': token}

            return response
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    def post(self, request):
        try:
            phone_number = request.data['phone_number']

            user = User.objects.filter(phone_number=phone_number).first()

            if user is None:
                raise AuthenticationFailed("User not found")

            token = jwt.encode(
                {'id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24), 'iat': datetime.utcnow()}, 'sercet',
                algorithm='HS256').encode('utf-8')

            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {'token': token}

            return response
        except:
            raise AuthenticationFailed("Phone number must be provided")


class UserView(APIView):
    def post(self, request):
        token = request.data.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed("Failed to authorize")
        try:
            payload = jwt.decode(token, 'sercet', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Authorization is expired")
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class AddDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure the user has an application to add documents to
            application, created = Application.objects.get_or_create(user=user)
            serializer.save(application=application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentStatusUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, document_id):
        document = Document.objects.get(id=document_id)
        status = request.data.get('status')
        if status in ['approved', 'rejected']:
            document.status = status
            document.save()
            document.application.calculate_score()
            return Response({'status': 'Document status updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)


class ApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            application = request.user.application
            serializer = ApplicationSerializer(application)
            return Response(serializer.data)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=404)
