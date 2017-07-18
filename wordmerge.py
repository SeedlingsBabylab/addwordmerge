import csv
import sys
import os

old_file = ""
new_file = ""

old_audiofile_data = []
new_audiofile_data = []
audio_merge_data = []

old_videofile_data = []
new_videofile_data = []
video_merge_data = []

# diffs = (index, [old_row, new_row], diff_indices[])
diffs = []
contains_new_word = False

def parse_old_file(type):
    with open(old_file, "rU") as file:
        reader = csv.reader(file)
        reader.next()
        if type == "video":
            for row in reader:
                old_videofile_data.append(row)
        if type == "audio":
            for row in reader:
                old_audiofile_data.append(row)

def parse_new_file(type):
    with open(new_file, "rU") as file:
        reader = csv.reader(file)
        reader.next()
        if type == "video":
            for row in reader:
                new_videofile_data.append(row)
        if type == "audio":
            for row in reader:
                new_audiofile_data.append(row)

def merge_audio():
    global contains_new_word

    old_groups = []
    unique_old_groups = []

    old_word_count = 0
    new_word_count = 0

    fix_me_count_file = open("fix_me_count_audio", "a")
    fix_me_count = 0

    # if "03_08" in old_file:
    #     print

    # group all the old entres into identical groups
    for index, element in enumerate(old_audiofile_data):
        indices = find_all_match_audio2(element,
                                       old_audiofile_data)

        old_groups.append(indices)

        if indices not in unique_old_groups:
            unique_old_groups.append(indices)
            old_word_count += len(indices)

    empty_groups = [group for group in old_groups if len(group) < 1]



    new_groups = []

    for index, element in enumerate(new_audiofile_data):
        new_indices = find_all_match_audio2(element,
                                            new_audiofile_data)


        if new_indices not in new_groups:
            new_groups.append(new_indices)
            new_word_count += len(new_indices)

        old_group = find_group_match_audio2(element, old_groups)

        if not old_group:
            merge_data = element
            merge_data[6] = "***FIX ME***"
            audio_merge_data.append([merge_data])
            fix_me_count += 1
            contains_new_word = True
            continue

        if len(old_group) > 1:
            matched, not_matched = group_diff_audio(old_group, new_indices)
            diff_group = matched + not_matched
            if len(diff_group) != len(new_indices):
                print "mismatch: {}    {}".format(new_indices, diff_group)
            if diff_group not in audio_merge_data:
                audio_merge_data.append(diff_group)
            continue

        elif len(old_group) == 1:
            merge_data = old_audiofile_data[old_group[0]]
            diff_result = diff_audio(index, merge_data, element)
            if diff_result:
                if diff_result[1] not in diffs:
                    diffs.append(diff_result[1])
                    diffed_entry = diff_result[0]
                    audio_merge_data.append([diffed_entry[:7]])
            else:
                merge_data[1] = element[1]
                if "+" in merge_data[1] and not merge_data[1][0].islower():
                    merge_data[6] = element[6].lower().capitalize()
                if merge_data[6] != "NA" and any(not x.islower() for x in merge_data[6]):
                    cap_x, cap_y = number_of_capitals(merge_data[1], merge_data[6])
                    if cap_x != cap_y:
                        merge_data[6] = merge_data[1]

                audio_merge_data.append([merge_data])

    fix_me_count_file.write("fix_me_count {}: {}\n".format(os.path.basename(old_file)[:5], fix_me_count))
    fix_me_count_file.close()

def number_of_capitals(x, y):
    num_x = 0
    num_y = 0

    for ch in x:
        if not ch.islower():
            num_x += 1
    for ch in y:
        if not ch.islower():
            num_y += 1
    return (num_x, num_y)

def merge_video2():
    global contains_new_word

    old_groups = []
    unique_old_groups = []

    old_word_count = 0
    new_word_count = 0

    fix_me_count_file = open("fix_me_count_video", "a")
    fix_me_count = 0

    # group all the old entres into identical groups
    for index, element in enumerate(old_videofile_data):
        indices = find_all_match_video2(element,
                                       old_videofile_data)

        old_groups.append(indices)

        if indices not in unique_old_groups:
            unique_old_groups.append(indices)
            old_word_count += len(indices)

    empty_groups = [group for group in old_groups if len(group) < 1]



    new_groups = []

    for index, element in enumerate(new_videofile_data):
        new_indices = find_all_match_video2(element,
                                            new_videofile_data)


        if new_indices not in new_groups:
            new_groups.append(new_indices)
            new_word_count += len(new_indices)

        old_group = find_group_match_video2(element, old_groups)

        if not old_group:
            merge_data = element
            merge_data[7] = "***FIX ME***"
            video_merge_data.append([merge_data])
            contains_new_word = True
            fix_me_count += 1
            continue

        if len(old_group) > 1:
            matched, not_matched = group_diff_video(old_group, new_indices)
            diff_group = matched + not_matched
            if len(diff_group) != len(new_indices):
                print "mismatch: {}    {}".format(new_indices, diff_group)
            if diff_group not in video_merge_data:
                video_merge_data.append(diff_group)
            continue


        elif len(old_group) == 1:
            merge_data = old_videofile_data[old_group[0]]
            diff_result = diff_video(index, merge_data, element)
            if diff_result:
                if diff_result[1] not in diffs:
                    diffs.append(diff_result[1])

                video_merge_data.append([diff_result[0]])
            else:
                merge_data[3] = element[3]
                if "+" in merge_data[3] and not merge_data[3][0].islower():
                    #merge_data[3] = element[3]
                    merge_data[7] = element[7].lower().capitalize()
                if any(not x.islower() for x in merge_data[7]) and merge_data[7] != "NA":
                    cap_x, cap_y = number_of_capitals(merge_data[3], merge_data[7])
                    if cap_x != cap_y:
                        merge_data[7] = merge_data[3]

                video_merge_data.append([merge_data])

    fix_me_count_file.write("fix_me_count {}: {}\n".format(os.path.basename(old_file)[:5], fix_me_count))
    fix_me_count_file.close()

def find_all_match_audio(entry, data):
    found =[]
    for old_index, element in enumerate(data):
        if audio_match(entry, element):
            found.append(old_index)
    if not found:
        found.append(-1)
    return found

def find_all_match_audio2(entry, data):
    found =[]
    for old_index, element in enumerate(data):
        if audio_match2(entry, element):
            found.append(old_index)
    if not found:
        found.append(-1)
    return found

def find_group_match_audio(entry, groups):
    for group_index, group in enumerate(groups):
        if audio_match(entry, old_audiofile_data[group[0]]):
            return group
    return False

def find_group_match_audio2(entry, groups):
    for group_index, group in enumerate(groups):
        if audio_match2(entry, old_audiofile_data[group[0]]):
            return group
    return False

def find_group_match_video(entry, groups):
    for group_index, group in enumerate(groups):
        if video_match(entry, old_videofile_data[group[0]]):
            return group
    return False

def find_group_match_video2(entry, groups):
    for group_index, group in enumerate(groups):
        if video_match2(entry, old_videofile_data[group[0]]):
            return group
    return False

def find_all_match_video(entry, data):
    found =[]
    for old_index, element in enumerate(data):
        if video_match(entry, element):
            found.append(old_index)
    if not found:
        found.append(-1)
    return found

def find_all_match_video2(entry, data):
    found =[]
    for old_index, element in enumerate(data):
        if video_match2(entry, element):
            found.append(old_index)
    if not found:
        found.append(-1)
    return found

def audio_match(new_item, old_item):
    if new_item[0] == old_item[0] and \
       new_item[1].lower() == old_item[1].lower() and \
       new_item[5] == old_item[5]:
        return True
    return False



def audio_match2(new_item, old_item):
    split_new_time = map(int, new_item[5].split("_"))
    split_old_time = map(int, old_item[5].split("_"))
    if new_item[1].lower() == old_item[1].lower() and \
       soft_time_match(split_old_time, split_new_time):
        return True
    return False

def soft_time_match(old, new):
    if old[0] == new[0] and old[1] == new[1]:
        return True
    if old[0] == new[0]:
        return True
    if old[1] == new[1]:
        return True
    if old[0] > new[0] and old[0] < new[1]:
        return True
    if old[1] > new[0] and old[1] < new[1]:
        return True
    if new[0] > old[0] and new[0] < old[1]:
        return True
    if new[1] > old[0] and new[1] < old[1]:
        return True
    return False

def video_match(new_item, old_item):
    if new_item[1] == old_item[1] and \
       new_item[2] == old_item[2] and \
       new_item[3].lower() == old_item[3].lower():
        return True
    return False

def video_match2(new_item, old_item):
    old_time = map(int, [old_item[1], old_item[2]])
    new_time = map(int, [new_item[1], new_item[2]])

    if soft_time_match(old_time, new_time) and \
       new_item[3].lower() == old_item[3].lower():
        return True
    return False

def output_merged_audiocsv(path):
    with open(path, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(["tier", "word", "utterance_type",
                        "object_present", "speaker", "timestamp",
                        "basic_level"])
        for group in audio_merge_data:
            for element in group:
                if len(element) == 8:
                    if element[7] == "NA":
                        element[7] = ""
                writer.writerow(element)
        #writer.writerows(audio_merge_data)

    if diffs and not batch_process:
        print "\nThere were other changes in the new file besides additions"
        print "Please check them in the diffs.csv file that was just made"
        print "It's in the /diffs folder in this script's directory\n"

        problems = find_problem_diffs_audio()
        if problems:
            print "\n\nThere were diffs that require manual updates:\n\n"
            print problems
        output_audio_diffs()

    elif batch_process:
        problems = find_problem_diffs_audio()
        if problems:
            print problems

        output_audio_diffs()

def output_merged_videocsv(path):
    with open(path, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(["labeled_object.ordinal", "labeled_object.onset",
                         "labeled_object.offset", "labeled_object.object",
                         "labeled_object.utterance_type",
                         "labeled_object.object_present",
                         "labeled_object.speaker", "labeled_object.basic_level"])
        writer.writerows(video_merge_data)

    if diffs and not batch_process:
        print "\nThere were other changes in the new file besides additions"
        print "Please check them in the diffs.csv file that was just made"
        print "It's in the /diffs folder in this script's directory\n"

        problems = find_problem_diffs_audio()
        if problems:
            print "\n\nThere were diffs that require manual updates:\n\n"
            print problems

        output_video_diffs()
    elif batch_process:
        problems = find_problem_diffs_video()
        if problems:
            print problems

        output_video_diffs()


def output_audio_diffs():
    if not diffs:
        append_to_no_diffs_csv()
        return

    out_path = os.path.join("diffs", os.path.split(new_file)[1].replace(".csv",
                                                                        "_diffs.csv"))
    with open(out_path, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(["original_csv_index", "old_new", "entry", "diff_indices",
                         "tier","word","utterance_type","object_present","speaker","timestamp"])
        for element in diffs:
            diff_row = [" "]*7
            for index in element[2]:
                diff_row[int(index)] = "+++"
            writer.writerow([element[0], "old", element[1][0], "-".join(element[2])])
            writer.writerow([element[0], "new", element[1][1], "-".join(element[2])]+diff_row)

def output_video_diffs():
    if not diffs:
        append_to_no_diffs_csv()
        return

    out_path = os.path.join("diffs", os.path.basename(new_file).replace(".csv",
                                                                        "_diffs.csv"))
    with open(out_path, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(["original_csv_index", "old_new", "entry", "diff_indices",
                         "ordinal","onset","offset","object","utterance_type",
                         "object_present","speaker"])
        for element in diffs:
            diff_row = [" "]*8
            for index in element[2]:
                diff_row[int(index)] = "+++"
            writer.writerow([element[0], "old", element[1][0], "-".join(element[2])])
            writer.writerow([element[0], "new", element[1][1], "-".join(element[2])]+diff_row)

def figure_out_filetype(file):
    with open(file, "rU") as file:
        reader = csv.reader(file)
        header = reader.next()
        video_csv = False
        audio_csv = False
        for element in header:
            if "labeled_object" in element:
                video_csv = True
        if header[0] == "tier":
            audio_csv = True
        if audio_csv and video_csv:
            print "Check the formatting of these files. The headers are unusual"
    if video_csv:
        return "video"
    if audio_csv:
        return "audio"

def diff_audio(line_index, old, new):
    diff_indices = []
    for index, element in enumerate(old[:6]):
        if new[index] != element and index != 6:
            if index == 1 and new[index].lower() == element.lower():
                continue
            diff_indices.append(str(index))
    if diff_indices:
        diff_info = (line_index, [old, new], diff_indices)

        if "+" in old[6] and not old[6][0].islower():
            new[6] = old[6].lower().capitalize()
        else:
            new[6] = old[6]
            if old[6] != "NA" and any(not x.islower() for x in old[6]):
                cap_x, cap_y = number_of_capitals(new[1], old[6])
                if cap_x != cap_y:
                    new[6] = new[1]

        return (new, diff_info)
    else:
        if "+" in old[6] and not old[6][0].islower():
            new[6] = old[6].lower().capitalize()
        else:
            new[6] = old[6]
            if old[6] != "NA" and any(not x.islower() for x in old[6]):
                cap_x, cap_y = number_of_capitals(new[1], old[6])
                if cap_x != cap_y:
                    new[6] = new[1]
        return None

def group_diff_audio(old, new):
    matched = []
    not_matched = []

    old_group = old[:]
    new_group = new[:]

    old_count = len(old_group)
    new_count = len(new_group)

    while not group_match_condition(matched, not_matched, old_count, new_count):
        if len(old_group) == 0:
            for i in new_group:
                new_audiofile_data[i][6] = "***FIX ME***"
                not_matched.append(new_audiofile_data[i])
            break
        for new_index, new_element_index in enumerate(new_group):
            new_element = new_audiofile_data[new_element_index]

            for old_index, old_element_index in enumerate(old_group):
                old_element = old_audiofile_data[old_element_index]
                diff_result = diff_audio(new_index, old_element, new_element)
                if not diff_result:
                    matched.append(new_element)
                    del old_group[old_index]
                    del new_group[new_index]
                    break
                elif old_index == len(old_group) - 1:
                    if diff_result[1] not in diffs:
                        diffs.append(diff_result[1])
                    not_matched.append(new_element)
                    del old_group[old_index]
                    del new_group[new_index]
                    if len(old_group) == 0:
                        for i in new_group:
                            new_audiofile_data[i][6] = "***FIX ME***"
                            not_matched.append(new_audiofile_data[i])
                        return (matched, not_matched)

    #not_matched = [new_audiofile_data[index] for index in new_group if new_audiofile_data[index] not in matched]

    return (matched, not_matched)

def group_match_condition(matched, not_matched, old, new):
    if len(matched) == new:
        return True
    if len(matched + not_matched) == new:
        return True
    return False


def diff_video(line_index, old, new):
    if old[3].startswith("%com"):
        print
    diff_indices = []
    for index, element in enumerate(old[:7]):
        if new[index] != element and index != 7 and index != 0:
            if index == 3 and new[index].lower() == element.lower():
                continue
            diff_indices.append(str(index))
    if diff_indices:
        diff_info = (line_index, [old, new], diff_indices)
        if len(new) == 8:
            new[7] = old[7]
            if "+" in old[7] and not old[7][0].islower():
                new[7] = old[7].lower().capitalize()
            if old[7] != "NA" and any(not x.islower() for x in old[7]):
                cap_x, cap_y = number_of_capitals(new[3], old[7])
                if cap_x != cap_y:
                    new[7] = new[3]
        elif len(new) == 7:
            if "+" in old[7] and not old[7][0].islower():
                new.append(old[7].lower().capitalize())
            elif old[7] != "NA" and any(not x.islower() for x in old[7]):
                cap_x, cap_y = number_of_capitals(new[3], old[7])
                if cap_x != cap_y:
                    new.append(new[3])
            else:
                new.append(old[7])
        return (new, diff_info)
    else:
        if len(new) == 8:
            new[7] = old[7]
            if "+" in old[7] and not old[7][0].islower():
                new[7] = old[7].lower().capitalize()
            if old[7] != "NA" and any(not x.islower() for x in old[7]):
                cap_x, cap_y = number_of_capitals(new[3], old[7])
                if cap_x != cap_y:
                    new[7] = new[3]
        elif len(new) == 7:
            if "+" in old[7] and not old[7][0].islower():
                new.append(old[7].lower().capitalize())
            elif old[7] != "NA" and any(not x.islower() for x in old[7]):
                cap_x, cap_y = number_of_capitals(new[3], old[7])
                if cap_x != cap_y:
                    new.append(new[3])
            else:
                new.append(old[7])
        return None

def group_diff_video(old, new):
    matched = []
    not_matched = []

    old_group = old[:]
    new_group = new[:]

    old_count = len(old_group)
    new_count = len(new_group)

    while not group_match_condition(matched, not_matched, old_count, new_count):
        if len(old_group) == 0:
            for i in new_group:
                new_videofile_data[i][7] = "***FIX ME***"
                not_matched.append(new_videofile_data[i])
            break
        for new_index, new_element_index in enumerate(new_group):
            new_element = new_videofile_data[new_element_index]

            for old_index, old_element_index in enumerate(old_group):
                old_element = old_videofile_data[old_element_index]
                diff_result = diff_video(new_index, old_element, new_element)
                if not diff_result:
                    matched.append(new_element)
                    del old_group[old_index]
                    del new_group[new_index]
                    break
                elif old_index == len(old_group) - 1:
                    if diff_result[1] not in diffs:
                        diffs.append(diff_result[1])
                    not_matched.append(new_element)
                    del old_group[old_index]
                    del new_group[new_index]
                    if len(old_group) == 0:
                        for i in new_group:
                            the_entry = new_videofile_data[i]
                            the_entry[7] = "***FIX ME***"
                            not_matched.append(the_entry)
                        return (matched, not_matched)

    return (matched, not_matched)

def rewrite_video_ordinals():
    global video_merge_data
    sorted_data = sorted(video_merge_data, key=lambda data: int(data[0][1]))
    new_data = []
    i = 0
    for index, value in enumerate(sorted_data):
        for element in value:
            # if element[0] != i:
            #     print i
            element[0] = i
            i += 1
            new_data.append(element)

    video_merge_data = new_data

# def rewrite_video_ordinals2():
#     global video_merge_data
#     sorted_data = sorted(video_merge_data, key=lambda data: int(data[1]))
#     new_data = []
#
#     for index, entry in enumerate(sorted_data):
#         entry[0] = index
#         new_data.append(entry)
#
#     video_merge_data = new_data

def find_problem_diffs_audio():
    problems = []

    curr_index = 0
    for index, diff in enumerate(diffs):
        for comp_diff in diffs[index+1:]:
            if diff_match_video(diff, comp_diff):
                problems.append(diff)
    return problems

def find_problem_diffs_video():
    problems = []
    for index, diff in enumerate(diffs):
        for comp_diff in diffs[index+1:]:
            if diff_match_video(diff, comp_diff):
                problems.append(diff)
    return problems

def diff_match_audio(diff, comp_diff):
    if diff[1][0][1] == comp_diff[1][0][1] and \
       diff[1][0][2] == comp_diff[1][0][2] and \
       diff[1][0][3] == comp_diff[1][0][3]:
        return True
    return False

def diff_match_video(diff, comp_diff):
    if diff[1][0][1] == comp_diff[1][0][1] and \
       diff[1][0][2] == comp_diff[1][0][2] and \
       diff[1][0][3] == comp_diff[1][0][3]:
        return True
    return False


def append_to_fix_me_csv():
    with open(fix_me_csv, "a") as output:
        output.write("{}\n".format(os.path.basename(new_file)))

def append_to_no_diffs_csv():
    with open(diffs_csv, "a") as output:
        output.write("{}\n".format(os.path.basename(new_file)))

#
# def flatten_video_merge_data():
#     global video_merge_data
#     new_data = []
#     for group in video_merge_data:
#         for element in group:
#             if element not in new_data:
#                 new_data.append(element)
#     video_merge_data = new_data

if __name__ == "__main__":
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    output = sys.argv[3]

    batch_process = False
    fix_me_csv = ""
    diffs_csv = ""
    if len(sys.argv) > 4:
        batch_process = True
        fix_me_csv = sys.argv[5]
        diffs_csv = sys.argv[6]

    old_file_type = figure_out_filetype(old_file)
    new_file_type = figure_out_filetype(new_file)

    if old_file_type != new_file_type:
        print "old file and new file are of different types"
        print "old file = " + old_file_type
        print "new_file = " + new_file_type
        sys.exit(0)

    parse_old_file(old_file_type)
    parse_new_file(new_file_type)
    #
    # print "\nold_file_type = " + old_file_type
    # print "new_file_type = " + new_file_type

    if old_file_type == "video":
        merge_video2()
        #flatten_video_merge_data()
        #rewrite_video_ordinals2()
        rewrite_video_ordinals()
        output_merged_videocsv(output)
        if contains_new_word and batch_process:
            append_to_fix_me_csv()

    else:
        merge_audio()
        output_merged_audiocsv(output)
        if contains_new_word and batch_process:
            append_to_fix_me_csv()
