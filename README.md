# Things to Know for extract.py



This script uses `argparse` for option to output to either a `.csv` or a `.json`.

```
python3 extract.py --format [csv or json]
```

If left empty, the script will output to .csv by default.


**Line 42:**

```
def fetch_all_plants(start_id=1, end_id=50):
```

In the arguments of this function you can specify how many rows you want by altering the `end_id`.
