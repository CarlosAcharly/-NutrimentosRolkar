from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(UserMixin):

    def get_id(self):
        return(self.id_usuario)
    
    def __init__(self,id_usuario,username,password,tipo,activo,creado,editado) -> None:
        self.id_usuario=id_usuario
        self.username=username
        self.password=password
        self.tipo=tipo
        self.activo=activo
        self.creado=creado
        self.editado=editado

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

#print(generate_password_hash("1234"))