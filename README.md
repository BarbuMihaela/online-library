# Library-Project

## Flask Library Management System

### Features
- **User Registration & Login**: Users can register and log in to access library services.
- **Admin Panel**: Admin users can manage books, authors, genres, and view borrowing history.
- **Book Borrowing & Returning**: Users can borrow books and extend the return date or return books.
- **Book Management**: Admins can add, remove, and view books, authors, and genres.
- **Loan Management**: Track borrowing and pending returns of books.
- **History Tracking**: Users can view their borrowing history.

---

### Endpoints

#### **User Endpoints**
- **/login**: User login
- **/register_user**: User registration
- **/home_user**: User home page
- **/borrow_book**: Borrow a book
- **/return_book**: Return or extend a book

#### **Admin Endpoints**
- **/books**: View all books
- **/add_book**: Add a new book
- **/remove_book**: Remove a book
- **/view_books**: View available books for borrowing
- **/pending_books**: View pending book returns
- **/user_borrow_history**: View the borrowing history of a user

---

### Database Schema

The application uses the following tables in the **`project`** schema:

#### **authors**
Stores author information.
- **author_id** (Primary Key): Unique identifier for each author.
- **full_name**: The full name of the author.

#### **books**
Stores book information.
- **book_id** (Primary Key): Unique identifier for each book.
- **title**: The title of the book.
- **description**: A description of the book.
- **page_count**: Number of pages in the book.
- **author_id** (Foreign Key): Reference to the `author_id` in the `authors` table.
- **genre_id** (Foreign Key): Reference to the `genre_id` in the `genres` table.

#### **genres**
Stores genre information.
- **genre_id** (Primary Key): Unique identifier for each genre.
- **genre_name**: The name of the genre (e.g., Fiction, Non-fiction, Fantasy, etc.).

#### **loans**
Stores information about books borrowed by users.
- **loan_id** (Primary Key): Unique identifier for each loan.
- **user_id** (Foreign Key): Reference to the `user_id` in the `users` table.
- **book_id** (Foreign Key): Reference to the `book_id` in the `books` table.
- **loan_date**: The date when the book was borrowed.
- **return_date**: The date when the book is due to be returned.

#### **users**
Stores user information.
- **user_id** (Primary Key): Unique identifier for each user.
- **username**: The username of the user.
- **password**: The password of the user (stored securely).
- **is_admin**: A flag indicating whether the user is an admin (`'Da'` for yes, `'Nu'` for no).
- **full_name**: The full name of the user.
- **borrowed_books_count**: The number of books currently borrowed by the user.

#### **history**
Stores the borrowing history of users.
- **id_history** (Primary Key): Unique identifier for each entry in the history.
- **user_id** (Foreign Key): Reference to the `user_id` in the `users` table.
- **loan_id** (Foreign Key): Reference to the `loan_id` in the `loans` table.


#### **Installation:**
1. **Clone the repository:**
   ```bash
   git clone <repository-url>

2. **Navigate into the project directory:**
   ```bash
   cd <project-directory>

3. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv

4. **Activate the virtual environment(For Linux/macOS):**
   ```bash
   source venv/bin/activate

5. **Activate the virtual environment(For Windows):**
   ```bash
   pip install -r requirements.txt

6. **Set the PostgreSQL database password as an environment variable:**
   ```bash
   cd <project-directory>

7. **Navigate into the project directory:**
   ```bash
   export POSTGRES_PASSWORD=<your-password>
   set POSTGRES_PASSWORD=<your-password>

8. **Run the Flask application:**
   ```bash
   python flask_app.py


### Docker Setup
1. **Build the Docker image::**
   ```bash
   docker build -t flask-library-management .

2. **Run the Docker container:**
   ```bash
   docker run -p 5010:5010 flask-library-management
   
### Contributing

If you would like to contribute to this project, please follow these steps:

1. **Fork the repository**:
   - Click the "Fork" button at the top-right of the repository page on GitHub to create your own copy of the repository.

2. **Create a feature branch**:
   - After forking, create a new branch to work on your changes:
     ```bash
     git checkout -b feature-branch-name
     ```

3. **Make your changes**:
   - Make the necessary changes or additions to the code.

4. **Open a pull request**:
   - Push your changes to your forked repository and open a pull request (PR) to the original repository.
   - In the PR, include a detailed description of the changes you've made, and why they are beneficial.
