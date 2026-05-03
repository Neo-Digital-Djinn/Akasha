
# Event Model

An Event is the atomic unit of Akasha.

Every observation, measurement, or anomaly is represented as a structured record.

Fields:

event_id – unique identifier  
timestamp – ISO timestamp (usually from akasha-time-nexus)  
location – optional geo coordinates  
category – event type  
source – origin of data  
payload – domain specific data  
confidence – optional probability score
