import requests 
import datetime
from dateutil import parser
import os 
from tqdm import tqdm

import unicodedata
import re

def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def print_banner():
	print(
		f"""{bcolors.OKBLUE}
 ________   ___  __  __   _____    _    ______   __
|__  / _ \ / _ \|  \/  | | ____|  / \  / ___\ \ / /
  / / | | | | | | |\/| | |  _|   / _ \ \___ \\\ V /
 / /| |_| | |_| | |  | | | |___ / ___ \ ___) || |
/____\___/ \___/|_|  |_| |_____/_/   \_\____/ |_|

 __  __ _____ _____ _____ ___ _   _  ____ ____
|  \/  | ____| ____|_   _|_ _| \ | |/ ___/ ___|
| |\/| |  _| |  _|   | |  | ||  \| | |  _\___ \\
| |  | | |___| |___  | |  | || |\  | |_| |___) |
|_|  |_|_____|_____| |_| |___|_| \_|\____|____/
		{bcolors.ENDC}"""
	)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
	try:
		print_banner()
		print()
		print(f"{bcolors.HEADER}Welcome to Zoom easy meetings {bcolors.ENDC}")

		_user_id = input("Insert your email / userID: ")
		_jwt_token = input("Insert your JWT access token: ")

		os.system("cls")
		print_banner()
		print()

		start_year = int(input("Insert your starting year: "))
		end_year = int(input("Insert your stop year: "))
		starting_month = int(input("Insert your starting month: "))

		if len(str(start_year)) != 4 or len(str(end_year)) != 4:
			print(f"{bcolors.FAIL}You have inserted a wrong formatted year {bcolors.ENDC}")
			return;

		if starting_month < 1 or starting_month > 12:
			print(f"{bcolors.FAIL}You have inserted a wrong month {bcolors.ENDC}")

		for year in range(start_year, end_year):
			for month in range(starting_month,13):
				next_month = month + 1
				next_year = year

				if month == 12:
					next_month = 1
					next_year = year + 1

				start_date = datetime.datetime(year,month,1)
				next_date = datetime.datetime(next_year,next_month,1)

				get_recording(_user_id, _jwt_token, start_date, next_date, year, month, end_year)

	except Exception as e:
		print(f"{bcolors.WARNING}Something unexpected has occured {bcolors.ENDC}")
		print("--------------------")
		print(f"{bcolors.WARNING}error: {bcolors.ENDC}{bcolors.FAIL}{e}{bcolors.ENDC}")

def get_recording(user_id, jwt_token, start_date, next_date, year, month, end_year):
    date_string = '%Y-%m-%d'
    url = 'https://api.zoom.us/v2/users/{}/recordings?from={}&to={}&page_size=300&'.format(
        user_id,
        start_date.strftime(date_string),
        next_date.strftime(date_string)
    )

    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'content-type': 'application/json',
    }

    response = requests.get(
		url,
		headers=headers
	)

    data = response.json()

    for meeting in data['meetings']:
        topic = meeting["topic"]
        meeting_id = meeting["id"]
        start_data = parser.parse(meeting["start_time"])
        for record in meeting['recording_files']:
            if record['status'] != 'completed' or record["file_type"] != "MP4":
                continue

            download_recording(
                jwt_token,
                record['download_url'], 
                record['recording_start'].replace(':','-'),
                topic,
                start_data,
                meeting_id,
                year,
                month,
                end_year,
            )


def download_recording(jwt_token, download_url, filename, topic, date, meeting_id, year, month, end_year):
    rainbow = [bcolors.FAIL, bcolors.WARNING, bcolors.OKGREEN, bcolors.OKCYAN, bcolors.OKBLUE, bcolors.HEADER]

    os.system('cls')
    print_banner()
    print(f"{bcolors.OKGREEN}Downloading the file please wait...{bcolors.ENDC}")

    download_access_url = '{}?access_token={}'.format(download_url, jwt_token)
    response = requests.get(download_access_url, stream=True)

    os.system("cls")
    print_banner()
    print(f"{bcolors.OKGREEN}Loading...{bcolors.ENDC}")
    os.system("cls")
    print_banner()

    PATH = './meetings/'

    local_filename = '{}{}-{}-{}-{}.mp4'.format(PATH, date.strftime("%Y-%m-%d"), slugify(topic), meeting_id, filename)
    local_filename_bar = '{}-{}-{}.mp4'.format(slugify(topic), date.strftime("%Y-%m-%d"), meeting_id)

    with open(local_filename, 'wb') as f:
        print(f"Currently processing: {bcolors.OKGREEN}starting year: {year} end: {end_year} and month: {month}/12")
        print(f"{bcolors.ENDC}Currently processed file: {bcolors.OKGREEN}{local_filename_bar} {bcolors.ENDC}")

        color = 0
        updater = 0

        with tqdm(total=int(response.headers["Content-length"]), desc=f"{rainbow[color]}Processing...") as bar:
            for chunk in response.iter_content(chunk_size=8192):
                updater += 1
                if updater >= 2048: 
                    color += 1
                    bar.set_description(f"{rainbow[color]}Processing...")
                    updater = 0

                bar.update(8192)
                f.write(chunk)
                if color >= 5:
                    color = 0
	   
if __name__ == '__main__':
	main()
