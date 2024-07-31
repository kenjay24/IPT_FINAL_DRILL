# Need Libraries for perform the REST-API-PROGRAMMING
from flask import Flask, make_response, jsonify, request, abort
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
import dicttoxml 
from xml.dom.minidom import parseString


# using flask application 
app = Flask(__name__)

# call out of auth to our client
auth = HTTPBasicAuth()

# my SQL configuration to out database connect to python
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "enrollment_management_system"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# Verify password function
@auth.verify_password
def verify_password(username, password):
    return username == "ron09" and password == "77777"



# Helper function to convert data to XML

def convert_to_xml(data):
    xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
    dom = parseString(xml)
    return dom.toprettyxml()



# Using postman Helper function to format response

def format_response(data):
    response_format = request.args.get('format', 'json').lower()
    if response_format == 'xml':
        xml_data = convert_to_xml(data)
        return make_response(xml_data, 200, {'Content-Type': 'application/xml'})
    else:
        return make_response(jsonify(data), 200)
    
    

# Protected routes with authentication

@app.route("/protected")
@auth.login_required
def protected_resource():
    data = {"message": "You are authorized to access this resource."}
    return format_response(data)


#USING GET: RETRIEVE OR VIEW HISTORY

@app.route("/customer", methods=["GET"])
@auth.login_required
def get_customer():
    data = data_fetch("SELECT * FROM customer")
    return format_response(data)

@app.route("/customer/<int:id>", methods=["GET"])
@auth.login_required
def get_customer_by_id(id):
    data = data_fetch(f"SELECT * FROM customer WHERE id_Customer = {id}")
    return format_response(data)

@app.route("/customer/<int:id>/customer_satisfaction", methods=["GET"])
@auth.login_required
def get_customer_by_id_Customer(id):
    data = data_fetch(f"""
       SELECT customer.id_Customer, customer_satisfaction.rate
        FROM customer
        INNER JOIN customer_satisfaction
        ON customer.id_Customer = customer_satisfaction.rate
        WHERE customer.id_Customer = {id}""")
    response_data = {"id_Customer": id, "count": len(data), "rate": data}
    return format_response(response_data)

#USING POST: ADD USER

@app.route("/customer", methods=["POST"])
@auth.login_required
def add_customer():
    if not request.is_json:
        abort(400, description="Request must be in JSON format.")
    cur = mysql.connection.cursor()
    info = request.get_json()
    id_Customer = info["id_Customer"]
    Last_name = info["Last_name"]
    First_name = info["First_name"]
    Contact_No = info["Contact_No"]
    Email = info["Email"]
    Location = info["Location"]
    Password = info["Password"]

    if not all([id_Customer, Last_name, First_name, Contact_No, Email, Location, Password]):
        abort(400, description="Missing required fields in JSON data.")
        
    cur.execute(
        """ INSERT INTO customer (id_Customer, Last_name, First_name, Contact_No, Email, Location, Password) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (id_Customer, Last_name, First_name, Contact_No, Email, Location, Password))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    data = {"message": "customer added successfully", "rows_affected": rows_affected}
    return format_response(data)

#USING PUT: UPDATE THE BEFORE POST USING POSTMAN 

@app.route("/customer/<int:id>", methods=["PUT"])
@auth.login_required
def update_customer(id):
    if not request.is_json:
        abort(400, description="Request must be in JSON format.")
    cur = mysql.connection.cursor()
    info = request.get_json()
    Last_name = info["Last_name"]
    First_name = info["First_name"]
    Contact_No = info["Contact_No"]
    Email = info["Email"]
    Location = info["Location"]
    Password = info["Password"]

    if not all([Last_name, First_name, Contact_No, Email, Location, Password]):
        abort(400, description="No data provided for update.")
        
    cur.execute(
        """ UPDATE customer SET Last_name = %s, First_name = %s, Contact_No = %s, Email = %s, Location = %s, Password = %s 
        WHERE id_Customer = %s """,
        (Last_name, First_name, Contact_No, Email, Location, Password, id))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    data = {"message": "Customer updated successfully", "rows_affected": rows_affected}
    return format_response(data)

#USING DELETE TO POSTMAN ALREADY DELETE THE DATA IN MYSQL WORKBENCH

@app.route("/customer/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_customer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE id_Customer = %s", (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    data = {"message": "customer deleted successfully", "rows_affected": rows_affected}
    return format_response(data)

def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

# Getting URI parameters in a GET request

@app.route("/customer/format", methods=["GET"])
@auth.login_required  
def get_params():
    fmt = request.args.get('id')
    foo = request.args.get('aaaa')
    return make_response(jsonify({"format": fmt, "foo": foo}), 200)



if __name__ == "__main__":
    app.run(debug=True)

