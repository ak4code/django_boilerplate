.PHONY: env

env:
	@if [ -f .env ]; then \
		echo ".env уже существует, пропускаю."; \
	else \
		cp .env.example .env && echo "Создано .env из .env.example."; \
	fi