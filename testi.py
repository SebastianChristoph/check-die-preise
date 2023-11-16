# with open("/home/pi/crawler/output.txt", "w") as file:
#     file.write("hallo")

# print("done")

import paramiko
host = "ssh.pythonanywhere.com"
port = 22
password = ".YXbu.83!xP4DTx"
username = "SebastianChristoph"

print("set instance")
ssh = paramiko.SSHClient()
print("set missing hostkey")
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("connect")
ssh.connect(host, port, username, password)

try:
    print("instanz sftp")
    sftp = ssh.open_sftp()
    path = "/home/SebastianChristoph/mysite/static/crawler/jsons/out.txt"
    localpath = "/home/pi/crawler/output.txt"
    print("upload")
    sftp.put(localpath, path)
    print("close sftp")
    sftp.close()
except Exception as e:
    print("nope")
    print(e)

print("close")
ssh.close()
