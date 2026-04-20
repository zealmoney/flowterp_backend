from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import StrainFeedback, build_feedback_signature, normalize_feedback_filters
from .serializers import (
    StrainFeedbackReadSerializer,
    StrainFeedbackWriteSerializer,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .memory_services import build_user_memory_summary


class StrainFeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StrainFeedback.objects.filter(user=self.request.user).select_related("strain")

        params = self.request.query_params
        has_filter_params = any(
            key in params
            for key in [
                "state",
                "effect",
                "terpene",
                "time_of_day",
                "strain_type",
                "featured",
                "min_thc",
                "max_thc",
                "mode",
            ]
        )

        if has_filter_params:
            raw_filters = {
                "state": params.get("state"),
                "effect": params.get("effect"),
                "terpene": params.get("terpene"),
                "time_of_day": params.get("time_of_day"),
                "strain_type": params.get("strain_type"),
                "featured": params.get("featured") == "true",
                "min_thc": params.get("min_thc"),
                "max_thc": params.get("max_thc"),
                "mode": params.get("mode"),
            }
            normalized = normalize_feedback_filters(raw_filters)

            queryset = queryset.filter(
                filters_json__state=normalized["state"],
                filters_json__effect=normalized["effect"],
                filters_json__terpene=normalized["terpene"],
                filters_json__time_of_day=normalized["time_of_day"],
                filters_json__strain_type=normalized["strain_type"],
                filters_json__featured=normalized["featured"],
                filters_json__min_thc=normalized["min_thc"],
                filters_json__max_thc=normalized["max_thc"],
                filters_json__mode=normalized["mode"],
            )

        return queryset

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return StrainFeedbackWriteSerializer
        return StrainFeedbackReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        strain = serializer.validated_data["strain"]
        filters_json = serializer.validated_data.get("filters_json", {})
        feedback_value = serializer.validated_data["feedback"]

        signature = build_feedback_signature(strain.id, filters_json)

        instance, created = StrainFeedback.objects.update_or_create(
            user=request.user,
            strain=strain,
            filters_signature=signature,
            defaults={
                "feedback": feedback_value,
                "filters_json": filters_json,
            },
        )

        read_serializer = StrainFeedbackReadSerializer(instance, context={"request": request})

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FlowMemoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        summary = build_user_memory_summary(request.user)
        return Response(summary)