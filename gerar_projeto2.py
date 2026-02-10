import os, textwrap

BASE="sistema_carteirinha"

def w(p,c):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,"w",encoding="utf8").write(textwrap.dedent(c))

os.makedirs(BASE,exist_ok=True)

w(f"{BASE}/requirements.txt","""
flask
psd-tools
pillow
reportlab
""")

w(f"{BASE}/run.py","""
from flask import Flask
from app.routes import bp
app=Flask(__name__)
app.secret_key="dev"
app.register_blueprint(bp)
app.run(host="0.0.0.0",port=5000)
""")

w(f"{BASE}/app/routes.py","""
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
""")

w(f"{BASE}/app/psd_engine.py","""
from psd_tools import PSDImage
from PIL import Image,ImageDraw
from reportlab.pdfgen import canvas

def analisar_psd(p):
    psd=PSDImage.open(p)
    campos={}
    for l in psd.descendants():
        if l.is_text_layer():
            b=l.bbox
            campos[l.name]={"x":int(b.x1),"y":int(b.y1)}
    psd.composite().save("static/preview.png")
    return campos

def render_final(template,dados,foto):
    img=Image.open("static/preview.png").copy()
    d=ImageDraw.Draw(img)

    for c,p in template["campos"].items():
        d.text((p["x"],p["y"]),dados.get(c,""),fill="black")

    img.save("final.png")

    c=canvas.Canvas("final.pdf")
    c.drawImage("final.png",0,0,400,250)
    c.save()

    return open("final.pdf","rb").read()
""")

w(f"{BASE}/app/templates/admin.html","""
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
.box{position:absolute;border:2px solid red;cursor:move}
#wrap{position:relative}
</style>
</head>
<body class="p-3">

<h3>Configurar PSD</h3>

<form method="post" enctype="multipart/form-data">
<input type="file" name="psd" required>
<button class="btn btn-primary">Analisar</button>
</form>

<div id="wrap">
<img src="/static/preview.png" id="img">
{% for c,p in template.campos.items() %}
<div class="box" style="left:{{p.x}}px;top:{{p.y}}px" data-name="{{c}}">{{c}}</div>
{% endfor %}
</div>

<a href="/operacao" class="btn btn-success mt-3">Ir para operação</a>

<script>
document.querySelectorAll(".box").forEach(b=>{
 let oX,oY
 b.onmousedown=e=>{
  oX=e.offsetX;oY=e.offsetY
  document.onmousemove=m=>{
   b.style.left=(m.pageX-oX)+"px"
   b.style.top=(m.pageY-oY)+"px"
  }
  document.onmouseup=_=>{
   document.onmousemove=null
  }
 }
})
</script>

</body>
</html>
""")

w(f"{BASE}/app/templates/operacao.html","""
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-3">

<h3>Gerar carteirinha</h3>

<form method="post" enctype="multipart/form-data">
{% for c in template.campos %}
<input class="form-control mb-2" name="{{c}}" placeholder="{{c}}">
{% endfor %}
<input type="file" name="foto">
<button class="btn btn-primary mt-2">Gerar PDF</button>
</form>

</body>
</html>
""")

print("Sistema completo criado com editor visual!")
