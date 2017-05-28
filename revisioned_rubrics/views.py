from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest

from revisioned_rubrics.models import Attempt


class StudentAttemptView(View):
    def get(self, request, *args, **kwargs):
        query_params = request.GET
        try:
            question_id, revision_id = int(query_params['question'][0]), int(query_params['revision'][0])
        except (KeyError, IndexError, ValueError):
            return HttpResponseBadRequest("IDs of question and revision are required")
        else:
            student_id = int(kwargs['student_id'])
            rubrics, edges = Attempt.get_serialised_rubric_tree_for_student_question_revision(
                student_id, question_id, revision_id
            )
            return JsonResponse({
                'rubrics': rubrics,
                'edges': edges
            })
