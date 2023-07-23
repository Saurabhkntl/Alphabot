
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted
import pymongo
from datetime import datetime
import time
import sys
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
class SayAllEventsAfterADate(Action):
    def name(self) -> Text:
        return "action_say_allevents"
    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        found = coll.find({"EventDate":{"$gte":current_time}},{"_id":0})
        c=1
        if found is None:
            dispatcher.utter_message("No more events are scheduled after today for this year")
        else:    
            dispatcher.utter_message(text="The list of remaining events are:")
            for i in found:
                event_name = i["EventName"]
                event_date = i["EventDate"]
                desired_foramt = "%Y-%m-%d"
                parsed_date = event_date.strftime(desired_foramt)
                datetime_object = datetime.strptime(parsed_date, "%Y-%m-%d")
                day_number = datetime_object.weekday()
                event_location = i["Location"]
                event_desc = i["Description"]
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                message = str(c)+". "+event_name+" on "+parsed_date+"("+days[day_number]+")\n"+"Location: "+event_location+"\nDescription: "+event_desc
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text=" ")             
                c=c+1
            return[]
class SayAllEvents(Action):
    def name(self) -> Text:
        return "action_say_alleventsall"
    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        timestr = "1900-01-01"
        timeobj = datetime.strptime(timestr,"%Y-%m-%d")
        found = coll.find({"EventDate":{"$gte":timeobj}},{"_id":0})
        c=1
        if found is None:
            dispatcher.utter_message("No more events are scheduled after today for this year")
        else:    
            dispatcher.utter_message(text="The list of events are:")
            for i in found:
                event_name = i["EventName"]
                event_date = i["EventDate"]
                desired_foramt = "%Y-%m-%d"
                parsed_date = event_date.strftime(desired_foramt)
                datetime_object = datetime.strptime(parsed_date, "%Y-%m-%d")
                day_number = datetime_object.weekday()
                event_location = i["Location"]
                event_desc = i["Description"]
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                message = str(c)+". "+event_name+" on "+parsed_date+"("+days[day_number]+")\n"+"Location: "+event_location+"\nDescription: "+event_desc
                dispatcher.utter_message(text=message)
                dispatcher.utter_message(text=" ")             
                c=c+1
            return[]
class giveUserEventLink(Action):
    def name(self) -> Text:
        return "action_givegformlink"
    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])
        Eventname = next((entity for entity in entities if entity['entity'] == 'eventname'), None)
        Eventnamevalue = str(Eventname['value'])
        found = coll.find_one({"EventName": Eventnamevalue},{"_id":0})       
        if found is not None:
            link = found['GformLink']
            dispatcher.utter_message(text="You chose to register for "+Eventnamevalue+"\nHere is the google form link "+link)
        else:
            dispatcher.utter_message(text="The Registration for "+Eventnamevalue+" has not begun yet")
