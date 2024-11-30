from flask import Flask, render_template
from pymongo import MongoClient
from routes.productos import productos_bp
from routes.carritos import carritos_bp  # Importa carritos antes de registrar el Blueprint

app = Flask(__name__)

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['tienda_ropa_alpaca']

# Registrar los Blueprints
app.register_blueprint(productos_bp)
app.register_blueprint(carritos_bp)  # Registra carritos después de productos

@app.route("/")
def index():
    categorias = list(db.categorias.find())
    return render_template("index.html", categorias=categorias)

@app.route("/productos/<categoria_id>")
def productos(categoria_id):
    productos = list(db.productos.find({"categoria": categoria_id}))
    return render_template("productos.html", productos=productos)

@app.route("/test")
def test():
    return "¡Flask está funcionando!"

@app.route("/carrito/<usuario>")
def ver_carrito(usuario):
    carrito = db.carritos.find_one({"usuario": usuario})
    if not carrito:
        return jsonify({"mensaje": "El carrito no existe"}), 404
    return render_template("carrito.html", carrito=carrito, usuario=usuario)

@app.route('/carrito/<usuario>/quitar', methods=['POST'])
def quitar_producto(usuario):
    datos = request.form
    producto_id = datos["producto_id"]

    # Buscar el carrito del usuario
    carrito = db.carritos.find_one({"usuario": usuario})
    if not carrito:
        return jsonify({"mensaje": "El carrito no existe"}), 404

    # Eliminar el producto del carrito
    carrito["productos"] = [p for p in carrito["productos"] if p["producto_id"] != producto_id]

    # Actualizar el total
    carrito["total"] = sum(p.get("subtotal", 0) for p in carrito["productos"])
    db.carritos.update_one({"usuario": usuario}, {"$set": carrito})
    return redirect(url_for('carritos.ver_carrito', usuario=usuario))  # Redirigir al carrito actualizado


if __name__ == "__main__":
    app.run(debug=True)

