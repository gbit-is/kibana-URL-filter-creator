# kibana-URL-filter-creator
A small flask service that generates Kibana dashboard URL's with filters preset      
The code is heavily commented and is quite short, I won't be going too much into the code here, more the purpose and usage of this project.


# What is the purpose and what's up with Kibana URL's ?
In older version of kibana you could create a dashboard with filters that were filled by URL parameters which is very useful for generating links to reports that contain for example multiple datasets but you wish to be able to dynamically generate links to filter it down to a specific service, customer, location etc. 

That functionality is no longer avaivable but I needed it, searching google I found multiple discussions of people wishing to recreate the same functionality in newer versions of kibana but not being able to.

Those URL's looked something like this: 
```
"your_kibana_url/#/dashboard/elasticsearch/your_dashboard?field=value&foo=bar
```

While this is no longer avaivable, it is possible to go to a dashboard, add filters to it and share the URL since it contains the parameters in the URL, however the URL looks something like this:

```
https://your_kibana_url/app/kibana#/dashboard/welcome_dashboard?_g=(filters:!())&_a=(description:'Main%20landing%20page%20for%20Elastic%20Demo%20Gallery;%20a%20good%20reset%20point%20if%20you%20get%20lost.',filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'filebeat-*',key:agent.id,negate:!f,params:(query:foo),type:phrase,value:foo),query:(match:(agent.id:(query:foo,type:phrase)))),('$state':(store:appState),meta:(alias:!n,disabled:!f,index:d3d7af60-4c81-11e8-b3d7-01146121b73d,key:OriginAirportID,negate:!f,params:(query:bar),type:phrase,value:bar),query:(match:(OriginAirportID:(query:bar,type:phrase))))),fullScreenMode:!f,options:(darkTheme:!f,hidePanelTitles:!f,useMargins:!t),panels:!((embeddableConfig:(),gridData:(h:10,i:'2',w:48,x:0,y:44),id:'51cbcc10-9211-11e8-8fa2-3d5f811fbd0f',panelIndex:'2',title:'KIBANA%20VISUALIZATIONS',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:10,i:'3',w:48,x:0,y:8),id:welcome-beats-modules-visualization,panelIndex:'3',title:'BEATS%20%26%20LOGSTASH',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'4',w:12,x:36,y:31),id:'68131db0-9212-11e8-8fa2-3d5f811fbd0f',panelIndex:'4',title:'ELASTICSEARCH%20SQL',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'6',w:12,x:24,y:31),id:'69e69340-9214-11e8-8fa2-3d5f811fbd0f',panelIndex:'6',title:'MACHINE%20LEARNING',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:11,i:'8',w:24,x:0,y:54),id:'55c90dc0-9287-11e8-8fa2-3d5f811fbd0f',panelIndex:'8',title:'TRY%20IT%20%7C%20ELASTIC%20CLOUD',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:11,i:'9',w:24,x:24,y:54),id:'10553fb0-9288-11e8-8fa2-3d5f811fbd0f',panelIndex:'9',title:'TRY%20IT%20%7C%20DOWNLOAD',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'10',w:12,x:0,y:31),id:'482b9ef0-9299-11e8-8fa2-3d5f811fbd0f',panelIndex:'10',title:'ELASTIC%20APM',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'11',w:12,x:12,y:31),id:'196d0660-153b-11e9-9985-f1ba5bcab6e5',panelIndex:'11',title:CANVAS,type:visualization,version:'6.5.4'),(embeddableConfig:(),gridData:(h:13,i:'12',w:12,x:36,y:18),id:'700317b0-153d-11e9-9985-f1ba5bcab6e5',panelIndex:'12',title:INFRASTRUCTURE,type:visualization,version:'6.5.4'),(embeddableConfig:(),gridData:(h:13,i:'13',w:12,x:24,y:18),id:'10624140-65ed-11e9-97a8-4d57d901c672',panelIndex:'13',title:MAPS,type:visualization,version:'7.0.0-rc2'),(embeddableConfig:(),gridData:(h:13,i:'14',w:12,x:12,y:18),id:a9871430-6611-11e9-97a8-4d57d901c672,panelIndex:'14',title:UPTIME,type:visualization,version:'7.0.0-rc2'),(embeddableConfig:(),gridData:(h:8,i:'15',w:48,x:0,y:0),id:'95caa470-6616-11e9-97a8-4d57d901c672',panelIndex:'15',type:visualization,version:'7.0.0-rc2'),(embeddableConfig:(),gridData:(h:13,i:'16',w:12,x:0,y:18),id:e7037a10-a739-11e9-aced-376b520cfdd0,panelIndex:'16',title:SIEM,type:visualization,version:'7.2.0')),query:(language:kuery,query:''),timeRestore:!f,title:'Welcome%20Dashboard',viewMode:view)
```

And this is over 3000 letters, contains multiple UUID's, version numbers, grid locations and more things.

This flask service recreates the function of old kibana by offering you to create URL's that get translated to these long kibana URL's
```
your_flask_service?id=nameOfDashboard&field=value
```
becomes:
```
https://your_kibana_url/app/kibana#/dashboard/412729e3-1f69-494d-aafe-085a4353d2ad?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-1h,to:now))&_a=(description:'',filters:!(('$state':(store:appState),meta:(disabled:!f,key:field,negate:!f,params:(query:value),type:phrase,value:value),query:(match:(field:(query:value,type:phrase))))))
```


The URL's created a actually a shorted version of the URL's created in the browser, roughly speaking those URL's get split into 5 sectors:
```
|PATH                                      |UUID    | Time Filter Parameters                                                  | Filter Param
http://your_kibana_url/app/kibana/dashboard/UUID?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-1h,to:now))('$state':(store:appState),meta:(disabled:!f,key:FIELD,negate:!f,params:(query:MATCH),type:phrase,value:MATCH),query:(match:(FIELD:(query:MATCH,type:phrase))))
```
And then there is a section called meta, which makes up the bulk of the url, is this case it's 2600 out of the 3000 letters in the URL
```
meta:(alias:!n,disabled:!f,index:d3d7af60-4c81-11e8-b3d7-01146121b73d,key:OriginAirportID,negate:!f,params:(query:bar),type:phrase,value:bar),query:(match:(OriginAirportID:(query:bar,type:phrase))))),fullScreenMode:!f,options:(darkTheme:!f,hidePanelTitles:!f,useMargins:!t),panels:!((embeddableConfig:(),gridData:(h:10,i:'2',w:48,x:0,y:44),id:'51cbcc10-9211-11e8-8fa2-3d5f811fbd0f',panelIndex:'2',title:'KIBANA%20VISUALIZATIONS',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:10,i:'3',w:48,x:0,y:8),id:welcome-beats-modules-visualization,panelIndex:'3',title:'BEATS%20%26%20LOGSTASH',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'4',w:12,x:36,y:31),id:'68131db0-9212-11e8-8fa2-3d5f811fbd0f',panelIndex:'4',title:'ELASTICSEARCH%20SQL',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'6',w:12,x:24,y:31),id:'69e69340-9214-11e8-8fa2-3d5f811fbd0f',panelIndex:'6',title:'MACHINE%20LEARNING',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:11,i:'8',w:24,x:0,y:54),id:'55c90dc0-9287-11e8-8fa2-3d5f811fbd0f',panelIndex:'8',title:'TRY%20IT%20%7C%20ELASTIC%20CLOUD',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:11,i:'9',w:24,x:24,y:54),id:'10553fb0-9288-11e8-8fa2-3d5f811fbd0f',panelIndex:'9',title:'TRY%20IT%20%7C%20DOWNLOAD',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'10',w:12,x:0,y:31),id:'482b9ef0-9299-11e8-8fa2-3d5f811fbd0f',panelIndex:'10',title:'ELASTIC%20APM',type:visualization,version:'6.3.1'),(embeddableConfig:(),gridData:(h:13,i:'11',w:12,x:12,y:31),id:'196d0660-153b-11e9-9985-f1ba5bcab6e5',panelIndex:'11',title:CANVAS,type:visualization,version:'6.5.4'),(embeddableConfig:(),gridData:(h:13,i:'12',w:12,x:36,y:18),id:'700317b0-153d-11e9-9985-f1ba5bcab6e5',panelIndex:'12',title:INFRASTRUCTURE,type:visualization,version:'6.5.4'),(embeddableConfig:(),gridData:(h:13,i:'13',w:12,x:24,y:18),id:'10624140-65ed-11e9-97a8-4d57d901c672',panelIndex:'13',title:MAPS,type:visualization,version:'7.0.0-rc2'),(embeddableConfig:(),gridData:(h:13,i:'14',w:12,x:12,y:18),id:a9871430-6611-11e9-97a8-4d57d901c672,panelIndex:'14',title:UPTIME,type:visualization,version:'7.0.0-rc2'),(embeddableConfig:(),gridData:(h:8,i:'15',w:48,x:0,y:0),id:'95caa470-6616-11e9-97a8-4d57d901c672',panelIndex:'15',type:visualization,version:'7.0.0-rc2'),(embeddableConfig:(),gridData:(h:13,i:'16',w:12,x:0,y:18),id:e7037a10-a739-11e9-aced-376b520cfdd0,panelIndex:'16',title:SIEM,type:visualization,version:'7.2.0')),query:(language:kuery,query:''),timeRestore:!f,title:'Welcome%20Dashboard',viewMode:view)
```

This flask service does not create the meta section, which is not needed.


# Using This

To use this service, just open a URL like this in your browser:
```
your_flask_service?id=nameOfDashboard&field=value&anotherField=someOtherValue
```
Options:    
id: ID can be left empty for a default dashboard to be provided, or it can be set to the UUID of a dashboard or an alias can be created in uuiDict.ini with a simple key/value pair syntax. this config get's re-read on every alias call so no need to restart the service when updating them

Other then that, any "Field is value" filter can be added to the url as field=value 

UUID/Alias logic:
![alt text](https://raw.githubusercontent.com/gbit-is/kibana-URL-filter-creator/master/flowchart.PNG "Logo Title Text 1")


# Installing 
## Linux:
apt-get install python3-flask    
or     
pip3 install flask    

## Windows:
..... no idea


## As service on Ubuntu
Edit the urlmaker.service file to match your environment    
place it in /etc/systemd/system/urlmaker.service    
$ sudo systemctl daemon-reload    
$ systemctl start urlmaker.service


# Configuration
There are 3 parameters that have to be set on lines 23-25    

* base: The base URL your kibana instance (for example: "https://your_kibana_url/app/kibana#/dashboard/") 

* defaultBoardId: if no board id is provided, this is what it will default to (for example: "8f64416c-3f95-46b9-bf86-ae99dc03eabc" )  

* defaultIndexId: If no index id is provived, this is that it will default to (for example: "8f64416c-3f95-46b9-bf86-ae99dc03eabc" )    



# Kibana versions this works on:
I do not know if this works on older Kibana versions, but I am guessing it works with at least all 6 and 7 releases. I wrote this for my usage on 7.4. Also confirmed on 7.5, 7.6, 7.6.2 aaaand I have been using this through constant updates until at least 7.9, I just don't update this readme.md often

If you end up trying this on a diffirent version, please leave me a comment so I can note down here which version work and which versions don't 
