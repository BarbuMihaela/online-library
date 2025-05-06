
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2
from datetime import datetime, timedelta
from flask_api import app

@app.route("/home")
def web_home():
    return render_template("admin_page.html")



@app.route("/remove_member", methods=["GET", "DELETE"])
def remove_member():
    if request.method == "DELETE":
        data = request.get_json()
        remove_member_id = data.get("user_id")

        if remove_member_id:
            try:
                connection = psycopg2.connect(**database_config)
                cursor = connection.cursor()
                cursor.execute("""
                    select b.title, l.return_date
                    from project.loans l
                    join project.books b on l.book_id = b.book_id
                    where l.user_id = %s and l.return_date IS NULL
                    """, (remove_member_id,))
                loaned_books = cursor.fetchall()
                if loaned_books:
                    book_title = loaned_books[0][0]
                    message = f"The member cannot be removed. They have borrowed the book '{book_title}' which must be returned first."
                    return jsonify({"success": False, "message": message})

                cursor.execute("delete from project.users where user_id = %s", (remove_member_id,))
                connection.commit()
                return jsonify({"success": True, "message": "Member removed successfully."})

            except Exception as e:
                return jsonify({"success": False, "message": f"Error: {str(e)}"})

            finally:
                cursor.close()
                connection.close()

    users = read_from_db("select user_id, full_name from project.users where is_admin != 'Da'")
    return render_template("remove_member.html", users=users)


@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        fullname = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')  # nou
        is_admin = request.form['is_admin']

        if not fullname or not username or not password or not confirm_password or not is_admin:
            flash("Please fill in all fields.", "error")
            return render_template("add_member.html", username=username)

        check_query = "select * from project.users where username = %s"
        existing_user = read_from_db(check_query, params=(username,))
        if existing_user:
            flash("Username already exists. Please choose another one.", "error")
            return render_template("add_member.html", username=username)

        if username.isnumeric():
            flash("Username cannot contain only numbers.", "error")
            return render_template("add_member.html", username=username)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("add_member.html", username=username)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("add_member.html", username=username)

        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute(
                "insert into project.users (full_name, username, password, is_admin) values (%s, %s, %s, %s)",
                (fullname, username, password, is_admin)
            )
            connection.commit()
            flash("User added successfully!", "success")
            cursor.close()
            connection.close()
            return redirect(url_for("add_member"))

        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while adding the user.", "error")
            return render_template("add_member.html", username=username)
    return render_template("add_member.html")


@app.route("/pending_borrowings")
def pending_borrowings():
    query = """
        select u.full_name, b.title, l.loan_date, l.return_date
        from project.loans l
        join project.books b on b.book_id = l.book_id
        join project.users u on u.user_id = l.user_id
        order by l.return_date asc
    """
    borrowings = read_from_db(query)
    return render_template("pending_borrowings.html", borrowings=borrowings)
