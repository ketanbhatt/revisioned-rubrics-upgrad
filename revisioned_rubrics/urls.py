from django.conf.urls import url

from revisioned_rubrics.views import StudentAttemptView

urlpatterns = [
    url(r'^student-performance/(?P<student_id>[0-9]+)$', StudentAttemptView.as_view(), name='student-performance'),
]
