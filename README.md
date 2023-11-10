# Mailer

Módulo para enviar mails usando `python` y el protocolo `SMTP`. Viene preconfigurado para usar gmail, pero se puede utilizar otros servidores `SMTP`:
```python
from mailer import EmailAPI

sender_email = os.getenv("GMAIL_USER")
sender_password = os.getenv("GMAIL_PASS")

mailer = EmailAPI(sender_email, sender_pass)

# si hace falta usar otro mail (outlook, etc) se puede especificar el servidor de mails:
sender_email = os.getenv("OUTLOOK_USER")
sender_password = os.getenv("OUTLOOK_PASS")

mailer_outlook = EmailAPI(sender_email, sender_password, smtp_server_addr="smtp-mail.outlook.com:587")

# o también:
mailer_outlook = EmailAPI(sender_email, sender_password, smtp_server_addr="smtp-mail.outlook.com", smtp_server_port=587)

# enviar emails es sencillo
emails = ["foo@foo.com", "bar@bar.com", "baz@baz.com"]
body = "hello, this is my email"

mailer.send_email(to=emails, body=body)

# se puede especificar subject y archivos que adjuntar:
files = ["./myfile.png", "./myreport.pdf"]
mailer.send_email(to=emails, body=body, subject="Hello", files=files)

# para definir el nombre de los archivos en el mail, se puede usar un diccionario:
files_dict = {"./myfile.png": "clusters.png", "./myreport.pdf": "report.pdf"}
mailer.send_email(to=emails, body=body, subject="Hello", files=files_dict)
```
La clase implementa `MailerInterface`, que define la siguiente interfaz:
```python
class MailerInterface(ABC):
    @abstractmethod
    def send_email(self, \
	    to: Union[str, List[str]], \
		body: Union[str, Dict[Literal['plain', 'csv', 'html', 'rtf'], str]], \
		subject: Union[str, None] = None, \
		files: Union[Dict[str, str], List[str]] = []) \
		-> bool
	
	def enable_sftp(self, \
		host: str, \
		user: str, \
		password: str, \
		sftp_pk_path: str) \
		-> bool:
```
Esto implica que cualquier código que use `EmailAPI` no tiene que cambiar si `MailerInterface` no se ha cambiado (a menos que explícitamente se usen métodos y atributos internos de `EmailAPI`, lo cual es mala praxis)

---
### Enviar emails desde cuentas de gmail
Para enviar emails desde una cuenta de gmail hay que usar `app specific passwords`. Para generar una, hay que seguir los siguientes pasos:
- Conectado a la cuenta de gmail que se quiere habilitar, ve a [la página de seguridad de la cuenta](https://myaccount.google.com/security)
- En `How you sign in to Google`, activa `2-Step Verification`
- Cuando esté activada, en el mismo menú de `2-Step Verification`, navega al final de la página y crea una `app password`.

Cuando la contraseña esté creada, hay que guardarla en algún lugar porque Google no permite verla después de haberla creado. Si una contraseña no se usa o se pierde, se pueden borrar en el mismo menú de `app passwords`. Cambiar la contraseña del email borra todas las `app passwords`

---
### Habilitar archivos adjuntos por FTP remoto
Utilizando el método `enable_sftp` se puede registrar un servidor sftp para coger archivos adjuntos. Una vez usado, el mailer dejará de buscar archivos en el ordenador local, y pasará a cogerlos del servidor remoto:

```python
# busca los archivos en local:
files = ["./myfile.png", "./myreport.pdf"]
mailer.send_email(to=emails, body=body, subject="Hello", files=files)

sftp_host = os.getenv("SFTP_HOST")
sftp_user = os.getenv("SFTP_USER")
sftp_pass = os.getenv("SFTP_PASS")
sftp_pk_path = os.getenv("SFTP_PK_PATH")

mailer.enable_sftp(host=sftp_host, user=sftp_user, password=sftp_pass, sftp_pk_path=sftp_pk_path)

# ahora sftp está activado, buscará los archivos en el servidor
mailer.send_email(to=emails, body=body, subject="Hello", files=files)
```
Además de los parámetros típicos para conectarse, hay que pasarle el parámetro `sftp_pk_path`. Este parámetro es el path a un archivo que contiene la llave pública del servidor al que se va a conectar el mailer. Es una medida de seguridad para prevenir ataques `Man In The Middle` (MITM).

#### Obtener la llave pública de un servidor

Para obtener la llave pública de un servidor, basta con usar el comando `ssh-keyscan`. Luego se copia la línea que contenga `ssh-rsa` en un archivo `.txt`.

Una vez copiada, ya se puede usar para validar la dirección del servidor en el mailer.

---
### Utilizar en un proyecto

#### Instalar como paquete (recomendado)
Para instalar como paquete de python hay que añadir lo siguiente en el Pipfile del proyecto:
```pipfile
[packages]
mailer = {git = "https://github.com/rafael-bardisa-cetaqua/mailer.git"}
```

Se puede instalar también con pip:
```bash
pip install "mailer @ git+https://github.com/rafael-bardisa-cetaqua/mailer.git"
```
En ambos casos se puede especificar una rama o un tag añadiendo @<\rama o tag\> al final del string de conexión ( `https://github.com/rafael-bardisa-cetaqua/mailer@0.1.0` en pip o `{git = "https://github.com/rafael-bardisa-cetaqua/mailer.git", ref=0.1.0}` en pipenv).

Una vez instalado, se usa como un paquete cualquiera:
```python
from mailer import EmailAPI, EmailInterface
...
```
#### Git submodules (manera antigua)
Git tiene un comando que permiten integrar proyectos dentro de otros, de manera que no haga falta actualizarlos manualmente. El mailer se puede añadir automáticamente a un proyecto. En una terminal, navegas a la raíz del proyecto y ejecutas:

```bash
git submodule init
git submodule add -b submodule https://github.com/rafael-bardisa-cetaqua/mailer carpeta/objetivo
git submodule update
```
Estos comandos descargan la rama `submodule` en la carpeta objetivo. Si se usa `VSCode`, seguramente se añada al menú de `source control`, desde donde se pueden descargar commits nuevos automáticamente.

Una vez descargado el submódulo, se puede importar la clase `EmailAPI` (y la clase abstracta `MailerInterface`) desde la misma carpeta donde se ha guardado, no hace falta entrar dentro del submódulo para ver dónde están:

```python
from carpeta.objetivo import EmailAPI, MailerInterface
...
```
Si en algún momento se quiere quitar del proyecto, desde la raíz del proyecto:
```bash
git submodule deinit -f -- carpeta/objetivo
rm -rf .git/modules/carpeta/objetivo
git rm -f carpeta/objetivo
```

TO DO:
- [x] Imports relativos dentro del paquete
- [ ] Tests para verificar que funcione
- [ ] Error handling
	- [ ] Verificar credenciales
- [x] Soporte para utilizar attachments remotos