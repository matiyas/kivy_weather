#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
import kivy
kivy.require("1.9.0")

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from BeautifulSoup import BeautifulSoup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.accordion import Accordion, AccordionItem


def weather_json(woeid):
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid={} and u='c'".format(woeid)
    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    result = urllib2.urlopen(yql_url).read()
    data = json.loads(result)

    with open('weather.json', 'w') as weather:
        weather.write(json.dumps(data, indent=4, sort_keys=True))

    return data


class CurrentWeather(AccordionItem):
    def __init__(self):
        super(CurrentWeather, self).__init__()
        self.main_box = BoxLayout(orientation="vertical")
        self.time_bar = BoxLayout(orientation="horizontal")
        self.date_box = BoxLayout(orientation="vertical")
        self.temp_box = FloatLayout(orientation="horizontal")
        self.hour_label = Label(markup=True)
        self.date_label = Label(markup=True)
        self.main_temp_label = Label(markup=True, pos_hint={'x': 0, 'y': 0})
        self.weather_image = Image(markup=True, pos_hint={'x': -.2, 'y': .2})
        self.extreme_temp_label = Label(markup=True)

        self.time_bar.add_widget(self.hour_label)
        self.time_bar.add_widget(self.date_box)
        self.date_box.add_widget(self.date_label)
        self.temp_box.add_widget(self.weather_image)
        self.temp_box.add_widget(self.main_temp_label)
        self.temp_box.add_widget(Label())

        self.main_box.add_widget(self.time_bar)
        self.main_box.add_widget(self.temp_box)
        self.main_box.add_widget(self.extreme_temp_label)

        self.add_widget(self.main_box)
        

class Forecast(AccordionItem):
    def __init__(self):
        super(Forecast, self).__init__()
        self.main_box = BoxLayout(orientation="vertical")
        self.day_box = [BoxLayout(orientation="horizontal") for _ in xrange(5)]
        self.date_label = [Label(markup=True) for _ in xrange(5)]
        self.day_label = [Label(markup=True) for _ in xrange(5)]
        self.weather_image = [Image() for _ in xrange(5)]
        self.extreme_temp = [Label(markup=True) for _ in xrange(5)]

        for i in xrange(5):
            self.day_box[i].add_widget(self.day_label[i])
            self.day_box[i].add_widget(self.date_label[i])
            self.day_box[i].add_widget(self.weather_image[i])
            self.day_box[i].add_widget(self.extreme_temp[i])
            self.main_box.add_widget(self.day_box[i])

        self.add_widget(self.main_box)


class GUI(Accordion):
    def __init__(self):
        super(GUI, self).__init__()
        self.current = CurrentWeather()
        self.forecast = Forecast()

        self.add_widget(self.forecast)
        self.add_widget(self.current)

        self.weather_update()

    def weather_update(self):
        json_data = weather_json("522678")
        weather = json_data["query"]["results"]["channel"]["item"]
        time = json_data["query"]["created"]

        self.current.hour_label.text = "[size=40][b]{}[/b]".format(str(int(time[11:13]) + 2) + time[13:16])
        self.current.date_label.text = "   [size=35]{}\n[size=15]{}".format(weather["condition"]["date"].split()[0][:-1],
                                                                            " ".join(weather["condition"]["date"].split()[1:4]))
        self.current.main_temp_label.text = u"[size=100][b]{}\u00b0[/b]".format(weather["condition"]["temp"])
        self.current.extreme_temp_label.text = u"[size=18]Min. temp.:    {}\u00b0\n" \
                                               u"Max. temp.:    {}\u00b0".format(weather["forecast"][0]["low"],
                                                                                 weather["forecast"][0]["high"])
        soup = BeautifulSoup(weather["description"])
        src = BeautifulSoup(soup.findAll(text=True)[0]).find("img")["src"]
        urllib.urlretrieve(src, "weather.gif")
        self.current.weather_image.source = "weather.gif"
        self.current.weather_image.reload()

        for i in xrange(5):
            self.forecast.weather_image[i].source = "weather.gif"
            self.forecast.date_label[i].text = weather["forecast"][i + 1]["date"]
            self.forecast.day_label[i].text = weather["forecast"][i + 1]["day"]
            self.forecast.extreme_temp[i].text = u"Max: {}\u00b0\nMin: {}\u00b0".format(weather["forecast"][i + 1]["high"],
                                                                                        weather["forecast"][i + 1]["low"])


class Application(App):
    def build(self):
        return GUI()

if __name__ == "__main__":
    Application().run()
