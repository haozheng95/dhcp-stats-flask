from flask import Flask
from flask import render_template
from fabric.connection import Connection
import re

app = Flask(__name__)


def get_leases_table():
    ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    content = []
    with Connection(host="10.98.90.60:22", user="root", connect_kwargs={"password": "VMware1!"}) as c, c.sftp() as sftp, \
            sftp.open('/var/lib/dhcpd/dhcpd.leases') as file:
        map = dict()
        for line in file:
            line = line.strip()
            if line.startswith("lease"):
                map["ip"] = re.search(ip_regex, line).group(0)
            elif line.startswith("binding"):
                map["binding"] = line[14:-1]
            elif line.startswith("hardware"):
                map["mac"] = line[18:-1]
            elif line.startswith("client-hostname"):
                map["client_hostname"] = line[17:-2]
            elif line.startswith("}"):
                content.append(map)
                map = dict()

    leases_table = []
    map = dict()
    for ele in content:
        if ele.get("binding") == "active" and not map.get(ele.get("ip")):
            leases_table.append(ele)
            map[ele.get("ip")] = 1
    return leases_table


@app.route('/')
def index():  # put application's code here
    ip_total_count = 460
    leases_table = get_leases_table()
    ip_usage_count = len(leases_table)
    return render_template('index.html', leases_table=leases_table, ip_total_count=ip_total_count,
                           ip_usage_count=ip_usage_count)


if __name__ == '__main__':
    app.run()
