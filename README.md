Este aplicativo es un sistema de gestión de clientes y pedidos desarrollado con Flask y SQLAlchemy. Está diseñado para un negocio que maneja menús y realiza entregas. Sus principales funcionalidades incluyen:

Gestión de clientes: Crear, leer, actualizar y eliminar registros de clientes.
Gestión de pedidos: Registrar pedidos, consultar el historial de pedidos, y actualizar el estado de los pedidos.
Cálculo de ventas totales: Mantiene un registro de las ventas totales.
Frontend estático: Integra un frontend estático que se sirve desde la carpeta build.
Gestión de datos: Incluye una opción para borrar todos los registros de clientes y pedidos.
Características principales:
Endpoints principales:
/api/clientes: Maneja la creación y actualización de clientes.
/api/pedidos: Permite consultar y actualizar pedidos.
/api/ventas: Calcula y devuelve las ventas totales.
/api/borrar_todo: Borra todos los registros en la base de datos.
Base de datos: Utiliza SQLAlchemy para interactuar con una base de datos relacional. Contiene dos modelos principales:
Cliente: Información personal del cliente.
Pedido: Detalles del pedido, incluyendo menú, cantidad de personas, estado, y montos de pago.
Lógica de negocio: Calcula los totales de pedidos basados en un catálogo de precios y permite pagos parciales.
Diagrama de Arquitectura
El diagrama a continuación describe la estructura del sistema:

plaintext
Copy code
+----------------------------------------------------+
|                        Usuario                     |
+----------------------------------------------------+
                  |                     ^
                  v                     |
+--------------------------------+     |
|          Frontend              |     | Estático (HTML/CSS/JS)
|  (Servido desde `/build`)      |     |
+--------------------------------+     |
                  |                     ^
                  v                     |
+---------------------------------------------+
|                 Flask API                   |
|  -----------------------------------------  |
|  Endpoints principales:                     |
|  - /api/clientes (CRUD de clientes)         |
|  - /api/pedidos (CRUD de pedidos)           |
|  - /api/ventas (Consulta de ventas totales) |
|  - /api/borrar_todo (Eliminar registros)    |
+---------------------------------------------+
                  |                                
                  v                                
+---------------------------------------------+
|         Base de Datos (SQLAlchemy)          |
|  -----------------------------------------  |
|  Tablas:                                    |
|  - Cliente                                  |
|     - id                                    |
|     - nombre                                |
|     - telefono                              |
|     - direccion                             |
|  - Pedido                                   |
|     - id                                    |
|     - cliente_id                            |
|     - menu                                  |
|     - cantidad_personas                     |
|     - total                                 |
|     - estado                                |
|     - hora_entrega                          |
|     - anticipo                              |
|     - restante                              |
+---------------------------------------------+
