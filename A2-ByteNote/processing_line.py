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
        Analyse your time complexity of this method.
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
        Analyse your time complexity of this method.
        """
        self._critical_trans=critical_transaction
        self._before_critical=LinkedStack()
        self._after_critical=LinkedQueue()
        self._it_created=False

    def __iter__(self):
        """
        Analyse your time complexity of this method.
        """
        if self._it_created:
            raise Exception("Only one iterator can be created at a time.")
        self._it_created=True 
        if    

    def add_transaction(self, transaction):
        """
        Analyse your time complexity of this method.
        """
        pass

class ProcessingLineIterator:
    def __init__(self, line: ProcessingLine):
        """
        Analyse your time complexity of this method.
        """
        self._before_critical=line._before_critical
        self._after_critical=line._after_critical
        self._critical_=line._critical_trans
        self.stage=0

    def __iter__(self):
        return self

    def __next__(self):  
        """
        Return the next transaction in the correct order and sign it if needed.
        :raises StopIteration: when all transactions have been processed.
        :complexity:
            Best: O(1) for returning a transaction from either the before-queue or after-stack, or the critical one.
            Worst: O(1) per call, so overall O(N) for N total transactions in the line, since each
                transaction is signed and returned exactly once.
        """
        #  Stage 0: before_critical group, oldest -> newest
        if self._stage == 0:
            if not self._before_critical.is_empty():
                tx = self._before_critical.serve()
                if tx.signature is None:
                    tx.sign()
                return tx
            self._stage = 1  

        # Stage 1: critical (exactly once)
        if self._stage == 1:
            self._stage = 2
            tx = self._critical_
            if tx.signature is None:
                tx.sign()
            return tx

        # Stage 2: after_critical group, newest -> oldest
        if self._stage == 2:
            if not self._after_critical.is_empty():
                tx = self._after_critical.pop()
                if tx.signature is None:
                    tx.sign()
                return tx
            self._stage = 3

        # Stage 3: DONE
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