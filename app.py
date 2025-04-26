import routes.admin_routes
import routes.book_routes
import routes.home_routes
import routes.user_routes
from flask import Flask, render_template, request, url_for, session, jsonify, redirect, flash
from flask_smorest import abort
from config import read_from_db, database_config
from flask_restful import abort
import psycopg2
from datetime import datetime, timedelta
from flask_api import app








if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5011)
    app.run(DEBUG=True)
