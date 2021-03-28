import re


class JackTokenizer:
    """Produces tokens from a .jack file"""
    KEYWORDS_STR = 'class|method|constructor|function|field|static|var|int|char|boolean|void|true|false|null|this|' \
                   'let|do|if|else|while|return'
    SYMBOLS_STR = '\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||\<|\>|=|~'
    INTEGER_CONSTANTS = '\d+'  # \d  - Digit (0-9)    +  - 1 or More
    STRING_CONSTANTS = '"[^"]*"'  # [^ ]  - Matches Characters not in the Brackets     *  - 0 or More
    IDENTIFIERS = '[A-z_][A-z_\d]*'  # []  - Matches Characters in Brackets

    def __init__(self, file):
        new_file = re.sub('//.*?\n', '\n', file)
        self._code = re.sub('/\*.*?\*/', '', new_file, flags=re.DOTALL)
        self._tokens = []
        split_code = re.split('(' + '|'.join(expression for expression in [self.SYMBOLS_STR, self.STRING_CONSTANTS])
                              + ')|\s+', self._code)
        for token in split_code:
            if token is None or re.match('^\s*$', token):
                continue

            for expression, token_type in [(self.KEYWORDS_STR, 'keyword'), (self.SYMBOLS_STR, 'symbol'),
                                           (self.INTEGER_CONSTANTS, 'integerConstant'),
                                           (self.STRING_CONSTANTS, 'stringConstant'), (self.IDENTIFIERS, 'identifier')]:
                if re.match(expression, token):
                    self._tokens.append((token_type, token))
                    break

    def advance(self):
        """Gets the next token from the input and makes it the current token. Initially there is no current token."""
        return self._tokens.pop(0)

    def current_token(self):
        """Returns the token type"""
        return self._tokens[0]
