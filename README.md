# wordmerge
This script helps with updating basic_level.csv files after adding a new entry in the original .cha or .opf.

After exporting your updated .cha or .opf to a csv, you can use wordmerge.py to fill all the basic_level values from the original .csv into this new/updated csv file.

## usage

The script takes 3 arguments:

```bash
$: python wordmerge.py [original_csv] [new_csv] [output_path.csv]
```

This will output a new csv file with the two files merged. All the basic_level entries from the original will be filled into their appropriate places in the new file.
The new entries won't have basic_level's yet though, since they're new. They'll have "***FIX ME***" in the basic level column for that entry.

## diffs

If there are any differences between the entries in the original_csv and the new_csv, the script will output a diffs.csv file associated to the files you're merging.
You should make sure any differences found are intended and correct.
