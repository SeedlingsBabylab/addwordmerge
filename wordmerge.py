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
    for index, element in enumerate(new_audiofile_data):
        indices = find_all_match_audio(element,
                                       old_audiofile_data)

        # find the correct index. elements with the same timestamp could
        # be different words, with different basic_levels. If there is a
        # -1 in the indices list, this means this a new entry, not originally
        # in the old csv file
        olddata_index = None
        for index in indices:
            if index == -1:
                break
            if old_audiofile_data[index][1] == element[1]:
                olddata_index = index
                # if none of the found timestamps have words equal to the
                # current element, then this is a new word that happens to
                # share timestamps with other words. olddata_index is still None

        # still haven't found it, must be a new entry
        if olddata_index is None:
            merge_data = element
            merge_data[6] = "***FIX ME***"
            audio_merge_data.append(merge_data)
            continue

        merge_data = old_audiofile_data[olddata_index]
        diff_result = diff_audio(index, merge_data, element)
        if diff_result:
            audio_merge_data.append(diff_result)
        else:
            audio_merge_data.append(merge_data)

def merge_video():
    for index, element in enumerate(new_videofile_data):
        indicies = find_all_match_video(element,
                                        old_videofile_data)
        olddata_index = None
        for index in indicies:
            if index == -1:
                break
            if old_videofile_data[index-2][3] == element[3]:
                olddata_index = index-2

        if olddata_index is None:
            merge_data = element
            if "%com" in merge_data[3]:
                merge_data.append("NA")
            else:
                merge_data.append("***FIX ME***")
            video_merge_data.append(merge_data)
            continue

        merge_data = old_videofile_data[olddata_index]
        diff_result = diff_video(index, merge_data, element)
        if diff_result:
            video_merge_data.append(diff_result)
        else:
            video_merge_data.append(merge_data)

def find_all_match_audio(entry, data):
    found =[]
    for index, element in enumerate(data):
        if audio_match(entry, element):
            found.append(index)
    if not found:
        found.append(-1)
    return found

def find_all_match_video(entry, data):
    found =[]
    for index, element in enumerate(data):
        if video_match(entry, element):
            found.append(index+2)
    if not found:
        found.append(-1)
    return found

def audio_match(new_item, old_item):
    if new_item[0] == old_item[0] and \
       new_item[1] == old_item[1] and \
       new_item[5] == old_item[5]:
        return True
    return False

def video_match(new_item, old_item):
    if new_item[1] == old_item[1] and \
       new_item[2] == old_item[2] and \
       new_item[3] == old_item[3]:
        return True
    return False

def output_merged_audiocsv(path):
    with open(path, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(["tier", "word", "utterance_type",
                        "object_present", "speaker", "timestamp",
                        "basic_level"])
        writer.writerows(audio_merge_data)

    if diffs:
        print "\nThere were other changes in the new file besides additions"
        print "Please check them in the diffs.csv file that was just made"
        print "It's in the /diffs folder in this script's directory\n"

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

    if diffs:
        print "\nThere were other changes in the new file besides additions"
        print "Please check them in the diffs.csv file that was just made"
        print "It's in the /diffs folder in this script's directory\n"

        output_video_diffs()

def output_audio_diffs():
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
    out_path = os.path.join("diffs", os.path.split(new_file)[1].replace(".csv",
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

def diff_audio(line, old, new):
    diff_indices = []
    for index, element in enumerate(old):
        if new[index] != element and index != 6:
            diff_indices.append(str(index))
    if diff_indices:
        diffs.append((line, [old, new], diff_indices))
        new[6] = old[6]
        return new
    else:
        return None

def diff_video(line, old, new):
    diff_indices = []
    for index, element in enumerate(old[:7]):
        if new[index] != element and index != 7 and index != 0:
            diff_indices.append(str(index))
    if diff_indices:
        diffs.append((line, [old, new], diff_indices))
        new.append(old[7])
        return new
    else:
        return None


if __name__ == "__main__":
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    output = sys.argv[3]

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
        merge_video()
        output_merged_videocsv(output)
    else:
        merge_audio()
        output_merged_audiocsv(output)


