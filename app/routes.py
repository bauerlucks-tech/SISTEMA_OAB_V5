
from flask import Blueprint,render_template,request,redirect,send_file
from .psd_engine import analisar_psd,render_final
import json

bp=Blueprint("bp",__name__)
template={"campos":{}, "foto":{}}

@bp.route("/",methods=["GET","POST"])
def admin():
    global template
    if request.method=="POST":
        f=request.files["psd"]
        f.save("base.psd")
        template["campos"]=analisar_psd("base.psd")
    return render_template("admin.html",template=template)

@bp.route("/salvar",methods=["POST"])
def salvar():
    global template
    template=json.loads(request.data)
    return "ok"

@bp.route("/operacao",methods=["GET","POST"])
def operacao():
    if request.method=="POST":
        return render_final(template,request.form,request.files["foto"])
    return render_template("operacao.html",template=template)
