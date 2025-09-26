from data_structures import ArrayR

from processing_line import Transaction

from data_structures.linked_stack import LinkedStack


class ProcessingBook:
    LEGAL_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, current_level=0, root_book=None):
        """
        :complexity:
            Best: O(1), only creates one ArrayR of length 36 and sets fields.
            Worst: O(1), same work regardless of input.
        """
        # make 36 pages for this book
        self.pages = ArrayR(len(ProcessingBook.LEGAL_CHARACTERS))
        self.current_level = current_level

        # the very first book (root) keeps global counters
        if root_book is None:
            self._root = self
            self.total_transactions = 0
            self.total_errors = 0
        else:
            self._root = root_book

        self.local_transactions = 0    
    
    def page_index(self, character):
        """
        You may find this method helpful. It takes a character and returns the index of the relevant page.
        Time complexity of this method is O(1), because it always only checks 36 characters.
        :complexity:
            Best: O(1), alphabet is constant size 36 so lookup is bounded.
            Worst: O(1), scanning fixed-size LEGAL_CHARACTERS string.
        
        """
        return ProcessingBook.LEGAL_CHARACTERS.index(character)

    
    def __setitem__(self, one_transaction: Transaction, one_amount: int):
        """
        :complexity:
            Best: O(L), when the page is empty and we insert directly, only check one character.
            Worst: O(L), when there are long collisions and we must recurse/promote down to the last character.
            L is the length of the transaction signature.
        """
        signature = one_transaction.signature
        index = self.page_index(signature[self.current_level])
        current_page = self.pages[index]

        if current_page is None:
            # page empty → just store the transaction and amount
            self.pages[index] = (one_transaction, one_amount)
            self._root.total_transactions += 1
            self.local_transactions += 1   
            return

        if isinstance(current_page, ProcessingBook):
            # already a child book → go deeper
            current_page[one_transaction] = one_amount
            self.local_transactions += 1
            return

        # otherwise the page has a leaf (old_transaction, old_amount)
        old_transaction, old_amount = current_page

        if old_transaction.signature == signature:
            # same transaction
            if old_amount != one_amount:
                self._root.total_errors += 1  # illegal update
            # if amounts are same → do nothing
            return
        else:
            # collision with different transaction
            # make a new child book one level deeper
            new_child_book = ProcessingBook(
                current_level=self.current_level + 1,
                root_book=self._root
            )
            # move old one into child (without counting again)
            new_child_book._move_leaf_without_count(old_transaction, old_amount)
            # put the child book into this page
            self.pages[index] = new_child_book
            # insert the new transaction into the child (normal counting)
            new_child_book[one_transaction] = one_amount
            self.local_transactions += 1

    def __getitem__(self, one_transaction: Transaction) -> int:
        """
        :complexity:
            Best: O(L), when the transaction is found directly at its page.
            Worst: O(L), when we must follow recursive books all the way to the last character.
            L is the length of the transaction signature.
        """
        signature = one_transaction.signature
        index = self.page_index(signature[self.current_level])
        current_page = self.pages[index]

        if current_page is None:
            raise KeyError("Transaction not found")

        if isinstance(current_page, ProcessingBook):
            return current_page[one_transaction]

        old_transaction, old_amount = current_page
        if old_transaction.signature == signature:
            return old_amount
        else:
            raise KeyError("Transaction not found")

    def _move_leaf_without_count(self, one_transaction: Transaction, one_amount: int):
        """ 
        :complexity:
            Best: O(L), when the correct page is empty at this level, we place the item immediately.
            Worst: O(L), when collisions continue for many levels until the signatures diverge.
            L is the length of the transaction signature.
        """
        signature = one_transaction.signature
        index = self.page_index(signature[self.current_level])
        current_page = self.pages[index]

        if current_page is None:
            self.pages[index] = (one_transaction, one_amount)
            self.local_transactions += 1
            return

        if isinstance(current_page, ProcessingBook):
            current_page._move_leaf_without_count(one_transaction, one_amount)
            self.local_transactions += 1
            return

        # still a collision deeper
        old_transaction, old_amount = current_page
        if old_transaction.signature == signature:
            return  # same one → ignore

        # promote again
        new_child_book = ProcessingBook(
            current_level=self.current_level + 1,
            root_book=self._root
        )
        new_child_book._move_leaf_without_count(old_transaction, old_amount)
        self.pages[index] = new_child_book
        new_child_book._move_leaf_without_count(one_transaction, one_amount)
        self.local_transactions += 1
    
    def get_error_count(self):
        """
        Returns the number of errors encountered while storing transactions.
        :complexity:
            Best: O(1), direct read from root field.
            Worst: O(1), no loops or recursion.
        
        """
        return self._root.total_errors
    
    def __len__(self) -> int:
        """
        :complexity:
            Best: O(1), direct read from root field.
            Worst: O(1), no loops or recursion.
        """
        return self._root.total_transactions
    

    # task 2.2 
    def __delitem__(self, one_transaction: Transaction):    
        """
        Delete a transaction. Collapse child book if only 1 left.
        :complexity:
            Best: O(L), when the transaction is found and removed directly.
            Worst: O(L), when we recurse deep and also collapse.
            L is the length of the transaction signature.
        """
        signature = one_transaction.signature
        index = self.page_index(signature[self.current_level])
        current_page = self.pages[index]

        if current_page is None:
            raise KeyError("Transaction not found")

        if isinstance(current_page, ProcessingBook):
            # recurse into child
            del current_page[one_transaction]
            self.local_transactions -= 1

            # collapse if child has only one item left
            if current_page.local_transactions == 1:
                only_leaf = current_page._get_only_leaf()
                self.pages[index] = only_leaf
            return

        # page has a leaf
        old_transaction, old_amount = current_page
        if old_transaction.signature == signature:
            self.pages[index] = None
            self._root.total_transactions -= 1
            self.local_transactions -= 1
            return
        else:
            raise KeyError("Transaction not found")


    
    def _get_only_leaf(self):
        """
        Find the one remaining leaf in this book (used for collapse).
        :complexity:
            Best: O(1), must check each page but constant bound 36.
            Worst: O(1), still constant, since alphabet is fixed 36.
        """
        for i in range(len(ProcessingBook.LEGAL_CHARACTERS)):
            slot = self.pages[i]
            if slot is None:
                continue
            if isinstance(slot, ProcessingBook):
                return slot._get_only_leaf()
            else:
                return slot
        return None


    # task 2.3
    def __iter__(self):
        """ 
        :complexity
        Best: O(1) if first leaf is near the start.
        Worst: O(L) if it has to descend down several nested books to reach the first leaf.
        Overall: O(L) worst-case setup.
        """
        self._stack = LinkedStack()
        self._stack.push((self,0))   # tuple = (book, index)
        self._next_item = None
        self._advance()   # move to first leaf
        return self

    def __next__(self):
        """
        :complexity
        Returning the result is O(1)
        """
        if self._next_item is None:
            raise StopIteration
        result = self._next_item
        self._advance()
        return result

    def _advance(self):
        """
        :complexity
        Amortized per call: O(1).
        Across all N items: O(N).
        """
        LEGAL = ProcessingBook.LEGAL_CHARACTERS
        L = len(LEGAL)
        self._next_item = None

        while len(self._stack) > 0:
            book, i = self._stack.pop()

            if i >= L:
                # done with this book
                continue

            # push back with next index to try later
            self._stack.push((book, i+1))

            page = book.pages[i]
            if page is None:
                continue

            if isinstance(page, ProcessingBook):
                # go deeper
                self._stack.push((page,0))
                continue

            # found a leaf
            self._next_item = page
            return

        # nothing left
        self._next_item = None



    def sample(self, required_size):
        """
        1054 Only - 1008/2085 welcome to attempt if you're up for a challenge, but no marks are allocated.
        Analyse your time complexity of this method.
        """
        pass


if __name__ == "__main__":
    """
    Write tests for your code here...
    We are not grading your tests, but we will grade your code with our own tests!
    So writing tests is a good idea to ensure your code works as expected.
    """
    # Let's create a few transactions
    tr1 = Transaction(123, "sender", "receiver")
    tr1.signature = "abc123"

    tr2 = Transaction(124, "sender", "receiver")
    tr2.signature = "0bbzzz"

    tr3 = Transaction(125, "sender", "receiver")
    tr3.signature = "abcxyz"

    # Let's create a new book to store these transactions
    book = ProcessingBook()

    book[tr1] = 10
    print(book[tr1])  # Prints 10

    book[tr2] = 20
    print(book[tr2])  # Prints 20

    book[tr3] = 30    # Ends up creating 3 other nested books
    print(book[tr3])  # Prints 30
    print(book[tr2])  # Prints 20

    book[tr2] = 40
    print(book[tr2])  # Prints 20 (because it shouldn't update the amount)

    # more test for task2.1
    print("error count:", book.get_error_count())  # expect 1
    print("book length:", len(book)) # expect 3

    t4 = Transaction(126, "x", "y"); t4.signature = "aaa111"
    t5 = Transaction(127, "x", "y"); t5.signature = "aaa222"
    book[t4] = 7
    book[t5] = 8
    assert book[t4] == 7 and book[t5] == 8
    print("Task 2.1 tests passed")

    del book[tr1]     # Delete the first transaction. This also means the nested books will be collapsed. We'll test that in a bit.
    try:
        print(book[tr1])  # Raises KeyError
    except KeyError as e:
        print("Raised KeyError as expected:", e)

    print(book[tr2])  # Prints 20
    print(book[tr3])  # Prints 30

    # We deleted T1 a few lines above, which collapsed the nested books.
    # Let's make sure that actually happened. We should be able to find tr3 sitting
    # in Page A of the book:
    print(book.pages[book.page_index('a')])  # This should print whatever details we stored of T3 and only T3

    # --- Clean collapse test for Task 2.2 ---

    b = ProcessingBook()

    x1 = Transaction(1, "s", "r"); x1.signature = "abc123"
    x2 = Transaction(2, "s", "r"); x2.signature = "abcxyz"

    b[x1] = 10
    b[x2] = 20

    # Both are under page 'a' -> nested book created
    idx_a = b.page_index('a')
    assert isinstance(b.pages[idx_a], ProcessingBook)

    # Delete one; child now has exactly 1 item -> should collapse to a leaf tuple
    del b[x1]

    slot = b.pages[idx_a]
    assert isinstance(slot, tuple), "Expected collapse to a leaf (transaction, amount) tuple"
    tx, amt = slot
    assert tx.signature == "abcxyz" and amt == 20
    print("Task 2.2 collapse test passed")

    # --- Iteration test for Task 2.3 ---
    b = ProcessingBook()
    t1 = Transaction(1,"s","r"); t1.signature = "a11111"
    t2 = Transaction(2,"s","r"); t2.signature = "z22222"
    b[t1] = 10
    b[t2] = 20

    for tx, amt in b:
        print(tx.signature, amt)
    # Output should be:
    # a11111 10
    # z22222 20