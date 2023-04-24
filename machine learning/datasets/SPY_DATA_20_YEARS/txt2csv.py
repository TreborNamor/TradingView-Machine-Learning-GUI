import csv

# Open the input and output files
with open('SPX_1hour.txt', 'r') as input_file, open(
        'SPX_1hour.csv', 'w', newline='') as output_file:
    # Create a CSV writer object
    csv_writer = csv.writer(output_file)

    # Write the column headers to the CSV file
    csv_writer.writerow(['time', 'open', 'high', 'low', 'close'])

    # Loop through each line in the input file
    for line in input_file:
        # Split the line on commas and strip any whitespace
        fields = [field.strip() for field in line.split(',')]

        # Divide the numeric fields by 10 and round to 2 decimal places
        for i in range(1, len(fields)):
            fields[i] = round(float(fields[i]) / 10, 2)

        # Write the fields to the CSV file
        csv_writer.writerow(fields)
