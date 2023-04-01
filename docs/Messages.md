# Messages

## Introduction

The scripts should share information between them using a common format through
Kafka. For simplicity purposes, the chosen format is JSON. For example, a
message would look like this:
```json
{
    "event_code": "los-santos-26-03-2023",
    "data": "r5640c11|to|2:27.\nr5636c11|to|2:09.\nr5629c11|to|2:04.",
    "source": "ws-listener",
    "created_at": 1679818221.08147,
    "updated_at": 1679818221.083976
}
```

## Schema

The JSON is composed by several keys:
- `event_code`: A verbose code to identify the event.
- `data`: It may contain any kind of information, such as an string, a number
  or, even, another JSON.
- `source`: Name of the script that generated the message.
- `created_at`: Timestamp when the data was generated.
- `updated_at`: Timestamp when the data was updated by another script.

Optionally, it may contain these fields if there was any error with the message:
- `error_description`: Description of the error.
- `error_trace`: Trace with the details of the bugged code.

## Difference between `created_at` and `updated_at`

Each message contains two timestamps and each of them has a different purpose.
With these two values, we may describe things like the performance of the whole
pipeline (how much time took the data to reach the end of the pipeline of
scripts) or the longevity of the data.

On the one hand, `created_at` is necessary to know when the very first data was
created. This timestamp is immutable, that is, it will be always the same along
the pipeline. On the other hand, `updated_at` will change every time we need to
apply an action to the data, including analysis or transformation.
