# Django WebSocket Chat Application

This project is a real-time chat application using Django, Django Channels, and WebSocket. The application supports real-time messaging and file sharing between two types of users: sellers and customers.

### Prerequisites
- **Python 3.11.5**
- **Django 5.1.2**
- **Django Channels**
- **Redis** (for WebSocket layer)
- **sqlite3** (default Django database)

### Setup Instructions

1. **Clone the Repository**
    ```bash
    git clone https://github.com/abdulmanaf6361/chat_app.git
    cd chat_app/chat
    ```

2. **Set Up a Virtual Environment and Install Dependencies**  
   Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    .\venv\Scripts\Activate
    ```
   Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run Migrations**  
   Apply the database migrations:
    ```bash
    python manage.py migrate
    ```

4. **Configure Redis for Channels**  
   Install Redis and start it locally:

   #### Installing Redis on Windows

   i. **Download Redis for Windows**
      - Visit the [Redis for Windows releases page](https://github.com/microsoftarchive/redis/releases).
      - Download the latest `.msi` installer (e.g., `Redis-x64-<version>.msi`).

   ii. **Run the Installer**
      - Double-click the downloaded `.msi` file to start the installation.
      - Follow the prompts to install Redis. You can select the default options.

   iii. **Start Redis Server**
      - After installation, open a Command Prompt (cmd) window to start the Redis server.
      - Navigate to the Redis installation directory (by default, it might be `C:\Program Files\Redis` or `C:\Program Files\Redis-x64`).
      - Run the Redis server with the following command:
        ```bash
        redis-server
        ```

   iv. **Verify Redis is Running**
      - Open another Command Prompt window.
      - Run the Redis CLI (Command Line Interface) by executing:
        ```bash
        redis-cli
        ```
      - To test if Redis is working, run a simple command:
        ```bash
        ping
        ```
      - You should see a response of `PONG`.

5. **Create a Superuser (Optional)**  
   Create an admin user to manage the app:
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the Server**  
   Start the Django server:
    ```bash
    python manage.py runserver
    ```

7. **Access the Application**  
   Open your browser and navigate to:
    ```
    http://127.0.0.1:8000/
    ```

8. **Open Another Browser Window**  
   For a different user session, open another browser or use incognito mode and navigate to:
    ```
    http://127.0.0.1:8000/
    ```
