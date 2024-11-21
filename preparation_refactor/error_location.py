import cirq

class Single_Error:
    def __init__(self, q: cirq.Qid, m: cirq.Moment, index: int, error_rate:float):
        self.q = q
        self.m = m
        self.index = index
        self.error_rate = error_rate
        self.propagated_to = []
        self.op = m.operation_at(q)


    def propagate(self,other):
        for location in other.propagated_to:
            if self.propagated_to.count(location) == 1:

                self.propagated_to.remove(location)
            else:
                self.propagated_to.append(location)

    def objective_cost_1(self):
        return len(self.propagated_to)*self.error_rate


#hash map
class ErrorLocation:
    def __init__(self, errors):
        self.flagged = False
        self.errors = errors

    def get_qubit(self):
        return self.errors[0].q

    def start_at(self) -> cirq.Moment:
        return self.errors[0].m

    def end_at(self) -> cirq.Moment:
        return self.errors[-1].m

    def add_single_error(self, single_error: Single_Error):
        self.errors.append(single_error)

    def set_flag(self):
        pass

    def combine(self,other):
        self.errors += other.errors
        del other

    def error_rate(self):
        pass

    def union(self,other):
        pass

    def difference(self,other):
        pass

    def objective_cost_1(self):
        cost = 0
        for error in self.errors:
            cost += error.objective_cost_1()
        return cost





