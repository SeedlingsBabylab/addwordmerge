# wordmerge
This script helps with updating basic_level.csv files after adding a new entry in the original .cha or .opf.

After exporting your updated .cha or .opf to a csv, you can use wordmerge.py to fill all the basic_level values from the original .csv into this new/updated csv file.

## usage

##### wordmerge.py

The script takes 3 arguments:

```bash
$: python wordmerge.py [original_csv] [new_csv] [output_path.csv]
```

This will output a new csv file with the two files merged. All the basic_level entries from the original will be filled into their appropriate places in the new file.
The new entries won't have basic_level's yet though, since they're new. They'll have "***FIX ME***" in the basic level column for that entry.

##### batch_wordemerge.py

```
$: python batch_wordmerge.py [start_directory] [output_directory]
```

This will batch merge an entire directory (start_directory) containing pairs of old/new basic_level files. It will fill the [output_directory] with the result of merging the pairs. If there are diffs that are problematic (i.e. wordmerge can't update them and it requires a human doing it manually), it will fill a file with a list of these problem diffs. This file will be called "problem_diffs.txt". These entries will have the following form:

```
10_14_coderTE_audio_checkSD.csv --- old --- 195 -- ['*FAN', 'hands', 'i', 'y', 'MOT', '21705570_21708500', 'hand']
10_14_coderTE_audio_checkSD.csv --- new --- 195 -- ['*FAN', 'hands', 'd', 'y', 'FAT', '21705570_21708500', 'hand']
```

This means that in file "10_14_coderTE_audio_checkSD.csv", at index 195, there was an entry of the word "hands" that occured multiple times with the same timestamp, leading to ambiguity about which "hands" entry to update. Whenever there's multiple identical words with identical timestamps in a basic_level, these will be problem diffs that need humans to update manually. All other diffs will be updated automatically by the script. 

## diffs

If there are any differences between the entries in the original_csv and the new_csv, the script will output a diffs.csv file associated to the files you're merging.
You should make sure any differences found are intended and correct.
