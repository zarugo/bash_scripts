#!/usr/bin/python3
# The csv file must be in the format
# cardNumber,mediaType,start_validity,end_validity,enabled,accessPolicyId,customerFirstName,CustomerLastName,displayCardNumber
# 123456,proximity,1559347200000,2556057600000,TRUE,9,Bob,Marley,,

# primary_fields = ['firstname', 'lastname', 'email']
# result = []
# with open('mydata.csv') as csv_file:
#     reader = csv.DictReader(csv_file, skipinitialspace=True)
#     for row in reader:
#         d = {k: v for k, v in row.items() if k in primary_fields}
#         d['extraFields'] = [{'name': k, 'value': v} for k, v in row.items() if k not in primary_fields]
#         result.append(d)
#
# print(json.dumps(result, indent=2))




import os, sys, csv, json, requests, datetime


now = datetime.datetime.now()
jms = input("Type the ip of JMS:  ")
username = input("Type the username of the third party:  ")
password = input("Type the password of the third party:  ")
while True:
    input_file = input("Type the name of the file (if it's in another directory, specify the full path): ")
    if os.path.isfile(input_file) is False:
        print("The csv file does not exists on this directory, please check that the name is correct.")
    else:
        break

# Do the login and get the token every time

auth_url = "http://" + jms + ":8080/janus-integration/api/ext/login"
log_headers = { "Content-Type": "application/json" , "Accept": "application/json"}
logindata = { "username": username,	"password": password }
try:
    r = requests.post(auth_url, json=logindata, headers=log_headers, timeout=10.0)
    if r.status_code == 401:
        print("The user or password are not correct. Verify that the Third Party account is set up on JMS")
        quit()
    else:
        token = (json.loads(r.text)["item"]["token"]["value"])
except Exception as e:
    print("Soething went wrong, the error is " + str(e))
    quit()

#parse the csv and upload it to JMS as json

with open(input_file) as csvfile:
    reader = csv.DictReader(csvfile)
    title = reader.fieldnames
    for line in reader:
        csv_lines = {}
        nested = ["start_validity" , "end_validity" , "enabled"]
        csv_lines = {k: v for k, v in line.items() if k not in nested}
        csv_lines["cardParameters"] = [{'name': k, 'value': v} for k, v in line.items() if k in nested]
        print(csv_lines)
        create_url = "http://" + jms + ":8080/janus-integration/api/ext/card/create"
        headers = { "Content-Type": "application/json" , "Accept": "application/json", "Janus-TP-Authorization": token }
        data = (json.dumps(csv_lines, sort_keys=False, indent=4, separators=(",",": "), ensure_ascii=False))
        print(data)
        try:
            r = requests.post(create_url, headers=headers, data=data, timeout=10.0)
            with open("upload_results.log", "a") as log:
                log.write( now.strftime("%Y-%m-%d %H:%M:%S") + "  Contract inserted: " + r.text + ' ' + "Response Code from JMS was: " + str(r.status_code) + "\n" )
        except Exception as e:
            print("Soething went wrong, the error is " + str(e))
        if 

print("The upload is done, please check on JMS that the customers are there. The log file is upload_results.log.")