import pandas as pd

import datetime
from functools import lru_cache
from itertools import islice
import os


class BikeShareData:
    dataset_names = {
        'chicago': 'chicago.csv',
        'new york': 'new_york_city.csv',
        'washington': 'washington.csv'
    }

    def __init__(self, folder_path: str):
        """
        Initialize the class

        :param folder_path: str, path to folder containing all three datasets
        (chicago.csv, new_york_city.csv, washington.csv)
        """
        if not os.path.isdir(folder_path):
            raise Exception('Given path is not valid, make sure its a directory/ folder')

        self.dir_path = folder_path
        self.df = pd.DataFrame

    def get_data(self):
        """
        Get dataset and store it in cache for future use
        """
        prompt = '\nWould you like to view data for: Chicago, New York, or Washington ? '
        dataset_keys = list(self.dataset_names.keys())
        input_city = get_input(prompt=prompt, options=dataset_keys)

        file_name = self.dataset_names[input_city]
        self.df = self._get_data_helper(file_name=file_name)

    @lru_cache(maxsize=3)
    def _get_data_helper(self, file_name: str):
        """
        A helper for importing the CSV file, it stores the last three times it was called in cache,
        so there is no need to load the dataset time and time again.
        """
        file_path = self.dir_path + file_name
        df = pd.read_csv(file_path)

        df['Start Time'] = pd.to_datetime(df['Start Time'], format='%Y-%m-%d %H:%M:%S')
        df['Start hour'] = df['Start Time'].dt.hour
        df['month'] = df['Start Time'].dt.month_name()
        df['day_of_week'] = df['Start Time'].dt.day_name()
        df = df.rename(columns={'Unnamed: 0': 'index'})
        return df

    def get_statistics(self):
        """
        print statistics about the dataset
        """
        print('- Stats for nerds:')
        day_group = self.df.groupby('day_of_week')

        if 'Gender' in self.df.columns:  # column present in only two of three datasets
            print('Users by gender:', self.df['Gender'].value_counts().to_dict())
            print_cyan('- ' * 25)

        if 'Birth Year' in self.df.columns:
            self.df['age'] = datetime.datetime.now().year - self.df['Birth Year']
            x = {'Average': self.df['age'].mean(), 'Median': self.df['age'].median()}
            print(f"Average/ Median user's age: {x}")
            print_cyan('- ' * 25)

        print(f'User types:', self.df["User Type"].value_counts().to_dict())
        print_cyan('- ' * 25)

        print(f'Average trip duration by day: \n', day_group['Trip Duration'].mean())
        print_cyan('- ' * 25)

        print('Most common Start hour by day:')
        for day in day_group.groups:
            group = day_group.get_group(day)
            value = group['Start hour'].value_counts().idxmax()
            print(f'{day:<10} {value}')
        print_cyan('- ' * 25)

        start = self.df['Start Station'].value_counts()
        end = self.df['End Station'].value_counts()
        data = {**start}
        for key, val in end.items():
            data.setdefault(key, 0)
            data[key] += val
        print('Most common used station: \t', max(data, key=data.get))

        print_cyan('-' * 100)

    def filter_data_by_month(self):
        """
        Filter DataFrame by month
        """
        print('- Filters:')

        month_options = list(self.df["month"].unique())
        prompt = 'For which Month would you like to view data: \n'\
                 f'Options: {month_options}, or press ENTER to view all: '
        input_month = get_input(prompt=prompt, options=month_options + [''])

        if input_month != '':
            filt = self.df['month'] == input_month.title()
            self.df = self.df[filt]

    def filter_data_by_dow(self):
        """
        Filter DataFrame by week-day
        """
        day_options = list(self.df["day_of_week"].unique())
        prompt = '\nFor which Week-day would you like to view data: \n'\
                 f'Options: {day_options}, or press ENTER to view all: '
        input_day = get_input(prompt=prompt, options=day_options + [''])

        if input_day != '':
            filt = self.df['day_of_week'] == input_day
            self.df = self.df[filt]

        print_cyan('-' * 100)

    def display_data(self):
        """
        Displays the data in dict like format, row by row.
        By default, it shows 10 rows.
        """
        print('Data:')
        generator = self._row_generator()
        prompt = 'Do you wish to view data ? Enter Yes or No: '
        options = ['yes', 'no']

        while get_input(prompt=prompt, options=options) == 'yes':

            next_five = get_next_n(generator=generator, size=5)
            print('\n'.join([str(x) for x in next_five]))

        print_cyan('-' * 100)

    def _row_generator(self):
        """
        Generator that yields DataFrame rows one by one
        :yield: pandas row as dict
        """
        if len(self.df) == 0:
            print('DataFrame is empty')
            yield []
        for row in self.df.iterrows():
            yield row[1].to_dict()


def get_input(prompt: str, options: list):
    """
    Ask user for input and make sure it's a valid option, otherwise:
    print(message, options) and try again

    :param prompt: str
    :param options: List[str]
    :return: input as: str.strip().lower()
    """
    options = list(map(lambda x: x.lower(), options))
    input_ = input(prompt).strip().lower()

    if input_ not in options:
        print_red(f'Error: given input is not valid ({input_}), must be one of these options: {options}')
        return get_input(prompt, options)
    return input_


def get_next_n(generator, size: int):
    """
    Gets next N value of elements from generator,
    and returns it in a list

    :param size:
    :param generator: generator function
    """
    return [x for x in islice(generator, size)]


def print_red(text):
    print(f"\033[91m{text}\033[00m")


def print_cyan(text):
    print(f"\033[96m{text}\033[00m")


def main():
    bike_data = BikeShareData("C:/Users/Shner/Learning/data/")
    while True:
        bike_data.get_data()
        bike_data.get_statistics()
        bike_data.filter_data_by_month()
        bike_data.filter_data_by_dow()
        bike_data.display_data()


if __name__ == '__main__':
    main()
