from data_structures.linked_queue import LinkedQueue
from data_structures.linked_stack import LinkedStack

class Transaction:

    def __init__(self, timestamp, from_user, to_user):
        self.timestamp = timestamp
        self.from_user = from_user
        self.to_user = to_user
        self.signature = None  
    
    def sign(self):
        """
        :complexity:
        Let n = len(from_user) + len(to_user) + digits(timestamp) + 2.
        - Hash accumulation loop: O(n), one modular multiply/add per character.
        - Base-36 conversion loop: at most 36 iterations (since value < 36^36) → O(1).
        - Padding to fixed length: O(1).
        Overall: O(n) time.
        """
        value = 0
        base = 31
        TABLE_SIZE = 36**36

        ALPH = "0123456789abcdefghijklmnopqrstuvwxyz"

        data = str(self.timestamp) + "|" + self.from_user + "|" + self.to_user

        for char in data:
            value = (value * base + ord(char)) % TABLE_SIZE

        sig_str = ""

        while value > 0:
            value, rem = divmod(value, 36)
            sig_str = ALPH[rem] + sig_str

        if sig_str == "":
            sig_str = "0"
        
        if len(sig_str) < 36:
            sig_str = ("0" * (36 - len(sig_str))) + sig_str
        
        self.signature = sig_str
                
                




class ProcessingLine:
    def __init__(self, critical_transaction):
        """
        :complexity:
            Best & Worst: O(1) – just field initialisation.
        """
        self._critical_trans = critical_transaction
        # BEFORE (t <= critical): FIFO so we can output oldest -> newest before the critical
        self._before_critical = LinkedQueue()
        # AFTER (t > critical):  LIFO so we can output newest -> oldest after the critical
        self._after_critical = LinkedStack()
        # Locking / single-iterator flags
        self._it_created = False
        self._line_fixed = False

    def __iter__(self):
        """
        :complexity:
            Best & Worst: O(1) – set flags and return iterator.
        """
        if self._it_created:
            raise RuntimeError("Only one iterator can be created.")
        self._it_created = True
        self._line_fixed = True
        return ProcessingLineIterator(self)

    def add_transaction(self, transaction):
        """
        :complexity:
            Best & Worst: O(1) – one append or one push.
        """
        if self._line_fixed:
            raise RuntimeError("Iteration has started; no more transactions can be added.")
        if transaction.timestamp <= self._critical_trans.timestamp:
            self._before_critical.append(transaction)  # enqueue to BEFORE (FIFO)
        else:
            self._after_critical.push(transaction)     # push to AFTER (LIFO)


class ProcessingLineIterator:
    def __init__(self, line: ProcessingLine):
        """
        :complexity:
            Best & Worst: O(1) – store references and set stage.
        """
        self._before_critical = line._before_critical   # LinkedQueue
        self._after_critical  = line._after_critical    # LinkedStack
        self._critical_       = line._critical_trans
        self._stage = 0  # 0 = before, 1 = critical, 2 = after, 3 = done

    def __iter__(self):
        """
        :complexity:
            Best & Worst: O(1)
        """
        return self

    def __next__(self):
        """
        Return the next transaction in the required order;
        The order is:
          1) oldest -> newest (FIFO) BEFORE the critical
          2) critical (once)
          3) newest -> oldest (LIFO) AFTER the critical
        :raises StopIteration: when all transactions have been processed.
        :complexity:
            Best: O(1) – one queue serve / one stack pop / or the critical.
            Worst: O(1) per call; overall O(N) across the full traversal.
        """

        if self._stage == 0:
            if not self._before_critical.is_empty():
                tx = self._before_critical.serve()
                if tx.signature is None:
                    tx.sign()
                return tx
            self._stage = 1  

    
        if self._stage == 1:
            self._stage = 2
            tx = self._critical_
            if tx.signature is None:
                tx.sign()
            return tx


        if self._stage == 2:
            if not self._after_critical.is_empty():
                tx = self._after_critical.pop()
                if tx.signature is None:
                    tx.sign()
                return tx
            self._stage = 3  


        raise StopIteration


        

if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    # Here's something to get you started...
    transaction1 = Transaction(50, "alice", "bob")
    transaction2 = Transaction(100, "bob", "dave")
    transaction3 = Transaction(120, "dave", "frank")

    line = ProcessingLine(transaction2)
    line.add_transaction(transaction3)
    line.add_transaction(transaction1)

    print("Let's print the transactions... Make sure the signatures aren't empty!")
    line_iterator = iter(line)
    while True:
        try:
            transaction = next(line_iterator)
            print(f"Processed transaction: {transaction.from_user} -> {transaction.to_user}, "
                  f"Time: {transaction.timestamp}\nSignature: {transaction.signature}")
        except StopIteration:
            break