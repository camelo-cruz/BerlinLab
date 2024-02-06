import random
import csv

def generate_shuffled_lists(input_list, repeat_times=1, num_rows=1000, output_file='shuffled_lists.csv'):
    all_shuffled_lists = []

    for _ in range(num_rows):
        shuffled_list = input_list.copy()  # Create a copy of the original list
        random.shuffle(shuffled_list)
        
        for _ in range(repeat_times):
            all_shuffled_lists.extend([shuffled_list])

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        for num in range(num_rows):
            row = all_shuffled_lists[num]
            csv_writer.writerow(row)

    print(f"Shuffled lists written to {output_file}")

def main():
    my_list = [1,2,3,4,5,6]
    repeat_times = 2
    total_rows = 1000
    generate_shuffled_lists(my_list, repeat_times, total_rows)

if __name__ == '__main__':
    main()
