# Contributing to EduPilot AI

Thank you for your interest in contributing to EduPilot AI!

## Development Setup

1. Follow the setup instructions in the [README.md](README.md)
2. Create a new branch for your feature: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes with a descriptive message
6. Push to your fork and submit a pull request

## Code Style

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Run `black` for formatting: `black app/`
- Run `flake8` for linting: `flake8 app/`

### Frontend (TypeScript/React)

- Follow the existing code style
- Use TypeScript for all new files
- Use functional components with hooks
- Run `npm run lint` to check for issues
- Run `npm run format` to format code

## Commit Messages

Use conventional commit format:

- `feat: Add new feature`
- `fix: Fix bug in component`
- `docs: Update documentation`
- `style: Format code`
- `refactor: Refactor component`
- `test: Add tests`
- `chore: Update dependencies`

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Ensure all tests pass
3. Update documentation if you're changing functionality
4. The PR will be merged once approved by maintainers

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Questions?

Feel free to open an issue for any questions or concerns.
