import urllib3.request
import json

class cachet(object):
    _baseURL = "";
    _email= "";
    _password="";
    _apiToken="";
    
    def __init__(self, baseURL=None, email=None, password=None, apiToken=None):
        self._baseURL = baseURL;
        self._email = email;
        self._password = password;
        self.apiToken = apiToken;
        
    def setBaseURL(self, baseURL):
        self._baseURL = baseURL;
        
    def setEmail(self, email):
        self._email = email;
    
    def setPassword(password):
        self._password = password;
        
    def setApiToken(self, apiToken):
        self._apiToken = apiToken;
        
    def sanityCheck(self, authorizationRequired=True):
        if (self._baseURL ==""):
            raise Exception("cachet.py: The baseURL is not set for your cachet Instance. Set it on initiation or with the setBaseURL method.");
            return False;
        elif (authorizationRequired and (self._apiToken != None or (self._email != None and self._password != None))):
            raise Exception("cachet.py: the apiToken or the Email/password need to be set to securly access Cachet site. Please set on initiation or with the setApiToken and setEmail/setPassword methods")
            return False;
        return True;
     
    def ping(self, ):
        self.sanityCheck(False);

        http= urllib3.PoolManager()
        r = http.request("GET", self._baseURL+"/ping")
        
        if (r.status != 200):
            raise Exception("cachet.py: Recieved bad response from %s", self._baseURL)
        
        data = json.loads(r.data);
        
        return data["data"]
        
    def isWorking(self,):
        return (self.ping() == "Pong!")
        
    def get(self, type):
        if (type not in ("components", "incidents", "metrics")):
            raise Exception("cachet.py: Invalid Type Specified. Must be \'components\', \'incidents\' or \'metrics\'.'");
        
        self.sanityCheck(False);
        http= urllib3.PoolManager()
        r = http.request("GET", self._baseURL+"/"+type)
        data = json.loads(r.data);

        if data.has_key("data"):        
            datalist = data["data"]
            data["meta"]["pagination"]["links"]["next_page"], \
            data["meta"]["pagination"]["current_page"], \
            data["meta"]["pagination"]["total"]
            
            total_pages = data["meta"]["pagination"]["total_pages"]
            total_items = data["meta"]["pagination"]["total"]
            current_page= data["meta"]["pagination"]["current_page"]
            
            for cntr in range(1, total_pages):
                next_page = data["meta"]["pagination"]["links"]["next_page"]
                r = http.request("GET", next_page)
                data = json.loads(r.data)
                datalist.extend(data["data"])
            
            return datalist
        else:
            return data
    
    def getByID(self, type, id):
        if (type not in ("components", "incidents", "metrics")):
            raise Exception("cachet.py: Invalid Type Specified. Must be \'components\', \'incidents\' or \'metrics\'.'");
        
        self.sanityCheck(False);
        
        http= urllib3.PoolManager()
        r = http.request("GET", self._baseURL+"/"+type+"/"+id)
        data = json.loads(r.data);
        
        return data["data"]

    def getComponents(self, ):
        return self.get("components")
        
    def getIncidents(self, ):
        return self.get("incidents")
        
    def getMetrics(self, ):
        return self.get("metrics")
    
    def getComponentsByID(self, id):
        return self.getByID("components", id)
        
    def getIncidentsByID(self, id):
        return self.getByID("incidents", id)
        
    def getMetricsByID(self, id):
        return self.getByID("metrics". id)
    
    def createComponents(self, name, status, **kwargs):
        self.sanityCheck(False);
        
        data = {}
        if name == None:
            raise Exception("cachet.py: Name required field for component Creation");
        else:
            data["name"] = name
            
        if status == None:
            raise Exception("cachet.py: Status required field for component Creation");
        else:
            data["status"] = status

        for k, v in kwargs.items():
            if (k == 'groupID'):
                data['group_id'] = v
            else:
                data[k] = v;

        urlHeader = {}
        urlHeader['Content-Type']='application/json'
        urlHeader['X-Cachet-Token']=self.apiToken
        
        print json.dumps(data)
        
        http= urllib3.PoolManager();
        r = http.urlopen("POST", self._baseURL+"/components", headers=urlHeader, body=json.dumps(data))
        
        if (r.status <> 200):
            raise Exception("Cachet.py: Bad Response in create component")
        
        return json.loads(r.data)
    
    def updateComponentsByID(self, id, **kwargs):
        self.sanityCheck(False);
        
        data = {}
        for k, v in kwargs.items():
            if (k == 'groupID'):
                data['group_id'] = v
            else:
                data[k] = v;
        
        urlHeader = {}
        urlHeader['Content-Type']='application/json'
        urlHeader['X-Cachet-Token']=self.apiToken
        
        http= urllib3.PoolManager();
        r = http.urlopen("PUT", self._baseURL+"/components/"+str(id), headers=urlHeader, body=json.dumps(data))

        if (r.status <> 200):
            raise Exception("Cachet.py: Bad Response in create component")

        return json.loads(r.data)

    def deleteComponentsByID(self, id):
        self.sanityCheck(False);
           
        urlHeader = {}
        urlHeader['Content-Type']='application/json'
        urlHeader['X-Cachet-Token']=self.apiToken
        
        http= urllib3.PoolManager();
        r = http.urlopen("DELETE", self._baseURL+"/components/"+str(id), headers=urlHeader)

        if (r.status not in (200, 204, 404)):
            raise Exception("Cachet.py: Bad Response in Delete component")

        if (r.status == 404):
            raise Exception("Cachet.py: Component %s not found." % str(id))

if __name__ == "__main__":
    ch = cachet(baseURL="https://status.metoceanview.com/api/v1" , apiToken="t9GMA7NM9SDn8FCTok9P")
    
    comp = ch.getComponents()
    #print comp
    components = {}
    for item in comp:
        if (item["group_id"] in ['7', '8', '9']):
            components[item["name"]] = item
            print ">>>>>>>>>>>>>>>>>>>"
            print item
            print ">>>>>>>>>>>>>>>>>>>"
            
#    print components
    print len(components)
    
    print "finish"