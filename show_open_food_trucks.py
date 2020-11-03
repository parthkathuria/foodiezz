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
        """
        The main class which loads the App config and interacts with the ApiService to retrieve Food truck data.
        This class is also responsible for how the data is printed on the console.
        """
        self.display_message("===============================| Foodiezz |===============================\n")
        self.display_message("Hello! Welcome to Foodiezz!")
        # load the AppConfig
        config = AppConfig()
        self.socrata_dataset_id = config.socrata_dataset_id
        self.page_limit = config.page_limit
        # initialize the the ApiService object
        self.api_service = ApiService(config.socrata_domain, config.app_token)
        self.foodtruck_dataset = {}
        # initializing PrettyTable object with 'Name' and 'Address' as the header
        # I am using PrettyTable to print the final output in an organized and structured way on the console.
        self.foodtruck_table = PrettyTable(field_names=['Name', 'Address'])
        self.foodtruck_table.min_width = 60
        self.total_foodtrucks_open = 0

    def search(self, time_now=datetime.now()):
        """
        This method takes datetime object and searches all the Food trucks that are open at the time that is passed
        as argument. If no value is passed then it takes the current time as default.
        :param time_now: Python datetime object. Default value is current time
        :return: None
        """
        # getting day of the week. this is used to filter the 'dayorder' field in Socrata data
        current_day_order = time_now.isoweekday()
        # formatting time stamp into HH:MM format. this will be used as a filter out food trucks whose start and end
        # time do not contain current timestamp
        time_str = "'{}'".format(time_now.strftime('%H:%M'))
        self.display_message("\nTime is: {}".format(time_now.strftime("%c")))
        try:
            # initialize Halo spinner object to display spinner in console while we fetch data from the SODA API
            spinner = Halo()
            spinner.start("Finding food trucks for you...")
            # here the query is selecting 'applicant', 'location', 'start24', 'end24', 'dayorder', 'dayofweekstr' only
            # it is also filtering the result where 'start24' of the food truck data is less than the current time and
            # 'end24' is greater than equal to current time (start24 <= time_str <= end24). It is also filtering the
            # result by the day of the week by specifying dayorder=current_day_order. And finally it orders the result
            # in ascending order of 'applicant' field which is the name of the Food Truck.
            socrata_data = self.api_service.select(
                ['applicant', 'location', 'start24', 'end24', 'dayorder', 'dayofweekstr']).where(
                start24__lte=time_str, end24__gte=time_str, dayorder=current_day_order).order_by('applicant').query(
                self.socrata_dataset_id)
            # stop and clear the spinner from the console to clean it up before printing the final output
            spinner.stop()
            spinner.clear()
            # parse and convert the response JSON into a List of SocrataData model object
            socrata_data_list = parse_obj_as(List[SocrataData], socrata_data)
            # for some Food trucks, there are multiple entries in the result because of different timings in the day
            # I only need any one out of these. As we are getting already filtered result that fit our criteria from the
            # API, I can sure that all these entries are valid. To remove duplicate I am using a python dictionary where
            # the key is a unique combination of 'applicant' and 'location' field. I am using a dictionary instead of
            # hash set because I want maintain the insertion order of the already sorted result. In Python3, sets don't
            # guarantee insertion order but by default a dictionary is ordered in Python 3.
            for data in socrata_data_list:
                self.foodtruck_dataset[(data.applicant, data.location)] = data
            self.total_foodtrucks_open = len(self.foodtruck_dataset)
            # Once I have the dictionary of the dataset, I am updating the PrettyTable rows with the data
            self.__update_ptable()
        except requests.exceptions.HTTPError as ex:
            logging.error(str(ex))
        except:
            traceback.print_exc()
            logging.error("unhandled exception occurred while searching food trucks")

    def __update_ptable(self):
        """
        Internal method to update data in the PTable object
        :return: None
        """
        # initializing two variables here that will be used to define the minimum width of the columns
        # the minimum width will the length of longest name in the data. By setting the minimum width to the length
        # of the longest name, aligns the console output in one line.
        min_name_len = 0
        min_location_len = 0
        for key in self.foodtruck_dataset:
            name = key[0]
            location = key[1]
            # add name and location to the table object one by one
            self.foodtruck_table.add_row([name, location])
            if len(name) > min_name_len:
                min_name_len = len(name)
            if len(location) > min_location_len:
                min_location_len = len(location)

        if min_name_len > 0 and min_location_len > 0:
            self.foodtruck_table._min_width = {"Name": min_name_len, "Address": min_location_len}
        self.foodtruck_table.align['Name'] = 'l'  # Align the 'Name' column to left
        self.foodtruck_table.align['Address'] = 'r'  # Align the 'Address' column to right

    def print_table(self, paginate=True):
        """
        This method will print the response of the query in the required format.

        :param paginate: True if the output needs to be paginated. False if we want to print all at once
        :return: None
        """
        if self.total_foodtrucks_open > 0:
            self.display_message("\nFound these Food Trucks that are open now:\n")
            if not paginate:
                # display all the results if paginate is False
                self.display_message(self.foodtruck_table.get_string(header=False, border=False))
            else:
                # Loop from 0 to total number of records, stepping at page_limit and printing the result to the console
                for i in range(0, self.total_foodtrucks_open, self.page_limit):
                    self.display_message(
                        self.foodtruck_table.get_string(start=i, end=i + self.page_limit, header=False, border=False))
                    # Call the __show_prompt() to show prompt on the console.
                    self.__show_prompt(i)
            self.display_message(
                "===============================| {} Food Trucks found |===============================".format(
                    self.total_foodtrucks_open))
        else:
            self.display_message("\nUh-oh! Looks like no Food Truck is open right now!")

    def __show_prompt(self, offset):
        """
        This method will display a prompt on the console asking the user if he/she would like to view more results
        :param offset: starting index of the result. Used to display number of results displayed on the console.
        :return: None
        """
        if offset + self.page_limit < self.total_foodtrucks_open:
            print("\n---------------------------")
            print("Showing {} of {} results.".format(offset + self.page_limit, self.total_foodtrucks_open))
            # ask the used if he/she would like to see more results
            input("Press enter to view more...")
            # following print statements are read by the console as Up Arrow action
            # the reason for these statements is to move 4 lines up before the program starts printing the next results
            # this way we have clean list of Food trucks in the output.
            print("\033[A                                   \033[A")
            print("\033[A                                   \033[A")
            print("\033[A                                   \033[A")
            print("\033[A                                   \033[A")

    def done(self):
        """
        This method closes the ApiService session. This method is called before exiting the process.
        :return: None
        """
        self.api_service.close()
        self.display_message("\nThank you for using Foodiezz!!")

    @staticmethod
    def display_message(msg=None):
        print(msg)


if __name__ == '__main__':
    """
    This is the entry point of the process or 'main' function.
    I initialize the App() object and call the 'search' method to start fetching data from the SODA API. After that
    I call the print_table() method to print the table in formatted way.
    """
    try:
        app = App()
        try:
            app.search()
            app.print_table()
        except KeyboardInterrupt:
            """
            Catching Keyboard Interrupts done by user like Ctrl+C, so that I can close the session in a clean way.
            """
            pass
        except:
            """
            Catching all the unhandled exceptions in the process.
            """
            traceback.print_exc()
            logging.error("unhandled exception occurred in the app")
        finally:
            """
            Finally closing everything.
            """
            app.done()
    except:
        logging.error("Unable to initialize the App!")
