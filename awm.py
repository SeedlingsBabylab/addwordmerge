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
    print "hello"

def merge_video():
    print "hello"

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

def check_audio_timestamps():
    old_file_timestamps = [entry[5] for entry in old_audiofile_data]
    new_file_timestamps = [entry[5] for entry in new_audiofile_data]
    for index, timestamp in enumerate(old_file_timestamps):
        if timestamp not in new_file_timestamps:
            print "Timestamp at line: " + index + "  is only in the old file. Not found in new file\n"
    for index, timestamp in enumerate(new_file_timestamps):
        if timestamp not in old_file_timestamps:
            print "Timestamp at line: " + index + "  is only in the new file. Not found in old file\n"
            
if __name__ == "__main__":

    old_file = sys.argv[1]
    new_file = sys.argv[2]

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
    else:
        merge_audio()
