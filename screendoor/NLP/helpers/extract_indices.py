class ExtractIndices:

    def __init__(self, starting_index=0):
        self.lower_bound = starting_index
        self.upper_bound = starting_index

    def update_lower_bound(self, index):
        if index < self.lower_bound:
            self.lower_bound = index

    def update_upper_bound(self, index):
        if index > self.upper_bound:
            self.upper_bound = index

    def update_indices_with_index(self, index):
        self.update_lower_bound(index)
        self.update_upper_bound(index)

    def update_indices_with_list(self, list):
        for index in list:
            self.update_lower_bound(index)
            self.update_upper_bound(index)

    def retrieve_indices(self,):
        return [self.lower_bound, self.upper_bound]

    def get_lower_bound(self):
        return self.lower_bound

    def get_upper_bound(self):
        return self.upper_bound

    def does_not_contain(self, index):
        if index < self.lower_bound and index > self.update_upper_bound:
            return True
        return False

    def __repr__(self):
        return str(self.lower_bound) + ' - ' + str(self.upper_bound)
