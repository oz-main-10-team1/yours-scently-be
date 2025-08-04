from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import FragrancePreference


class FragrancePreferenceDeleteView(APIView):

    # 사용자가 등록한 향기 취향을 삭제하는 API (DELETE)
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        # 사용자가 본인 요청인지 확인
        if request.user.id != user_id:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 향기 취향 존재 여부 확인
        try:
            preference = FragrancePreference.objects.get(user_id=user_id)
        except FragrancePreference.DoesNotExist:
            return Response({"detail": "사용자의 취향 정보가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 삭제 수행
        preference.delete()
        return Response({"message": "사용자 향기 취향이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
