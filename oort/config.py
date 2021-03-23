import argparse

parser = argparse.ArgumentParser()

# Path configuration
parser.add_argument('--exe_path', type=str, default='./', help='Data store of the framework')
parser.add_argument('--zoo_path', type=str, default='./zoo', help='Path of the model zoo')

# Framework configuration
parser.add_argument('--num_of_processes', type=int, default=16, help='Number of threads used for mapping (~CPU cores)')

args = parser.parse_args()