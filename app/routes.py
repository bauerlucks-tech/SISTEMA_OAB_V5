@bp.route("/salvar_foto/<face>", methods=["POST"])
def salvar_foto(face):
    TEMPLATE[face]["foto"] = request.json
    return "ok"
