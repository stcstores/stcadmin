.PHONY: docs

init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

re-init:
	pipenv --rm
	make init

deploy:
	cd deploy_tools && pipenv run fab deploy:host=stcstores@stcadmin.stcstores.co.uk

staging-deploy:
	cd deploy_tools && pipenv run fab deploy:host=stcstores@staging.stcadmin.stcstores.co.uk

docs:
	cd docs && pipenv run make html

lock:
	pipenv lock -d
