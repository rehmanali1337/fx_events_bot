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


async def send_event_notification(event: Event, queue):
    queue.put(event)


class Scraper:
    def __init__(self, bot):
        self.config = json.load(open('config.json'))
        self.db = DB()
        self.bot = bot
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        webdriver_path = self.config.get("WEBDRIVER_PATH")
        self.driver = webdriver.Chrome(
            executable_path=webdriver_path, options=options)
        self.driver.implicitly_wait(10)
        self.loop = asyncio.new_event_loop()
        self.URL = 'https://www.investing.com/economic-calendar/'
        self.itter_time = 300
        # self.jobstore = {
        #     'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        # }
        self.schedular = AsyncIOScheduler(
            event_loop=self.loop)
        self.schedular.start()
        self.schedular.print_jobs()
        self.tz_name = 'America/New_York'

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
        # test_trigger = DateTrigger(run_date=dt.now() + timedelta(seconds=30))
        self.schedular.add_job(send_event_notification, trigger=trigger,
                               args=(event, self.queue), replace_existing=True)

    async def get_all_events(self):
        self.driver.get(self.URL)
        table_xpath = '//table[@id="economicCalendarData"]'
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, table_xpath))
            )
        except exceptions.TimeoutException:
            return None
        table = self.driver.find_element_by_xpath(
            '//table[@id="economicCalendarData"]')
        tbody = table.find_element_by_tag_name('tbody')
        rows = tbody.find_elements_by_tag_name('tr')
        rows.pop(0)
        events = list()
        for row in rows:
            event = Event()
            row_id = row.get_attribute("id").replace("eventRowId_", '').strip()
            event.id = row_id
            date_time = row.get_attribute("data-event-datetime")
            date = date_time.split(' ')[0]
            year = int(date.split('/')[0])
            month = int(date.split('/')[1])
            day = int(date.split('/')[2])
            time = date_time.split(' ')[-1].strip()
            hours = int(time.split(':')[0])
            minutes = int(time.split(':')[1])
            event.event_time = dt(year=year, month=month, day=day,
                                  hour=hours, minute=minutes, tzinfo=pytz.timezone(self.tz_name))
            event.date = f'{year}/{month}/{day}'
            event.time = time
            event.currency = row.find_element_by_class_name(
                "flagCur").text.strip()
            event.impact = row.find_element_by_class_name(
                "sentiment").get_attribute("title").strip()
            event.title = row.find_element_by_class_name("event").text
            event.link = row.find_element_by_class_name(
                "event").find_element_by_tag_name("a").get_attribute("href")
            actual = row.find_element_by_id(
                f'eventActual_{row_id}').text.strip()
            if actual != '':
                event.actual = actual
            forecast = row.find_element_by_id(
                f'eventForecast_{row_id}').text.strip()
            if forecast != '':
                event.forecast = forecast
            prev = row.find_element_by_id(
                f'eventPrevious_{row_id}').text.strip()
            if prev != '':
                event.previous = prev
            events.append(event)
        return events
