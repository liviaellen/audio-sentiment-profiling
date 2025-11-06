# Contributing to Audio Emotion Analysis

Thank you for your interest in contributing! This document provides guidelines for contributing to this Omi community plugin.

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/audio-sentiment-profiling.git
   cd audio-sentiment-profiling
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Install ffmpeg
   brew install ffmpeg  # macOS
   sudo apt-get install ffmpeg  # Linux

   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Testing

Before submitting changes:

```bash
# Test basic functionality
python main.py

# Test notifications
python tests/test_notification.py

# Test audio chunking
python tests/test_chunking.py
```

### Commit Messages

Use clear, descriptive commit messages:

```
Good: Add support for custom emotion thresholds
Bad: Fixed stuff
```

Format:
```
<type>: <subject>

<body>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Test your changes** thoroughly
3. **Update README.md** if adding new features
4. **Create a pull request** with a clear description:
   - What does this PR do?
   - Why is this change needed?
   - How has it been tested?

## Areas for Contribution

### High Priority
- [ ] Additional emotion analysis models
- [ ] Performance optimizations
- [ ] Better error handling
- [ ] More comprehensive tests

### Feature Ideas
- [ ] Historical emotion trend analysis
- [ ] Customizable notification templates
- [ ] Multi-language support
- [ ] Integration with other services
- [ ] Advanced dashboard visualizations

### Documentation
- [ ] Video tutorials
- [ ] More use case examples
- [ ] API documentation improvements
- [ ] Translation to other languages

## Reporting Issues

When reporting issues, please include:

1. **Description** of the problem
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (OS, Python version, etc.)
6. **Logs** if applicable

## Questions?

- Open an issue for questions
- Check existing issues and pull requests first
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make this plugin better!
