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

        if "03_08" in old_file and "dots" in element:
            print
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
            #print "found a new word"
            continue

        if len(old_group) > 1:
            # if 227 in new_indices:
            #     print "hello"
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
                audio_merge_data.append([diff_result[0]])
            else:
                audio_merge_data.append([merge_data])

    fix_me_count_file.write("fix_me_count {}: {}\n".format(os.path.basename(old_file)[:5], fix_me_count))
    fix_me_count_file.close()

def merge_video():
    global contains_new_word
    for index, element in enumerate(new_videofile_data):
        indicies = find_all_match_video(element,
                                        old_videofile_data)
        olddata_index = None
        for index in indicies:
            if index == -1:
                break
            if old_videofile_data[index][3] == element[3]:
                olddata_index = index

        if olddata_index is None:
            merge_data = element
            if "%com" in merge_data[3]:
                if len(merge_data) == 8:
                    merge_data[7] = "NA"
                elif len(merge_data) == 7:
                    merge_data.append("NA")
            else:
                if len(merge_data) == 8:
                    merge_data[7] = "***FIX ME***"
                elif len(merge_data) == 7:
                    merge_data.append("***FIX ME***")
                contains_new_word = True
            video_merge_data.append(merge_data)
            continue

        merge_data = old_videofile_data[olddata_index]
        diff_result = diff_video(index, merge_data, element)
        if diff_result:
            video_merge_data.append(diff_result)
        else:
            video_merge_data.append(merge_data)

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
    split_new_time = new_item[5].split("_")
    split_old_time = old_item[5].split("_")
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
    old_time = [old_item[1], old_item[2]]
    new_time = [new_item[1], new_item[2]]

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
            diff_indices.append(str(index))
    if diff_indices:
        diff_info = (line_index, [old, new], diff_indices)
        #diffs.append((line_index, [old, new], diff_indices))
        new[6] = old[6]
        return (new, diff_info)
    else:
        new[6] = old[6]
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
    diff_indices = []
    for index, element in enumerate(old[:7]):
        if new[index] != element and index != 7 and index != 0:
            diff_indices.append(str(index))
    if diff_indices:
        diff_info = (line_index, [old, new], diff_indices)
        #diffs.append((line_index, [old, new], diff_indices))
        if len(new) == 8:
            new[7] = old[7]
        elif len(new) == 7:
            new.append(old[7])
        return (new, diff_info)
    else:
        if len(new) == 8:
            new[7] = old[7]
        elif len(new) == 7:
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
                            new_videofile_data[i][7] = "***FIX ME***"
                            not_matched.append(new_videofile_data[i])
                        return (matched, not_matched)

    return (matched, not_matched)

def rewrite_video_ordinals():
    global video_merge_data
    sorted_data = sorted(video_merge_data, key=lambda data: int(data[0][1]))
    new_data = []
    i = 0
    for index, value in enumerate(sorted_data):
        for element in value:
            element[0] = i
            i += 1
            new_data.append(element)

    video_merge_data = new_data

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
        rewrite_video_ordinals()
        output_merged_videocsv(output)
        if contains_new_word:
            append_to_fix_me_csv()

    else:
        merge_audio()
        output_merged_audiocsv(output)
        if contains_new_word and batch_process:
            append_to_fix_me_csv()
