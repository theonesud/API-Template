# Cursor Agent with **_Production Ready FastAPI Backend_**

## Build Your Next Backend API, Faster with AI

This is a production-ready FastAPI backend blueprint designed to be the perfect companion for **Cursor**, the AI-first code editor.

It provides a robust and feature-rich foundation, allowing you to leverage the power of AI to accelerate your backend development workflow.

Think of it as your intelligent **Cursor Agent** for building and deploying APIs rapidly.

Built with best practices and essential functionalities baked in, all under the permissive MIT license.

Stop reinventing the wheel and jumpstart your next project with the power of AI!

## Core Features - Production Ready, AI-Optimized

This blueprint is packed with features designed to streamline your development process and ensure your API is robust and production-ready, especially when used with Cursor:

-   **🚀 CI/CD Ready:**

    -   Automated Continuous Integration and Continuous Deployment pipelines configured with GitHub Actions for seamless deployments to AWS servers.

-   **✨ Code Quality Tools:**

    -   Pre-configured with autoformatting (e.g., Black), linting (e.g., Flake8, Pylint), and automatic import management (e.g., isort) to maintain code consistency and quality.

-   **🔒 Scalable & Safe Database:**

    -   Robust database connection management ensuring scalability and secure interactions.

-   **🔑 User Authentication:**

    -   Secure user authentication implemented with Google OAuth, with a bypass mechanism for simplified local development.

-   **📝 Comprehensive Logging:**

    -   Detailed user journey logging to local files for debugging and monitoring.

-   **📢 Slack Error Notifications:**

    -   Real-time error notifications sent to Slack to ensure rapid issue detection and resolution.

-   **🐳 Dockerized:**

    -   Docker and Docker Compose configurations included for easy containerization and deployment.

-   **✅ Automated Testing:**

    -   Comprehensive test suite with realistic request replication using the `requests` library and `pytest`.

-   **🗂️ Database Migrations:**

    -   Integrated database migration framework (e.g., Alembic) for effortless schema management and updates.

-   **✅ API Validation:**

    -   Automatic API request and response validation using Pydantic to ensure data integrity.

-   **📚 Automatic API Documentation:**

    -   Swagger/OpenAPI documentation automatically generated, keeping your API documentation up-to-date.

-   **🎮 API Playground:**

    -   Interactive API playground UI (e.g., Swagger UI or ReDoc) for easy API exploration and testing.
    -   Test your API endpoints directly from the browser.

-   **🛠️ Convenient Scripts:**
    -   Shell scripts provided for common development tasks: running the development server, executing tests, deploying, running database migrations, and setting up AWS servers.

## Get Started in Minutes - With Cursor by Your Side

1.  **Clone the Repository:**

    -   Begin by cloning this repository to your local machine.

2.  **Customize Your Project:**

    -   Use Cursor's AI capabilities to tailor the blueprint to your specific needs by modifying these files:
        -   Enable the setting in Cursor to include `.cursorrules` file.
        -   `.env`: Configure environment variables like database URLs and API keys. (Copy from `.env.template`)
        -   `main.py`: The main application entry point. Customize API routes and application logic.
        -   `deploy.sh`: Deployment script for your chosen environment.
        -   `docker-compose.yml`: Define and manage multi-container Docker applications.
        -   `.github/workflows/deploy-dev.yml`: CI/CD workflow for development deployments.
        -   `.github/workflows/deploy-prod.yml`: CI/CD workflow for production deployments.
        -   `alembic.ini`: Alembic configuration file. (Copy from `alembic.ini.template`)

3.  **Set Up Python Environment:**

    -   Ensure you have Python 3.11 installed and create a virtual environment to manage dependencies.
    -   Let Cursor guide you through this!

    ```bash
    ./run.sh
    ```

4.  **Run Tests & Initialize:**

    -   **Health Check:** Verify the server is running:
        ```bash
        curl localhost:8000/
        ```
    -   **Initialize Database:** Create database tables and seed with initial data (development only - **remember to comment out `/reset_db` in `main.py` for production**):
        ```bash
        curl localhost:8000/reset_db
        ```
    -   **Run Tests:** Execute the test suite to ensure everything is working as expected:
        ```bash
        ./test.sh test_settings.py::test_update_company
        ```
        -   Use Cursor to analyze and fix any failing tests!

5.  **Unleash AI-Powered Development with Cursor & SuperWhisper:**

    -   **Cursor Composer:** Open Cursor Composer and select `gemini-2.0-flash-thinking` as your model for intelligent code generation and assistance.
    -   **Seamless File Integration:** Add project files to Cursor by clicking the "+" button. This gives Cursor's AI a complete understanding of your backend codebase, enabling smarter code generation, refactoring, and debugging.
    -   **AI-Driven Backend Development:** Start chatting with Cursor to accelerate feature development, debug complex issues faster, and explore architectural improvements with an AI partner.
    -   **SuperWhisper (Optional):** For the ultimate hands-free coding experience and a truly immersive flow state, consider installing [SuperWhisper](https://superwhisper.com/) for voice-controlled coding with Cursor.

## Google OAuth Setup

-   Create project in Google Cloud Console. Enable the “Google+ API” in the “APIs & Services > Dashboard” section.
-   Create OAuth Consent Screen. Type: External. Fill company info. Select Scopes:

    -   https://www.googleapis.com/auth/userinfo.email
    -   https://www.googleapis.com/auth/userinfo.profile

-   Publish the app in the OAuth consent screen.
-   Create credentials. Type: OAuth Client ID. Application type: Webapp.

    -   Origin: http://localhost:3000
    -   Redirect URIs: http://localhost:8000/user/token
    -   Add for other domains if needed.

## Future Enhancements - AI-Powered Roadmap

We are continuously working to enhance this blueprint with even more production-ready features, leveraging AI to guide our development:

-   **🏗️ Infrastructure as Code:**

    -   Terraform scripts to automate the creation and management of AWS environments.

-   **🚦 Rate Limiting:**

    -   Implement rate limiting to protect your API from abuse and ensure fair usage.

-   **🗄️ Caching:**

    -   Integrate caching mechanisms to improve API performance and reduce database load.

-   **📊 Observability Suite:**
    -   User activity tracking and monitoring with Loki, Grafana, Tempo, and Prometheus for comprehensive insights into your API's performance and usage.

## Contribute and Shape the Future of AI-Powered Backend Development!

This project is open source and thrives on community contributions. We encourage you to get involved and help us build the ultimate **Cursor Agent** for backend development!

-   **🛠️ Fork and Contribute:**

    -   Fork the repository, implement your improvements or new features, and submit a Pull Request.

-   **🙋 Report Issues & Suggest Features:**
    -   Help us improve by creating issues to report bugs, suggest enhancements, or propose new features.
