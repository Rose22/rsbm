class BaseInterpreter(object):
    """Handles command-line arguments"""

    def __init__(self):
        self._helpmsg = ""

        # Contains a dictionary that maps words to functions
        self._funcmap = {}

        self._separator = "-------------\n"

    def interpret(self, args):
        """Calls the method appropriate to the command-line arguments presented, using the function map (_funcmap) defined in derived classes"""

        # No args? display help
        if len(args) <= 1:
            print self._helpmsg
            return True

        # Don't proceed if the command doesn't exist
        proceed = False
        for command in self._funcmap.keys():
            if command == args[1]:
                proceed = True

        if not proceed:
            return False

        # Run the instance method determined by the user's chosen command
        func = self._funcmap.get(args[1])
        return func(args)
