from flask import Flask, render_template, redirect, url_for, request, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
from aplicacion.forms import FormCategoria, FormArticulo
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config.from_object(config)
Bootstrap(app)
db = SQLAlchemy(app)


@app.route('/')
@app.route('/categoria/<id>')
def inicio(id='0'):
    from aplicacion.models import Articulos, Categorias
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId=id)
    categorias = Categorias.query.all()
    return render_template("inicio.html", articulos=articulos,
                           categorias=categorias, categoria=categoria)


@app.route('/categorias')
def categorias():
    from aplicacion.models import Categorias
    categorias = Categorias.query.all()
    return render_template("categorias.html", categorias=categorias)


@app.route('/categorias/new', methods=["get", "post"])
def categorias_new():
    from aplicacion.models import Categorias
    form = FormCategoria(request.form)
    if form.validate_on_submit():
        cat = Categorias(nombre=form.nombre.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
    else:
        return render_template("categorias_new.html", form=form)


@app.route('/categorias/<id>/edit', methods=["get", "post"])
def categorias_edit(id):
    from aplicacion.models import Categorias
    cat = Categorias.query.get(id)
    if cat is None:
        abort(404)
    form = FormCategoria(request.form, obj=cat)
    if form.validate_on_submit():
        form.populate_obj(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
    return render_template("categorias_new.html", form=form)


@app.route('/articulos/new', methods=["get", "post"])
def articulos_new():
    from aplicacion.models import Articulos, Categorias
    form = FormArticulo()
    categorias = [(c.id, c.nombre) for c in Categorias.query.all()[1:]]
    form.CategoriaId.choices = categorias
    if form.validate_on_submit():
        try:
            f = form.photo.data
            nombre_fichero = secure_filename(f.filename)
            f.save(app.root_path + "/static/upload/" + nombre_fichero)
        except:
            nombre_fichero = ""
        art = Articulos()
        form.populate_obj(art)
        art.image = nombre_fichero
        db.session.add(art)
        db.session.commit()
        return redirect(url_for("inicio"))
    else:
        return render_template("articulos_new.html", form=form)


@app.route('/articulos/<id>/edit', methods=["get", "post"])
def articulos_edit(id):
    from aplicacion.models import Articulos, Categorias
    art = Articulos.query.get(id)
    if art is None:
        abort(404)
    form = FormArticulo(obj=art)
    categorias = [(c.id, c.nombre) for c in Categorias.query.all()[1:]]
    form.CategoriaId.choices = categorias
    if form.validate_on_submit():
        # Borramos la imagen anterior si hemos subido una nueva
        if form.photo.data:
            os.remove(app.root_path + "/static/upload/" + art.image)
            try:
                f = form.photo.data
                nombre_fichero = secure_filename(f.filename)
                f.save(app.root_path + "/static/upload/" + nombre_fichero)
            except:
                nombre_fichero = ""
        else:
            nombre_fichero = art.image
        form.populate_obj(art)
        art.image = nombre_fichero
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_new.html", form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="P??gina no encontrada..."), 404
