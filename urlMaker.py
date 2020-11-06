#! /usr/bin/python3

# Import needed flask functions
import flask
from flask import request
from flask import redirect
# Used for UUID validation
from uuid import UUID
# Used for alias mapping
import configparser
# Used for time math
import datetime
import dateutil.parser



# Initialise the config file
config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

# Get parameters from config file
port =              config["settings"]["flaskPort"]
baseUrl =           config["settings"]["baseUrl"]
defaultBoardId =    config["settings"]["defaultBoardId"]
defaultIndexId =    config["settings"]["defaultIndexId"]
defaultTimeString = config["settings"]["defaultTimeString"]
DEBUG =             bool(config["settings"]["debug"])

# Static values
refresh = "?_g=(filters:!(),refreshInterval:(pause:!t,value:0)," # neccesary part of the URL
qhead = "&_a=(description:'',filters:!(" # Neccesary string to build the URL




# Print debug or not
def debug(msg):
    if DEBUG:
        print("DEBUG: " + str(msg))


# Just used for validating UUID's
def validate_uuid4(uuid_string):
    try:
        val = UUID(uuid_string, version=4)
        return True
    except ValueError:
        return False

# Check the config file for alias names 
def checkDict(name):
    config.read('config.ini') # So we re-read the dict and can update it without restarting flask

    try:
        value = config["dict"][name]
        debug(name + " Is defined")
    except:
        value = "failed"
        debug(name + " Is not defined")
    return value



# Here we create a single filter parameter 
def makeParam(field,match,index): # field is the field and match is, what we wanna match, this only supports "field is something" filters 

    # Base format of the query string
    base = '''('$state':(store:appState),meta:(disabled:!f,index:'INDEX',key:FIELD,negate:!f,params:(query:MATCH),type:phrase,value:MATCH),query:(match:(FIELD:(query:MATCH,type:phrase))))''' 
    # populate the string with values
    base = base.replace("FIELD",field)
    match = "'" + match + "'"
    base = base.replace("MATCH",match)
    base = base.replace("INDEX",index)
    return base


# Get the time part of the URL
def makeTime(timeString):

    # If no time is defined, return the default time value
    if timeString == "default":
        return defaultTimeString

    # Is is easy to mess up the time values, if a parsing error occurs, default time is used
    try: 
        # Get the timestamp and first delta value
        timeData = timeString.split("|")
        tstamp = timeData[0] 
        preTime = int(timeData[1])

        # If a second delta value is defined, use it, if not, use the first one
        print(timeData)
        print(type(timeData))
        if len(timeData) == 3:
            postTime = int(timeData[2])
        else:
            postTime = preTime

        # turn the string into datetime
        tstamp = dateutil.parser.parse(tstamp)


        # calculate a new timestamp
        sTime = tstamp - datetime.timedelta(minutes=preTime)
        eTime = tstamp + datetime.timedelta(minutes=postTime)

        # make the timestamps compatible strings
        sTime = sTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        eTime = eTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        # Build the new URL parameters 
        param =  "time:(from:'" + sTime + "',to:'" + eTime + "'))"

        return param



    except Exception as e:
        debug(str(e))
        return defaultTimeString




# creations of the URL
def makeUrl(id,params,index,space,time): 
    
    # Params must be a nested list,for example: [ ["foo","123"],["bar":"asdf"] ]
    # If only one param is used it must be like this for example: [ ["foo","123"] ]


    # check if a UUID was provided
    if validate_uuid4(id):
        uuid = id
    else:
        # if not, check the dict
        uuid = checkDict(id)


    if validate_uuid4(index):
        pass
    else:
        indexName = index
        index = checkDict(index)

    if index == "failed":
        return "invalid?index=" + str(indexName) 


    time = makeTime(time)


    # If neither a UUID nor an alias, return an error
    if uuid == "failed":
        return "invalid?id=" + str(id) 

    else:

    
        if space == "":
            #baseUrl = baseUrl.replace("SPACE","")
            urlBase = baseUrl.replace("SPACE","")

        else:
            spaceStr = "s/" + space + "/"
            urlBase = baseUrl.replace("SPACE",spaceStr)



        # Build the first parts of the URL
        #url = urlBase + uuid + time + qhead 
        url = urlBase + uuid + refresh + time + qhead 

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
    id = 0 # Initalise ID for later comparison
    params = [ ] # Initalise list for later nesting of params
    index = defaultIndexId
    space = ""
    time = "default"

    for arg in args: # For each argument provided

        # First we check if it's a special parameter
        if arg == "id":
            id = args[arg]
        elif  arg == "_index":
            index = args[arg]
        elif arg == "_space":
            space = args[arg]
        elif arg == "_time":
            time = args[arg]


        # If not, it must be a filter        
        else:
            param = [ arg, args[arg] ]
            params.append(param)


    # If no ID was provided, set the default ID as the ID
    if id == 0:
        id = defaultBoardId


    url = makeUrl(id,params,index,space,time) # Send all params to the URL creation function
    debug("Returned: " + url)
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
    debug(message)
    return message




# If run as a program directly, start flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
