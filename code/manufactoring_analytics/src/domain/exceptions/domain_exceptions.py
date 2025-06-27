# src/domain/exceptions/domain_exceptions.py
class DomainException(Exception):
    """Base domain exception"""
    pass

class OrderNotFoundException(DomainException):
    """Raised when order is not found"""
    def __init__(self, order_id: str):
        super().__init__(f"Order with ID {order_id} not found")
        self.order_id = order_id

class MachineNotFoundException(DomainException):
    """Raised when machine is not found"""
    def __init__(self, machine_name: str):
        super().__init__(f"Machine {machine_name} not found")
        self.machine_name = machine_name

class InvalidDateRangeException(DomainException):
    """Raised when date range is invalid"""
    def __init__(self, message: str = "Invalid date range"):
        super().__init__(message)

class ExportFailedException(DomainException):
    """Raised when export operation fails"""
    def __init__(self, message: str):
        super().__init__(f"Export failed: {message}")

class SchedulerException(DomainException):
    """Raised when scheduler operation fails"""
    def __init__(self, message: str):
        super().__init__(f"Scheduler error: {message}")