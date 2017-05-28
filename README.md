## Checklist:
- [x] Design for Rubric
- [x] Design for versioning in Rubric
- [x] Design for Import for grades
- [x] Implement all models
- [x] Implement CSV importing (handle versioning)
- [x] Create API for getting Student and Question's Rubric details
- [ ] Implement method for getting stats like average marks for rubric etc


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
