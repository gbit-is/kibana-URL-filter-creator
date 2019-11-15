#! /usr/bin/python3

# Import needed flask functions
import flask
from flask import request
from flask import redirect
# Used for UUID validation
from uuid import UUID
# Used for alias mapping
import configparser


# Initialise the config file
config = configparser.ConfigParser()
config.sections()
config.read('uuiDict.ini')


port = 8000 # Port for flask server



base = "https://your_kibana_url/app/kibana#/dashboard/" # Base URL
defaultBoardId = "3f95-46b9-bf86-ae99dc03eabc" # If no ID is provided, this gets used
defaultIndexId = "3f95-46b9-bf86-ae99dc03eabc" # required for proper functioning, otherwise dashboards break when you try to edit the filters

time = "?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-1h,to:now))" # Here the default time is set for dashboard view from this
qhead = "&_a=(description:'',filters:!(" # Neccesary string to build the URL



# Just used for validating UUID's
def validate_uuid4(uuid_string):
    try:
        val = UUID(uuid_string, version=4)
        return True
    except ValueError:
        return False

# Check the config file for alias names 
def checkDict(name):
    config.read('uuiDict.ini') # So we re-read the dict and can update it without restarting flask

    try:
        value = config["dict"][name]
    except:
        value = "failed"
    return value



# Here we create a single filter parameter 
def makeParam(field,match,index): # field is the field and match is, what we wanna match, this only supports "field is something" filters 
    base = '''('$state':(store:appState),meta:(disabled:!f,index:'INDEX',key:FIELD,negate:!f,params:(query:MATCH),type:phrase,value:MATCH),query:(match:(FIELD:(query:MATCH,type:phrase))))''' # Base string 
    # populate the string with values
    base = base.replace("FIELD",field)
    match = "'" + match + "'"
    base = base.replace("MATCH",match)
    base = base.replace("INDEX",index)
    return base


# creations of the URL
def makeUrl(id,params,index): 
    
    # Params must be a nested list,for example: [ ["foo","123"],["bar":"asdf"] ]
    # If only one param is used it must be like this for example: [ ["foo","123"] ]


    # check if a UUID was provided for the dashboard
    if validate_uuid4(id):
        uuid = id
    else:
        # if not, check the dict
        uuid = checkDict(id)

    # Check if the index refernece is a UUID
    if validate_uuid4(index):
        pass
    else:
        # If not, check the dict
        indexName = index
        index = checkDict(index)

    
    # If index is neither a UUID nor an alias, return an error
    if index == "failed":
        return "invalid?index=" + str(indexName) 


    # If dashboard is neither a UUID nor an alias, return an error
    if uuid == "failed":
        return "invalid?id=" + str(id) 

    else:

        # Build the first parts of the URL
        url = base + uuid + time + qhead 

        # Initialise some logic for the parameter parsins
        paramCount = len(params)
        counter = 1

        for param in params:
            res = makeParam(param[0],param[1],index) # send the parameter provided to the makeParam function
            url = url + res
        
            if counter == paramCount: # if we have reached the final parameter, close the brackets
                url = url + "))"
            else: # If not, add a comma so we can parse another field
                url = url + ","
            counter = counter + 1

        return url # Return the fully prepared url





# Initialise flask
app = flask.Flask(__name__)


# Create the default route
@app.route("/")
def hello():
    args = request.args # collect args from url
    id = defaultBoardId # Initalise ID as default, will be overwritten if argument is present
    params = [ ] # Initalise list for later nesting of params
    index = defaultIndexId # Initialise index as default, will be overwritten if argument is present
    
    for arg in args: # For each argument provided

        # ID's are handled unlike other params
        if arg == "id":
            id = args[arg]
        # All normal params get put into a list and then appended to the collection list
        elif  arg == "_index":
            index = args[arg]
        else:
            param = [ arg, args[arg] ]
            params.append(param)



    url = makeUrl(id,params,index) # Send all params to the URL creation function
    return redirect(url,code=302) # redirect the user to the generated URL

# If an invalid UUID or alias is provided by the user, they get send here instead of a broken Kibana link

@app.route("/invalid")
def invalid():
    args = request.args # Collect the args from the url
    for arg in args: # Only one parameter is created by the makeURL() function, so this method is not as terrible as it looks
        type = str(arg)
        value = str(args[arg])
    # Create a message for the user to recieve 
    message = "<br><br><h2>You provided an invalid " + type + " that is neither a UUID nor a defined alias<br>" + type + " that was provided was:<b> " + str(value) + "</b></h2>"
    return message


# If run as a program directly, start flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)

