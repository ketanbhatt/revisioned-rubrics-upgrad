# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from django.contrib.auth.models import User
from django.db import models

from bulk_update.helper import bulk_update
from django.db.models import Q

from revisioned_rubrics.constants import RUBRIC_DEFAULT_MAX_MARKS, DEFAULT_INDEX_FOR_MARKS


class CreateUpdateAbstractModel(models.Model):
    """
    Abstract model that adds fields for storing creation and updation times for objects
    """
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RubricTree(CreateUpdateAbstractModel):
    """
    Rubric Tree that connects a Question to its rubrics'
    """
    pass


class Rubric(CreateUpdateAbstractModel):
    """
    Each rubric represents an attribute against which the student is graded for the question.
    NOTE: Only leaf rubrics in a Rubric Tree are graded by the grader
    """
    name = models.CharField(max_length=32)
    tree = models.ForeignKey(RubricTree)
    max_marks = models.PositiveSmallIntegerField(default=RUBRIC_DEFAULT_MAX_MARKS)
    grading_guidelines = models.TextField(help_text="Guidelines on how to grade the rubric")
    is_leaf = models.BooleanField(default=False, help_text="Is the Rubric a leaf? Only leaf rubrics get graded")

    def __str__(self):
        return "{0}: {1}".format(self.id, self.name)


class RubricEdge(CreateUpdateAbstractModel):
    """
    The connector that connects a parent rubric to its children.
    """
    tree = models.ForeignKey(RubricTree)
    src_rubric = models.ForeignKey(Rubric, related_name='out_edges')
    dest_rubric = models.ForeignKey(Rubric, related_name='in_edges')


class GradingRevision(models.Model):
    """
    A rubric might undergo multiple revisions (grading, rechecking etc.)
    This model keeps track of the revisions that are allowed.
    """
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return self.user.username


class Question(CreateUpdateAbstractModel):
    q_text = models.TextField(help_text="Text for the question that the student sees")
    rubric_tree = models.ForeignKey(RubricTree)

    def __str__(self):
        return "{0}".format(self.q_text)[:100] + "..."


class Attempt(CreateUpdateAbstractModel):
    """
    Tracks each attempt of a question by the student
    """
    student = models.ForeignKey(Student)
    question = models.ForeignKey(Question)

    # Maintains the rubric tree for which this particular attempt was graded. Handles cases when Question's Rubric
    # tree is changed, past attempts will not be get broken
    rubric_tree = models.ForeignKey(RubricTree)

    def __str__(self):
        return "Attempt ID: {0}".format(self.id)

    @classmethod
    def import_grade_sheet(cls, grading_sheet_name, attempt_id, revision_id):
        with open(grading_sheet_name, 'rb') as f:
            grade_sheet = csv.reader(f)

            # Remove headers from the sheet
            grade_sheet.next()

            marks_for_revision = MarksRubricAttempt.get_marks_for_revision(attempt_id, revision_id)
            if marks_for_revision:
                MarksRubricAttempt.update_marks_for_revision(marks_for_revision, grade_sheet)
            else:
                MarksRubricAttempt.store_marks_for_revision(attempt_id, revision_id, grade_sheet)

    @classmethod
    def get_serialised_rubric_tree_for_student_question_revision(cls, student_id, question_id, revision_id):
        """
        Returns Serialised Rubrics and Edges in the format:
        1. Rubrics:
            [{
                "max_marks": 10,
                "marks": 10,
                "rubric_id": 1,
                "id": 1,
                "name": "A"
            }, {
                "max_marks": 10,
                "marks": 10,
                "rubric_id": 2,
                "id": 2,
                "name": "B"
            }, {
                "max_marks": 10,
                "marks": 10,
                "rubric_id": 3,
                "id": 3,
                "name": "C"
            }]
        
        2. Edges:
            [{
                "source": 1,
                "destination": 2
            }, {
                "source": 2,
                "destination": 3
            }]
        """
        marks_for_attempt = MarksRubricAttempt.objects.filter(
            attempt__student_id=student_id, attempt__question_id=question_id, revision_id=revision_id
        ).select_related('rubric').only(
            'id', 'rubric_id', 'marks', 'rubric__name', 'rubric__max_marks', 'rubric__is_leaf'
        )

        rubric_ids = [marks_obj.rubric_id for marks_obj in marks_for_attempt]
        rubric_edges = RubricEdge.objects.filter(
            Q(src_rubric_id__in=rubric_ids) | Q(dest_rubric_id__in=rubric_ids)
        )

        serialised_rubrics = [
            {
                'id': marks_obj.id,
                'rubric_id': marks_obj.rubric_id,
                'name': marks_obj.rubric.name,
                'marks': marks_obj.marks,
                'max_marks': marks_obj.rubric.max_marks
            } for marks_obj in marks_for_attempt
        ]

        serialised_edges = [
            {
                'source': edge.src_rubric_id,
                'destination': edge.dest_rubric_id,
            } for edge in rubric_edges
        ]

        return serialised_rubrics, serialised_edges


class MarksRubricAttempt(CreateUpdateAbstractModel):
    """
    Tracks marks given for each rubric of a question for each attempt.
    Also handles revision of marks.
    """
    attempt = models.ForeignKey(Attempt)
    rubric = models.ForeignKey(Rubric)
    marks = models.PositiveSmallIntegerField()
    revision = models.ForeignKey(GradingRevision)

    @classmethod
    def get_marks_for_revision(cls, attempt_id, revision_id):
        """
        Returns MarksRubricAttempt objects for the given attempt and revision
        """
        return cls.objects.filter(attempt_id=attempt_id, revision_id=revision_id)

    @classmethod
    def update_marks_for_revision(cls, marks_rubric_attempt_objs, updated_grades):
        """
        Updates marks for the given MarksRubricAttempt objects according to the specified marks
        """
        rubric_to_marks_map = {
            marks_obj.rubric_id: marks_obj for marks_obj in marks_rubric_attempt_objs
        }
        marks_reset = set()

        def update_marks_obj(rubric_id, rubric_marks):
            rubric = int(rubric_id)
            marks_obj = rubric_to_marks_map[rubric]

            if rubric in marks_reset:
                marks_obj.marks += rubric_marks
            else:
                marks_obj.marks = rubric_marks
                marks_reset.add(rubric)

        for updated_grade_row in updated_grades:
            if updated_grade_row[DEFAULT_INDEX_FOR_MARKS]:
                marks = int(updated_grade_row[DEFAULT_INDEX_FOR_MARKS])
                rubric_l1, rubric_l2, rubric_l3 = updated_grade_row[:3]

                update_marks_obj(rubric_l1, marks)

                if rubric_l2:
                    update_marks_obj(rubric_l2, marks)
                else:
                    continue

                if rubric_l3:
                    update_marks_obj(rubric_l3, marks)
                else:
                    continue

        bulk_update(rubric_to_marks_map.values(), update_fields=['marks'])

    @classmethod
    def store_marks_for_revision(cls, attempt_id, revision_id, new_grades):
        """
        Creates MarksRubricAttempt objects for the given attempt and revision, according to the specified marks
        """
        rubric_to_marks_map = {}

        def create_or_update_marks_obj(rubric_id, rubric_marks):
            rubric = int(rubric_id)
            try:
                marks_obj = rubric_to_marks_map[rubric]
            except KeyError:
                rubric_to_marks_map[rubric] = MarksRubricAttempt(
                    attempt_id=attempt_id, revision_id=revision_id, rubric_id=rubric_id, marks=rubric_marks
                )
            else:
                marks_obj.marks += rubric_marks

        for new_grade_row in new_grades:
            if new_grade_row[DEFAULT_INDEX_FOR_MARKS]:
                marks = int(new_grade_row[DEFAULT_INDEX_FOR_MARKS])
                rubric_l1, rubric_l2, rubric_l3 = new_grade_row[:3]

                create_or_update_marks_obj(rubric_l1, marks)

                if rubric_l2:
                    create_or_update_marks_obj(rubric_l2, marks)
                else:
                    continue

                if rubric_l3:
                    create_or_update_marks_obj(rubric_l3, marks)
                else:
                    continue

        cls.objects.bulk_create(rubric_to_marks_map.values())
