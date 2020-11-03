#!/usr/bin/env python
import logging
import traceback
import requests
from datetime import datetime
from typing import List
from halo import Halo
from prettytable import PrettyTable
from pydantic import parse_obj_as
from api_service import ApiService
from config import AppConfig
from models import SocrataData


class App:
    def __init__(self):
        self.display_message("===============================| Foodiezz |===============================\n")
        self.display_message("Hello! Welcome to Foodiezz!")
        config = AppConfig()
        self.socrata_dataset_id = config.socrata_dataset_id
        self.page_limit = config.page_limit
        self.api_service = ApiService(config.socrata_domain, config.app_token)
        self.foodtruck_dataset = {}
        self.foodtruck_table = PrettyTable(field_names=['Name', 'Address'])
        self.foodtruck_table.min_width = 60
        self.total_foodtrucks_open = 0

    def search(self, time_now=datetime.now()):
        current_day_order = time_now.isoweekday()
        time_str = "'{}'".format(time_now.strftime('%H:%M'))
        self.display_message("\nTime is: {}".format(time_now.strftime("%c")))
        try:
            spinner = Halo()
            spinner.start("Finding food trucks for you...")
            socrata_data = self.api_service.select(
                ['applicant', 'location', 'start24', 'end24', 'dayorder', 'dayofweekstr']).where(
                start24__lte=time_str, end24__gte=time_str, dayorder=current_day_order).order_by('applicant').query(
                self.socrata_dataset_id)
            spinner.stop()
            spinner.clear()
            socrata_data_list = parse_obj_as(List[SocrataData], socrata_data)
            for data in socrata_data_list:
                self.foodtruck_dataset[(data.applicant, data.location)] = data
            self.total_foodtrucks_open = len(self.foodtruck_dataset)
            self.__update_ptable()
        except requests.exceptions.HTTPError as ex:
            logging.error(str(ex))
        except:
            traceback.print_exc()
            logging.error("unhandled exception occurred while searching food trucks")

    def __update_ptable(self):
        min_name_len = 0
        min_location_len = 0
        for key in self.foodtruck_dataset:
            name = key[0]
            location = key[1]
            self.foodtruck_table.add_row([name, location])
            if len(name) > min_name_len:
                min_name_len = len(name)
            if len(location) > min_location_len:
                min_location_len = len(location)

        if min_name_len > 0 and min_location_len > 0:
            self.foodtruck_table._min_width = {"Name": min_name_len, "Address": min_location_len}
        self.foodtruck_table.align['Name'] = 'l'
        self.foodtruck_table.align['Address'] = 'r'

    def print_table(self, paginate=True):
        if self.total_foodtrucks_open > 0:
            self.display_message("\nFound these Food Trucks that are open now:\n")
            if not paginate:
                self.display_message(self.foodtruck_table.get_string(header=False, border=False))
            else:
                for i in range(0, self.total_foodtrucks_open, self.page_limit):
                    self.display_message(
                        self.foodtruck_table.get_string(start=i, end=i + self.page_limit, header=False, border=False))
                    self.__show_prompt(i)
            self.display_message(
                "===============================| {} Food Trucks found |===============================".format(
                    self.total_foodtrucks_open))
        else:
            self.display_message("\nUh-oh! Looks like no Food Truck is open right now!")

    def __show_prompt(self, offset):
        if offset + self.page_limit < self.total_foodtrucks_open:
            print("\n---------------------------")
            print("Showing {} of {} results.".format(offset + self.page_limit, self.total_foodtrucks_open))
            input("Press enter to view more...")
            print("\033[A                                   \033[A")
            print("\033[A                                   \033[A")
            print("\033[A                                   \033[A")
            print("\033[A                                   \033[A")

    def done(self):
        self.api_service.close()
        self.display_message("\nThank you for using Foodiezz!!")

    @staticmethod
    def display_message(msg=None):
        print(msg)


if __name__ == '__main__':
    try:
        app = App()
        try:
            app.search()
            app.print_table()
        except KeyboardInterrupt:
            pass
        except:
            traceback.print_exc()
            logging.error("unhandled exception occurred in the app")
        finally:
            app.done()
    except:
        logging.error("Unable to initialize the App!")
