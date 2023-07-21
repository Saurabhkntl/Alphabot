
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted
import pymongo
from datetime import datetime

current_time = datetime.now()
client = pymongo.MongoClient("mongodb://localhost:27017")
db= client["Trial_event_database"]
coll=db["Year_1"]
class ConvoRestart(Action):
    def name(self) -> Text:
        return "restart_convo"
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
        return[Restarted()]
class say_events_(Action):

    def name(self) -> Text:
         return "action_say_events"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        found = coll.find_one({"EventDate":{"$gt":current_time}}, {"_id":0})
        event_name = found["EventName"]
        event_type = found["EventType"]
        event_start= found["StartTime"] 
        event_end = found["EndTime"]
        event_date = found["EventDate"]
        desired_format = "%Y-%m-%d"
        parsed_datetime = event_date.strftime(desired_format)
        datetime_object = datetime.strptime(parsed_datetime, "%Y-%m-%d")
        day_of_week_number = datetime_object.weekday()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        message = "The next event in the college is "+event_name+". It is a "+event_type+" event, from "+event_start+" to "+event_end+" on "+parsed_datetime+"("+days[day_of_week_number]+")"
        dispatcher.utter_message(text=message)
        return []
class say_events_month(Action):

    def name(self) -> Text:
         return "action_say_mevents"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])
        month_entity = next((entity for entity in entities if entity['entity'] == 'month_name'), None)
        months=["january","february","march","april","may","june","july","august","september","october","november","december"]
        month_value = str(month_entity['value'])
        userin=month_value.lower()
        index=0
        for i in range(0,12):
            if(userin==months[i]):
                index=i+1
                break
        years=current_time.year

        index1 = str(years)+"-"+str(index)+"-01"
        days30Months=[4,6,9,11]
        days31Months=[1,3,5,7,8,10,12]
        if(int(years)%4==0 and index == 2):
            index2 = str(years)+"-"+str(index)+"-29"
        if(index in days30Months):
            index2 = str(years)+"-"+str(index)+"-30"
        if(index in days31Months):
            index2 = str(years)+"-"+str(index)+"-31"
        if(int(years)%4!=0 and index==2):
            index2 = str(years)+"-"+str(index)+"-28"    
        month_date_open = datetime.strptime(index1, "%Y-%m-%d")
        month_date_end = datetime.strptime(index2, "%Y-%m-%d")
        found = coll.find_one({"EventDate":{"$gte":month_date_open,"$lte":month_date_end}}, {"_id":0})
        if found:
            event_name = found["EventName"]
            event_type = found["EventType"]
            event_start= found["StartTime"] 
            event_end = found["EndTime"]
            event_date = found["EventDate"]
            desired_format = "%Y-%m-%d"
            parsed_datetime = event_date.strftime(desired_format)
            datetime_object = datetime.strptime(parsed_datetime, "%Y-%m-%d")
            day_of_week_number = datetime_object.weekday()
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            message = "Yes, there is an event in that month. The event is "+event_name+". It is a "+event_type+" event, from "+event_start+" to "+event_end+" on "+parsed_datetime+"("+days[day_of_week_number]+")"
        else:
            message = "No important events are going to be hosted in that month"
        dispatcher.utter_message(text=message)
        return []
