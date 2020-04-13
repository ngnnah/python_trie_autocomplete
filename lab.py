# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, trie_type = None, value = None):
        self.value = value
        self.children = {}
        self.type = trie_type


    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        msg1 = "Trie expects type of str/tuple"
        msg2 = f"Trie expects type of {self.type}"
        if len(self.children) == 0:
            if not ((type(key) is str) or (type(key) is tuple)):
                raise TypeError(f"Type of key is {type(key)}, " + msg1)
            self.type = type(key)
        elif self.type is not None and type(key) != self.type:
            raise TypeError(f"Type of key is {type(key)}, " + msg2)

        # the trie 
        node = self
        for c in key:
            if self.type is tuple:
                c = (c,)
            node.children.setdefault(c, Trie(self.type))
            node = node.children[c]
        node.value = value


    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie()
        >>> t['bat'] = True
        >>> t['bat']
        True
        >>> t['bark'] = True
        >>> t['bar'] = 20
        >>> t['bar']
        20
        >>> t['bar'] = True
        >>> t['bar']
        True
        """
        if self.type is None or self.type != type(key): 
            raise TypeError('type of key and Trie mismatched')
        
        node = self.find(key)
        if node is False:
            raise KeyError(f"Trie does not contain key {key}")
        return node.value

    def find(self, key):
        """
        Helper function for __getitem__ and __contains__
        return False if key is not in the trie
        else return the value for given key
        """
        node = self
        for c in key:
            if self.type is tuple:
                c = (c,)
            if c not in node.children:
                return False
            node = node.children[c]
        if node.value is None:
            return False
        return node

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        self.__getitem__(key)
        self.__setitem__(key, None)

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        """
        return False if self.find(key) is False else True

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """

        def gen(key, node):
            if node.value is not None:
                yield (key, node.value)
            for child, trie in node.children.items():
                yield from gen(key + child, trie)

        if self.type is None: # empty Trie
            return
            yield
        else:
            node = self
            yield from gen(self.type(), node)

def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    t = Trie()
    for sentence in tokenize_sentences(text): 
        # each sentence is a string of words separated by whitespace
        for word in sentence.split():
            if word not in t:
                t[word] = 1
            else:
                t[word] = t[word] + 1
    return t

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    t = Trie()
    for sentence in tokenize_sentences(text):
        sentence = tuple(sentence.split())
        if sentence not in t:
            t[sentence] = 1
        else:
            t[sentence] += 1
    return t


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    >>> t = make_word_trie("bat bat bark bar")
    >>> autocomplete(t, "ba", 1)
    ['bat']
    >>> autocomplete(t, "be", 1)
    []
    """
    topword_and_freq = find_completes_prefix(trie, prefix, max_count)
    return [topword for topword, freq in topword_and_freq]


def find_completes_prefix(trie, prefix, max_count):
    """
    HELPER to the autocomplete function
    Returns a tuple (auto-completed word, freq)
    """
    if type(prefix) != trie.type: 
        raise TypeError('type of key and Trie mismatched')
    for c in prefix:
        if trie.type is tuple:
            c = (c,)
        if c not in trie.children: # prefix is not in trie
            return []
        trie = trie.children[c]

    # trie is now the prefix trie
    # concatenate prefix to key to get the completed words
    top_occuring = [(prefix + key, freq) for key, freq in trie]
    top_occuring.sort(key= lambda tup: tup[1], reverse= True)
    if max_count is None:
        return top_occuring
    return top_occuring[:max_count]


def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    # keys in trie are strings
    completions = autocomplete(trie, prefix, max_count)

    if max_count is not None and len(completions) == max_count: 
        # found all max_count completions
        return completions

    #Generate all possible edits (insert,delete,replace,transpose) from a given prefix
    edit_insert, edit_delete, edit_replace, edit_transpose = set(), set(), set(), set()
    for i in range(len(prefix)+1):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            edit_insert.add(prefix[:i] + c + prefix[i:])
    for i in range(len(prefix)):
        edit_delete.add(prefix[:i] + prefix[i+1:])
        for c in 'abcdefghijklmnopqrstuvwxyz':
            edit_replace.add(prefix[:i] + c + prefix[i+1:])
        if i > 0:
            edit_transpose.add(prefix[:i-1] + prefix[i] + prefix[i-1] + prefix[i+1:])
    possible_edits = edit_insert | edit_delete | edit_replace | edit_transpose
    
    completions = set(find_completes_prefix(trie, prefix, max_count))
    valid_edits = set()

    while possible_edits:
        edit = possible_edits.pop()
        if edit != prefix and edit in trie \
            and (edit, trie[edit]) not in completions: 
            # a valid edit, dont include edits that match auto-completions
            valid_edits.add((edit, trie[edit]))
    
    if max_count is not None: 
        valid_edits = set(sorted(valid_edits, key= lambda tup: tup[1], reverse= True)[:max_count-len(completions)])
    return [word for word, freq in completions | valid_edits]


def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
        
    def is_match(word, pattern, w_index, p_index):
        # base cases
        if w_index >= len(word): # matched all characters in word
            if p_index >= len(pattern): # matched all characters in pattern
                return True
            return set(pattern[p_index:]) == {'*'} # only * remains in pattern
        if p_index >= len(pattern): 
            return False

        # w_index < len(word), p_index < len(pattern)
        if (pattern[p_index] != '*'):
            # match single now, and match later
            w, p = word[w_index], pattern[p_index]
            return (p == '?' or p == w) and is_match(word, pattern, w_index+1, p_index+1)
        
        return (is_match(word, pattern, w_index, p_index+1)  # match * with zero character
                or is_match(word, pattern, w_index+1, p_index)) # match * with 1+ character

    return [(word, freq) for word, freq in trie if is_match(word, pattern, 0, 0)]


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    import doctest
    doctest.testmod()
   

    with open("alice.txt", encoding="utf-8") as f:
        text = f.read()
        trie = make_phrase_trie(text)
        print(autocomplete(trie, tuple(), 6))
        [('said', 'alice'), ('thought', 'alice'), ('wow',), ('said', 'the', 'caterpillar'), ('said', 'the', 'march', 'hare'), ('beauootiful', 'soooop')]
        print(len(tokenize_sentences(text)))
        print(len(list(trie)))

        trie = make_word_trie(text)
        print(autocorrect(trie, 'hear', 12))
        
        
    with open("metamorphosis.txt", encoding='utf-8') as f:
        text = f.read()
        trie = make_word_trie(text)
        print(autocomplete(trie, 'gre', 6))
        print(word_filter(trie, 'c*h'))

    with open("twocities.txt", encoding="utf-8") as f:
        text = f.read()
        trie = make_word_trie(text)
        print(word_filter(trie, 'r?c*t'))

    with open("pride_prejudice.txt", encoding="utf-8") as f:
        text = f.read()
        trie = make_word_trie(text)
        print(autocorrect(trie, 'hear'))

    with open("dracula.txt", encoding="utf-8") as f:
        # distinct words
        text = f.read()
        trie = make_word_trie(text)
        print(len(list(trie)))
        print(sum([len(sen.split()) for sen in tokenize_sentences(text)]))