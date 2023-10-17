import datetime
import pendulum
import os
import lxml.etree as ET

import requests
from airflow.decorators import dag, task
from asnake.client import ASnakeClient

@dag(
    dag_id="automate-archival-description",
    schedule_interval="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def AutomateArchivalDescription():
    @task
    def get_data():
        # NOTE: configure this as appropriate for your airflow environment
        data_path = "/opt/airflow/working/archive_space/data.xml"
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

        client = ASnakeClient(baseurl="http://spec-as-prod.stanford.edu:8089",
                              username="",
                              password="")
        client.authorize()

        # for c in collection_data["Identifier/Collection number"][57:]:
        for c in ["SC0932"]:
            c = c.strip()
            try:
                find_res_id = client.get('repositories/2/find_by_id/resources', params={'identifier[]': [f'["{c}"]']})
                res_id = find_res_id.json()["resources"][0]["ref"].split("/resources/")[1]
                print(c, "=>", res_id)

                collection = client.get(f"/repositories/2/resources/{res_id}").json()
                try:
                    resourceID = collection.get("uri").split("/resources/")[1]
                    params = {"include_daos": True}
                    eadResponse = client.get("repositories/2/resource_descriptions/" + resourceID + ".xml", params=params)
                    f = open(data_path, "w", encoding="utf-8")
                    f.write(eadResponse.text)
                    f.close()
                except:
                    print("No uri key.: ")
            except:
                print(f"Can't return resource url id for {c}: ")

        with open(data_path, "w") as file:
            file.write(response.text)

    @task
    def enrich_data():
        with open(data_path, "w") as file:
            tree = ET.fromstring(file.read(), parser=ET.HTMLParser())
            contentnav = tree.find(".//")
            contentnav.addnext(ET.XML("<div style='clear: both'></div>"))
            file.write(ET.tostring(tree))


    get_data() >> enrich_data()


dag = AutomateArchivalDescription()
