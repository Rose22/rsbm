class RsbmCalculator(object):
    """Does all the financial calculations"""

    def calculate_sum(self, items, only_paid=False):
        total_price = 0.00
        for item in items:
            if only_paid and not item['paid']:
                continue

            total_price += float(item['price'])

        return total_price

    def calculate(self, data):
        """Calculate all the needed financial data"""

        expected_income_total               = self.calculate_sum(data['income'], only_paid=False)
        received_income_total               = self.calculate_sum(data['income'], only_paid=True)

        expected_bills_total                = self.calculate_sum(data['monthly_bills'], only_paid=False)
        paid_bills_total                    = self.calculate_sum(data['monthly_bills'], only_paid=True)

        budgetable_total                    = received_income_total-expected_bills_total
        expected_budgetable_total           = expected_income_total-expected_bills_total

        spent_total                         = self.calculate_sum(data['expenses'])

        budget_total                        = self.calculate_sum(data['budgets'])
        budget_percent_budgetable           = (100*(budget_total/budgetable_total))
        budget_percent_expected_budgetable  = (100*(budget_total/expected_budgetable_total))
        budget_available                    = budgetable_total-budget_total
        budget_overbudgeted                 = -budget_available
        budget_overspent                    = -(budget_total-spent_total)

        expected_budgetable_overbudgeted        = -(expected_budgetable_total-budget_total)

        budgetable_available                = budgetable_total-budget_total
        expected_budgetable_available       = expected_budgetable_total-budget_total

        spent_percent_budget                = (100*(spent_total/budget_total))
        spendable_in_budget                 = budget_total-spent_total

        bank_balance                        = received_income_total-paid_bills_total-spent_total
        leftover                            = received_income_total-expected_bills_total-spent_total
        leftover_if_spent_budget            = received_income_total-expected_bills_total-budget_total

        calculations = {
            'expected_income_total': expected_income_total,
            'received_income_total': received_income_total,
            'expected_bills_total': expected_bills_total,
            'paid_bills_total': paid_bills_total,
            'spent_total': spent_total,
            'budgetable_total': budgetable_total,
            'expected_budgetable_total': expected_budgetable_total,
            'budget_total': budget_total,
            'budget_percent_budgetable': budget_percent_budgetable,
            'budget_available': budget_available,
            'budget_percent_expected_budgetable': budget_percent_expected_budgetable,
            'budget_overbudgeted': budget_overbudgeted,
            'expected_budgetable_overbudgeted': expected_budgetable_overbudgeted,
            'budgetable_available': budgetable_available,
            'expected_budgetable_available': expected_budgetable_available,
            'spent_percent_budget': spent_percent_budget,
            'spendable_in_budget': spendable_in_budget,
            'budget_overspent': budget_overspent,
            'bank_balance': bank_balance,
            'leftover': leftover,
            'leftover_if_spent_budget': leftover_if_spent_budget,
        }

        return calculations

    def calculate_budget(self, category_data, expenses_data):
        """Per budget category, calculate a bunch of stuff"""
        
        # TODO: rename budget to category

        category_expenses = 0.00
        for expense in expenses_data:
            if expense['budget'] == category_data['name']:
                category_expenses += expense['price']

        category_available = category_data['price']-category_expenses

        """WOULD INTRODUCE TOO MUCH COMPLEXITY
        cutoff_done = False
        for price in category_expenses:
            category_spent += price
            if (category_spent >= category_data['price'] and not cutoff_done):
                # Cutoff
                difference = category_spent-category_data['price']
                category_available -= price-difference
                category_leftover -= difference

                cutoff_done = True
            elif (category_spent > category_data['price'] and cutoff_done):
                category_leftover -= price
            else:
                category_available -= price
        """

        return {
            'budgeted_total': category_data['price'],
            'expenses_total': category_expenses,
            'available_total': category_available,
        }
