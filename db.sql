ALTER TABLE users
ADD COLUMN is_admin VARCHAR(3) DEFAULT 'Nu';

ALTER TABLE project.users
ADD COLUMN full_name VARCHAR(100);

SELECT column_name, column_default, is_identity
FROM information_schema.columns
WHERE table_schema = 'project' AND table_name = 'authors';

SELECT setval('authors_author_id_seq', (SELECT MAX(author_id) FROM project.authors));

SELECT setval('books_book_id_seq', (SELECT MAX(book_id) FROM project.books));

ALTER TABLE project.users
ADD COLUMN borrowed_books_count INTEGER DEFAULT 0;

CREATE TABLE history (
    id_history SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    loan_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES project.users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (loan_id) REFERENCES project.loans(loan_id) ON DELETE CASCADE
);

ALTER TABLE project.loans
ADD COLUMN extend INT;











