# pylint: disable=global-statement,redefined-outer-name
import argparse
import csv
import glob
import json
import os

import yaml
from flask import Flask, jsonify, redirect, render_template, send_from_directory
from flask_frozen import Freezer
from flaskext.markdown import Markdown

site_data = {}
by_uid = {}


def main(site_data_path):
    global site_data, extra_files
    extra_files = ["README.md"]
    # Load all for your sitedata one time.
    for f in glob.glob(site_data_path + "/*"):
        extra_files.append(f)
        name, typ = f.split("/")[-1].split(".")
        if typ == "json":
            site_data[name] = json.load(open(f))
        elif typ in {"csv", "tsv"}:
            site_data[name] = list(csv.DictReader(open(f)))
        elif typ == "yml":
            site_data[name] = yaml.load(open(f).read(), Loader=yaml.SafeLoader)

    for typ in ["papers", "speakers", "workshops"]:
        by_uid[typ] = {}
        for p in site_data[typ]:
            by_uid[typ][p["UID"]] = p

    print("Data Successfully Loaded")
    return extra_files


# ------------- SERVER CODE -------------------->

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)
markdown = Markdown(app)


# MAIN PAGES


def _data():
    data = {}
    data["config"] = site_data["config"]
    return data


@app.route("/")
def index():
    data = _data()
    data["team"] = site_data["team"]["team"]
    return redirect("/index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(site_data_path, "favicon.ico")


# TOP LEVEL PAGES


@app.route("/index.html")
def home():
    data = _data()
    data["team"] = site_data["team"]["team"]
    return render_template("index.html", **data)

@app.route("/molecule.html")
def molecule():
    data = _data()
    return render_template("molecule.html", **data)

@app.route("/protein.html")
def protein():
    data = _data()
    return render_template("protein.html", **data)

@app.route("/brain.html")
def brain():
    data = _data()
    return render_template("brain.html", **data)

@app.route("/physics.html")
def physics():
    data = _data()
    return render_template("physics.html", **data)

@app.route("/nlp.html")
def nlp():
    data = _data()
    return render_template("nlp.html", **data)

@app.route("/social.html")
def social():
    data = _data()
    return render_template("social.html", **data)

@app.route("/collab.html")
def collab():
    data = _data()
    return render_template("collab.html", **data)

@app.route("/circuit.html")
def circuit():
    data = _data()
    return render_template("circuit.html", **data)

@app.route("/traffic.html")
def traffic():
    data = _data()
    return render_template("traffic.html", **data)

@app.route("/authen.html")
def authen():
    data = _data()
    return render_template("authen.html", **data)

@app.route("/IoT.html")
def IoT():
    data = _data()
    return render_template("IoT.html", **data)

@app.route("/skeleton.html")
def skeleton():
    data = _data()
    return render_template("skeleton.html", **data)

@app.route("/scene.html")
def scene():
    data = _data()
    return render_template("scene.html", **data)

@app.route("/synthetic.html")
def synthetic():
    data = _data()
    return render_template("synthetic.html", **data)


#@app.route("/help.html")
#def about():
#    data = _data()
#    data["FAQ"] = site_data["faq"]["FAQ"]
#    return render_template("help.html", **data)

@app.route("/team.html")
def team():
    data = _data()
    data["team"] = site_data["team"]["team"]
    return render_template("team.html", **data)


@app.route("/blogs.html")
def blogs():
    data = _data()
    data["team"] = site_data["team"]["team"]
    return render_template("index.html", **data)


def extract_list_field(v, key):
    value = v.get(key, "")
    if isinstance(value, list):
        return value
    else:
        return value.split("|")


def format_paper(v):
    list_keys = ["authors", "keywords", "sessions"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "UID": v["UID"],
        "title": v["title"],
        "forum": v["UID"],
        "authors": list_fields["authors"],
        "keywords": list_fields["keywords"],
        "abstract": v["abstract"],
        "TLDR": v["abstract"],
        "recs": [],
        "sessions": list_fields["sessions"],
        # links to external content per poster
        "pdf_url": v.get("pdf_url", ""),  # render poster from this PDF
        "code_link": "https://github.com/Mini-Conf/Mini-Conf",  # link to code
        "link": "https://arxiv.org/abs/2007.12238",  # link to paper
    }


def format_workshop(v):
    list_keys = ["authors"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "id": v["UID"],
        "title": v["title"],
        "organizers": list_fields["authors"],
        "abstract": v["abstract"],
    }


# ITEM PAGES


@app.route("/poster_<poster>.html")
def poster(poster):
    uid = poster
    v = by_uid["papers"][uid]
    data = _data()
    data["paper"] = format_paper(v)
    return render_template("poster.html", **data)


@app.route("/speaker_<speaker>.html")
def speaker(speaker):
    uid = speaker
    v = by_uid["speakers"][uid]
    data = _data()
    data["speaker"] = v
    return render_template("speaker.html", **data)


@app.route("/workshop_<workshop>.html")
def workshop(workshop):
    uid = workshop
    v = by_uid["workshops"][uid]
    data = _data()
    data["workshop"] = format_workshop(v)
    return render_template("workshop.html", **data)


@app.route("/chat.html")
def chat():
    data = _data()
    return render_template("chat.html", **data)


# FRONT END SERVING


@app.route("/papers.json")
def paper_json():
    json = []
    for v in site_data["papers"]:
        json.append(format_paper(v))
    return jsonify(json)


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)


@app.route("/serve_<path>.json")
def serve(path):
    return jsonify(site_data[path])


# --------------- DRIVER CODE -------------------------->
# Code to turn it all static


@freezer.register_generator
def generator():
#    for paper in site_data["papers"]:
#        yield "poster", {"poster": str(paper["UID"])}
#    for speaker in site_data["speakers"]:
#        yield "speaker", {"speaker": str(speaker["UID"])}
#    for workshop in site_data["workshops"]:
#        yield "workshop", {"workshop": str(workshop["UID"])}

    for key in site_data:
        yield "serve", {"path": key}


def parse_arguments():
    parser = argparse.ArgumentParser(description="MiniConf Portal Command Line")

    parser.add_argument(
        "--build",
        action="store_true",
        default=False,
        help="Convert the site to static assets",
    )

    parser.add_argument(
        "-b",
        action="store_true",
        default=False,
        dest="build",
        help="Convert the site to static assets",
    )

    parser.add_argument("path", help="Pass the JSON data path and run the server")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()

    site_data_path = args.path
    extra_files = main(site_data_path)

    if args.build:
        freezer.freeze()
    else:
        debug_val = False
        if os.getenv("FLASK_DEBUG") == "True":
            debug_val = True

        app.run(port=5000, debug=debug_val, extra_files=extra_files)
