from django.contrib import admin

from revisioned_rubrics.models import GradingRevision, Question, AttemptEvaluation, Attempt, Rubric, Student


class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'question', 'created_at')


class AttemptEvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'rubric', 'marks', 'revision')


class RubricAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_leaf')


admin.site.register(GradingRevision)
admin.site.register(Question)
admin.site.register(Attempt, AttemptAdmin)
admin.site.register(AttemptEvaluation, AttemptEvaluationAdmin)
admin.site.register(Rubric, RubricAdmin)
admin.site.register(Student)
