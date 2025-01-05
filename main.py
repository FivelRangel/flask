from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, static_folder='build')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Toma el valor de DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    tipo_tamal = db.Column(db.String(50), nullable=False)  # Cambiado de `menu` a `tipo_tamal`
    cantidad_tamales = db.Column(db.Integer, nullable=False)  # Cambiado de `cantidad_personas`
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='Por entregar')
    hora_entrega = db.Column(db.String(50), nullable=False)
    anticipo = db.Column(db.Float, default=0.0, nullable=False)
    restante = db.Column(db.Float, nullable=False)


PRECIO_TAMAL = 15  # Precio por tamal en MXN

# Ventas totales
ventas_totales = 0

@app.route('/api/clientes', methods=['POST'])
def registrar_cliente_y_pedido():
    try:
        # Log inicial
        print("Inicio del endpoint /api/clientes [POST]")
        
        # Log de los datos recibidos
        data = request.json
        print(f"Datos recibidos: {data}")

        # Validar datos requeridos
required_fields = ['nombre', 'telefono', 'direccion', 'tipoTamal', 'cantidadPersonas', 'horaEntrega']
        for field in required_fields:
            if field not in data:
                error_message = f"Falta el campo requerido: {field}"
                print(f"Error: {error_message}")
                return jsonify({"error": error_message}), 400

        # Crear cliente
        nuevo_cliente = Cliente(
            nombre=data['nombre'],
            telefono=data['telefono'],
            direccion=data['direccion']
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        print(f"Cliente creado con ID: {nuevo_cliente.id}")

        # Calcular total, anticipo y restante
        total = PRECIO_TAMAL * data['cantidadPersonas']  
        anticipo = data.get('anticipo', 0)
        restante = total - anticipo
        print(f"Total calculado: {total}, Anticipo: {anticipo}, Restante: {restante}")

        # Crear pedido
        nuevo_pedido = Pedido(
            cliente_id=nuevo_cliente.id,
            tipo_tamal=data['tipoTamal'],  # Usando el campo correcto
            cantidad_personas=data['cantidadPersonas'],
            total=total,
            hora_entrega=data['horaEntrega'],
            anticipo=anticipo,
            restante=restante
        )
        db.session.add(nuevo_pedido)
        db.session.commit()
        print(f"Pedido creado con ID: {nuevo_pedido.id}")

        # Respuesta exitosa
        print("Cliente y pedido registrados exitosamente.")
        return jsonify({
            "message": "Cliente y pedido registrados",
            "total": total,
            "anticipo": anticipo,
            "restante": restante
        }), 201

    except Exception as e:
        # Log de errores
        print(f"Error en /api/clientes [POST]: {str(e)}")
        return jsonify({"error": "Error interno del servidor.", "details": str(e)}), 500


@app.route('/api/pedidos/<int:id>', methods=['PATCH'])
def cambiar_estado_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    data = request.json

    if data['estado'] not in ['Por entregar', 'Entregado']:
        return jsonify({"error": "Estado no válido"}), 400

    if pedido.estado != 'Entregado' and data['estado'] == 'Entregado':
        global ventas_totales
        ventas_totales += pedido.total

    pedido.estado = data['estado']
    db.session.commit()

    return jsonify({"message": "Estado actualizado"}), 200

@app.route('/api/pedidos', methods=['GET'])
def obtener_clientes_y_pedidos():
    pedidos = Pedido.query.all()
    resultado = []

    for pedido in pedidos:
        resultado.append({
            "cliente": {
                "id": pedido.cliente.id,
                "nombre": pedido.cliente.nombre,
                "telefono": pedido.cliente.telefono,
                "direccion": pedido.cliente.direccion
            },
            "pedido": {
                "id": pedido.id,
                "tipo_tamal": pedido.tipo_tamal,  # Cambiado de `menu`
                "cantidad_tamales": pedido.cantidad_tamales,  # Cambiado de `cantidad_personas`
                "total": pedido.total,
                "estado": pedido.estado,
                "hora_entrega": pedido.hora_entrega,
                "anticipo": pedido.anticipo,
                "restante": pedido.restante
            }
        })

    return jsonify(resultado), 200


@app.route('/api/clientes/<int:id>', methods=['GET'])
def obtener_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    pedidos = Pedido.query.filter_by(cliente_id=id).all()

    return jsonify({
        "cliente": {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
            "direccion": cliente.direccion
        },
        "pedidos": [ {
            "id": pedido.id,
            "tipo_tamal": pedido.tipo_tamal,  # Cambiado de `menu`
            "cantidad_tamales": pedido.cantidad_tamales,  # Cambiado de `cantidad_personas`
            "total": pedido.total,
            "estado": pedido.estado,
            "hora_entrega": pedido.hora_entrega,
            "anticipo": pedido.anticipo,
            "restante": pedido.restante
        } for pedido in pedidos]
    }), 200


@app.route('/api/clientes/<int:id>', methods=['PUT'])
def actualizar_cliente_y_pedidos(id):
    cliente = Cliente.query.get_or_404(id)
    data = request.json

    # Actualizar datos del cliente
    cliente.nombre = data.get('nombre', cliente.nombre)
    cliente.telefono = data.get('telefono', cliente.telefono)
    cliente.direccion = data.get('direccion', cliente.direccion)

    # Actualizar pedidos
    for pedido_data in data.get('pedidos', []):
        pedido = Pedido.query.get_or_404(pedido_data['id'])
        pedido.menu = pedido_data.get('menu', pedido.menu)
        pedido.cantidad_personas = pedido_data.get('cantidad_personas', pedido.cantidad_personas)
        pedido.total = pedido_data.get('total', pedido.total)
        pedido.anticipo = pedido_data.get('anticipo', pedido.anticipo)
        pedido.restante = pedido_data.get('restante', pedido.restante)
        pedido.hora_entrega = pedido_data.get('hora_entrega', pedido.hora_entrega)
        pedido.estado = pedido_data.get('estado', pedido.estado)

    db.session.commit()
    return jsonify({"message": "Cliente y pedidos actualizados correctamente"}), 200

@app.route('/api/ventas', methods=['GET'])
def calcular_ventas_totales():
    return jsonify({"ventasTotales": ventas_totales}), 200

# Servir el frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/borrar_todo', methods=['DELETE'])
def borrar_todo():
    try:
        # Eliminar todos los pedidos
        Pedido.query.delete()
        # Eliminar todos los clientes
        Cliente.query.delete()
        # Confirmar los cambios en la base de datos
        db.session.commit()
        return jsonify({"message": "Todos los registros han sido eliminados"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": "Error al intentar borrar registros", "details": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
