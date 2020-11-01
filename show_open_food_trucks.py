#!/usr/bin/env python
import logging
import sys
import time
import traceback
from datetime import datetime
from typing import List

import requests
from halo import Halo
from prettytable import PrettyTable
from pydantic import parse_obj_as

from api_service import ApiService
from config import AppConfig
from models import SocrataData

if __name__ == '__main__':
    print("==================Foodiezz==================\n")
    print("Hello! Welcome to Foodiezz!")
    app_config = AppConfig()
    socrata_domain = app_config.socrata_domain
    socrata_dataset_id = app_config.socrata_dataset_id
    app_token = app_config.app_token
    query_limit = app_config.query_limit

    now = datetime.now()
    current_day_order = now.isoweekday()
    time_str = "'{}'".format(now.strftime('%H:%M'))
    print("\nTime is: {}".format(now.strftime("%c")))
    api_service = ApiService(socrata_domain, app_token)
    try:
        socrata_data = None
        offset = 0
        food_truck_table = PrettyTable()
        food_truck_table.field_names = ['Name', 'Address']
        food_truck_table.align['Name'] = "l"
        food_truck_table.align['Address'] = "r"
        spinner = Halo()
        total_entries = 0
        while socrata_data is None or len(socrata_data) > 0:
            try:
                spinner.start("Finding food trucks for you...")
                socrata_data = api_service.select(
                    ['applicant', 'location', 'start24', 'end24', 'dayorder', 'dayofweekstr']).where(
                    start24__lte=time_str, end24__gte=time_str, dayorder=current_day_order).order_by('applicant').limit(
                    query_limit).offset(offset).query(socrata_dataset_id)
                spinner.stop()
                spinner.clear()
                offset += query_limit
                dataset = parse_obj_as(List[SocrataData], socrata_data)
                for data in dataset:
                    food_truck_table.add_row([data.applicant, data.location])
                    total_entries += 1
                if len(socrata_data) > 0:
                    if offset == query_limit:
                        print("\nFound these Food Trucks that are open now:")
                    print(
                        food_truck_table.get_string(start=offset - query_limit, end=offset, header=False, border=False))
                    if len(socrata_data) < 10:
                        print("\n====No more Food Trucks found====")
                        break
                    else:
                        input("Showing {} results. Press enter to view more...".format(total_entries))
                        print("\033[A                             \033[A")
                else:
                    print("\nUh-oh! Looks like no Food Truck is open right now!")
            except requests.exceptions.HTTPError as ex:
                logging.error(str(ex))
                break
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
        logging.error("unhandled exception occurred")
    finally:
        print("\nBye!!")
        api_service.close()
