logs_to_clean = ["ALDI", "DM", "IKEA", "FRESSNAPF", "HELLWEG", "LEGO", "LIDL", "MEDIKAMENTE", "SHOPAPOTHEKE"]

for log in logs_to_clean:
    with open("/home/pi/crawlerlog_"+log+".txt", "w") as file:
        print(log, "cleaned")

