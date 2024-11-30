from flask import Blueprint, request, jsonify
from models.db import db

productos_bp = Blueprint('productos', __name__)

# Obtener todos los productos
@productos_bp.route('/productos', methods=['GET'])
def obtener_productos():
    productos = list(db.productos.find())
    for producto in productos:
        producto["_id"] = str(producto["_id"])  # Convertir ObjectId a string
    return jsonify(productos)

# Crear un producto
@productos_bp.route('/productos', methods=['POST'])
def crear_producto():
    datos = request.json
    db.productos.insert_one(datos)
    return jsonify({"mensaje": "Producto creado exitosamente"}), 201

# Actualizar un producto
@productos_bp.route('/productos/<id>', methods=['PUT'])
def actualizar_producto(id):
    datos = request.json
    db.productos.update_one({"_id": id}, {"$set": datos})
    return jsonify({"mensaje": "Producto actualizado exitosamente"})

# Eliminar un producto
@productos_bp.route('/productos/<id>', methods=['DELETE'])
def eliminar_producto(id):
    db.productos.delete_one({"_id": id})
    return jsonify({"mensaje": "Producto eliminado exitosamente"})
