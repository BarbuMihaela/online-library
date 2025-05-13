
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2
from datetime import datetime, timedelta
from flask_api import app

@app.route("/home")
def web_home():
    """
    This function handles the route /home of the application and renders the admin's main page.
    :return:
    """
    return render_template("admin_page.html")



@app.route("/remove_member", methods=["GET", "DELETE"])
def remove_member():
    """
    Endpoint to display and remove a member from the database.
    :return:- For GET requests:
        - Renders the "remove_member.html" template with the list of non-admin users.
        - For DELETE requests:
        - JSON response indicating success or failure.
        - If the user has borrowed books, returns an error message with status code 400.
    """
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
                    where l.user_id = %s
                    """, (remove_member_id,))
                loaned_books = cursor.fetchall()
                if loaned_books:
                    message = "The member cannot be removed because they have active loans and must return the borrowed books first."
                    return jsonify({"success": False, "message": message}), 400

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
    """
    Endpoint to add a new member to the system.
    :return:Renders the form with error messages if validation fails,
         or redirects back after a successful addition.
    """
    if request.method == "POST":
        full_name = " ".join(request.form['full_name'].split()).title()
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')
        is_admin = request.form['is_admin']


        if read_from_db("select * from project.users WHERE username = %s", params=(username,)):
            flash("Username already exists. Please choose another one.", "error")
            return render_template("add_member.html", username=username)

        elif username.isnumeric():
            flash("Username cannot contain only numbers.", "error")
            return render_template("add_member.html", username=username)

        elif len(password) < 6 or not any(c.isupper() for c in password) or not any(c in "!@_%&" for c in password):
            flash("Password must be at least 6 characters long, with one uppercase letter and one special character (!@_%&).",
                "error")
            return render_template("add_member.html", username=username)

        elif password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("add_member.html", username=username)
        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute(
                "insert into project.users (full_name, username, password, is_admin) values (%s, %s, %s, %s)",
                (full_name, username, password, is_admin)
            )
            connection.commit()
            flash("User added successfully!", "success")
            cursor.close()
            connection.close()
            return redirect(url_for("add_member"))
        except (ValueError, TypeError) as e:
            flash(f"Invalid input type or format: {e}", "error")
            return render_template("add_member.html", username=username)
        except Exception as e:
            print(f"Error: {e}")
            flash(f"An error occurred while adding the user: {e}.", "error")
            return render_template("add_member.html", username=username)

    return render_template("add_member.html")



@app.route("/pending_borrowings")
def pending_borrowings():
    """
    Endpoint to display a list of books that are currently borrowed and not yet returned.
    :return:Renders the 'pending_borrowings.html' template with a list of unreturned loans,
             ordered by the expected return date.
    """
    query = """
        select u.full_name, b.title, l.loan_date, l.return_date
        from project.loans l
        join project.books b on b.book_id = l.book_id
        join project.users u on u.user_id = l.user_id
        where l.status_return = False 
        order by l.return_date asc
    """
    borrowings = read_from_db(query)
    return render_template("pending_borrowings.html", borrowings=borrowings)
