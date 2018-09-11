.PHONY: docs

init:
	pip install pipenv --upgrade
	pipenv sync --dev

clear-environment:
	pipenv --rm | true

re-init:
	make clear-environment
	make init

production-init:
	make clear-environment
	make update-environment
	pipenv sync

update-environment:
	pip install pipenv --upgrade
	pipenv run pip install --upgrade pip

deploy:
	cd deploy_tools && pipenv run fab deploy:host=stcstores@stcadmin.stcstores.co.uk

staging-deploy:
	cd deploy_tools && pipenv run fab deploy:host=stcstores@staging.stcadmin.stcstores.co.uk

docs:
	cd reference/help && pipenv run make html

lock:
	pipenv lock -d

test:
	pipenv run python manage.py test
