# Contributing to Procurement System

Thank you for your interest in contributing to the Procurement System! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

### Our Pledge
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git** for version control

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/procurement-system.git`
3. Navigate to the project: `cd procurement-system`
4. Follow the setup instructions in [README.md](./README.md)

## Development Workflow

### Branch Strategy
We use a modified GitFlow workflow:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: New features (`feature/inventory-management`)
- **bugfix/**: Bug fixes (`bugfix/fix-order-calculation`)
- **hotfix/**: Critical production fixes (`hotfix/security-patch`)

### Creating a Feature Branch
```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Work on your feature
# ...

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Convention
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat(auth): add JWT token refresh functionality

fix(inventory): resolve stock calculation error

docs: update API documentation for purchase orders

test(suppliers): add unit tests for supplier validation
```

## Coding Standards

### Python (Backend)
- **Style Guide**: Follow PEP 8
- **Formatter**: Use `black` for code formatting
- **Linter**: Use `pylint` and `flake8`
- **Type Hints**: Use type hints for all functions and methods
- **Imports**: Use `isort` for import organization

```bash
# Format code
black .

# Sort imports
isort .

# Run linters
pylint app/
flake8 app/

# Type checking
mypy app/
```

### TypeScript/JavaScript (Frontend)
- **Style Guide**: Follow Airbnb JavaScript Style Guide
- **Formatter**: Use `prettier` for code formatting
- **Linter**: Use `eslint` with TypeScript rules
- **Type Safety**: Use TypeScript strict mode

```bash
# Format code
npm run format

# Run linter
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Type checking
npm run type-check
```

### General Guidelines
- Write self-documenting code with clear variable and function names
- Add comments for complex business logic
- Keep functions small and focused (single responsibility)
- Use meaningful commit messages
- Write tests for new functionality

## Testing Guidelines

### Backend Testing
- **Framework**: pytest
- **Coverage**: Maintain >80% code coverage
- **Test Types**: Unit, integration, and end-to-end tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py
```

### Frontend Testing
- **Framework**: Vitest + React Testing Library
- **Coverage**: Maintain >80% code coverage
- **Test Types**: Unit, component, and integration tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run specific test
npm run test -- auth.test.ts
```

### Test Guidelines
- Write tests before or alongside feature development (TDD/BDD)
- Test both happy path and edge cases
- Use descriptive test names
- Mock external dependencies
- Keep tests isolated and independent

## Pull Request Process

### Before Submitting
1. **Sync with latest changes**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout your-feature-branch
   git rebase develop
   ```

2. **Run all tests**:
   ```bash
   # Backend
   cd backend && poetry run pytest
   
   # Frontend
   cd frontend && npm run test
   ```

3. **Check code quality**:
   ```bash
   # Backend
   black . && isort . && pylint app/ && mypy app/
   
   # Frontend
   npm run lint && npm run type-check
   ```

### Pull Request Template
When creating a PR, use this template:

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### Review Process
1. At least one reviewer approval required
2. All CI checks must pass
3. No merge conflicts
4. Branch is up to date with target branch

## Issue Guidelines

### Bug Reports
Use the bug report template:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. iOS]
- Browser [e.g. chrome, safari]
- Version [e.g. 22]
```

### Feature Requests
Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Development Environment

### Recommended Tools
- **IDE**: VS Code with recommended extensions
- **Database**: PostgreSQL with pgAdmin or DBeaver
- **API Testing**: Postman or Insomnia
- **Git Client**: Command line or GitKraken

### VS Code Extensions
- Python extension pack
- TypeScript and JavaScript Language Features
- Prettier - Code formatter
- ESLint

Thank you for contributing to the Procurement System! 🚀