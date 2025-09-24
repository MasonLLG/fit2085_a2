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
        pass

    def add_transaction(self, transaction):
        """
        Analyse your time complexity of this method.
        """
        pass


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