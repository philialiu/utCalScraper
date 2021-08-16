# -*- coding: utf-8 -*-

import ics
import re
import urllib3 as urllib
from bs4 import BeautifulSoup
from datetime import datetime


def main():
    url = "https://sgs.calendar.utoronto.ca/sessional-dates"

    # get web content
    html = askURL(url)
    soup = BeautifulSoup(html, "html.parser")

    # divide into sessions and decode
    session = getSession(soup)
    cal = ics.icalendar.Calendar()
    for s in session:
        cal = getCalendar(s, cal)

    # save file
    with open('utcalendar.ics', 'w') as f:
        f.writelines(cal)


def askURL(url):
    http = urllib.PoolManager()
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
    }

    response = http.request('GET', url, headers=header)
    html = response.data.decode("utf-8")
    return html


def getSession(soup: BeautifulSoup):
    items = []
    for item in soup.find_all(style="page-break-inside: avoid"):
        items.append(item)
    return items


def getCalendar(session, cal):
    year = int(re.findall(r'\d{4}', str(session.h2))[0])

    # decode for each line
    for line in session.tbody.children:
        if str(line) == '\n':
            continue

        dataDate = line.contents[1]
        dataEvent = line.contents[3]

        # decode date
        matchDate = re.search(r'(\w+)\s(\d+)', str(dataDate))
        if matchDate:
            month = matchDate.group(1)
            day = matchDate.group(2)
            date = datetime.strptime(str(year) + month + day, '%Y%B%d')
        else:
            continue

        # decode event
        description = dataEvent.get_text()
        description = re.compile(r'([(](\d+)[)])|(\n)').sub('', description)
        # print(description)
        # print('----------')

        e = ics.event.Event()
        e.name = "UT Event"
        e.begin = date
        e.description = description
        e.make_all_day()
        cal.events.add(e)

    return cal


if __name__ == "__main__":
    main()
