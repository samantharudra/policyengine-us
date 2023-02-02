from policyengine_us.model_api import *


class nyc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # If had contribution(s) to Charitable Gifts Trust Fund accounts AND
        # itemized those contributions, would subtract the contribution(s)
        # amount from their NY AGI and the their itemized decudtion amount.
        # https://www.tax.ny.gov/pdf/2022/printable-pdfs/inc/it201i-2022.pdf#page=16

        # First get their NY AGI.
        ny_agi = tax_unit("ny_agi", period)

        # Get parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.exemptions

        # Get number of dependents.
        count_dependents = tax_unit("tax_unit_dependents", period)

        # Subtract dependent exemption amount.
        nyc_taxable_income = ny_agi - p.dependent * count_dependents

        return nyc_taxable_income
