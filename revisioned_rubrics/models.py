# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from revisioned_rubrics.constants import RUBRIC_DEFAULT_MAX_MARKS


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
    tree = models.ForeignKey(RubricTree)
    max_marks = models.PositiveSmallIntegerField(default=RUBRIC_DEFAULT_MAX_MARKS)
    grading_guidelines = models.TextField(help_text="Guidelines on how to grade the rubric")
    is_leaf = models.BooleanField(default=False, help_text="Is the Rubric a leaf? Only leaf rubrics get graded")


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


class Student(models.Model):
    user = models.OneToOneField(User)


class Question(CreateUpdateAbstractModel):
    q_text = models.TextField(help_text="Text for the question that the student sees")
    rubric_tree = models.ForeignKey(RubricTree)


class Attempt(CreateUpdateAbstractModel):
    """
    Tracks each attempt of a question by the student
    """
    student = models.ForeignKey(Student)
    question = models.ForeignKey(Question)

    # Maintains the rubric tree for which this particular attempt was graded. Handles cases when Question's Rubric
    # tree is changed, past attempts will not be get broken
    rubric_tree = models.ForeignKey(RubricTree)


class MarksRubricAttempt(CreateUpdateAbstractModel):
    """
    Tracks marks given for each rubric of a question for each attempt.
    Also handles revision of marks.
    """
    attempt = models.ForeignKey(Attempt)
    rubric = models.ForeignKey(Rubric)
    marks = models.PositiveSmallIntegerField()
    revision = models.ForeignKey(GradingRevision)
