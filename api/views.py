from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters import rest_framework as rest_filters
from rest_framework import filters, mixins, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.models import Category, Genre, Review, Title, User
from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModeratorOrReadOnly
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreatePatchSerializer,
    TitleGetSerializer,
    EmailSerializer,
    UserSerializer,
    UserRegistrationSerializer
)
from api_yamdb.settings import NOREPLY_EMAIL


class ListCreateDestroyNameSlugModelsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [rest_filters.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'slug']
    filterset_classes = ['name']
    lookup_field = 'slug'


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    serializer_class = UserSerializer
    search_fields = ['username', ]
    lookup_field = 'username'
    permission_classes = (IsAdmin,)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated, ),
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmailConfirmViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        url_path='email',
        permission_classes=(permissions.AllowAny,),
    )
    def send_confirmation_code(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, create = User.objects.get_or_create(
            email=serializer.validated_data['email'].lower(),
        )
        token = default_token_generator.make_token(user)
        mail_subject = 'Confirmation code'
        message = f'Use this code to gain access: "{token}"'
        send_mail(
            mail_subject,
            message,
            NOREPLY_EMAIL,
            [user.email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        url_path='token',
        permission_classes=(permissions.AllowAny,),
    )
    def user_registration(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = get_object_or_404(
            User, email=serializer.validated_data['email'].lower()
        )
        code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(email, code):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(email)
        return Response(
            {'token': f'{token.access_token}'},
            status=status.HTTP_200_OK
        )


class GenreViewSet(ListCreateDestroyNameSlugModelsViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDestroyNameSlugModelsViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-pk', 'name')
    filter_backends = [rest_filters.DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitleCreatePatchSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)
