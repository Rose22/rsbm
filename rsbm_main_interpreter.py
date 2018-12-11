import datetime
import json

import rsbm_interpreter
import rsbm_calculator
from config import *

class MainInterpreter(rsbm_interpreter.BaseInterpreter):
    """Handles all user interaction with the program"""

    def __init__(self, storage):
        super(MainInterpreter, self).__init__()

        # Storage (save file)
        self._storage = storage

        # Used for mapping command line arguments to instance methods
        self._funcmap = {
            'add': self.add,
            'set': self.set,
            'del': self.delete,
            'list': self.list,
            'check': self.check,
            'uncheck': self.uncheck,
            'bank': self.bank_balance,
            'next_month': self.next_month,
            'api': self.api,
        }

        # Calculator
        self._calculator = rsbm_calculator.RsbmCalculator()
        self._calculations = self._calculator.calculate(self._storage.data)
        self._c = self._calculations

        # Sort the list of commands
        commands = []
        for command in self._funcmap.keys():
            commands.append(command)

        commands.sort()

        self._helpmsg = """
Welcome to Rose's Simple Budget Manager (RSBM)

For first-time usage:
First, add your income sources: rsbm add income my_source my_amount_of_money (example: rsbm add income Paycheck 1500)
Then, add your bills: rsbm add bill name amount_of_money due_date
Then, add your budget categories: rsbm add budget groceries 200
Now look at your budget: rsbm list budgets

The commands that are available are: %s
Use any of them without further parameters to get more information about the commands.
""" % ', '.join(commands)

    # Internal functions
    # -------------
    def _format_name(self, name):
        return name.replace('_', ' ')

    def _format_name_reverse(self, name):
        return name.replace(' ', '_').lower()

    def _find_by_name(self, list, name):
        """Find an item by name"""

        index = 0
        target_index = 0
        found = False
        for item in list:
            if item['name'] == name:
                target_index = index
                found = True

            index += 1

        if not found:
            return None

        return target_index

    def _translate_item_type(self, item_type):
        "Singular to plural for item types"

        list_name = False

        if item_type == "income":
            list_name = "income"
        elif item_type == "budget":
            list_name = "budgets"
        elif item_type == "bill":
            list_name = "monthly_bills"
        elif item_type == "expense":
            list_name = "expenses"

        return list_name

    def _help_on_type(self, item_type):
        """Displays individual help texts for each item type"""

        if item_type == "bill":
            return "<name> <price> <day of month>"
        elif item_type == "expense":
            return "<category> <name> <price>"
        elif item_type == "budget":
            return "<name>"
        elif item_type == "income":
            return "<name> <price>"

    # API
    # -------------
    def api(self, args):
        """Calls the command supplied with API mode turned on"""

        cmd = args[2]
        if cmd not in self._funcmap.keys():
            return json.dumps(False)

        del(args[0])
        return self._funcmap[cmd](args, api=True)

    # Item functions
    # -------------
    def add(self, args, api=False):
        """Add an item of the user's choosing to the corresponding list"""

        if len(args) <= 2:
            if not api:
                available_types = ', '.join(self._storage.data.keys())

                output = ""
                output += "Usage: add <type> <type stuff>\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return json.dumps(False)
        if len(args) <= 3:
            if not api:
                output = "Usage: add %s %s" % (args[2], self._help_on_type(args[2]))
                return output
            else:
                return json.dumps(False)

        list_name = self._translate_item_type(args[2])

        new_item = {}

        if list_name == "income":
            new_item['name'] = args[3]
            new_item['price'] = float(args[4])
            new_item['paid'] = False
        elif list_name == "budgets":
            new_item['name'] = args[3]
            new_item['price'] = args[4]
        elif list_name == "monthly_bills":
            new_item['name'] = args[3]
            new_item['price'] = float(args[4])
            new_item['day'] = int(args[5])
            new_item['paid'] = False
        elif list_name == "expenses":
            new_item['name'] = args[3]
            new_item['price'] = float(args[4])
            new_item['budget'] = self._format_name_reverse(args[5])
        else:
            return "Unknown item type."

        new_item['name'] = self._format_name_reverse(new_item['name'])

        self._storage.data[list_name].append(new_item)
        self._storage.save()

        if api:
            return json.dumps(True)

        return "New %s \"%s\" added to %s" % (args[2], self._format_name(new_item['name']), self._format_name(list_name))

    def set(self, args, api=False):
        """Edit an item of the user's choosing"""

        if len(args) <= 2:
            if not api:
                available_types = ', '.join(self._storage.data.keys())

                output = ""
                output += "Usage: set <type> <type stuff>\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return json.dumps(False)
        if len(args) <= 3:
            if not api:
                output = "Usage: set %s %s" % (args[2], self._help_on_type(args[2]))
                return output
            else:
                return json.dumps(False)

        list_name = self._translate_item_type(args[2])
        item_name = self._format_name_reverse(args[3])
        target_index = self._find_by_name(self._storage.data[list_name], item_name)

        if target_index == None:
            if not api:
                return "Could not find that %s" % args[2]
            else:
                return json.dumps(False)

        modified_item = self._storage.data[list_name][target_index]
        if list_name == "income":
            modified_item['name'] = args[3]
            modified_item['price'] = float(args[4])
            modified_item['paid'] = False
        elif list_name == "budgets":
            modified_item['name'] = args[3]
            modified_item['price'] = float(args[4])
        elif list_name == "monthly_bills":
            modified_item['name'] = args[3]
            modified_item['price'] = float(args[4])
            modified_item['day'] = int(args[5])
            modified_item['paid'] = False
        elif list_name == "expenses":
            modified_item['name'] = args[3]
            modified_item['price'] = float(args[4])
            modified_item['budget'] = self._format_name_reverse(args[5])
        else:
            return "Unknown item type."

        modified_item['name'] = self._format_name_reverse(modified_item['name'])

        self._storage.data[list_name][target_index] = modified_item
        self._storage.save()

        if api:
            return json.dumps(True)

        return "%s \"%s\" modified." % (args[2], self._format_name(args[3]))

    def delete(self, args, api=False):
        """Delete an item by name"""

        if len(args) <= 3:
            if not api:
                available_types = ', '.join(self._storage.data.keys())

                output = ""
                output += "Usage: del <type> <name>\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return json.dumps(False)

        item_name = self._format_name_reverse(args[3])
        list_name = self._translate_item_type(args[2])
        target_index = self._find_by_name(self._storage.data[list_name], item_name)

        if target_index == None:
            if not api:
                return "Could not find that %s" % args[2]
            else:
                return json.dumps(False)

        del self._storage.data[list_name][target_index]
        self._storage.save()

        if api:
            return json.dumps(True)

        return "%s \"%s\" deleted from %s." % (args[2].capitalize(), self._format_name(item_name), self._format_name(list_name))

    def list(self, args, api=False):
        """Print any of the lists as human-readable tables"""

        output = ""

        # Initialization
        if len(args) <= 2:
            if not api:
                available_types = ', '.join(self._storage.data.keys())
                output += "Usage: list type\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return json.dumps(False)

        list_name = args[2]
        if list_name == "bills": list_name = "monthly_bills"

        # API support.. spit out pure YAML data
        if api:
            return json.dumps(self._storage.data[list_name])

        if list_name not in self._storage.data.keys():
            return "That type does not exist."

        # Headers
        if list_name == "budgets":
            output += "| %-60s| %-9s| %-10s| %-10s |\n\n" % ("Name", "Budgeted", "Spent", "Available")
        elif list_name == "monthly_bills":
            output += "| %-2s| %-60s| %-10s| %-4s |\n\n" % ("P", "Name", "Cost", "Day")
        elif list_name == "income":
            output += "| %-2s| %-60s| %-10s |\n\n" % ("P", "Name", "Cost")
        elif list_name == "expenses":
            output += "| %-30s| %-30s| %-8s|\n\n" % ("Name", "Budget", "Price")

        if len(self._storage.data[list_name]) == 0:
            output += "No items\n"

        total_price = 0
        # Different list depending on list type
        for item in self._storage.data[list_name]:
            if list_name == "budgets":
                budget_data = self._calculator.calculate_budget(item, self._storage.data['expenses'])

                output += "| %-60s| $%-8.2f| -$%-8.2f| $%-8.2f |\n" % (self._format_name(item['name']).capitalize(), item['price'], budget_data['expenses_total'], budget_data['available_total'])
                total_price += item['price']
            elif list_name == "monthly_bills":
                paid_string = "O"
                if item['paid']: paid_string = "X"
                output += "| %-2s| %-60s| $%-9.2f| %-4d |\n" % (paid_string, self._format_name(item['name']).capitalize(), item['price'], item['day'])
                total_price += item['price']
            elif list_name == "expenses":
                if len(args) > 3:
                    if item['budget'] == self._format_name_reverse(args[3]):
                        output += "| %-60s| $%.2f|\n" % (self._format_name(item['name']).capitalize(), item['price'])
                        total_price += item['price']
                else:
                    output += "| %-30s| %-30s| $%-6.2f |\n" % (self._format_name(item['name']).capitalize(), self._format_name(item['budget']).capitalize(), item['price'])
                    total_price += item['price']
            elif list_name == "income":
                paid_string = "O"
                if item['paid']: paid_string = "X"

                output += "| %-2s| %-60s| $%-9.2f |\n" % (paid_string, self._format_name(item['name']).capitalize(), item['price'])
                total_price += item['price']

        output += "\n"

        if len(self._storage.data[list_name]) == 0:
            return output

        # Footer
        if list_name == "budgets":
            if total_price == 0:
                return output

            output += "%d%% ($%.2f) of total currently budgetable $%.2f is assigned to budgets." % (self._c['budget_percent_budgetable'], self._c['budget_total'], self._c['budgetable_total'])
            if (self._c['budget_overbudgeted'] >= 1):
                output += " You've gone $%.2f over the working budget.\n" % self._c['budget_overbudgeted']
            else:
                output += " Still available for budgeting: $%.2f\n" % (self._c['budgetable_available'])

            output += "%d%% ($%.2f) of total monthly budgetable $%.2f is assigned to budgets." % (self._c['budget_percent_expected_budgetable'], self._c['budget_total'], self._c['expected_budgetable_total'])
            if (self._c['expected_budgetable_overbudgeted'] >= 1):
                output += " You've gone $%.2f over the monthly budget.\n" % self._c['expected_budgetable_overbudgeted']
            else:
                output += " Still available for budgeting: $%.2f\n" % (self._c['expected_budgetable_available'])

            output += "%d%% ($%.2f) of total budgeted $%.2f has been spent so far." % (self._c['spent_percent_budget'], self._c['spent_total'], self._c['budget_total'])
            if (self._c['budget_overspent'] >= 1):
                output += " You've spent $%.2f over your budget.\n" % self._c['budget_overspent']
            else:
                output += " You have $%.2f left to spend inside your budget.\n" % (self._c['spendable_in_budget'])

            output += "\n"
            output += "$%.2f will currently be left over at the end of the month.\n" % (self._c['leftover'])
            output += "$%.2f would be left over at the end of the month if you spent all of your budget.\n" % (self._c['budgetable_total']-self._c['budget_total'])
            output += "\n"
            output += "Your current bank balance should be: $%.2f\n" % self._c['bank_balance']
        elif list_name == "income":
            output += "Total currently received: $%.2f\n" % self._c['received_income_total']
            output += "Total to still receive: $%.2f\n" % (self._c['expected_income_total']-self._c['received_income_total'])
            output += "Total expected income: $%.2f\n" % total_price
        elif list_name == "monthly_bills":
            output += "Total paid so far: %.2f\n" % (self._c['paid_bills_total'])
            output += "Total still to be paid: %.2f\n" % (self._c['expected_bills_total']-self._c['paid_bills_total'])
            output += "Total: $%.2f\n" % self._c['expected_bills_total']
        else:
            output += "Total: $%.2f\n" % total_price

        return output

    def check(self, args, invert=False, api=False):
        """Mark an income item as received or a bill as paid (and the inverse)"""

        if len(args) <= 3:
            if not api:
                return "Usage: check income/bill <name>"
            else :
                return json.dumps(False)

        target_category = ''
        if args[2] == 'bill':
            target_category = 'monthly_bills'
        elif args[2] == 'income':
            target_category = 'income'
        else:
            if not api:
                return "That is not a bill or income source."
            else:
                return json.dumps(False)

        target_index = self._find_by_name(self._storage.data[target_category], self._format_name_reverse(args[3]))

        if target_index == None:
            return "Could not find that bill."

        if not invert:
            self._storage.data[target_category][target_index]['paid'] = True
            output = "%s \"%s\" marked as paid." % (args[2], args[3])
        else:
            self._storage.data[target_category][target_index]['paid'] = False
            output = "%s \"%s\" marked as not paid." % (args[2], args[3])
        self._storage.save()

        if api:
            return json.dumps(True)

        return "%s \"%s\" marked as paid." % (args[2], args[3])

    def uncheck(self, args, api=False):
        """Calls check() with an argument that makes it do the inverse of checking (unchecking)"""
        
        return self.check(self, args, invert=True, api=api)

    # Calculation display
    # -------------
    def bank_balance(self, args, api=False):
        """Show what the bank balance is calculated as, in order to make sure it's synced up to your bank"""

        output = ""

        if api:
            formatted_balance = "%.2f" % (self._c['bank_balance'])
            return json.dumps(float(formatted_balance))

        output += "BANK BALANCE CALCULATION\n"
        output += "Your bank balance should match the outcome of this calculation.\n"
        output += self._separator

        output += "Current total received income ($%.2f)\n-\nPaid bills ($%.2f)\n-\nTotal spent from budget ($%.2f)\n=\n" % (self._c['received_income_total'], self._c['paid_bills_total'], self._c['spent_total'])
        output += "$%.2f\n" % (self._c['bank_balance'])

        return output

    # Misc
    # -------------
    def debug(self, args):
        """debug function (DEV)"""

        """
        # Create budget leftover trackers
        date_string = datetime.date.today().strftime("%B_%Y").lower()


        self._storage.data['budget_leftovers'][date_string] = []

        index = 0
        for budget in self._storage.data['budgets']:
            # Calculate how much is left over
            total_spent_in_budget = 0
            for expense in self._storage.data['expenses']:
                if expense['budget'] == budget['name']:
                    total_spent_in_budget += expense['price']

            leftover = budget['price']-total_spent_in_budget

            # Create data entry
            self._storage.data['budgets'][index]['leftover_price'] = leftover

            index += 1

        pprint(self._storage.data['budgets'])

        #self._storage.save()
        """

        pass

    def next_month(self, args):
        """Makes a backup, then removes all expenses and unchecks everything that is checked"""

        # Back up the current data according to the month

        date_string = datetime.date.today().strftime("%B_%Y").lower()
        backup_file_path = CONFIG['path']+"rsbm_"+date_string+".json"

        if os.path.exists(backup_file_path):
            return "A backup of this month has already been made! If you are sure, delete that backup."

        with open(backup_file_path, 'w') as f:
            f.write(json.dumps(self._storage.data, indent=4))

        for key in self._storage.data.keys():
            # Data to clear
            if key in ['expenses']:
                self._storage.data[key] = []

            # Data to reset paid flag for
            if key in ['monthly_bills', 'income']:
                index = 0
                for item in self._storage.data[key]:
                    self._storage.data[key][index]['paid'] = False
                    index += 1

        self._storage.save()

        return "Moved over to next month.."
