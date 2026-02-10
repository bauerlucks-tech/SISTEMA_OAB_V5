
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
