
from flask import render_template, request, url_for, session, redirect, flash
from config import read_from_db, database_config, write_to_db
from flask_restful import abort
import psycopg2
from datetime import datetime, timedelta
from flask_api import app


@app.route("/login", methods=["POST"])
def web_login():
    """
    Endpoint to handle user login.
    :return: Renders the login page or redirects to the appropriate home page based on login success.
    """
    try:
        user = request.form['username']
        passwd = request.form['password']
        query = read_from_db("""
            select user_id, username, full_name, password, is_admin
            from project.users
            where username = %s
        """, params=(user,))

        if not query:
            flash("You don't have an account, please register.", "error")
            return render_template("login.html")

        user_data = query[0]

        if passwd != user_data['password']:
            flash("Incorrect password. Please try again.", "error")
            return render_template("login.html")
        session['user_id'] = user_data['user_id']
        session['username'] = user_data['username']
        session['full_name'] = user_data['full_name']
        session['is_admin'] = user_data['is_admin']

        if session['is_admin'].lower() == "da":
            return redirect(url_for("web_home"))
        else:
            return redirect(url_for("web_home_users"))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Logs out the user and redirects them to the home page.
    Clears all session data and redirects the user to the home page
    :return:Redirects to the home page.
    """
    session.clear()
    return redirect(url_for("home"))


@app.route("/")
def welcome():
    """
    Renders the welcome page.
    :return:Renders the "welcome.html" template.
    """
    return render_template("welcome.html")

@app.route("/login")
def home():
    """
     Renders the login page.
    :return:Renders the "login.html" template.
    """
    return render_template("login.html")



@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    """
     This function is responsible for rendering the registration page and processing the registration form.
    :return:Renders the "register_user.html" template with any validation errors or the registration form.
    """
    if request.method == "POST":
        full_name = " ".join(request.form['full_name'].split()).title()
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        check_query = "select * from project.users where username = %s"
        existing_user = read_from_db(check_query, params=(username,))

        if existing_user:
            error = "Username already exists. Please choose another one."
        elif username.isnumeric():
            error = "Username cannot contain only numbers."
        elif len(password) < 6 or not any(c.isupper() for c in password) or not any(c in "!@_%&" for c in password):
            error = "Password must be at least 6 characters long, with one uppercase letter and one special character (!@_%&)."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            insert_query = """
                insert into project.users (full_name, username, password, is_admin)
                values (%s, %s, %s, 'Nu')
            """
            write_to_db(insert_query, params=(full_name, username, password))
            return redirect(url_for("web_login"))

        return render_template("register_user.html", error=error, username=username)

    return render_template("register_user.html")

