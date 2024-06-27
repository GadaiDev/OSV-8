from flask import Flask, request, session, redirect, send_file
from flask_cors import CORS
from uuid import uuid4
from json import load, dump
from random import choices, randint
from datetime import datetime

import glob
import re


def f_open(fname):
    return open(fname,"r", encoding="utf-8").read()

def text_replace(text:str):
    text = text.replace("\n","<br>")
    text = re.sub(r"!Img:\"(.+)\"",r"<img src='\1' class='k_img'>", text)
    return text


def post_replace(text:str, name:str, id_, thr):
    for i in range(text.count("!Random")):
        text = text.replace("!Random",f"<b class='k_spc1'>{str(randint(0,100))}</b>")

    if thr == "root":
        ich = text
    else:
        ich = thr["dat"][0]["text"]

    if "!無個性" in ich:
        name = "OSVの名無しさん"
        id_ = "0000"

    return text, name, id_

app = Flask(__name__)
app.secret_key = "yajusenpai"
CORS(app)

@app.route("/")
def page_index():
    if session.get("ID") is None:
        session["ID"] = "".join(choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
    
    html = f_open("./HTML/index.html")
    thrl = []
    for i in glob.glob("./BBS/*.json"):
        thr = load(open(i, "r", encoding="utf-8"))
        tid = i.replace('./BBS\\','').replace('.json','')
        thrl.append(f"        <a href='/thread/{tid}'>{thr['title']}({len(thr['dat'])})</a><a href='/thread/{tid}?Proxy'>[P]</a>")
    html = html.replace("{{ Name }}",session.get("Name",""))
    return html.replace("{{ thi }}", "<br>\n".join(thrl))


@app.route("/thread/<thrid>")
def page_t(thrid):
    if session.get("ID") is None:
        session["ID"] = "".join(choices("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))

    thr = load(open(f"./BBS/"+thrid+".json", "r", encoding="utf-8"))
    
    if request.args.get("Proxy") == None:
        html = f_open("./HTML/thread.html")
    else:
        html = f_open("./HTML/threadP.html")
        html = html.replace("{{ ttl }}", thr["title"])

    html = html.replace("{{ thrid }}", thrid)
    html = html.replace("{{ Name }}",session.get("Name",""))
    return html



@app.route("/api/post", methods=["POST"])
def api_post_thr():
    thrid = request.form.get("thrID","").replace("/","").replace("..","")
    name = request.form.get("name","名無しさん").replace(">","&gt;").replace("<","&lt;")
    text = request.form.get("text","NoneType").replace(">","&gt;").replace("<","&lt;")

    session["Name"] = name

    if name == "":
        name = "OSVの名無しさん"

    id_ = session.get("ID","???")


    thr = load(open(f"./BBS/{thrid}.json", "r", encoding="utf-8"))

    text, name, id_ = post_replace(text, name, id_, thr)

    thr["dat"].append(
        {
            "name": name,
            "date": str(datetime.now()),
            "id": id_,
            "text": text 
        }
    )
    dump(thr, open(f"./BBS/{thrid}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
    return "ok"
@app.route("/api/get")
def api_get_thr():
    thrid = request.args.get("thrID","").replace("/","").replace("..","")
    thr = load(open(f"./BBS/{thrid}.json", "r", encoding="utf-8"))

    out = []
    
    for i, d in enumerate(thr["dat"]):
        if thr["dat"][0]["id"] == d["id"]:
            out.append(f"<dl><dt><a onclick='addanker({i + 1})'>{i + 1}</a>:<b class='k_name'>{d['name']}</b>, {d['date']}, <b class='t_title'>ID:{d['id']}</b></dt><dd>{text_replace(d['text'])}</dd></dl>")
        else:
            out.append(f"<dl><dt><a onclick='addanker({i + 1})'>{i + 1}</a>:<b class='k_name'>{d['name']}</b>, {d['date']}, ID:{d['id']}</dt><dd>{text_replace(d['text'])}</dd></dl>")
    
    return f"<h1 class='t_title'>{thr['title']}</h1>\n"+"\n".join(out)

@app.route("/api/gtitle")
def api_get_thr_title():
    thrid = request.args.get("thrID","").replace("/","").replace("..","")
    thr = load(open(f"./BBS/{thrid}.json", "r", encoding="utf-8"))

    return thr['title']



@app.route("/api/post-thread", methods=["POST"])
def api_post_thr_mk():
    thrid = str(uuid4())
    name = request.form.get("name","名無しさん").replace(">","&gt;").replace("<","&lt;")
    session["Name"] = name
    text = request.form.get("text","NoneType").replace(">","&gt;").replace("<","&lt;")
    title = request.form.get("title","[私はタイトルを入れられない馬鹿です]").replace(">","&gt;").replace("<","&lt;")

    if name == "":
        name = "OSVの名無しさん"

    if title == "":
        title = "[私はタイトルを入れられない馬鹿です]"


    id_ = session.get("ID","???")

    text, name, id_ = post_replace(text, name, id_, "root")

    thr = {}
    thr["title"] = title
    thr["dat"] = [
        {
            "name": name,
            "date": str(datetime.now()),
            "id": id_,
            "text": text 
        }
    ]
    dump(thr, open(f"./BBS/{thrid}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
    return redirect("/thread/"+thrid)

@app.route("/fupload")
def page_fupload():
    return f_open("./HTML/FileUP.html")

@app.route("/api/FU", methods=["POST"])
def api_FileUpload():
    file = request.files["file"]
    fname = file.filename.split(".")
    kak = fname[len(fname) - 1]

    fid = str(uuid4())

    file.save(f"./File/{fid}.{kak}")
    return redirect(f"/File/{fid}.{kak}")

@app.route("/File/<fname>")
def page_file(fname):
    return send_file(f"./File/{fname}")

app.run("::",80, False)