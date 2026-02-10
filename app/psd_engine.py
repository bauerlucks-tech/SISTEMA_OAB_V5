from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, PageBreak

TEMPLATE = {
    "frente": {"campos": {}, "foto": None},
    "verso": {"campos": {}, "foto": None}
}

def analisar_psd(path):
    psd = PSDImage.open(path)
    campos = {}

    for layer in psd.descendants():
        if layer.is_text_layer():
            box = layer.bbox
            campos[layer.name] = {
                "x": int(box.x1),
                "y": int(box.y1),
                "size": int(layer.text_data.font_size)
            }

    preview = psd.composite()
    preview.save(f"static/{path}.png")

    return campos


def render_face(face, dados, foto):
    base = Image.open(f"static/{face}.psd.png").copy()
    draw = ImageDraw.Draw(base)

    for nome, c in TEMPLATE[face]["campos"].items():
        draw.text((c["x"], c["y"]), dados.get(nome, ""), fill="black")

    if TEMPLATE[face]["foto"]:
        x,y,w,h = TEMPLATE[face]["foto"]
        f = Image.open(foto).resize((w,h))
        base.paste(f,(x,y))

    return base


def gerar_carteirinha(dados, foto_path):
    frente = render_face("frente", dados, foto_path)
    verso  = render_face("verso", dados, foto_path)

    frente.save("static/final_frente.png")
    verso.save("static/final_verso.png")

    pdf = SimpleDocTemplate("static/final.pdf")
    pdf.build([
        RLImage("static/final_frente.png", 400,250),
        PageBreak(),
        RLImage("static/final_verso.png", 400,250)
    ])

    return "static/final.pdf"
