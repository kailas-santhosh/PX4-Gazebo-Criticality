class EventManager:

    def __init__(self):
        self.events = []

    # ------------------------------------------

    def add_event(self, event):
        self.events.append(event)

    # ------------------------------------------

    def update(
        self,
        x,
        y,
        z,
        timestamp,
        experiment_start_time=None,
    ):

        for event in self.events:

            event.update(
                x=x,
                y=y,
                z=z,
                timestamp=timestamp,
                experiment_start_time=experiment_start_time,
            )

    # ------------------------------------------

    def finalize(self, timestamp):

        for event in self.events:

            event.finalize(timestamp)
