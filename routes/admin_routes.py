
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

@app.route("/view_members")
def view_members():
    query = read_from_db("SELECT full_name FROM project.users WHERE is_admin != 'Da'")
    return render_template("view_members.html", members=query)


@app.route("/remove_member", methods=["GET", "DELETE"])
def remove_member():
    if request.method == "DELETE":
        data = request.get_json()
        remove_member_id = data.get("user_id")
        if remove_member_id:
            try:
                connection = psycopg2.connect(**database_config)
                cursor = connection.cursor()
                cursor.execute("delete from project.users where user_id = %s", (remove_member_id,))
                connection.commit()
                flash("User removed successfully!", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
            finally:
                cursor.close()
                connection.close()
        return redirect(url_for("remove_member"))

    users = read_from_db("select user_id, full_name FROM project.users where is_admin != 'Da'")
    return render_template("remove_member.html", users=users)

@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        fullname = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form['is_admin']

        if not fullname or not username or not password or not is_admin:
            flash("Please fill in all fields.", "error")
            return render_template("add_member.html")

        try:
            connection = psycopg2.connect(**database_config)
            cursor = connection.cursor()
            cursor.execute("select * from project.users where username = %s", (username,))
            query_user = cursor.fetchall()

            if query_user:
                flash("User already exists.", "error")
            else:
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
            return render_template("add_member.html")

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
