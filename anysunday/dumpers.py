import errno
import json


class TimePointFile:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        try:
            with open(self.filename, mode="r") as f:
                return json.load(f)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
            return {}

    def _save(self):
        with open(self.filename, mode="w") as f:
            json.dump(self.data, f, indent=2)

    def add_timepoint(self, dt: datetime.datetime, entry):
        self.data[int(dt.timestamp())] = entry
        self._save()

    def add_timepoint_now(entry, remove_runs=False):
        """
        Add a timepoint now.

        If remove_runs is True, and if the entryis identical to the two immediately
        previous timepoints, it will replace the most recent, e.g. if it's now 4:00,
        calling `add_timepoint_now([1, 4, 8])` would do the following to the
        example series:

            3:45 [1, 2, 3]
            3:50 [1, 4, 8]
        +++ 4:00 [1, 4, 8]

            3:45 [1, 2, 3]
            3:50 [1, 4, 8]
        --- 3:55 [1, 4, 8]
        +++ 4:00 [1, 4, 8]

        The idea behind the latter is that there wasn't actually any updates between
        3:50 and 4:00, so recording an interim point is moot.
        """
        now = datetime.datetime.now()
        return self.add_timepoint(now, entry)
