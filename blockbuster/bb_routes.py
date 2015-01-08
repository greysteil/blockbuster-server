# 3rd Party Imports
from flask import request, Response
from flask import jsonify
from functools import wraps

# Local Imports
from blockbuster import app
import config as conf
import bb_auditlogger
from blockbuster import bb_request_processor
from blockbuster import bb_api_request_processor

bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'STARTUP', 'Application Startup')

# Following methods provide the endpoint authentication.
# Authentication is applied to an endpoint by decorating the route with @requires_auth
def passphrase_is_valid(passphrase):
    if passphrase == conf.api_passphrase:
        return True
    else:
        return False


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid."""
    auth_successful = username == conf.api_username and password == conf.api_passphrase
    print(str.format("Authentication Successful: {0}", auth_successful))
    return auth_successful


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth:
            print(str.format("API User: {0}", auth.username))
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# Core App Routes
@app.route("/InboundSMS/", methods=['POST'])
def post_inboundsms():
    bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'POST_INBOUNDSMS', request.form['Body'])
    return bb_request_processor.process_twilio_request(request)


@app.route("/status/", methods=['GET'])
def get_status():
    status = bb_api_request_processor.APIRequestProcessor().service_status_get()
    bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'GET_STATUS', status)
    return status


# API Routes
@app.route("/api/v1.0/stats/", methods=['GET'])
@requires_auth
def get_stats():
    result = bb_api_request_processor.APIRequestProcessor().service_stats_get()
    bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'GET_STATS', result)
    return jsonify(stats=result)


@app.route("/api/v1.0/cars/", methods=['GET'])
@requires_auth
def uri_get_cars():
    result = bb_api_request_processor.APIRequestProcessor()\
        .cars_getall()
    return jsonify(cars=result)


@app.route("/api/v1.0/cars/<registration>", methods=['GET'])
@requires_auth
def uri_get_registrations(registration):
    result = bb_api_request_processor.APIRequestProcessor().cars_get(registration)
    return jsonify(result)


@app.route("/api/v1.0/blocks/", methods=['GET'])
@requires_auth
def uri_get_blocksall():
    result = bb_api_request_processor.APIRequestProcessor().blocks_getall()
    return jsonify(blocks=result)


@app.route("/api/v1.0/status/<requestermobile>", methods=['GET'])
@requires_auth
def uri_get_status(requestermobile):
    return jsonify(bb_api_request_processor.APIRequestProcessor().status_get(requestermobile))


@app.route("/api/v1.0/smslogs/", methods=['GET'])
@requires_auth
def uri_get_smslogs():
    result = bb_api_request_processor.APIRequestProcessor().smslogs_get()
    return jsonify(logs=result)


@app.route("/api/v1.0/logs/", methods=['GET'])
@requires_auth
def uri_get_logs():
    result = bb_api_request_processor.APIRequestProcessor().logs_get()
    return jsonify(logs=result)


# Routes that I haven't finished yet...
@app.route("/api/v1.0/blocks", methods=['POST'])
def uri_post_blocks():
    content = request.get_json()
    block = content['block']
    blocker_reg = block['blocker_reg']
    blocked_reg = block['blocked_reg']
    response = blocker_reg + " has blocked in " + blocked_reg
    return response, 200
