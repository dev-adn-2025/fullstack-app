# Project Context & Guidelines for GitHub Copilot

## 1. High-Level Overview

This is a full-stack web application. The development philosophy emphasizes a clean architecture, robust security practices, and a consistent, containerized development environment for all team members.

## 2. Technology Stack

Adhere strictly to the technologies and libraries defined below.

### Frontend
- **Framework/Library:** React 18+
- **Language:** TypeScript
- **Build Tool:** Vite
- **State Management:** (Zustand / Redux Toolkit - *elige uno si ya lo decidiste*)
- **Styling:** Tailwind CSS
- **Testing:** Vitest for unit/integration tests and React Testing Library for component testing.
- **Package Manager:** npm

### Backend
- **Language:** Python 3.11+
- **Framework:** Flask (o FastAPI, sé consistente con lo que se use en el código base)
- **Dependency Management:** Poetry. All dependencies must be managed via `pyproject.toml`. Do not use `pip` directly.
- **API Specification:** OpenAPI 3.0 for API documentation.

### Database
- **System:** PostgreSQL 15+
- **Interaction:** Use SQLAlchemy 2.0 Core or ORM for all database interactions. Avoid writing raw SQL strings directly in the application logic.

## 3. Development Environment & DevOps Culture

The entire project is containerized to ensure consistency and eliminate "it works on my machine" issues.

- **Containerization:** Docker and Docker Compose are used to orchestrate all services (`frontend`, `backend`, `db`).
- **Development IDE:** The official development environment is Visual Studio Code using the **Dev Containers** extension.
- **Configuration:** The environment is defined in `.devcontainer/devcontainer.json` and `.devcontainer/docker-compose.yml`. VS Code attaches to the `backend` service container by default.

## 4. Code Quality & Best Practices

Code suggestions should always follow these standards.

### General
- **Security:** Follow OWASP Top 10 guidelines. Sanitize all user inputs, use parameterized queries for database access, and manage secrets via environment variables, not hardcoded in the source code.
- **Version Control:** Follow conventional commit message standards.

### Backend (Python)
- **Formatting:** All Python code **must** be formatted with **Black**.
- **Linting:** Use Flake8 or Ruff for linting.
- **Typing:** Use type hints extensively. Code without proper type hints will not be accepted.
- **Dependencies:** Add new dependencies using the `poetry add <package>` command.

### Frontend (React/TypeScript)
- **Formatting:** All code **must** be formatted with **Prettier**.
- **Linting:** ESLint is configured with a strict ruleset. Address all linting errors.
- **Component Structure:** Create components in their own folders, including the component file (`.tsx`), a style file if needed, and a test file (`.test.tsx`).
- **Hooks:** Favor functional components with React Hooks.

## 5. Project Directory Structure

```text
mi-proyecto/
├── .devcontainer/      \# VS Code Dev Container configuration
│   ├── devcontainer.json
│   └── docker-compose.yml
├── .github/
│   └── instructions/
│       └── instructions.md \# This file
├── backend/            \# Python/Flask source code
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
└── frontend/           \# React/TypeScript source code
	├── src/
	├── public/
	├── Dockerfile
	└── package.json
```