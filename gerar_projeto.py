import os, textwrap

BASE = "sistema_carteirinha"

def criar(path, conteudo=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(conteudo))

os.makedirs(BASE, exist_ok=True)

criar(f"{BASE}/requirements.txt", """
flask
psd-tools
pillow
reportlab
""")

criar(f"{BASE}/run.py", """
from flask import Flask
from app.routes import bp

app = Flask(__name__)
app.secret_key = "dev"

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
""")

criar(f"{BASE}/app/routes.py", """
from flask import Blueprint, render_template, request, redirect, send_file
from .psd_engine import analisar_psd, gerar_carteirinha

bp = Blueprint("bp", __name__)

template_data = {}

@bp.route("/", methods=["GET","POST"])
def admin():
    global template_data
    if request.method == "POST":
        psd = request.files["psd"]
        psd.save("template.psd")
        template_data = analisar_psd("template.psd")
    return render_template("admin.html", campos=template_data)

@bp.route("/operacao", methods=["GET","POST"])
def operacao():
    if request.method == "POST":
        return gerar_carteirinha(template_data, request.form, request.files["foto"])
    return render_template("operacao.html", campos=template_data)
""")

criar(f"{BASE}/app/psd_engine.py", """
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import card
from reportlab.pdfgen import canvas

def analisar_psd(path):
    psd = PSDImage.open(path)
    campos = {}
    for layer in psd.descendants():
        if layer.is_text_layer():
            box = layer.bbox
            campos[layer.name] = {
                "x": int(box.x1),
                "y": int(box.y1)
            }
    return campos

def gerar_carteirinha(campos, dados, foto):
    img = Image.new("RGB", (800,500), "white")
    draw = ImageDraw.Draw(img)

    for campo, pos in campos.items():
        draw.text((pos["x"], pos["y"]), dados.get(campo,""), fill="black")

    img.save("carteirinha.png")

    c = canvas.Canvas("carteirinha.pdf")
    c.drawImage("carteirinha.png", 0, 0, width=400, height=250)
    c.save()

    return send_file("carteirinha.pdf", as_attachment=True)
""")

criar(f"{BASE}/app/templates/admin.html", """
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
<h3>Admin PSD</h3>
<form method="post" enctype="multipart/form-data">
<input type="file" name="psd" required>
<button class="btn btn-primary">Analisar PSD</button>
</form>

<ul>
{% for c in campos %}
<li>{{c}}</li>
{% endfor %}
</ul>

<a href="/operacao">Ir para operação</a>
</body>
</html>
""")

criar(f"{BASE}/app/templates/operacao.html", """
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
<h3>Gerar carteirinha</h3>
<form method="post" enctype="multipart/form-data">
{% for c in campos %}
<input class="form-control mb-2" name="{{c}}" placeholder="{{c}}">
{% endfor %}
<input type="file" name="foto" class="mb-2">
<button class="btn btn-success">Gerar</button>
</form>
</body>
</html>
""")

print("Sistema criado em:", BASE)
