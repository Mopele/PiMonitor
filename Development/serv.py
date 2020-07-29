import sys
import os
import re
import glob
import json
import logging
import threading
import numpy
import pandas as pd
import psutil
import logging

from time import time, mktime
from flask import (
    Flask,
    render_template,
    send_file,
    request,
    g,
    abort,
    jsonify,
    url_for,
    session,
    redirect,
    flash,
)
from datetime import datetime
from termcolor import colored

# use bokeh version 1.3.4
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import Range1d, DatetimeTickFormatter
from bokeh.models.sources import AjaxDataSource, CustomJS

app = Flask(__name__)
app.secret_key = "tpsecret..."
logpath = "testlog.log"  # "/home/pi/Documents/mainlog.log"


class AjaxFilter(logging.Filter):
    def filter(self, record):
        return "api" not in record.getMessage()


log = logging.getLogger("werkzeug")
log.addFilter(AjaxFilter())


@app.route("/")
def server():
    html_components = [[], []]  # components container
    js_resources = INLINE.render_js()  # recources for bokeh plot
    css_resources = INLINE.render_css()

    try:
        # get the stuff to display on Webside
        script1, div1 = components(
            get_api("CPU - Usage in %", "cpu",
                    [100, 0], "red", "", 2000, "server",)
        )
        script2, div2 = components(
            get_api(
                "Memory - Usage in %", "memory", [100,
                                                  0], "blue", "", 2000, "server",
            )
        )
        script3, div3 = components(
            get_api("Disk - Usage in %", "disk",
                    [100, 0], "blue", "", 2000, "server",)
        )
    except Exception as e:
        flask_log(
            "SERVER",
            "Could get Server data! Error: " + str(e),
            "yellow",
            "404",
            "Serverinformationen konnten nicht geladen werden!",
            "danger",
            "home",
        )
    # fill container
    html_components[0].extend([script1, script2, script3])
    html_components[1].extend([div1, div2, div3])

    # get logs
    lines = []
    with open(logpath, "r") as f:
        for line in f:
            lines.append(line)

    return render_template(
        "server.html",
        outlines=lines[-20:],
        plot_script=html_components[0],
        plot_div=html_components[1],
        js_resources=js_resources,
        css_resources=css_resources,
    )


@app.route("/api/", methods=["POST"])  # used to supply the statusdata
def api():
    datapoint = request.headers["meta"].split(
        ",")[0]  # readout the wanted data

    # check what data to supply
    if datapoint == "cpu":
        data = psutil.cpu_percent()
    if datapoint == "memory":
        data = psutil.virtual_memory().percent
    if datapoint == "disk":
        data = psutil.disk_usage("/").percent

    # further processed in the JS-adapter
    return jsonify(x=int(time()), y=float(data))


def get_api(datatitle, datapoint, yrange, color, horse, refreshrate, mode):
    if mode == "server":
        msg = {"meta": datapoint}
        timeformat = "%H:%M:%S"
        adapter = CustomJS(
            code="""
            const result = {x: [cb_data.response.x * 1000], y: [cb_data.response.y]}
            console.log("[=>] Updated Ajax for " + cb_data.response.dp + ":", result)
            return result
        """
        )
        source = AjaxDataSource(
            data_url=request.url_root + "api" + "/",
            http_headers=msg,
            polling_interval=refreshrate,
            data=dict(y=[], x=[]),
            mode="append",
            adapter=adapter,
        )  # create  an AJAX source
        fig = figure(
            title=datatitle,
            plot_width=1000,
            plot_height=300,
            x_axis_type="datetime",
            sizing_mode="stretch_width",
        )  # get the figure
        fig.line(
            x="x", y="y", source=source, color=color, line_width=4
        )  # add plot to figure

        # get desired timeformat
        fig.xaxis.formatter = DatetimeTickFormatter(
            seconds=[timeformat],
            minutes=[timeformat],
            minsec=[timeformat],
            hours=[timeformat],
        )
        if yrange != "dynamic":
            fig.y_range = Range1d(float(yrange[1]), float(yrange[0]))
        fig.title.text_font_size = "12pt"
        return fig


def flask_log(process, message, color, code, flashmsg, flashtype, redir):
    # def to communicate with user
    flask_ip = "127.0.0.1"
    time = datetime.today()
    line = (
        flask_ip
        + " - - ["
        + time.today().strftime("%d/%m/%Y")
        + " "
        + time.today().strftime("%H:%M:%S")
        + "] "
        + '"'
        + colored(process + " " + message + '"', color)
        + " "
        + code
        + "-"
    )
    print(line)
    flash(flashmsg, flashtype)
    return redirect(url_for(redir))


if __name__ == "__main__":
    app.run(debug=True)
# author: Moritz Pfennig
