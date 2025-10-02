# A note on RunContext in Pydantic AI
**In this implementation, the LLM never sees the RunContext object directly. Here’s how it works and how it’s avoided:**

### How RunContext Is Used
- RunContext is only passed to Python functions registered as tools, system prompts, or instructions.
- These functions are executed by your agent code, not by the LLM itself.
- When the LLM is asked to call a tool, it only sees the tool’s name, description, and parameter schema (which are generated from the function signature and docstring).
- The LLM generates a tool call with simple, serializable arguments (like numbers, strings, dicts).
### What the LLM Sees
- The LLM sees a JSON schema describing the tool’s parameters.
It does not see the RunContext object, nor does it need to construct or pass it.
- The agent framework internally creates and passes RunContext when invoking the Python function.
### Why This Is Good
- LLMs are not responsible for constructing or passing complex objects.
- LLMs only interact with simple, serializable data.
- Your Python code handles all context and dependency injection