import sys
import csv
import os
import subprocess as sp

class FileGroup:
    def __init__(self, original_csv, new_csv):
        self.original = original_csv
        self.new = new_csv

    def __repr__(self):
        return "original: {}\nnew: {}\n\n".format(self.original, self.new)


def find_all_file_groups(start_dir):
    curr_index = 0
    curr_file = ""

    file_groups = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            curr_file = file
            if file_already_in_groups(file, file_groups):
                continue

            if "newmerge" not in curr_file:
                for file in files:
                    if file[0:5] == curr_file[0:5] and "newmerge" in file:
                        original_path = os.path.join(root, curr_file)
                        new_path = os.path.join(root, file)
                        group = FileGroup(original_path, new_path)
                        file_groups.append(group)
            curr_index += 1

    return file_groups

def file_already_in_groups(file, groups):
    for group in groups:
        if file == os.path.basename(group.original) or\
           file == os.path.basename(group.new):
            return True
    return False

def batch_merge_groups(groups):

    problem_diffs = []

    for group in groups:
        new_filename = os.path.basename(group.original)
        new_filename = new_filename.replace(".csv", "_merged.csv")
        new_filename = os.path.join(output_dir, new_filename)
        command = ["python", "wordmerge.py", group.original, group.new, new_filename, "--batch"]

        command_string = " ".join(command)
        #print command_string

        pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10 ** 8)
        out, err = pipe.communicate()
        if out:
            result = eval(out)
            result.append(os.path.basename(group.original))
            problem_diffs.append(result)
        #print out

    output_problem_diffs_csv(problem_diffs)


def output_problem_diffs_csv(problem_diffs):
    with open("problem_files.txt", "wb") as output:
        for diff in problem_diffs:
            output.write("{} --- old --- {} -- {}\n".format(diff[1], diff[0][0], diff[0][1][0]))
            output.write("{} --- new --- {} -- {}\n".format(diff[1], diff[0][0], diff[0][1][1]))

if __name__ == "__main__":

    start_dir = sys.argv[1]
    output_dir = sys.argv[2]

    file_groups = find_all_file_groups(start_dir)

    #print file_groups
    batch_merge_groups(file_groups)

