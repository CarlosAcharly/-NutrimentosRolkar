from flask import Flask, render_template, url_for, redirect, request, flash
import os
import uuid 
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect 

from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from Models.ModelUser import ModelUser
from Models.entities.user import User 

from functools import wraps
from flask import abort
from flask_login import current_user

app= Flask(__name__)
csrf= CSRFProtect()

#conexion con base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(host='localhost',
                                dbname='nutrimentosRolkar',
                               user=os.environ['DB_Usuario'],
                                password=os.environ['DB_Contrasenia'])                   
        return conn
    except psycopg2.Error as error:
        print(f"Error al conectar la base de datos:{error}")
        return None

Login_manager_app=LoginManager(app)

@Login_manager_app.user_loader
def load_user(idusuarios):
    return ModelUser.get_by_id(get_db_connection(),idusuarios)

def my_random_string(string_length=10):
    """Regresa una cadena aleatoria de la longitud de string_length."""
    random = str(uuid.uuid4()) # Conviente el formato UUID a una cadena de Python.
    random = random.upper() # Hace todos los caracteres mayusculas.
    random = random.replace("-","") # remueve el separador UUID '-'.
    return random[0:string_length] # regresa la cadena aleatoria.

#print(my_random_string(10)) # Por ejemplo, 9BC871E354

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ruta_alumnos=app.config['UPLOAD_FOLDER']='./app/static/img/uploads/alumnos/'
ruta_profesores=app.config['UPLOAD_FOLDER']='./app/static/img/uploads/profesores/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_username(username):
    # Define el patrón de la expresión regular para letras y números sin espacios ni caracteres especiales
    pattern = re.compile(r'^[a-zA-Z0-9]+$')
    # Comprueba si el nombre de usuario coincide con el patrón
    if pattern.match(username):
        return True
    else:
        return False

def listar_categorias():
    conn = get_db_connection() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM categorias ORDER BY id_categoria ASC;')
    categorias = cur.fetchall()
    cur.close()
    conn.close()
    return categorias

def listar_proveedores():
    conn = get_db_connection() 
    cur = conn.cursor()
    cur.execute('SELECT * FROM proveedor ORDER BY id_proveedor ASC;')
    proveedores = cur.fetchall()
    cur.close()
    conn.close()
    return proveedores

app.secret_key='mysecretkey'

@app.route("/")
@login_required
def inicioSesion():
    return render_template('login.html')
#-------------------DECORADORES----------------------------------

'''def role_required(rol):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.rol not in rol:
                abort(403)  # Prohibido
            return f(*args, **kwargs)
        return decorated_function
    return decorator'''

#---------------------PAGINADOR-------------
def paginador(sql_count,sql_lim,in_page,per_pages):
    page = request.args.get('page', in_page, type=int)
    per_page = request.args.get('per_page', per_pages, type=int)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(sql_count)
    total_items = cursor.fetchone()['count']

    cursor.execute(sql_lim, (per_page, offset))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (total_items + per_page - 1) // per_page

    return items, page, per_page, total_items, total_pages

#----------------------PRODUCTOS------------------------------------

@app.route("/dashboard_productos")
@login_required
def dashboardProductos():
    if current_user.tipo == 'admin':

        titulo = "Productos"
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 2, type=int)
        search_query = request.args.get('search', '', type=str)

        offset = (page - 1) * per_page

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Obtener el número total de productos que coinciden con la búsqueda
        cur.execute('SELECT COUNT(*) FROM vista_productos WHERE nombre_producto ILIKE %s OR marca ILIKE %s', 
                    (f'%{search_query}%', f'%{search_query}%'))
        total_items = cur.fetchone()['count']

        # Obtener los productos con límite, offset y búsqueda
        cur.execute('SELECT * FROM vista_productos WHERE nombre_producto ILIKE %s OR marca ILIKE %s LIMIT %s OFFSET %s',
                    (f'%{search_query}%', f'%{search_query}%', per_page, offset))
        productos = cur.fetchall()

        cur.close()
        conn.close()

        total_pages = (total_items + per_page - 1) // per_page

        return render_template(
            'dashboardProductos.html',
            titulo=titulo,
            productos=productos,
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            search_query=search_query
        )
    elif current_user.tipo == 'cajero':
        return redirect(url_for('cajeroVentas'))
    else:
        return redirect(url_for('login'))

@app.route("/productos_nuevo")
@login_required
def productosNuevo():
    return render_template('productosNuevo.html', categorias=listar_categorias(),proveedores=listar_proveedores())


@app.route('/dashboard/productos/crear', methods=('GET', 'POST'))
@login_required
def productosCrear():
    if request.method == 'POST':
        id_producto=request.form['id_producto']
        nombre = request.form['nombre']
        marca = request.form['marca']
        precio = request.form['precio']
        fecha_caducidad = request.form['fecha_caducidad']
        proveedor = request.form['id_proveedor']
        categoria = request.form['id_categoria']
        

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO productos (id_producto, nombre, marca, precio, fecha_cad, fk_proveedor, fk_categoria)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (id_producto, nombre, marca, precio,fecha_caducidad, proveedor, categoria))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Producto agregado exitosamente!')

        return redirect(url_for('dashboardProductos'))

    return redirect(url_for('productosNuevo'))

@app.route("/productos_categoria")
@login_required
def productosCategoria():
    return render_template('productosCategoria.html')

@app.route("/productos_editar/<string:id>")
@login_required
def productosEditar(id):
    titulo = "Editar Producto"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM productos WHERE id_producto={0}'.format(id))
    producto=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('productosEditar.html', titulo=titulo, producto=producto[0], categorias=listar_categorias(), proveedores=listar_proveedores())

@app.route('/dashboard/productos/actualizar/<string:id>', methods=['POST'])
@login_required
def productosActualizar(id):
    if request.method == 'POST':
        id_producto=request.form['id_producto']
        nombre = request.form['nombre']
        marca = request.form['marca']
        precio = request.form['precio']
       # categoria = request.form['categoria']
        fecha_caducidad = request.form['fecha_caducidad']
    
    conn = get_db_connection()
    cur = conn.cursor()
    sql="UPDATE productos SET nombre=%s, marca=%s, precio=%s, fecha_cad=%s WHERE id_producto=%s"        
    valores=(nombre, marca, precio, fecha_caducidad, id_producto)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
        
    flash('¡Producto actualizado exitosamente!')

    return redirect(url_for('dashboardProductos'))



@app.route('/dashboard/productos/eliminar/<string:id>')
@login_required
def productoEliminar(id):
    #activo = False
    #editado = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM productos WHERE id_producto={0}".format(id)
    #sql="UPDATE productos SET activo=%s WHERE id_producto=%s"
    valores=(id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Producto eliminado correctamente!')
    return redirect(url_for('dashboardProductos'))

@app.route('/dashboard/alumnos/eliminar/foto/<string:foto>/<string:id>')
@login_required
def alumnos_eliminar_foto(foto,id):
    if current_user.tipo == True:
        foto_anterior = os.path.join(ruta_alumnos,foto)
        editado = datetime.now()
        conn = get_db_connection()
        cur = conn.cursor()
        #sql="DELETE FROM alumnos WHERE id_alumno={0}".format(id)
        sql="UPDATE productos SET imagen=%s, editado=%s WHERE id_alumno=%s"
        valores=("",editado,id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()
        #Eliminar foto de perfil antigua
        print(foto_anterior)
        if foto != "":
            if os.path.exists(foto_anterior):
                os.remove(foto_anterior)
                flash('¡Foto eliminada correctamente!')
                return redirect(url_for('alumnos_editar', id=id))
        else:
            flash('Error: ¡No se puede ejecutar esta acción!')
            return redirect(url_for('alumnos_editar', id=id))
    else:
        return redirect(url_for('alumnos_dashboard'))

@app.route("/productos_detalles/<string:id>")
@login_required
def productosDetalles(id):
    titulo="Detalles Producto"
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM productos WHERE id_producto = {0}'.format(id))
    producto=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    #hora_actual=datetime.now()
    return render_template('productosDetalles.html', titulo=titulo, producto=producto[0])

#-----------------------PROVEEDORES-----------------------------------------------------
@app.route("/dashboard_proveedores")
@login_required
def dashboardProveedores():
    
    if current_user.tipo == 'admin':
        titulo = "Proveedores"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM proveedor;')
        proveedores = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('dashboardProveedores.html', titulo=titulo, proveedores=proveedores)
    else:
        return redirect(url_for('login'))

@app.route("/proveedor_nuevo")
@login_required
def proveedorNuevo():
    return render_template('proveedoresNuevo.html')

@app.route('/dashboard/proveedores/crear', methods=('GET', 'POST'))
@login_required
def proveedoresCrear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        marca = request.form['marca']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']
        cp = request.form['cp']
        id_proveedor=request.form['id_proveedor']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO proveedor (id_proveedor, nombre, ape_pat, ape_mat, marca, telefono, direccion, correo, cp)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (id_proveedor, nombre, paterno, materno, marca, telefono, direccion, correo, cp))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Proveedor agregado exitosamente!')

        return redirect(url_for('dashboardProveedores'))

    return redirect(url_for('proveedoresNuevo'))

@app.route("/proveedores_editar/<string:id>")
@login_required
def proveedoresEditar(id):
    titulo = "Editar Proveedor"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM proveedor WHERE id_proveedor={0}'.format(id))
    proveedores=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('proveedoresEditar.html', titulo=titulo, proveedor=proveedores[0])

@app.route('/dashboard/proveedores/actualizar/<string:id>', methods=['POST'])
@login_required
def proveedoresActualizar(id):
    if request.method == 'POST':
        id_proveedor=request.form['id_proveedor']
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        marca = request.form['marca']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']
        cp = request.form['cp']


        conn = get_db_connection()
        cur = conn.cursor()
        sql="UPDATE proveedor SET nombre=%s, ape_pat=%s, ape_mat=%s, marca=%s,  telefono=%s, direccion=%s, correo=%s, cp=%s WHERE id_proveedor=%s"        
        valores=( nombre, paterno, materno, marca, telefono, direccion, correo, cp, id_proveedor)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Proveedor actualizado exitosamente!')

        return redirect(url_for('dashboardProveedores'))
    
@app.route("/proveedores_detalles/<string:id>")
@login_required
def proveedoresDetalles(id):
    titulo="Detalles proveedor"
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM proveedor WHERE id_proveedor = {0}'.format(id))
    proveedor=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('proveedoresDetalles.html', titulo=titulo, proveedor=proveedor[0])

@app.route('/dashboard/proveedores/eliminar/<string:id>')
@login_required
def proveedorEliminar(id):
    #activo = False
    #editado = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM proveedor WHERE id_proveedor={0}".format(id)
    #sql="UPDATE productos SET activo=%s WHERE id_producto=%s"
    valores=(id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Proveedor eliminado correctamente!')
    return redirect(url_for('dashboardProveedores'))

#--------------------USUARIOS---------------------------------------------------------------------
@app.route("/dashboard_usuarios")
@login_required
def dashboardUsuarios():
    if current_user.tipo == 'admin':

        titulo = "Usuarios"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios;')
        usuarios = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('dashboardUsuarios.html', titulo=titulo, usuarios=usuarios)
    else:
        return redirect(url_for('login'))
    
@app.route("/usuarios_nuevo")
@login_required
def usuariosNuevo():
    return render_template('usuariosNuevo.html')

@app.route('/dashboard/usuarios/crear', methods=('GET', 'POST'))
@login_required
def usuariosCrear():
    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        username = request.form['username']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        activo = request.form['activo']

        # Hashear la contraseña antes de guardarla en la base de datos
        password_hashed = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO usuarios (id_usuario, username, password, tipo_usuario, activo)'
                    'VALUES (%s, %s, %s, %s, %s)',
                    (id_usuario, username, password_hashed, tipo_usuario, activo))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Usuario agregado exitosamente!')

        return redirect(url_for('dashboardUsuarios'))

    return redirect(url_for('usuariosNuevo'))

@app.route("/usuarios_editar/<string:id>")
@login_required
def usuariosEditar(id):
    titulo = "Editar Usuario"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario={0}'.format(id))
    usuario=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('usuariosEditar.html', titulo=titulo, usuario=usuario[0])

@app.route('/dashboard/usuarios/actualizar/<string:id>', methods=['POST'])
@login_required
def usuariosActualizar(id):
    if request.method == 'POST':
        id_usuario=request.form['id_usuario']
        username = request.form['username']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        activo= request.form['activo']
        

        conn = get_db_connection()
        cur = conn.cursor()
        sql="UPDATE usuarios SET username=%s, password=%s, tipo_usuario=%s, activo=%s WHERE id_usuario=%s"        
        valores=( username, password, tipo_usuario, activo, id)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Usuario actualizado exitosamente!')

        return redirect(url_for('dashboardUsuarios'))
    
@app.route("/usuarios_detalles/<string:id>")
@login_required
def usuariosDetalles(id):
    titulo="Detalles usuario"
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id_usuario = {0}'.format(id))
    usuario=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    #hora_actual=datetime.now()
    return render_template('usuariosDetalles.html', titulo=titulo, usuario=usuario[0])

@app.route('/dashboard/usuarios/eliminar/<string:id>')
@login_required
def usuarioEliminar(id):
    #activo = False
    #editado = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM usuarios WHERE id_usuario={0}".format(id)
    #sql="UPDATE productos SET activo=%s WHERE id_producto=%s"
    valores=(id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Usuario eliminado correctamente!')
    return redirect(url_for('dashboardUsuarios'))

#-------------------------------Clientes-------------------------------------------
@app.route("/dashboard_clientes")
@login_required
def dashboardClientes():
    if current_user.tipo == 'admin':

        titulo = "Clientes"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM cliente;')
        clientes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('dashboardCliente.html', titulo=titulo, cliente=clientes)
    else:
        return redirect(url_for('login'))
    
@app.route("/cliente_nuevo")
@login_required
def clienteNuevo():
    return render_template('clienteNuevo.html')

@app.route('/dashboard/cliente/crear', methods=('GET', 'POST'))
@login_required
def clienteCrear():
    if request.method == 'POST':
        id_cliente=request.form['id_cliente']
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo = request.form['correo']
        cp = request.form['cp']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO cliente (id_cliente, nombre, ape_pat, ape_mat, direccion, telefono, correo, cp)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (id_cliente, nombre, paterno, materno,direccion, telefono, correo, cp))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Cliente agregado exitosamente!')

        return redirect(url_for('dashboardClientes'))

    return redirect(url_for('clienteNuevo'))

@app.route("/cliente_editar/<string:id>")
@login_required
def clienteEditar(id):
    titulo = "Editar Cliente"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM cliente WHERE id_cliente={0}'.format(id))
    cliente=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('clienteEditar.html', titulo=titulo, cliente=cliente[0])

@app.route('/dashboard/cliente/actualizar/<string:id>', methods=['POST'])
@login_required
def clienteActualizar(id):
    if request.method == 'POST':
        id_cliente=request.form['id_cliente']
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo = request.form['correo']
        cp = request.form['cp']
        


        conn = get_db_connection()
        cur = conn.cursor()
        sql="UPDATE cliente SET nombre=%s, ape_pat=%s, ape_mat=%s, direccion=%s, telefono=%s , correo=%s, cp=%s WHERE id_cliente=%s"        
        valores=( nombre, paterno, materno, direccion, telefono, correo, cp, id_cliente)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Cliente actualizado exitosamente!')

        return redirect(url_for('dashboardClientes'))
    
@app.route("/cliente_detalles/<string:id>")
@login_required
def clienteDetalles(id):
    titulo="Detalles cliente"
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM cliente WHERE id_cliente = {0}'.format(id))
    cliente=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    #hora_actual=datetime.now()
    return render_template('clienteDetalles.html', titulo=titulo, cliente=cliente[0])

@app.route('/dashboard/cliente/eliminar/<string:id>')
@login_required
def clienteEliminar(id):
    #activo = False
    #editado = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM cliente WHERE id_cliente={0}".format(id)
    #sql="UPDATE productos SET activo=%s WHERE id_producto=%s"
    valores=(id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Cliente eliminado correctamente!')
    return redirect(url_for('dashboardClientes'))

#-----------------Categoria--------------------------

@app.route("/dashboard_categoria")
@login_required
def dashboardCategorias():
    if current_user.tipo == 'admin':

        titulo = "Categorias"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM categorias;')
        categorias = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('dashboardCategorias.html', titulo=titulo, categorias=categorias)
    else:
        return redirect(url_for('login'))
        
@app.route("/categorias_nuevo")
@login_required
def categoriasNuevo():
    return render_template('categoriasNuevo.html')

@app.route('/dashboard/categorias/crear', methods=('GET', 'POST'))
@login_required
def categoriasCrear():
    if request.method == 'POST':
        id_categoria=request.form['id_categoria']
        especie = request.form['especie']
        tipo= request.form['tipo']
        presentacion= request.form['presentacion']
    

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO categorias (id_categoria, especie, tipo, presentacion)'
                    'VALUES (%s, %s, %s, %s)',
                    (id_categoria, especie, tipo, presentacion))
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Categoria agregada exitosamente!')

        return redirect(url_for('dashboardCategorias'))

    return redirect(url_for('categoriasNuevo'))

@app.route("/categorias_editar/<string:id>")
@login_required
def categoriasEditar(id):
    titulo = "Editar Categoria"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM categorias WHERE id_categoria={0}'.format(id))
    categoria=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('categoriasEditar.html', titulo=titulo, categoria=categoria[0])

@app.route('/dashboard/categorias/actualizar/<string:id>', methods=['POST'])
@login_required
def categoriasActualizar(id):
    if request.method == 'POST':
        id_categoria=request.form['id_categoria']
        especie = request.form['especie']
        tipo= request.form['tipo']
        presentacion= request.form['presentacion']


        conn = get_db_connection()
        cur = conn.cursor()
        sql="UPDATE categorias SET especie=%s, tipo=%s, presentacion=%s WHERE id_categoria=%s"        
        valores=( especie, tipo, presentacion,id_categoria)
        cur.execute(sql,valores)
        conn.commit()
        cur.close()
        conn.close()

        flash('¡Categoria actualizado exitosamente!')

        return redirect(url_for('dashboardCategorias'))
    
@app.route("/categorias_detalles/<string:id>")
@login_required
def categoriasDetalles(id):
    titulo="Detalles categoria"
    conn= get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM categorias WHERE id_categoria = {0}'.format(id))
    categoria=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    #hora_actual=datetime.now()
    return render_template('categoriasDetalles.html', titulo=titulo, categoria=categoria[0])

@app.route('/dashboard/categoria/eliminar/<string:id>')
@login_required
def categoriaEliminar(id):
    #activo = False
    #editado = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    sql="DELETE FROM categorias WHERE id_categoria={0}".format(id)
    #sql="UPDATE productos SET activo=%s WHERE id_producto=%s"
    valores=(id)
    cur.execute(sql,valores)
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Categoria eliminado correctamente!')
    return redirect(url_for('dashboardCategorias'))
#----------------------MENU---------------------------------------
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

#-----------------------CAJERO---------------------------------------
@app.route('/cajero/ventas')
@login_required
def cajeroVentas():
        if current_user.tipo == 'cajero':
         return render_template('cajeroVentas.html')
        else:
            return redirect(url_for('login'))

@app.route('/cajero/corte')
@login_required
def cajeroCorte():
        if current_user.tipo == 'cajero':

            return render_template('cajeroCorte.html')
        else:
            return redirect(url_for('login'))


@app.route('/cajero/gastos')
@login_required
def cajeroGastos():
    if current_user.tipo == 'cajero':
        return render_template('cajeroGastos.html')
    else:
        return redirect(url_for('login'))

@app.route('/cajero/dashboardProductos')
@login_required
def cajeroProductos():
    titulo = "Productos"
    

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

   

    # Obtener los productos con límite y offset
    cur.execute('SELECT * FROM productos')
    productos = cur.fetchall()

    cur.close()
    conn.close()

    
    return render_template(
        'cajeroProductos.html',
        titulo=titulo,
        productos=productos
       
    )

#---------------LOGIN--------------------
@app.route('/login')
def login():
    return render_template('/login.html')


@app.route('/loguear', methods=('GET', 'POST'))
def loguear():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
       
        user=User(0,username,password,None,None,None,None)
        loged_user = ModelUser.login(get_db_connection(),user)
        

        if loged_user!=None:
            if loged_user.password:
                login_user(loged_user)
                return redirect(url_for('dashboardProductos'))

            else:
                flash("Nombre de usuario y/o contraseña incorrecta.")
                return redirect(url_for('login'))
        else:
            flash("Nombre de usuario y/o contraseña incorrecta.")
            return redirect(url_for('login'))
   
        
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def pagina_no_encontrada(error):
    return render_template('404.html')

def pagina_no_encontrada(error):
    return redirect('login')

if __name__ == '__main__':
    csrf.init_app(app)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, pagina_no_encontrada)
    app.run(debug=True, port=5000)