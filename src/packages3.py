from flask import Flask, render_template_string, request, send_file
import paramiko
import pandas as pd
import io
import xml.etree.ElementTree as ET

app = Flask(__name__)

LAST_RESULT = ""

HTML = """
<!doctype html>
<html>
<head>
<title>Red Hat Package Checker</title>
<style>
    body { font-family: Segoe UI, Arial; background: #f4f6f8; }
    .title { text-align:center; font-size:32px; margin:30px; font-weight:bold; }
    form { background:#fff; padding:25px; width:520px; margin:auto; border-radius:8px; box-shadow:0 0 10px #ccc; }
    textarea, input { width:100%; padding:8px; margin-top:8px; margin-bottom:15px; }
    button { padding:10px 18px; margin:5px; font-size:15px; cursor:pointer; }
    pre { background:#111; color:#eee; padding:15px; width:80%; margin:20px auto; overflow:auto; }
    .center { text-align:center; }
</style>
</head>
<body>

<div class="title">Red Hat Package Version Checker</div>

<form method="post">
    <label>Hostnames (one per line)</label>
    <textarea name="hostnames" required></textarea>

    <label>Package Name</label>
    <input type="text" name="package" required>

    <label>Username</label>
    <input type="text" name="username" required>

    <label>Password</label>
    <input type="password" name="password" required>

    <div class="center">
        <button type="submit">RUN</button>
    </div>
</form>

{% if result %}
<pre>{{ result }}</pre>

<div class="center">
    <form method="post" action="/export/txt" style="display:inline;">
        <button>Export TXT</button>
    </form>

    <form method="post" action="/export/xml" style="display:inline;">
        <button>Export XML</button>
    </form>

    <form method="post" action="/export/xls" style="display:inline;">
        <button>Export XLS</button>
    </form>
</div>
{% endif %}

</body>
</html>
"""

def get_package_version(host, username, password, package):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        cmd = f"rpm -q {package}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode() + stderr.read().decode()
        ssh.close()
        return output.strip()
    except Exception as e:
        return f"Error: {e}"

def get_versions_multiple_hosts(hosts, username, password, package):
    results = []
    for host in hosts:
        host = host.strip()
        if not host:
            continue
        result = get_package_version(host, username, password, package)
        results.append(f"[{host}]\n{result}")
    return "\n\n".join(results)

@app.route("/", methods=["GET", "POST"])
def index():
    global LAST_RESULT
    result = None
    if request.method == "POST":
        hosts = request.form["hostnames"].splitlines()
        package = request.form["package"]
        username = request.form["username"]
        password = request.form["password"]

        result = get_versions_multiple_hosts(hosts, username, password, package)
        LAST_RESULT = result

    return render_template_string(HTML, result=result)

@app.route("/export/txt", methods=["POST"])
def export_txt():
    return send_file(
        io.BytesIO(LAST_RESULT.encode()),
        mimetype="text/plain",
        as_attachment=True,
        download_name="package_result.txt"
    )

@app.route("/export/xml", methods=["POST"])
def export_xml():
    root = ET.Element("Results")
    for block in LAST_RESULT.split("\n\n"):
        entry = ET.SubElement(root, "HostResult")
        entry.text = block

    xml_io = io.BytesIO()
    ET.ElementTree(root).write(xml_io, encoding="utf-8", xml_declaration=True)
    xml_io.seek(0)

    return send_file(
        xml_io,
        mimetype="application/xml",
        as_attachment=True,
        download_name="package_result.xml"
    )

@app.route("/export/xls", methods=["POST"])
def export_xls():
    rows = []
    for block in LAST_RESULT.split("\n\n"):
        lines = block.splitlines()
        host = lines[0].strip("[]")
        version = " ".join(lines[1:])
        rows.append({"Host": host, "Package Version": version})

    df = pd.DataFrame(rows)

    excel_io = io.BytesIO()
    df.to_excel(excel_io, index=False)
    excel_io.seek(0)

    return send_file(
        excel_io,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="package_result.xlsx"
    )

if __name__ == "__main__":
    app.run(debug=True)
