
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config
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
    query = """
        select b.title, b.description, b.page_count, a.full_name as author, g.genre_name as genre
        from project.books b
        join project.authors a on b.author_id = a.author_id
        join project.genres g on b.genre_id = g.genre_id
    """
    books = read_from_db(query)
    return render_template("view_books.html", books=books)

@app.route("/user_view_books")
def user_view_books():
    query = """
        select b.title, b.description, b.page_count, a.full_name as author, g.genre_name as genre
        from project.books b
        join project.authors a on b.author_id = a.author_id
        join project.genres g on b.genre_id = g.genre_id
    """
    books = read_from_db(query)
    return render_template("user_view_books.html", books=books)

@app.route("/remove_book", methods=["GET", "POST"])
def remove_book():
    if request.method == "POST":
        book_id_to_remove = request.form.get('book_id')
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
        return redirect(url_for("remove_book"))

    books = read_from_db("select book_id, title from project.books")
    return render_template("remove_book.html", books=books)

@app.route("/borrow_book", methods=["GET", "POST"])
def borrow_book():

    user_id = session['user_id']
    load_date = datetime.now()
    return_date = load_date + timedelta(days=30)
    query = """
            select b.book_id, b.title, b.description, b.page_count, a.full_name as author, g.genre_name as genre
            from project.books b
            join project.authors a on b.author_id = a.author_id
            join project.genres g on b.genre_id = g.genre_id
        """
    books = read_from_db(query)
    print(books)
    if request.method == "POST":
        data = request.get_json()
        book_id_to_borrow = data.get("book_id")
        print(user_id, book_id_to_borrow, load_date, return_date)
        if book_id_to_borrow:
            try:
                connection = psycopg2.connect(**database_config)
                cursor = connection.cursor()
                cursor.execute("insert into project.loans (user_id, book_id, loan_date, return_date) values (%s, %s, %s, %s)",
                               (user_id, book_id_to_borrow, load_date, return_date))
                connection.commit()
                flash("Book borrow successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
            finally:
                cursor.close()
                connection.close()
        return redirect(url_for("borrow_book"))
    return render_template("borrow_book.html", books=books)


