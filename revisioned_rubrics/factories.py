from random import random

from django.contrib.auth.models import User
from factory import DjangoModelFactory, SubFactory, fuzzy

from revisioned_rubrics.models import RubricTree, Rubric, RubricEdge, Question, Student, Attempt


class RubricTreeFactory(DjangoModelFactory):

    class Meta:
        model = RubricTree


class RubricFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()
    tree = SubFactory(RubricTreeFactory)

    class Meta:
        model = Rubric


class RubricEdgeFactory(DjangoModelFactory):
    tree = SubFactory(RubricTreeFactory)
    src_rubric = SubFactory(RubricFactory)
    dest_rubric = SubFactory(RubricFactory)

    class Meta:
        model = RubricEdge


class QuestionFactory(DjangoModelFactory):
    rubric_tree = SubFactory(RubricTreeFactory)

    class Meta:
        model = Question


class UserFactory(DjangoModelFactory):
    username = fuzzy.FuzzyText()

    class Meta:
        model = User


class StudentFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)

    class Meta:
        model = Student


class AttemptFactory(DjangoModelFactory):
    student = SubFactory(StudentFactory)
    question = SubFactory(QuestionFactory)
    rubric_tree = SubFactory(RubricTreeFactory)

    class Meta:
        model = Attempt
