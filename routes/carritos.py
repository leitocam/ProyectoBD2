from flask import Blueprint, request, jsonify
from models.db import db

carritos_bp = Blueprint('carritos', __name__)

# Crear un carrito (si no existe para el usuario)
@carritos_bp.route('/carrito/<usuario>', methods=['POST'])
def crear_carrito(usuario):
    carrito = db.carritos.find_one({"usuario": usuario})
    if carrito:
        return jsonify({"mensaje": "El carrito ya existe"}), 400
    nuevo_carrito = {
        "usuario": usuario,
        "productos": [],
        "total": 0.00
    }
    db.carritos.insert_one(nuevo_carrito)
    return jsonify({"mensaje": "Carrito creado exitosamente"}), 201

# Añadir un producto al carrito
@carritos_bp.route('/carrito/<usuario>/agregar', methods=['POST'])
def agregar_producto(usuario):
    datos = request.json
    producto_id = datos["producto_id"]
    cantidad = datos["cantidad"]

    # Obtener el producto desde la colección de productos
    producto = db.productos.find_one({"_id": producto_id})
    if not producto:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

    # Buscar el carrito del usuario
    carrito = db.carritos.find_one({"usuario": usuario})
    if not carrito:
        return jsonify({"mensaje": "El carrito no existe"}), 404

    # Usar el campo 'precio' en lugar de 'precio_unitario'
    precio_unitario = producto.get("precio", 0)  # Usamos 'precio' como está en la base de datos
    if precio_unitario == 0:
        return jsonify({"mensaje": "Producto sin precio disponible"}), 400

    # Verificar si el producto ya está en el carrito
    for p in carrito["productos"]:
        if p["producto_id"] == producto_id:
            p["cantidad"] += cantidad
            # Asegurarse de que el 'subtotal' esté presente y actualizado
            p["subtotal"] = p["cantidad"] * precio_unitario
            break
    else:
        # Si el producto no está, lo agregamos con el campo 'subtotal'
        carrito["productos"].append({
            "producto_id": producto_id,
            "nombre": producto["nombre"],
            "cantidad": cantidad,
            "precio": precio_unitario,  # Guardamos el precio
            "subtotal": cantidad * precio_unitario  # Calculamos y agregamos el subtotal
        })

    # Actualizar el total del carrito
    carrito["total"] = sum(p.get("subtotal", 0) for p in carrito["productos"])  # Usar .get() para evitar KeyError
    db.carritos.update_one({"usuario": usuario}, {"$set": carrito})
    return jsonify({"mensaje": "Producto añadido al carrito"}), 200

# Ver el carrito
@carritos_bp.route('/carrito/<usuario>', methods=['GET'])
def ver_carrito(usuario):
    carrito = db.carritos.find_one({"usuario": usuario})
    if not carrito:
        return jsonify({"mensaje": "El carrito no existe"}), 404

    # Convertir ObjectId a string si es necesario
    for producto in carrito["productos"]:
        if "_id" in producto:
            producto["_id"] = str(producto["_id"])  # Convertir _id de ObjectId a string

    if "_id" in carrito:
        carrito["_id"] = str(carrito["_id"])  # Si necesitas convertir el _id del carrito también

    return jsonify(carrito)


# Quitar un producto del carrito
@carritos_bp.route('/carrito/<usuario>/quitar', methods=['DELETE'])
def quitar_producto(usuario):
    datos = request.json
    producto_id = datos["producto_id"]

    # Buscar el carrito del usuario
    carrito = db.carritos.find_one({"usuario": usuario})
    if not carrito:
        return jsonify({"mensaje": "El carrito no existe"}), 404

    # Eliminar el producto del carrito
    carrito["productos"] = [p for p in carrito["productos"] if p["producto_id"] != producto_id]

    # Actualizar el total
    carrito["total"] = sum(p.get("subtotal", 0) for p in carrito["productos"])  # Usar .get() para evitar KeyError
    db.carritos.update_one({"usuario": usuario}, {"$set": carrito})
    return jsonify({"mensaje": "Producto eliminado del carrito"}), 200

# Vaciar el carrito
@carritos_bp.route('/carrito/<usuario>/vaciar', methods=['DELETE'])
def vaciar_carrito(usuario):
    db.carritos.update_one({"usuario": usuario}, {"$set": {"productos": [], "total": 0.00}})
    return jsonify({"mensaje": "Carrito vaciado"}), 200