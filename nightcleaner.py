logs_to_clean = ["ALDI", "DM", "IKEA", "FRESSNAPF", "HELLWEG", "LEGO", "LIDL", "MEDIKAMENTE", "SHOPAPOTHEKE"]

for log in logs_to_clean:
    with open("/home/pi/crawlerlog_"+log+".txt", "w") as file:
        print(log, "cleaned")

with open("/home/pi/hourly_log_uploader.txt", "w") as file:
        print("hourly loguploader cleaned")

