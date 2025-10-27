# MakeGPT Knowledge Base

This directory contains example blueprints used for RAG (Retrieval-Augmented Generation).

## Purpose

The blueprint examples serve as training data and templates for the MakeGPT compiler:

1. **Pattern Learning**: The LLM learns common Make.com patterns
2. **Module Examples**: Real-world usage of Make.com modules
3. **Schema Reference**: Concrete examples of valid blueprint structure

## Blueprint Examples

### Simple Patterns

- `example_simple_form_to_email.json` - Basic trigger→action flow
  - Pattern: Google Forms trigger → Gmail send
  - Use case: Form submission notifications

### Control Flow

- `example_conditional_router.json` - Conditional routing with BasicRouter
  - Pattern: Trigger → Router → Multiple conditional paths
  - Use case: Priority-based task routing
  - Demonstrates: Filter conditions, route branching

### Error Handling

- `example_with_error_handling.json` - Resilient API calls
  - Pattern: Webhook → HTTP request (with retry) → Log result
  - Use case: External API integration with fault tolerance
  - Demonstrates: Error handlers, exponential backoff

## Adding New Examples

To add new blueprint examples:

1. Create a valid blueprint JSON file
2. Name it descriptively: `example_<pattern>_<usecase>.json`
3. Include comments in a companion `.md` file if needed
4. Test that it validates: `python -m src.schema_validator <file.json>`

## Future Enhancements

- [ ] Add more complex multi-step scenarios
- [ ] Include data transformation examples (SetVariable, functions)
- [ ] Add webhook and custom API integration examples
- [ ] Document common error patterns and solutions
- [ ] Create blueprint "recipes" for common use cases
