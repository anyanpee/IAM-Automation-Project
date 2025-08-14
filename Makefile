# IAM Automation Project Makefile

.PHONY: help setup test deploy-terraform destroy-terraform clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup local development environment
	python -m venv venv
	venv\Scripts\activate && pip install -r requirements.txt
	copy .env.example .env
	@echo "Setup complete! Edit .env file and run 'aws configure'"

test: ## Run tests
	venv\Scripts\activate && python -m pytest tests/ -v

lint: ## Run code linting
	venv\Scripts\activate && flake8 src/ --max-line-length=100

deploy-terraform: ## Deploy infrastructure with Terraform
	cd terraform && terraform init && terraform plan && terraform apply

destroy-terraform: ## Destroy Terraform infrastructure
	cd terraform && terraform destroy

terraform-output: ## Show Terraform outputs
	cd terraform && terraform output

clean: ## Clean up temporary files
	del /q *.zip 2>nul || true
	del /q terraform\*.zip 2>nul || true
	rmdir /s /q __pycache__ 2>nul || true
	rmdir /s /q .pytest_cache 2>nul || true

docker-build: ## Build Docker image
	docker build -t iam-automation .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

# Local CLI commands
create-user: ## Create IAM user (usage: make create-user USER=username)
	venv\Scripts\activate && python src\main.py create-user $(USER)

audit: ## Run IAM audit
	venv\Scripts\activate && python src\main.py audit

dry-run-audit: ## Run IAM audit in dry-run mode
	venv\Scripts\activate && python src\main.py --dry-run audit