# AI Chat With PDF API

![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.140.0-009688) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-316192) ![pgvector](https://img.shields.io/badge/pgvector-enabled-5E6CFF)

AI Chat With PDF is the backend for a secure, multi-user RAG application. Users can register, log in, upload documents, retrieve semantically relevant chunks, and ask questions about their documents through a conversational AI workflow.

The server exposes REST APIs built with FastAPI and uses PostgreSQL with pgvector for semantic retrieval, SQLAlchemy for database access, Alembic for migrations, and Google Gemini for chat and reranking.

## ✨ Features

- User registration and login
- JWT-based authentication with OAuth2 password bearer flow
- Secure document upload for PDF, DOCX, and PPTX files
- Document parsing and content chunking
- Embedding generation for semantic matching
- Vector similarity search with pgvector
- Gemini-powered chunk reranking and answer generation
- Document ownership validation for secure retrieval
- CRUD endpoints for documents
- Swagger documentation via FastAPI

## 🏗️ Architecture

```mermaid
flowchart TD
    User[User] --> Frontend[Client App]
    Frontend --> API[FastAPI API]
    API --> DB[(PostgreSQL)]
    API --> Vector[(pgvector)]
    API --> Gemini[Google Gemini]
    DB --> Vector
```

## 🧠 Beginner-Friendly Concepts

- JWT: A signed token that proves a user is authenticated without storing the password in every request.
- SQLAlchemy: A Python library that helps the app talk to the database using Python objects instead of writing raw SQL everywhere.
- Alembic: A migration tool that safely updates the database schema over time.
- pgvector: A PostgreSQL extension for storing and searching vector embeddings, which is useful for semantic similarity.
- Chunking: Splitting a large document into smaller sections so retrieval can focus on the most relevant parts.
- Embeddings: Numerical representations of text that allow the system to compare meaning, not just exact words.
- Semantic Search: Finding content based on meaning and context rather than simple keyword matching.
- Gemini: Google’s generative AI model used to rerank chunks and answer questions.

## 📁 Project Structure

| Folder            | Responsibility                                                        |
| ----------------- | --------------------------------------------------------------------- |
| app/main.py       | Application entry point and router registration                       |
| app/config.py     | Environment-based configuration                                       |
| app/routers/      | API route handlers for auth, upload, chat, and documents              |
| app/services/     | Business logic for parsing, chunking, embeddings, retrieval, and chat |
| app/database/     | SQLAlchemy models, session handling, and Alembic migrations           |
| app/schemas/      | Pydantic request and response models                                  |
| app/dependencies/ | Authentication and dependency injection helpers                       |
| app/utils/        | JWT and password utilities                                            |
| tests/            | Test suite for the backend                                            |

## 🛠️ Technology Stack

| Technology   | Purpose                              |
| ------------ | ------------------------------------ |
| FastAPI      | High-performance API framework       |
| Python       | Backend language                     |
| PostgreSQL   | Primary relational database          |
| SQLAlchemy   | ORM for database models and queries  |
| Alembic      | Database migration management        |
| pgvector     | Vector storage and similarity search |
| Pydantic     | Request/response validation          |
| Argon2       | Secure password hashing              |
| Google GenAI | Gemini client integration            |
| Uvicorn      | ASGI server for running the app      |

## 🔐 Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant API
    participant DB

    User->>Client: Enter email and password
    Client->>API: POST /auth/login
    API->>DB: Validate user credentials
    DB-->>API: User record
    API-->>Client: JWT access token
    Client->>API: Request protected resource with Bearer token
    API-->>Client: Authorized response
```

## 📤 Upload Flow

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant API
    participant Storage
    participant DB
    participant Gemini

    User->>Client: Upload document
    Client->>API: POST /upload/
    API->>Storage: Save uploaded file
    API->>API: Parse document and split into chunks
    API->>Gemini: Generate embeddings
    API->>DB: Store document and chunk records
    DB-->>API: Persisted data
    API-->>Client: Upload success response
```

## 💬 Chat Flow

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant API
    participant DB
    participant Gemini

    User->>Client: Ask a question
    Client->>API: POST /chat/
    API->>DB: Validate document ownership
    API->>DB: Retrieve relevant chunks
    API->>Gemini: Rerank and generate answer
    Gemini-->>API: Final answer
    API-->>Client: Answer + sources
    Client-->>User: Display response
```

## 🗄️ Database Schema

The main database entities are:

| Table     | Description                                               |
| --------- | --------------------------------------------------------- |
| users     | Stores user account information and password hash         |
| documents | Stores uploaded document metadata and ownership           |
| chunks    | Stores chunk text and vector embeddings for each document |

## 🔄 RAG Pipeline

1. A document is uploaded and stored on disk.
2. The backend parses the document into structured text.
3. The content is split into smaller chunks.
4. Each chunk is converted into an embedding.
5. The system stores the embedding in pgvector for similarity search.
6. When the user asks a question, the app generates an embedding for that question.
7. The backend finds the most relevant chunks using vector similarity.
8. Gemini reranks the retrieved chunks and generates a grounded answer.

## 🛡️ Security Features

- JWT-based authentication for protected routes
- OAuth2 password bearer login flow
- Document ownership checks before retrieval or deletion
- Password hashing with Argon2
- Input validation with Pydantic
- CORS enabled for API access

## 🌍 Environment Variables

Create a .env file in the server folder before running the app.

| Environment Variable            | Description                               |
| ------------------------------- | ----------------------------------------- |
| app_name                        | Application name shown in the API         |
| app_version                     | API version                               |
| host                            | Host address for the server               |
| port                            | Port number for the server                |
| upload_dir                      | Directory where uploaded files are stored |
| google_api_key                  | API key for Google Gemini access          |
| database_url                    | PostgreSQL connection string              |
| gemini_chat_model               | Gemini chat model name                    |
| JWT_SECRET_KEY                  | Secret key for signing JWT tokens         |
| JWT_ALGORITHM                   | JWT signing algorithm                     |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiration duration          |

### Sample .env

```env
app_name=AI Chat With PDF
app_version=1.0.0
host=0.0.0.0
port=8000
upload_dir=uploads
google_api_key=your_google_api_key
database_url=postgresql://xxxx:xxxx@localhost:5432/chat_with_pdf
gemini_chat_model=gemini-2.5-flash
JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## ⚙️ Installation

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🗂️ Setup

1. Make sure PostgreSQL is running.
2. Create a database for the application.
3. Add the required environment variables in a .env file.
4. Run database migrations.

## ▶️ Run the Server

```bash
python run.py
```

The API will be available at:

- http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## 🧪 Alembic Commands

Initialize or upgrade the database schema with Alembic:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Useful migration commands:

```bash
alembic current
alembic history
alembic downgrade -1
```

## 📚 API Endpoints

| Method | Endpoint                 | Description                              |
| ------ | ------------------------ | ---------------------------------------- |
| POST   | /auth/register           | Create a new user account                |
| POST   | /auth/login              | Authenticate user and return a JWT       |
| GET    | /auth/me                 | Fetch the current authenticated user     |
| POST   | /api/v1/upload/          | Upload and index a document              |
| POST   | /chat/                   | Ask a question about a selected document |
| GET    | /documents               | List documents owned by the current user |
| DELETE | /documents/{document_id} | Delete a document and its chunks         |

## 🧭 Future Improvements

- Add richer document format support and better parsing quality
- Improve retrieval with hybrid search strategies
- Add usage analytics and observability
- Add rate limiting and admin controls
- Expand automated test coverage

## 🤝 Contributing

Contributions are welcome. Please open an issue or submit a pull request with a clear description of the change.

## 📄 License

No explicit license file is currently present in this repository. If you plan to distribute the project publicly, add a license file such as MIT or Apache-2.0.
