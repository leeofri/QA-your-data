import csv
csv_rows = []
with open("data/Hebrew_reports.txt", "r") as f:
    lines = f.readlines()


for line in lines:
    try:
        print("line",line)
        parts = line.split(';')
        print ("parts",parts, len(parts))
        if len(parts) == 0:
            continue

        sender = parts[0]
        recipient = parts[1]
        time = parts[2]
        message = parts[3]

        csv_rows.append([sender, recipient, time, message])
    except:
        # Skip lines that don't fit the expected format
        continue

# Define the path for the CSV file
csv_path = "data/Hebrew_reports.csv"

# Write to CSV file
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Sender", "Recipient","Time", "Message"])  # header
    writer.writerows(csv_rows)

csv_path
