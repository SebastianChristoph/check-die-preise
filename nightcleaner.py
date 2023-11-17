import secret
import paramiko

logs_to_clean = ["ALDI", "DM", "IKEA", "FRESSNAPF", "HELLWEG", "LEGO", "LIDL", "MEDIKAMENTE", "SHOPAPOTHEKE"]

def upload_log(log_file_name):
        host = "ssh.pythonanywhere.com"
        port = 22
        password = secret.get_password()
        username = secret.get_username()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        try:
            sftp = ssh.open_sftp()
            path = "/home/SebastianChristoph/mysite/static/crawler/logging/crawlerlog_"+log_file_name+".txt"
            localpath = "/home/pi/crawlerlog_"+log_file_name
            sftp.put(localpath, path)
            sftp.close()
        except Exception as e:
            print("..no upload possible")
            print(e)

        ssh.close()

        print("Uploaded", log_file_name)



for log in logs_to_clean:
    upload_log(log)
    with open("/home/pi/crawlerlog_"+log+".txt", "w") as file:
        print(log, "cleaned")

