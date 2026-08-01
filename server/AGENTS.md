# AI Chat With PDF - Backend Agent Guide

This project is a production-style FastAPI backend implementing a secure multi-user RAG (Retrieval-Augmented Generation) system.

## Reading Strategy

When working on this project:

1. Read AGENTS.md first.
2. Read only the instruction files relevant to the task.
3. Do not scan unrelated folders.
4. Only inspect source code when implementation details are required.
5. Preserve the existing architecture and coding standards.

## Before making any code changes

Always read:

- instructions/project-structure.md
- instructions/backend-rules.md
- instructions/coding-standards.md

If working on authentication:

Read

- instructions/authentication.md

If working on RAG:

Read

- instructions/rag-pipeline.md

If working on APIs:

Read

- instructions/api-reference.md

If working on database models or migrations:

Read

- instructions/database.md

Never modify project architecture without explicit instruction.

Never change API contracts unless requested.

Always reuse existing services.

Keep controllers thin.

Business logic belongs inside services.

Always maintain JWT authentication.

Always maintain multi-user document isolation.

Use SQLAlchemy ORM.

Use Alembic for schema changes.

Use pgvector for vector search.

Never duplicate code.