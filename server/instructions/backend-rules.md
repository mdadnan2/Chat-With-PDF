Business logic belongs in services.

Routers only call services.

Schemas only contain validation.

Models only define database structure.

Never write raw SQL.

Always use SQLAlchemy.

Always use dependency injection.

Never bypass authentication.

Never bypass ownership validation.

Never hardcode secrets.

Use config.py for configuration.

Every endpoint must have response schemas.

Always use type hints.

Always use Pydantic models.