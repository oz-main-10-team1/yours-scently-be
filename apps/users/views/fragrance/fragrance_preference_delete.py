from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import FragrancePreference


class FragrancePreferenceDeleteView(APIView):

    def delete(self, request):
        user = request.user

        try:
            preference = FragrancePreference.objects.get(user=user)
        except FragrancePreference.DoesNotExist:
            return Response({"detail": "사용자의 취향 정보가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        preference.delete()

        return Response({"message": "사용자 향기 취향이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
