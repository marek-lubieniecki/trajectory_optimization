# Project Rules

## Development Guidelines

### Code Quality Standards

#### Python Code Style
- **RULE-001**: All Python code must follow PEP 8 style guidelines
- **RULE-002**: Use type hints for all function parameters and return values
- **RULE-003**: Maintain comprehensive docstrings for all classes and public methods
- **RULE-004**: Use meaningful variable and function names that clearly express intent
- **RULE-005**: Keep functions focused and under 50 lines when possible

#### Documentation Requirements
- **RULE-006**: All public APIs must be documented with clear examples
- **RULE-007**: Complex algorithms must include implementation notes and references
- **RULE-008**: README files must be maintained for each major component
- **RULE-009**: Changelog must be updated for all releases

### Testing Standards

#### Test Coverage
- **RULE-010**: Minimum 80% test coverage for all new code
- **RULE-011**: All critical paths must have comprehensive test coverage
- **RULE-012**: Unit tests must be fast-running (< 1 second each)
- **RULE-013**: Integration tests must validate end-to-end functionality

#### Test Organization
- **RULE-014**: Tests must be organized in a clear hierarchy matching source code structure
- **RULE-015**: Test data must be reproducible and version-controlled
- **RULE-016**: Mock external dependencies in unit tests
- **RULE-017**: Use descriptive test names that explain the scenario being tested

### Git and Version Control

#### Commit Standards
- **RULE-018**: Use conventional commit messages (feat, fix, docs, style, refactor, test, chore)
- **RULE-019**: Each commit must have a clear, concise description of changes
- **RULE-020**: Commits must be atomic and represent a single logical change
- **RULE-021**: No direct commits to main branch - all changes via pull requests

#### Branch Management
- **RULE-022**: Use feature branches for all development work
- **RULE-023**: Branch names must be descriptive and follow naming convention: `feature/description` or `fix/description`
- **RULE-024**: Keep branches up to date with main branch
- **RULE-025**: Delete feature branches after successful merge

#### Pull Request Process
- **RULE-026**: All pull requests require at least one review
- **RULE-027**: Pull requests must pass all automated checks (tests, linting, security scans)
- **RULE-028**: Pull request descriptions must clearly explain the changes and their purpose
- **RULE-029**: Link pull requests to related issues when applicable

### Dependencies and Security

#### Dependency Management
- **RULE-030**: Pin all dependencies to specific versions
- **RULE-031**: Regularly update dependencies and test for compatibility
- **RULE-032**: Minimize the number of external dependencies
- **RULE-033**: Document the purpose of each dependency

#### Security Practices
- **RULE-034**: Never commit secrets, API keys, or sensitive data
- **RULE-035**: Regularly scan dependencies for security vulnerabilities
- **RULE-036**: Use environment variables for configuration
- **RULE-037**: Follow principle of least privilege for access controls

### Architecture and Design

#### Code Organization
- **RULE-038**: Follow single responsibility principle for all classes and functions
- **RULE-039**: Use dependency injection for external dependencies
- **RULE-040**: Separate business logic from presentation logic
- **RULE-041**: Keep configuration separate from code

#### Performance Considerations
- **RULE-042**: Profile performance-critical code paths
- **RULE-043**: Optimize for readability first, performance second
- **RULE-044**: Document performance assumptions and constraints
- **RULE-045**: Use appropriate data structures for the problem domain

### Frontend Development (React)

#### Component Standards
- **RULE-046**: Use functional components with hooks
- **RULE-047**: Keep components small and focused on single responsibility
- **RULE-048**: Use TypeScript for all React components
- **RULE-049**: Follow React best practices for state management

#### UI/UX Guidelines
- **RULE-050**: Maintain consistent design language across all components
- **RULE-051**: Ensure accessibility compliance (WCAG 2.1 AA)
- **RULE-052**: Optimize for mobile responsiveness
- **RULE-053**: Provide loading states and error handling for all async operations

### Backend Development (Flask)

#### API Design
- **RULE-054**: Follow RESTful API design principles
- **RULE-055**: Use consistent error response formats
- **RULE-056**: Implement proper HTTP status codes
- **RULE-057**: Version APIs to maintain backward compatibility

#### Data Handling
- **RULE-058**: Validate all input data at API boundaries
- **RULE-059**: Use proper serialization for complex data types
- **RULE-060**: Implement proper logging for debugging and monitoring
- **RULE-061**: Handle edge cases gracefully with informative error messages

### Development Environment

#### Local Setup
- **RULE-062**: Use development containers for consistent environments
- **RULE-063**: Document all setup steps in README
- **RULE-064**: Automate environment setup where possible
- **RULE-065**: Keep development and production environments as similar as possible

#### Continuous Integration
- **RULE-066**: All tests must pass before merging
- **RULE-067**: Code must pass linting and formatting checks
- **RULE-068**: Security scans must pass before deployment
- **RULE-069**: Maintain fast CI/CD pipeline (< 10 minutes for full test suite)