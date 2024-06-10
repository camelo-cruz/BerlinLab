import random
import csv

def generate_shuffled_lists(input_list, repeat_times=1, num_rows=1000, output_file='shuffled_lists.csv'):
    all_shuffled_lists = []

    for _ in range(num_rows):
        group = []
        
        for _ in range(repeat_times):
            shuffled_list = input_list.copy()
            random.shuffle(shuffled_list)
            group.append(shuffled_list)
            
            new_list = [2 if element == 1 else 1 for element in shuffled_list]
            group.append(new_list)
            
        for element in group:
            all_shuffled_lists.append(element)

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        for num in range(num_rows):
            row = all_shuffled_lists[num]
            csv_writer.writerow(row)

    print(f"Shuffled lists written to {output_file}")

def main():
    my_list = [1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]
    repeat_times = 3
    total_rows = 1000
    generate_shuffled_lists(my_list, repeat_times, total_rows)

if __name__ == '__main__':
    main()
