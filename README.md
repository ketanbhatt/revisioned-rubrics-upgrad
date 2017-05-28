## Checklist:
- [x] Design for Rubric
- [x] Design for versioning in Rubric
- [x] Design for Import for grades
- [x] Implement all models
- [x] Implement CSV importing (handle versioning)
- [x] Create API for getting Student and Question's Rubric details
- [x] Implement method for getting stats like average marks for rubric etc


## Setup Demo:
1. `pip install requirements.txt -r`
2. `python manage.py migrate`
3. `python manage.py createsuperuser` --> To access admin
4. `python manage.py runserver`
5. Go to the admin and create a `Grading Revision`
6. `python manage.py seed_db` --> For creating dummy question, rubrics, and attempt

### CSV imports
1. Use `python manage.py import_grade_sheet <CSV_FILE_NAME> --revision <REVISION_ID> --attempt <ATTEMPT_ID` to import 
CSV in the decided format. 
2. Check Admin for necessary Updates

### Student API
1. Hit `http://localhost:8000/rubrics/student-performance/<student_id>?question=<question_id>&revision=<revision_id>` 
to get the required JSON response

### Other Analytics
1. Check out `AttemptEvaluation.get_avg_marks` for Average
2. Check out `AttemptEvaluation.get_percentile_rank_for_student` for percentile rank


## Assumptions and Future improvements
- Can break down the app into one containing students and questions and the other containing the Rubric System
- Validations on the models
- Marks are assumed to be in the `6th` Column. This can be derived from column name too.
- Marks are assumed to be `int`
- Maximum Levels are assumed to be 3 atm (only applicable for the import sheet)
- When a new revision is added for an attempt, import sheet contains all the marks, even those that were not updated
- The import sheet will contain IDs of the rubrics (assuming that they are coming from our own frontend client). Can be 
easily modified to take names
- Validation for things like finding cycles in the Rubric Tree
- Validation for Maximum Marks
