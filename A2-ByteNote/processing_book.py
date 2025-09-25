from data_structures import ArrayR

from processing_line import Transaction


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
            return

        if isinstance(current_page, ProcessingBook):
            # already a child book → go deeper
            current_page[one_transaction] = one_amount
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
        """Put an already-counted transaction deeper in the trie, without changing size.
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
            return

        if isinstance(current_page, ProcessingBook):
            current_page._move_leaf_without_count(one_transaction, one_amount)
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
        """
        pass
    
    def _get_only_leaf(self):
        """
        Find the one remaining leaf in this book (used for collapse).
        :complexity:
        """
        pass


    # task 2.3
    def __iter__(self):
        """
        Return an iterator over all (transaction, amount) pairs in alphabetical order.
        :complexity:
            
        """
        pass

    def __next__(self):
        """
        Return the next (transaction, amount) pair during iteration.
        :complexity:
            
        """
        pass

     def _collect_items(self, book):
        """
        collect all (transaction, amount) pairs recursively in page order.
        :complexity:
            
        """
        pass



    def sample(self, required_size):
        """
        1054 Only - 1008/2085 welcome to attempt if you're up for a challenge, but no marks are allocated.
        Analyse your time complexity of this method.
        """
        pass


if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.

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
