from __future__ import absolute_import

from django.core.management import BaseCommand
from django.db import transaction

from revisioned_rubrics.factories import RubricTreeFactory, RubricFactory, RubricEdgeFactory, QuestionFactory, \
    StudentFactory, AttemptFactory


class Command(BaseCommand):
    help = "Management command to seed the database with dummy values"

    def handle(self, *args, **options):
        self.stdout.write("############### Start seeding the Database ####################")

        with transaction.atomic():
            rubric_tree = self.create_rubric_tree()
            question = self.create_question(rubric_tree)
            student = self.create_student()
            self.create_attempt(student, question, rubric_tree)

        self.stdout.write("############### Database seeded ####################")

    def create_rubric_tree(self):
        rubric_tree = RubricTreeFactory()
        rubrics = RubricFactory.create_batch(2, tree=rubric_tree)
        leaf_rubrics = RubricFactory.create_batch(2, tree=rubric_tree, is_leaf=True)

        #     A
        #     +
        #     +
        #     B
        #    + +
        #    | |
        # C<-+ +->D

        RubricEdgeFactory(tree=rubric_tree, src_rubric=rubrics[0], dest_rubric=rubrics[1])
        RubricEdgeFactory(tree=rubric_tree, src_rubric=rubrics[1], dest_rubric=leaf_rubrics[0])
        RubricEdgeFactory(tree=rubric_tree, src_rubric=rubrics[1], dest_rubric=leaf_rubrics[1])

        return rubric_tree

    def create_question(self, rubric_tree):
        return QuestionFactory(rubric_tree=rubric_tree)

    def create_student(self):
        return StudentFactory()

    def create_attempt(self, student, question, rubric_tree):
        return AttemptFactory(student=student, question=question, rubric_tree=rubric_tree)
