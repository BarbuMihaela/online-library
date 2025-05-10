
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config, write_to_db, all_books_history
from flask_restful import abort
import psycopg2
from datetime import datetime, timedelta
from flask_api import app


@app.route("/books")
def get_all_books():
    return {"books": list(read_from_db("select * from project.books").values())}

@app.route("/books/<string:book_id>")
def get_book_by_id(book_id):
    try:
        return read_from_db(f"select * from project.books where book_id = {int(book_id)}")
    except KeyError:
        return {"message": "Bad request, Book Not found"}


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        page_count = request.form['page_count']
        author_name = str(request.form['author_id'])
        genre_name = request.form['genre_id']
        print(genre_name)
        if not title or not description or not page_count or not author_name or not genre_name:
            flash("Please fill in all fields.", "error")
            return render_template("add_book.html")
        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute(f"select * from project.authors where full_name = '{author_name}'")
            query_author = cursor.fetchall()

            if not query_author:
                cursor.execute(
                    "insert into  project.authors (full_name) VALUES (%s) RETURNING author_id",
                    (author_name,)
                )
                author_id = cursor.fetchone()[0]

                connection.commit()
            else:
                author_id = query_author[0][0]
            insert_query = """
                            insert into project.books (title, description, page_count, author_id, genre_id)
                            values (%s, %s, %s, %s, %s)
                        """
            cursor.execute(insert_query, (title, description, int(page_count), author_id, int(genre_name)))
            connection.commit()
            cursor.close()
            connection.close()

            flash("Book added successfully!", "Success")
            return redirect(url_for("web_home"))
        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while adding the book.", "Error")
            return render_template("add_book.html")
    elif request.method == "GET":
        query = read_from_db("select * from project.genres")
        list_genres = [(gen["genre_name"], gen["genre_id"]) for gen in query]
        return render_template("add_book.html", genres = list_genres)

    return render_template("add_book.html")


@app.route("/view_books")
def view_books():
    selected_pages = request.args.get("page_count")
    query = """
        SELECT b.title, b.book_id, b.description, b.page_count, a.full_name AS author, g.genre_name AS genre
        FROM project.books b
        JOIN project.authors a ON b.author_id = a.author_id
        JOIN project.genres g ON b.genre_id = g.
        where b.book_id not in (select book_id from project.loans where status_return = False)
    """

    if selected_pages and selected_pages.isdigit():
        selected_pages = int(selected_pages)
        if selected_pages == 1:
            query += " where b.page_count < 200"
        elif selected_pages == 2:
            query += " where b.page_count >= 200 AND b.page_count < 300"
        elif selected_pages == 3:
            query += " where b.page_count >= 300 AND b.page_count < 400"
        elif selected_pages == 4:
            query += " where b.page_count >= 400 AND b.page_count < 500"
        elif selected_pages == 5:
            query += " where b.page_count >= 500"

    books = read_from_db(query)
    return render_template("view_books.html", books=books, selected_page=str(selected_pages) if selected_pages else "")


@app.route("/user_view_books")
def user_view_books():
    selected_pages = request.args.get("page_count")
    query = """
        select b.title,b.book_id, b.description, b.page_count, a.full_name as author, g.genre_name as genre
        from project.books b
        join project.authors a on b.author_id = a.author_id
        join project.genres g on b.genre_id = g.genre_id
         where b.book_id not in (select book_id from project.loans where status_return = False)     
    """

    if selected_pages and selected_pages.isdigit():
        selected_pages = int(selected_pages)
        if selected_pages == 1:
            query += " where b.page_count < 200"
        elif selected_pages == 2:
            query += " where b.page_count >= 200 AND b.page_count < 300"
        elif selected_pages == 3:
            query += " where b.page_count >= 300 AND b.page_count < 400"
        elif selected_pages == 4:
            query += " where b.page_count >= 400 AND b.page_count < 500"
        elif selected_pages == 5:
            query += " where b.page_count >= 500"

    books = read_from_db(query)
    return render_template("user_view_books.html", books=books, selected_page=str(selected_pages) if selected_pages else "")


@app.route("/remove_book", methods=["POST"])
def remove_book():
    data = request.get_json()
    book_id_to_remove = data.get("book_id")
    print(book_id_to_remove)
    if book_id_to_remove:
        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute("delete from project.books where book_id = %s", (book_id_to_remove,))
            connection.commit()
            flash("Book removed successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        finally:
            cursor.close()
            connection.close()
    return redirect(url_for("view_books"))


@app.route("/borrow_book", methods=["POST"])
def borrow_book():
    user_id = session['user_id']
    load_date = datetime.now()
    return_date = load_date + timedelta(days=30)
    if request.is_json:
        data = request.get_json()
        book_id_to_borrow = data.get("book_id")
    else:
        return jsonify({"status": "error", "message": "Invalid request format"}), 400

    connection = psycopg2.connect(**database_config)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            select borrowed_books_count
            from project.users
            where user_id = %s
        """, (user_id,))
        borrowed_count = cursor.fetchone()[0]

        if borrowed_count >= 2:
            return jsonify({
                "status": "error",
                "message": "You can't borrow more than 2 books at a time."
            }), 400

        cursor.execute("""
            insert into project.loans (user_id, book_id, loan_date, return_date, extend, status_return)
            values (%s, %s, %s, %s, %s, %s)
        """, (user_id, book_id_to_borrow, load_date, return_date, 0, False))

        cursor.execute("""
            update project.users
            set borrowed_books_count = borrowed_books_count + 1
            where user_id = %s
        """, (user_id,))

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Book borrowed successfully!"
        })

    except Exception as e:
        connection.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error borrowing book: {str(e)}"
        }), 500

    finally:
        cursor.close()
        connection.close()



@app.route("/pending_books")
def pending_books():
    query = """
        select b.title, b.description, a.full_name as author_name, l.return_date
        from project.loans l
        join project.books b on b.book_id = l.book_id
        join project.authors a on a.author_id = b.author_id
        where l.return_date >= date(now()) and l.status_return = False
        order by l.return_date ASC
    """
    borrowings = read_from_db(query)

    return render_template("pending_books.html", borrowings=borrowings)



@app.route("/return_book", methods=["GET", "POST"])
def return_book():
    user_id = session['user_id']
    if request.method == "POST":
        loan_id = request.form.get("loan_id")
        action = request.form.get("action")
        if action == "return":
            try:
                connection = psycopg2.connect(**database_config)
                cursor = connection.cursor()
                cursor.execute("""
                    update project.loans
                    set status_return = True, return_date = CURRENT_DATE
                    where loan_id = %s and user_id = %s
                """, (loan_id, user_id))
                cursor.execute("""
                    update project.users
                    set borrowed_books_count = borrowed_books_count - 1
                    where user_id = %s and borrowed_books_count > 0
                """, (user_id,))
                connection.commit()
                flash("Book returned successfully!", "success")

            except Exception as e:
                flash(f"Error returning book: {str(e)}", "error")

            finally:
                cursor.close()
                connection.close()
        elif action == "extend":
            query = """
                select return_date, extend
                from project.loans
                where loan_id = %s and user_id = %s
            """
            result = read_from_db(query, params=(loan_id, user_id))
            if result:
                return_date = result[0]['return_date']
                extend_nr = result[0]['extend']
                if extend_nr == 1:
                    flash(f"You have already extended the return date once. Further extensions are not allowed.", "success")
                elif return_date:
                    if isinstance(return_date, datetime):
                        return_date = return_date.date()
                    today = datetime.today().date()
                    extend_start_date = return_date - timedelta(days=3)
                    if today >= extend_start_date:
                        new_return_date = return_date + timedelta(days=10)
                        update_query = """
                            update project.loans
                            set return_date = %s, extend = 1
                            where loan_id = %s AND user_id = %s
                        """
                        write_to_db(update_query, params=(new_return_date, loan_id, user_id))
                        flash(f"Deadline extended to {new_return_date.strftime('%Y-%m-%d')}.", "success")
                    else:
                        flash(f"You can extend the deadline starting on {extend_start_date.strftime('%Y-%m-%d')}.", "error")
                else:
                    flash("Extension is only available after a return date is set.", "error")
    query = """
        select b.title, a.full_name as author_name, l.loan_id, l.return_date
        from project.loans l
        join project.books b ON b.book_id = l.book_id
        join project.authors a ON b.author_id = a.author_id
        where l.user_id = %s and l.status_return = False
        order by l.loan_date ASC
    """
    borrowings = read_from_db(query, params=(user_id,))
    return render_template("return_book.html", borrowings=borrowings)


@app.route("/user_borrow_history")
def user_borrow_history():
    user_id = session['user_id']
    history_data = all_books_history(user_id)

    return render_template("user_borrow_history.html", history=history_data)
