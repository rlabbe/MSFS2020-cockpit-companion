
class CacheRequest:
    """
    Wraps a data source so that values can be range-checked before returning.

    Parameters
    ----------
    data_source : object
        The object that supplies .get(key) calls.
    """

    def __init__(self, data_source):
        self.data_source = data_source
        self.previous_values_ = {}
        self.ranges_ = {}

    def register_range(self, key, min_val, max_val):
        """
        Registers a valid range for a specific key.

        Sometimes we get bogus data from MSFS, this filters it out.

        Parameters
        ----------
        key : str
            The name of the datapoint.
        min_val : float
            The minimum acceptable value.
        max_val : float
            The maximum acceptable value.
        """
        self.ranges_[key] = (min_val, max_val)

    def get(self, key):
        """
        Retrieves a value for the given key, returning cached value if the new value
        is out of range. If no previous value exists when out of range, returns
        the new value.

        Parameters
        ----------
        key : str
            The datapoint name to retrieve.

        Returns
        -------
        float, int, str
            The validated value (cached if the new value is out of range).
        """

        # sometimes we get None, not sure why. But propogating that through the system just
        # causes problems in the render. So we force it to 0. if necessary
        new_value = self.data_source.get(key)

        # If no range is registered for this key, always return fresh data, saving
        if key not in self.ranges_:
            if new_value is None:
                new_value = 0.
            else:
                self.previous_values_[key] = new_value
            return new_value

        min_val, max_val = self.ranges_[key]
        if new_value is not None and min_val <= new_value <= max_val:
            self.previous_values_[key] = new_value
            return new_value
        else:
            print(f"Value {new_value} for {key} out of range ({min_val}, {max_val})")
            # Out of range - return previous if it exists, otherwise valid minimum
            return self.previous_values_.get(key, min_val)
