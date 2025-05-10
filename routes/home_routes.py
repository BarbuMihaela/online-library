from dbm import error

from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config, write_to_db
from flask_restful import abort
import psycopg2
from datetime import datetime, timedelta
from flask_api import app


@app.route("/login", methods=["POST"])
def web_login():
    try:
        if request.method == "POST":
            user = request.form['username']
            passwd = request.form['password']

            query = read_from_db(f"""
                SELECT user_id, username, full_name, password, is_admin
                FROM project.users
                WHERE username = '{user}' AND password = '{passwd}'
            """)

            if not query or isinstance(query[0], str):
                flash("You don't have an account, please register.", "Error")
            else:
                session['user_id'] = query[0]['user_id']
                session['username'] = user
                session['full_name'] = query[0]['full_name']
                session['is_admin'] = query[0]['is_admin']
                if session['is_admin'] == "Da":
                    return redirect(url_for("web_home"))
                else:
                    return redirect(url_for("web_home_users"))

        return render_template("login.html")

    except Exception as e:
        return f"Eroare: {str(e)}"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/login")
def home():
    return render_template("login.html")



@app.route("/register_user", methods=["GET", "POST"])
def register_user():
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

