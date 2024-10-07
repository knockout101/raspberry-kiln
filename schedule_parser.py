import csv
import sys
from matplotlib import pyplot as plt

temp_data = []
time_data = []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Add data file as argument to program call")
        exit(1)

    with open(sys.argv[1], "r") as file:
        rows = csv.reader(file)
        for row in rows:
            temp_data.append(float(row[0]))
            time_data.append(float(row[1]))

    ax = plt.gca()
    ax.set_ylim([0, 1300])
    ax.set_yticks(range(0, 1300, 100))
    plt.plot(time_data, temp_data)
    plt.show()