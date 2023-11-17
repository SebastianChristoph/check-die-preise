import secret
import paramiko
from datetime import datetime, timedelta

logs_to_clean = ["ALDI", "DM", "IKEA", "FRESSNAPF", "HELLWEG", "LEGO", "LIDL", "MEDIKAMENTE", "SHOPAPOTHEKE"]

def get_current_time():
        current_time = datetime.now()
        current_time_format = current_time.strftime("%d-%m  %H:%M")
        return current_time_format


def upload_log(log_file_name):
        host = "ssh.pythonanywhere.com"
        port = 22
        password = secret.get_password()
        username = secret.get_username()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        print("Connected for", log_file_name)
        try:
            sftp = ssh.open_sftp()
            path = "/home/SebastianChristoph/mysite/static/crawler/logging/crawlerlog_"+log_file_name
            localpath = "/home/pi/crawlerlog_"+log_file_name
            sftp.put(localpath, path)
            sftp.close()
            print("Put and closed")
        except Exception as e:
            print("..no upload possible")
            print(e)

        ssh.close()

        print("Uploaded", log_file_name)

current_time =get_current_time()
for log in logs_to_clean:
     upload_log(log+".txt")
     print(current_time, "uploaded", log)
     print("__________________________")
print("Finished")
print("##################################################################")