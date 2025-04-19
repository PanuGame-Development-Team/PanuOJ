from flask import *
from ui import *
from model import *
from lib import *
from constances import *
from settings import *
app = Blueprint("db_api","db_api",url_prefix="/api")
@app.route("/logging",methods=["GET"])
@app.route("/logging/",methods=["GET"])
@ACCESS_REQUIRE(["ADMIN"])
def get_logging(ses,user):
    if not lin(["limit","category"],request.args):
        return jsonify({"status":"Bad Request","data":[]}),400
    try:
        limit = int(request.args["limit"])
        category = int(request.args["category"])
    except ValueError:
        return jsonify({"status":"Bad Request","data":[]}),400
    if limit < 10 or limit > 300 or category < 0 or category > 5:
        return jsonify({"status":"Bad Request","data":[]}),400
    return jsonify({"status":"OK","data":[i.__todict__() for i in Logging.query.filter(Logging.category>=category).order_by(Logging.id.desc()).limit(limit).all()]})