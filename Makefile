.PHONY: docs

init:
	poetry install

clear-environment:
	poetry env remove python

re-init:
	make clear-environment
	make init

production-init:
	make clear-environment
	make update-environment
	poetry install --no-dev

update-environment:
	poetry run pip install --upgrade pip

deploy:
	cd deploy_tools && poetry run fab deploy:host=stcstores@stcadmin.stcstores.co.uk

staging-deploy:
	cd deploy_tools && poetry run fab deploy:host=stcstores@staging.stcadmin.stcstores.co.uk

docs:
	cd reference/help && poetry run make html

lock:
	poetry lock

test:
	poetry run python manage.py test
