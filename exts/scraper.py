from selenium import webdriver
import asyncio
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from datetime import datetime as dt
from datetime import timedelta
from models.models import Event
from exts.db import DB
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from datetime import timedelta
# import pendulum
import os


async def send_event_notification(event: Event, queue):
    queue.put(event)


class Scraper:
    def __init__(self, bot):
        self.config = json.load(open('config.json'))
        self.db = DB()
        self.bot = bot
        self.loop = asyncio.new_event_loop()
        self.URL = 'https://ftmo.com/en/calendar/'
        self.itter_time = 300
        # self.jobstore = {
        #     'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        # }
        self.schedular = AsyncIOScheduler(
            event_loop=self.loop)
        self.schedular.start()
        self.schedular.print_jobs()
        self.tz_name = 'America/New_York'
        self.tz = pytz.timezone(self.tz_name)
        self.start_driver()

    def start_driver(self):
        os.system('pkill chrom')
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.driver = webdriver.Chrome(
            executable_path=self.webdriver_path, options=self.options)
        self.driver.implicitly_wait(10)

    def start(self, queue):
        self.queue = queue
        self.loop.run_until_complete(self.main())

    async def main(self):
        while True:
            events = await self.get_all_events()
            for event in events:
                if not self.db.event_exists(event.id):
                    await self.schedule_notification(event)
                    self.db.add_event(event)
            await asyncio.sleep(self.itter_time)

    async def schedule_notification(self, event):
        trigger = DateTrigger(
            run_date=event.event_time - timedelta(hours=1), timezone=self.tz_name)
        trigger = DateTrigger(run_date=dt.now() + timedelta(seconds=30))
        self.schedular.add_job(send_event_notification, trigger=trigger,
                               args=(event, self.queue), replace_existing=True)

    async def get_all_events(self):
        try:
            self.driver.get(self.URL)
        except Exception as e:
            print(e.__dict__)
            print('Restarting the driver')
            self.start_driver()
            return await self.get_all_events()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'macroCal'))
            )
        except exceptions.TimeoutException:
            return None
        table = self.driver.find_element_by_class_name("macroCal")
        tbody = table.find_element_by_tag_name("tbody")
        rows = tbody.find_elements_by_class_name("fundament")
        events = list()
        for row in rows:
            event = Event()
            event.title = row.find_elements_by_tag_name("td")[0].text
            event.currency = row.find_elements_by_tag_name("td")[1].text
            timestamp = row.get_attribute("data-timestamp")
            date_time = dt.fromtimestamp(int(timestamp), tz=self.tz)
            event.date = f'{date_time.year}/{date_time.month}/{date_time.day}'
            event.time = f'{date_time.hour}:{date_time.minute}'
            event.event_time = dt.fromtimestamp(int(timestamp), tz=self.tz)
            event.id = f'{event.title}{event.currency}'.encode('utf-8').hex()
            events.append(event)
        return events
