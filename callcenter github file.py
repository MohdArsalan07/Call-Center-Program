# =========================================================
# CALL CENTER MANAGEMENT SYSTEM
# =========================================================

from abc import ABC, abstractmethod
from collections import deque
from enum import Enum



# =========================================================
# ENUMS
# =========================================================

class Rank(Enum):
    OPERATOR = 0
    SUPERVISOR = 1
    DIRECTOR = 2


class CallState(Enum):
    READY = 0
    IN_PROGRESS = 1
    COMPLETE = 2


# =========================================================
# CALL CLASS
# =========================================================

class Call:

    def __init__(self, caller_name, rank):
        self.caller_name = caller_name
        self.rank = rank
        self.state = CallState.READY
        self.employee = None

    def __str__(self):
        return f"Caller: {self.caller_name}, Rank: {self.rank.name}"


# =========================================================
# ABSTRACT EMPLOYEE CLASS
# =========================================================

class Employee(ABC):

    def __init__(self, emp_id, name, rank, call_center):

        self.emp_id = emp_id
        self.name = name
        self.rank = rank
        self.call_center = call_center
        self.call = None

    # -----------------------------------------------------

    def is_free(self):
        return self.call is None

    # -----------------------------------------------------

    def take_call(self, call):

        self.call = call
        call.employee = self
        call.state = CallState.IN_PROGRESS

        print(f"{self.rank.name} {self.name} is handling call from {call.caller_name}")

    # -----------------------------------------------------

    def complete_call(self):

        if self.call is not None:

            print(f"{self.name} completed call of {self.call.caller_name}")

            self.call.state = CallState.COMPLETE
            self.call = None

            # Check queued calls
            self.call_center.assign_waiting_calls()

    # -----------------------------------------------------

    @abstractmethod
    def escalate_call(self):
        pass

    # -----------------------------------------------------

    def _escalate_call(self):

        if self.call is None:
            print("No active call to escalate.")
            return

        print(f"{self.name} escalated the call.")

        self.call.state = CallState.READY

        escalated_call = self.call
        self.call = None

        self.call_center.dispatch_call(escalated_call)


# =========================================================
# OPERATOR CLASS
# =========================================================

class Operator(Employee):

    def __init__(self, emp_id, name, call_center):
        super().__init__(emp_id, name, Rank.OPERATOR, call_center)

    def escalate_call(self):

        if self.call is not None:
            self.call.rank = Rank.SUPERVISOR
            self._escalate_call()


# =========================================================
# SUPERVISOR CLASS
# =========================================================

class Supervisor(Employee):

    def __init__(self, emp_id, name, call_center):
        super().__init__(emp_id, name, Rank.SUPERVISOR, call_center)

    def escalate_call(self):

        if self.call is not None:
            self.call.rank = Rank.DIRECTOR
            self._escalate_call()


# =========================================================
# DIRECTOR CLASS
# =========================================================

class Director(Employee):

    def __init__(self, emp_id, name, call_center):
        super().__init__(emp_id, name, Rank.DIRECTOR, call_center)

    def escalate_call(self):
        print("Director cannot escalate further.")


# =========================================================
# CALL CENTER CLASS
# =========================================================

class CallCenter:

    def __init__(self):

        self.operators = []
        self.supervisors = []
        self.directors = []

        self.call_queue = deque()

    # -----------------------------------------------------
    # ADD EMPLOYEES
    # -----------------------------------------------------

    def add_operator(self, operator):
        self.operators.append(operator)

    def add_supervisor(self, supervisor):
        self.supervisors.append(supervisor)

    def add_director(self, director):
        self.directors.append(director)

    # -----------------------------------------------------
    # DISPATCH CALL
    # -----------------------------------------------------

    def dispatch_call(self, call):

        employee = None

        # Operator Call
        if call.rank == Rank.OPERATOR:

            employee = self.find_free_employee(self.operators)

            if employee is None:
                employee = self.find_free_employee(self.supervisors)

            if employee is None:
                employee = self.find_free_employee(self.directors)

        # Supervisor Call
        elif call.rank == Rank.SUPERVISOR:

            employee = self.find_free_employee(self.supervisors)

            if employee is None:
                employee = self.find_free_employee(self.directors)

        # Director Call
        elif call.rank == Rank.DIRECTOR:

            employee = self.find_free_employee(self.directors)

        # Assign or Queue
        if employee:
            employee.take_call(call)

        else:
            print(f"No employee available. Queuing call from {call.caller_name}")
            self.call_queue.append(call)

    # -----------------------------------------------------
    # FIND FREE EMPLOYEE
    # -----------------------------------------------------

    def find_free_employee(self, employees):

        for emp in employees:
            if emp.is_free():
                return emp

        return None

    # -----------------------------------------------------
    # ASSIGN WAITING CALLS
    # -----------------------------------------------------

    def assign_waiting_calls(self):

        if len(self.call_queue) == 0:
            return

        print("\nChecking queued calls...\n")

        pending_calls = len(self.call_queue)

        for _ in range(pending_calls):

            call = self.call_queue.popleft()

            before = self.total_busy_employees()

            self.dispatch_call(call)

            after = self.total_busy_employees()

            # If call still not assigned
            if before == after:
                self.call_queue.append(call)

    # -----------------------------------------------------
    # TOTAL BUSY EMPLOYEES
    # -----------------------------------------------------

    def total_busy_employees(self):

        count = 0

        all_employees = (
            self.operators +
            self.supervisors +
            self.directors
        )

        for emp in all_employees:
            if not emp.is_free():
                count += 1

        return count


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    print("\n=================================================")
    print("      CALL CENTER MANAGEMENT SYSTEM")
    print("=================================================\n")

    # -----------------------------------------------------
    # CREATE CALL CENTER
    # -----------------------------------------------------

    center = CallCenter()

    # -----------------------------------------------------
    # CREATE EMPLOYEES
    # -----------------------------------------------------

    op1 = Operator(1, "Arsalan", center)
    op2 = Operator(2, "Aban", center)

    sup1 = Supervisor(3, "Aqsa", center)

    dir1 = Director(4, "Bhatti", center)

    # -----------------------------------------------------
    # ADD EMPLOYEES
    # -----------------------------------------------------

    center.add_operator(op1)
    center.add_operator(op2)

    center.add_supervisor(sup1)

    center.add_director(dir1)

    # -----------------------------------------------------
    # CREATE CALLS
    # -----------------------------------------------------

    call1 = Call("Customer A", Rank.OPERATOR)
    call2 = Call("Customer B", Rank.OPERATOR)
    call3 = Call("Customer C", Rank.OPERATOR)
    call4 = Call("VIP Customer", Rank.DIRECTOR)
    call5 = Call("Customer D", Rank.OPERATOR)

    # -----------------------------------------------------
    # DISPATCH CALLS
    # -----------------------------------------------------

    print("======= DISPATCHING CALLS =======\n")

    center.dispatch_call(call1)
    center.dispatch_call(call2)
    center.dispatch_call(call3)
    center.dispatch_call(call4)
    center.dispatch_call(call5)

    # -----------------------------------------------------
    # ESCALATION
    # -----------------------------------------------------

    print("\n======= ESCALATING CALL =======\n")

    op1.escalate_call()

    # -----------------------------------------------------
    # COMPLETE CALLS
    # -----------------------------------------------------

    print("\n======= COMPLETING CALLS =======\n")

    op2.complete_call()

    sup1.complete_call()

    dir1.complete_call()

    # -----------------------------------------------------

    print("\n=================================================")
    print("              PROGRAM FINISHED")
    print("=================================================\n")
