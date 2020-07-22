from io import StringIO
import pandas as pd

message = 'r1963c8|in|0.480'

io_message = StringIO(message)
row = pd.read_csv(io_message, sep='|', header=None, dtype=str).iloc[0]

print(row)
print(type(row[2]))
