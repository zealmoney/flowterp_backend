from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import RecentFlow, SavedSetup
from .serializers import (
    FlowTerpTokenObtainPairSerializer,
    MeSerializer,
    RecentFlowSerializer,
    RecentFlowTrackSerializer,
    RegisterSerializer,
    SavedSetupSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class FlowTerpTokenObtainPairView(TokenObtainPairView):
    serializer_class = FlowTerpTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class SavedSetupListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedSetupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSetup.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedSetupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavedSetupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSetup.objects.filter(user=self.request.user)


class RecentFlowListView(generics.ListAPIView):
    serializer_class = RecentFlowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecentFlow.objects.filter(user=self.request.user).order_by("-last_used_at")[:6]


class RecentFlowDeleteView(generics.DestroyAPIView):
    serializer_class = RecentFlowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecentFlow.objects.filter(user=self.request.user)


class RecentFlowTrackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RecentFlowTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        filters_json = serializer.validated_data["filters_json"]
        source = serializer.validated_data["source"]

        existing = RecentFlow.objects.filter(
            user=request.user,
            name=name,
            filters_json=filters_json,
        ).first()

        if existing:
            existing.source = source
            existing.save(update_fields=["source", "last_used_at"])
            tracked = existing
        else:
            tracked = RecentFlow.objects.create(
                user=request.user,
                name=name,
                filters_json=filters_json,
                source=source,
            )

        stale_ids = list(
            RecentFlow.objects.filter(user=request.user)
            .order_by("-last_used_at")
            .values_list("id", flat=True)[6:]
        )

        if stale_ids:
            RecentFlow.objects.filter(user=request.user, id__in=stale_ids).delete()

        return Response(
            RecentFlowSerializer(tracked).data,
            status=status.HTTP_200_OK,
        )