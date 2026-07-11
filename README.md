# API E-commerce con Django REST Framework

Proyecto académico de una API REST para comercio electrónico, desarrollado con Django REST Framework.  
Permite gestionar usuarios, catálogo, variantes, carrito de compras, órdenes, cupones, pagos simulados, reseñas y facturas en PDF.

## Tecnologías utilizadas

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Docker y Docker Compose
- JWT con SimpleJWT
- Swagger/OpenAPI con drf-spectacular
- ReportLab para facturas PDF
- Postman para pruebas manuales

## Funcionalidades principales

- Registro e inicio de sesión de usuarios.
- Autenticación mediante JWT.
- Gestión de categorías, productos y variantes.
- Control de stock por talla, color o presentación.
- Carrito de compras por usuario.
- Checkout y creación de órdenes.
- Cupones porcentuales y de monto fijo.
- Pago simulado.
- Descuento de stock al confirmar el pago.
- Historial y detalle de órdenes.
- Estados de orden: `pending`, `paid`, `cancelled`, `shipped` y `delivered`.
- Reseñas y calificaciones de 1 a 5.
- Facturas en formato PDF.
- Permisos diferenciados para clientes y administradores.
- Carga automática de datos iniciales.

## Estructura del proyecto

```text
Proyecto_E-commerce/
├── cart/
├── catalog/
├── config/
├── cupones/
├── data/
├── facturas/
├── orders/
├── resenas/
├── users/
├── .dockerignore
├── .gitignore
├── compose.yaml
├── Dockerfile
├── manage.py
└── requirements.txt
```

## Requisitos previos

Antes de ejecutar el proyecto, se debe tener instalado:

- Git
- Docker Desktop
- Docker Compose

## Variables de entorno

Crear un archivo llamado `.env` en la raíz del proyecto.

Ejemplo:

```env
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_password
DB_HOST=db
DB_PORT=5432
```

El archivo `.env` no debe subirse al repositorio.

## Instalación con Docker

### 1. Clonar el repositorio

```bash
git clone https://github.com/hOshi123456/Proyecto_E-commerce.git
cd Proyecto_E-commerce
```

### 2. Crear el archivo `.env`

Usar como referencia el ejemplo de la sección anterior.

### 3. Construir e iniciar los contenedores

```bash
docker compose up --build -d
```

### 4. Verificar los servicios

```bash
docker compose ps
```

Deben aparecer los servicios `web` y `db`.

### 5. Aplicar migraciones

```bash
docker compose exec web python manage.py migrate
```

### 6. Crear un superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

### 7. Cargar datos iniciales

```bash
docker compose exec web python manage.py cargar_datos_iniciales
```

Este comando crea o actualiza:

- Un cliente de demostración.
- Categorías.
- Productos.
- Variantes con stock.
- Cupones.

Puede ejecutarse varias veces sin duplicar los registros principales.

## Accesos principales

### Swagger

```text
http://127.0.0.1:8000/api/docs/
```

### Django Admin

```text
http://127.0.0.1:8000/admin/
```

### Esquema OpenAPI

```text
http://127.0.0.1:8000/api/schema/
```

## Cliente de demostración

```text
Usuario: cliente_demo
Contraseña: Cliente2026
```

Estas credenciales son exclusivamente para pruebas académicas y no deben utilizarse en producción.

## Endpoints principales

### Usuarios

```text
POST /api/users/register/
POST /api/users/login/
POST /api/users/token/refresh/
GET  /api/users/me/
```

### Catálogo

```text
GET    /api/catalog/categories/
POST   /api/catalog/categories/
GET    /api/catalog/products/
POST   /api/catalog/products/
GET    /api/catalog/variants/
POST   /api/catalog/variants/
```

Las operaciones de escritura del catálogo requieren permisos administrativos.

### Carrito

```text
GET    /api/cart/
POST   /api/cart/add/
PATCH  /api/cart/items/{item_id}/
DELETE /api/cart/items/{item_id}/remove/
DELETE /api/cart/clear/
```

### Órdenes

```text
GET  /api/orders/
POST /api/orders/checkout/
GET  /api/orders/{order_id}/
POST /api/orders/{order_id}/pay/
```

### Administración de órdenes

```text
GET   /api/orders/admin/
PATCH /api/orders/admin/{order_id}/status/
```

Transiciones permitidas:

```text
pending → cancelled
paid → shipped
shipped → delivered
```

### Cupones

```text
POST /api/cupones/validate/
```

Los administradores también pueden crear, modificar y eliminar cupones.

### Reseñas

```text
GET    /api/resenas/
POST   /api/resenas/
PATCH  /api/resenas/{id}/
DELETE /api/resenas/{id}/
```

Un usuario solo puede reseñar un producto que haya comprado en una orden pagada.

### Facturas

```text
GET /api/facturas/orders/{order_id}/pdf/
```

La factura solo puede generarse para órdenes pagadas.

## Flujo de prueba recomendado

1. Iniciar sesión.
2. Copiar el token `access`.
3. Configurarlo como Bearer Token.
4. Consultar variantes.
5. Agregar una variante al carrito.
6. Consultar el carrito.
7. Realizar checkout con o sin cupón.
8. Simular el pago.
9. Verificar la reducción del stock.
10. Generar la factura PDF.
11. Crear una reseña del producto comprado.

## Ejemplo de login

```json
{
  "username": "cliente_demo",
  "password": "Cliente2026"
}
```

## Ejemplo para agregar al carrito

```json
{
  "variant": 1,
  "quantity": 2
}
```

## Ejemplo de checkout con cupón

```json
{
  "cupon_code": "DESC10"
}
```

## Pago simulado

La petición de pago no necesita cuerpo JSON.

```text
POST /api/orders/{order_id}/pay/
```

Debe utilizarse el ID numérico real de una orden pendiente.

Ejemplo:

```text
POST /api/orders/7/pay/
```

## Comandos útiles

### Iniciar el proyecto

```bash
docker compose up -d
```

### Detener el proyecto

```bash
docker compose down
```

### Ver logs de Django

```bash
docker compose logs -f web
```

### Ver logs de PostgreSQL

```bash
docker compose logs -f db
```

### Verificar Django

```bash
docker compose exec web python manage.py check
```

### Validar Swagger

```bash
docker compose exec web python manage.py spectacular --file schema.yml --validate
```

### Abrir una consola de Django

```bash
docker compose exec web python manage.py shell
```

## Persistencia de datos

PostgreSQL utiliza un volumen de Docker para conservar la información.

No se recomienda ejecutar:

```bash
docker compose down -v
```

Ese comando elimina los volúmenes y borra la base de datos del entorno Docker.

## Estado del proyecto

El proyecto incluye el flujo principal de un e-commerce:

```text
usuario
→ catálogo
→ variante
→ carrito
→ checkout
→ cupón
→ orden pendiente
→ pago
→ descuento de stock
→ factura
→ reseña
```

La integración con una pasarela de pago real puede incorporarse en una versión futura.

## Seguridad

- Las credenciales y claves privadas deben almacenarse en `.env`.
- Los tokens JWT no deben compartirse.
- `DEBUG` debe desactivarse antes de desplegar en producción.
- Las credenciales de demostración no deben utilizarse en un entorno real.

## Autores

Marian Romero Aliendre.

## Licencia

Uso académico y educativo.
