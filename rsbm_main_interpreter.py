import datetime
import yaml

import rsbm_interpreter
import rsbm_calculator
from config import *

class MainInterpreter(rsbm_interpreter.BaseInterpreter):
    def __init__(self, storage):
        super(MainInterpreter, self).__init__()

        self._storage = storage
        self._funcmap = {
            'add': self.add,
            'set': self.set,
            'del': self.delete,
            'list': self.list,
            'check': self.check,
            'uncheck': self.uncheck,
            'bank': self.bank_balance,
            'status': self.status,
            'next_month': self.next_month,
            'api': self.api,
        }

        commands = []
        for command in self._funcmap.keys():
            commands.append(command)

        commands.sort()

        self._helpmsg = "Commands: %s" % ', '.join(commands)

    # -------------

    def _format_name(self, name):
        return name.replace('_', ' ')
    def _format_name_reverse(self, name):
        return name.replace(' ', '_').lower()

    def _add_to_list(self, list_name, item_type, item):
        if list_name not in self._storage.data:
            raise Exception("Program tried to add something to list %s, list doesn't exist." % list_name)

        self._storage.data[list_name].append(item)
        self._storage.save()

        return "%s added." % item_type
    def _find_by_name(self, list, name):
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
    def _del_from_list(self, list_name, item_type, item_name):
        if list_name not in self._storage.data:
            raise Exception("Program tried to delete something from list %s, list doesn't exist." % list_name)

        if not item_name:
            return "Please specify a %s" % item_type

        target_index = self._find_by_name(self._storage.data[list_name], item_name)
        if target_index == None:
            return "%s not found" % item_type

        del self._storage.data[list_name][target_index]
        self._storage.save()
        return "%s deleted." % item_type

    # -------------

    def _translate_item_type(self, item_type):
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
        if item_type == "bill":
            return "<name> <price> <day of month>"
        elif item_type == "expense":
            return "<category> <name> <price>"
        elif item_type == "budget":
            return "<budget>"
        elif item_type == "income":
            return "<name> <price>"

    # -------------

    def api(self, args):
        # Calls the command supplied with API mode turned on

        cmd = args[2]
        if cmd not in self._funcmap.keys():
            return yaml.dump(False)

        del(args[0])
        return self._funcmap[cmd](args, api=True)

    # -------------

    def add(self, args, api=False):
        if len(args) <= 2:
            if not api:
                available_types = ', '.join(self._storage.data.keys())

                output = ""
                output += "Usage: add <type> <type stuff>\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return yaml.dump(False)
        if len(args) <= 3:
            if not api:
                output = "Usage: add %s %s" % (args[2], self._help_on_type(args[2]))
                return output
            else:
                return yaml.dump(False)

        list_name = self._translate_item_type(args[2])

        new_item = {}

        if list_name == "income":
            new_item['name'] = args[3]
            new_item['price'] = float(args[4])
            new_item['paid'] = False
        elif list_name == "budgets":
            new_item['name'] = args[3]
            new_item['price'] = 0.00
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
            return yaml.dump(True)

        return "New %s \"%s\" added to %s" % (args[2], self._format_name(new_item['name']), self._format_name(list_name))

    def set(self, args, api=False):
        if len(args) <= 2:
            if not api:
                available_types = ', '.join(self._storage.data.keys())

                output = ""
                output += "Usage: set <type> <type stuff>\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return yaml.dump(False)
        if len(args) <= 3:
            if not api:
                output = "Usage: set %s %s" % (args[2], self._help_on_type(args[2]))
                return output
            else:
                return yaml.dump(False)

        list_name = self._translate_item_type(args[2])
        item_name = self._format_name_reverse(args[3])
        target_index = self._find_by_name(self._storage.data[list_name], item_name)

        if target_index == None:
            if not api:
                return "Could not find that %s" % args[2]
            else:
                return yaml.dump(False)

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
            return yaml.dump(True)

        return "%s \"%s\" modified." % (args[2], self._format_name(args[3]))

    def delete(self, args, api=False):
        if len(args) <= 3:
            if not api:
                available_types = ', '.join(self._storage.data.keys())

                output = ""
                output += "Usage: del <type> <name>\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return yaml.dump(False)

        item_name = self._format_name_reverse(args[3])
        list_name = self._translate_item_type(args[2])
        target_index = self._find_by_name(self._storage.data[list_name], item_name)

        if target_index == None:
            if not api:
                return "Could not find that %s" % args[2]
            else:
                return yaml.dump(False)

        del self._storage.data[list_name][target_index]
        self._storage.save()

        if api:
            return yaml.dump(True)

        return "%s \"%s\" deleted from %s." % (args[2].capitalize(), self._format_name(item_name), self._format_name(list_name))

    def list(self, args, api=False):
        output = ""

        # Initialization
        if len(args) <= 2:
            if not api:
                available_types = ', '.join(self._storage.data.keys())
                output += "Usage: list type\n"
                output += "Available types: %s\n" % available_types
                return output
            else:
                return yaml.dump(False)

        list_name = args[2]
        if list_name == "bills": list_name = "monthly_bills"

        # API support.. spit out pure YAML data
        if api:
            return yaml.dump(self._storage.data[list_name])

        if list_name not in self._storage.data.keys():
            return "That type does not exist."

        # Headers
        if list_name == "budgets":
            output += "| %-60s| %-10s| %-11s| %-10s |\n\n" % ("Name", "Budgeted", "Spent", "Available")
        elif list_name == "monthly_bills":
            output += "| %-2s| %-60s| %-10s| %-4s |\n\n" % ("P", "Name", "Cost", "Day")
        elif list_name == "income":
            output += "| %-2s| %-60s| %-10s |\n\n" % ("P", "Name", "Cost")
        elif list_name == "expenses":
            output += "| %-30s| %-30s| %-8s|\n\n" % ("Name", "Budget", "Price")

        if len(self._storage.data[list_name]) == 0:
            output += "No items\n"

        # Different list depending on list type
        total_price = 0
        for item in self._storage.data[list_name]:
            if list_name == "budgets":
                total_spent_in_budget = 0.00
                for expense in self._storage.data['expenses']:
                    if expense['budget'] == item['name']:
                        total_spent_in_budget += expense['price']

                output += "| %-60s| $%-9.2f| -$%-9.2f| $%-9.2f |\n" % (self._format_name(item['name']).capitalize(), item['price'], total_spent_in_budget, item['price']-total_spent_in_budget)
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
            total_income = rsbm_calculator.total_price(self._storage.data['income'], only_paid=False)
            total_current_income = rsbm_calculator.total_price(self._storage.data['income'], only_paid=True)
            total_bills = rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=False)
            total_paid_bills = rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=True)
            total_spent = rsbm_calculator.total_price(self._storage.data['expenses'])
            total_budgeted = rsbm_calculator.total_price(self._storage.data['budgets'])
            total_budgetable = rsbm_calculator.total_price(self._storage.data['income'], only_paid=False)-rsbm_calculator.total_price(self._storage.data['monthly_bills'])
            total_currently_budgetable = rsbm_calculator.total_price(self._storage.data['income'], only_paid=True)-rsbm_calculator.total_price(self._storage.data['monthly_bills'])
            overbudgeted = -(total_budgetable-total_price)
            currently_overbudgeted = (-(total_currently_budgetable-total_price))
            overspent = -(total_price-total_spent)

            if total_price == 0:
                return output

            bank_balance = total_current_income-total_paid_bills-total_spent

            output += "%d%% ($%.2f) of total currently budgetable $%.2f is assigned to budgets." % ((100*(total_price/total_currently_budgetable)), total_price, total_currently_budgetable)
            if (currently_overbudgeted >= 1):
                output += " You've gone $%.2f over the working budget.\n" % currently_overbudgeted
            else:
                output += " Still available for budgeting: $%.2f\n" % (total_currently_budgetable-total_price)

            output += "%d%% ($%.2f) of total monthly budgetable $%.2f is assigned to budgets." % ((100*(total_price/total_budgetable)), total_price, total_budgetable)
            if (overbudgeted >= 1):
                output += " You've gone $%.2f over the monthly budget.\n" % overbudgeted
            else:
                output += " Still available for budgeting: $%.2f\n" % (total_budgetable-total_price)

            output += "%d%% ($%.2f) of total budgeted $%.2f has been spent so far." % ((100*(total_spent/total_price)), total_spent, total_price)
            if (overspent >= 1):
                output += " You've spent $%.2f over your budget.\n" % overbudgeted
            else:
                output += " You have $%.2f left to spend inside your budget.\n" % (total_price-total_spent)

            output += "\n"
            output += "$%.2f will currently be left over at the end of the month.\n" % (total_currently_budgetable-total_spent)
            output += "$%.2f would be left over at the end of the month if you spent all of your budget.\n" % (total_currently_budgetable-total_budgeted)
            output += "\n"
            output += "Your current bank balance should be: $%.2f\n" % bank_balance
        elif list_name == "income":
            output += "Total currently received: $%.2f\n" % rsbm_calculator.total_price(self._storage.data['income'], only_paid=True)
            output += "Total to still receive: $%.2f\n" % (
                rsbm_calculator.total_price(self._storage.data['income'], only_paid=False)
                - rsbm_calculator.total_price(self._storage.data['income'], only_paid=True)
            )
            output += "Total expected income: $%.2f\n" % total_price
        elif list_name == "monthly_bills":
            output += "Total paid so far: %.2f\n" % rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=True)
            output += "Total still to be paid: %.2f\n" % (total_price-rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=True))
            output += "Total: $%.2f\n" % total_price
        else:
            output += "Total: $%.2f\n" % total_price

        return output

    def check(self, args, api=False):
        if len(args) <= 3:
            if not api:
                return "Usage: check income/bill <name>"
            else :
                return yaml.dump(False)

        target_category = ''
        if args[2] == 'bill':
            target_category = 'monthly_bills'
        elif args[2] == 'income':
            target_category = 'income'
        else:
            if not api:
                return "That is not a bill or income source."
            else:
                return yaml.dump(False)

        target_index = self._find_by_name(self._storage.data[target_category], self._format_name_reverse(args[3]))

        if target_index == None:
            return "Could not find that bill."


        self._storage.data[target_category][target_index]['paid'] = True
        self._storage.save()

        if api:
            return yaml.dump(True)

        return "%s \"%s\" marked as paid." % (args[2], args[3])

    def uncheck(self, args, api=False):
        if len(args) <= 3:
            if not api:
                return "Usage: check income/bill <name>"
            else :
                return yaml.dump(False)

        target_category = ''
        if args[2] == 'bill':
            target_category = 'monthly_bills'
        elif args[2] == 'income':
            target_category = 'income'
        else:
            if not api:
                return "That is not a bill or income source."
            else:
                return yaml.dump(False)

        target_index = self._find_by_name(self._storage.data[target_category], self._format_name_reverse(args[3]))

        if target_index == None:
            if not api:
                return "Could not find that bill."
            else:
                return yaml.dump(False)


        self._storage.data[target_category][target_index]['paid'] = False
        self._storage.save()

        if api:
            return yaml.dump(True)

        return "%s \"%s\" marked as not paid." % (args[2], args[3])

    # -------------

    def bank_balance(self, args, api=False):
        output = ""

        total_current_income = float(rsbm_calculator.total_price(self._storage.data['income'], only_paid=True))
        total_paid_bills = rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=True)
        total_spent = rsbm_calculator.total_price(self._storage.data['expenses'])

        bank_balance = total_current_income-total_paid_bills-total_spent

        if api:
            formatted_balance = "%.2f" % (bank_balance)
            return yaml.dump(float(formatted_balance))

        output += "BANK BALANCE CALCULATION\n"
        output += "Your bank balance should match the outcome of this calculation.\n"
        output += self._separator

        output += "Current total received income ($%.2f)\n-\nPaid bills ($%.2f)\n-\nTotal spent from budget ($%.2f)\n=\n" % (total_current_income, total_paid_bills, total_spent)
        output += "$%.2f\n" % (bank_balance)

        return output

    def status(self, args):
        output = ""

        total_current_income = rsbm_calculator.total_price(self._storage.data['income'], only_paid=True)
        total_bills = rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=False)
        total_paid_bills = rsbm_calculator.total_price(self._storage.data['monthly_bills'], only_paid=True)
        total_spent = rsbm_calculator.total_price(self._storage.data['expenses'])
        total_budgeted = rsbm_calculator.total_price(self._storage.data['budgets'])
        total_budgetable = rsbm_calculator.total_price(self._storage.data['income'], only_paid=False)-rsbm_calculator.total_price(self._storage.data['monthly_bills'])
        total_currently_budgetable = rsbm_calculator.total_price(self._storage.data['income'], only_paid=True)-rsbm_calculator.total_price(self._storage.data['monthly_bills'])

        bank_balance = total_current_income-total_paid_bills-total_spent

        output += "Total money spent (includes bills):\n  Bills total at $%.2f\n  Total $%.2f spent out of received income $%.2f\n" % (
            total_paid_bills,
            (total_paid_bills+total_spent),
            total_current_income
        )
        output += "Total budgetable money:\n  $%.2f in total ($%.2f of it is budgeted)\n  $%.2f in actuality\n" % (
            total_budgetable,
            total_budgeted,
            total_currently_budgetable
        )
        output += "Total budget spent:\n  $%.2f out of total budget $%.2f\n" % (
            total_spent,
            total_budgeted
        )
        output += "Current bank balance should be:\n  $%.2f\n" % bank_balance

        return output

    # -------------

    def next_month(self, args):
        # Back up the current data according to the month

        date_string = datetime.date.today().strftime("%B_%Y").lower()
        backup_file_path = CONFIG['path']+"rsbm_"+date_string+".yaml"

        if os.path.exists(backup_file_path):
            return "A backup of this month has already been made! If you are sure, delete that backup."

        with open(backup_file_path, 'w') as f:
            f.write(yaml.dump(self._storage.data))

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

        return "All relevant data has been cleared and a backup of this month has been made."
