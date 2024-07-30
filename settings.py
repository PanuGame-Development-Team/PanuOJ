APP_NAME = "PanuOJ"
SECRET_KEY = open("secret.key").read()
APP_CONFIG = {"SQLALCHEMY_DATABASE_URI":"sqlite:///db.sqlite3",
              "SQLALCHEMY_TRACK_MODIFICATIONS":False}
VERSION = "2.0-240730-dev"

mdmodules = ["markdown.extensions.extra","markdown.extensions.codehilite","markdown.extensions.tables","markdown.extensions.toc"]#,"markdown_katex"
mdconfigs = {}
CPPCOMPILECOMMAND = """g++ {name}.cpp -o test -lm -O2 -std=c++14 -w"""
PRIMARYCOLOR = "#0080FF"
SECONDARYCOLOR = "#FF8000"
WHITE = "#FFFFFF"
BLACK = "#000000"
HOST = "0.0.0.0"
PORT = 8080
DEBUG = True
INSTALLED_MODS = ["mods.randproblem","mods.add_problem"]