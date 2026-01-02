from flask import Flask, render_template_string, request
import paramiko

app = Flask(__name__)

HTML = """
<!doctype html>
<<<<<<< HEAD
<title>Check Package Version</title>
<h2>Check Package Version on Red Hat Server</h2>
<form method="post">
  Hostname: <input type="text" name="hostname" required><br>
  Package: <input type="text" name="package" required><br>
  Username: <input type="text" name="username" required><br>
  Password: <input type="password" name="password" required><br>
  <input type="submit" value="RUN">
</form>
{% if result %}
  <h3>Result:</h3>
  <pre>{{ result }}</pre>
{% endif %}
=======
<html>
<head>
<title>Check Package Version</title>
<style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; color: #222; }
    .center-title { text-align: center; margin-top: 60px; margin-bottom: 30px; font-size: 2.5em; font-weight: bold; letter-spacing: 1px; }
    h2 { font-size: 2em; }
    form { background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 2px 8px #ccc; max-width: 500px; margin: auto; }
    label { font-weight: bold; }
    textarea, input[type=text], input[type=password] {
        width: 100%;
        font-size: 1.1em;
        margin-bottom: 1em;
        padding: 0.5em;
        border-radius: 4px;
        border: 1px solid #bbb;
        font-family: 'Fira Mono', 'Consolas', monospace;
    }
    textarea { height: 120px; resize: vertical; }
    input[type=submit] {
        background: #007bff; color: #fff; border: none; padding: 0.7em 2em; border-radius: 4px; font-size: 1.1em; cursor: pointer;
    }
    pre { background: #222; color: #eee; padding: 1em; border-radius: 6px; font-size: 1.1em; overflow-x: auto; }
</style>
</head>
<body>
<div class="center-title">Red Hat Package Checker</div>
<div class="center-title" style="font-size:1.5em; font-weight:normal; margin-top:0; margin-bottom:30px;">Check Package Version on Red Hat Server</div>
<form method="post">
    <label for="hostnames">Hostnames (one per line):</label><br>
    <textarea name="hostnames" id="hostnames" required></textarea><br>
    <label for="package">Package:</label><br>
    <input type="text" name="package" id="package" required><br>
    <label for="username">Username:</label><br>
    <input type="text" name="username" id="username" required><br>
    <label for="password">Password:</label><br>
    <input type="password" name="password" id="password" required><br>
    <input type="submit" value="RUN">
</form>
{% if result %}
    <h3>Result:</h3>
    <pre>{{ result }}</pre>
{% endif %}
</body>
</html>
>>>>>>> 6052b1b (package3)
"""

def get_package_version(hostname, username, password, package):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, timeout=10)
        cmd = f"rpm -q {package}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode() + stderr.read().decode()
        ssh.close()
        return output.strip()
    except Exception as e:
        return f"Error: {e}"

<<<<<<< HEAD
=======
def get_versions_multiple_hosts(hostnames, username, password, package):
    results = []
    for host in hostnames:
        host = host.strip()
        if not host:
            continue
        result = get_package_version(host, username, password, package)
        results.append(f"[{host}]\n{result}\n")
    return '\n'.join(results)

>>>>>>> 6052b1b (package3)
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
<<<<<<< HEAD
        hostname = request.form['hostname']
        package = request.form['package']
        username = request.form['username']
        password = request.form['password']
        result = get_package_version(hostname, username, password, package)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True)
=======
        hostnames = request.form['hostnames'].splitlines()
        package = request.form['package']
        username = request.form['username']
        password = request.form['password']
        result = get_versions_multiple_hosts(hostnames, username, password, package)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
>>>>>>> 6052b1b (package3)

