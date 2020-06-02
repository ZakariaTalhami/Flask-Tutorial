run_flaskr:
	export FLASK_APP=flaskr
	export FLASK_ENV=development
	flask run	

.PHONY: run_pytest
run_pytest:
	pytest

.PHONY: test_coverage
test_coverage:
	coverage run -m pytest

.PHONY: coverage_report
coverage_report:
	coverage report -m

.PHONY: test
test: test_coverage coverage_report

