.PHONY: serve
serve:
	@poetry run uvicorn app.main:app --reload


.PHONY: test
test:
	@poetry run python -m unittest
