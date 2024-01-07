coverage run --source=. -m pytest tests/test_book_models_extreme.py tests/test_book_models_inject.py tests/test_book_models_invalid.py tests/test_book_models_valid.py
coverage report -m
coverage html -d tests/html_report
