import csv
import sys

old_file = ""
new_file = ""

old_audiofile_data = []
new_audiofile_data = []
audio_merge_data = []

old_videofile_data = []
new_videofile_data = []
video_merge_data = []

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
    for element in new_audiofile_data:
        indices = find_all_with_timestamp_audio(element[5],
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
            merge_data[6] = "FIX ME"
            audio_merge_data.append(merge_data)
            continue

        merge_data = old_audiofile_data[olddata_index]
        audio_merge_data.append(merge_data)

def merge_video():
    print "hello"

def find_all_with_timestamp_audio(timestamp, data):
    found = []
    for index, element in enumerate(data):
        if element[5] == timestamp:
            found.append(index)
    if not found:
        found.append(-1)
    return found

def output_merged_audiocsv(path):
    with open(path, "wb") as file:
        writer = csv.writer(file)
        writer.writerow(["tier", "word", "utterance_type",
                        "object_present", "speaker", "timestamp",
                        "basic_level", "comment"])
        writer.writerows(audio_merge_data)
#
# def output_merged_videocsv(path):
#


# def check_audio_diff():
#     print "hello"


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

    print "\nold_file_type = " + old_file_type
    print "new_file_type = " + new_file_type

    if old_file_type == "video":
        merge_video()
        output_merged_videocsv(output)
    else:
        merge_audio()
        output_merged_audiocsv(output)
