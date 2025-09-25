from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

loginManager = LoginManager() #instanciando a função do Login Manager
db.init_app(app)
loginManager.init_app(app) #iniciando o Login manager na aplicação

#view login
loginManager.login_view = 'login' # ele vai usar essa rota para visualizar o login


@loginManager.user_loader
def loadUser(userId):
  return User.query.get(userId)

@app.route('/login', methods=['POST'])
def login():
  data = request.json

  username = data.get("username")
  password = data.get("password")

  if username and password:

    user = User.query.filter_by(username=username).first() #estou filtrando na tabela Users se encontra o username recebido pela api e retorna o primeiro
    if user and user.password == password:
      login_user(user)
      print(f"User: {current_user.is_authenticated}")
      return jsonify({
        "Message": "Autenticação Realizada com Sucesso",
        "id": user.id
      })

  return jsonify({
      "Message": "Credenciais Inválidas"
    }), 400

@app.route("/logout", methods=['GET'])
@login_required #protege a rota para apenas users autenticados
def logout():
  logout_user()
  return jsonify({
    "message": "Logout Realizado com sucesso!"
  })

@app.route("/user", methods=["POST"])
def createUser():
  data = request.json

  username = data.get("username")
  password = data.get("password")

  if username and password:
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
      "message": "Usuário Criado com Sucesso!"
    })

  return jsonify({
    "message": "Dados Inválidas"
  }), 400

@app.route("/user/<int:idUser>", methods=['GET'])
@login_required
def getInfoUser(idUser):
  user = User.query.get(idUser)

  if user:
    return {
      "username": user.username
    }
  
  return jsonify({
    "message": "Usuario não encontrado"
  }), 404

@app.route("/user/<int:idUser>", methods=['PUT'])
@login_required
def updateUser(idUser):
  data = request.json
  user = User.query.get(idUser)

  if user and data:
    user.password = data.get("password")

    return jsonify({
      "message": "Usuario Atualizado com Sucesso",
      "user": {
        "username": user.username,
        "password": user.password
      }
    })

  return jsonify({
    "message": "Não foi possível editar as informações"
  }), 404


@app.route("/user/<int:idUser>", methods=['DELETE'])
@login_required
def deleteUser(idUser):
  user = User.query.get(idUser)

  if idUser == current_user.id:
    return jsonify({
      "message": "Deleção não permitida"
    }), 403

  if user:
    db.session.delete(user)
    db.session.commit()
    return jsonify({
      "message": f"Usuario: {user.id} Removido com Sucesso",
    })
  
  return jsonify({
      "message": "Usuario não encontrado",
    }), 404


if __name__ == '__main__':
  app.run(debug=True)