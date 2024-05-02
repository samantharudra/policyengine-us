from policyengine_us.model_api import *


class ar_taxable_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable capital gains"
    unit = USD
    reference = (
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-815.html",
        "https://www.taxformfinder.org/forms/2023/2023-arkansas-form-ar1000d.pdf#page=1",
    )
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Line 1-3 - long term capital gain or loss
        lt_capital_gains = person("long_term_capital_gains", period)
        # Line 4-6 - short term capital loss
        st_capital_gains = person("short_term_capital_gains", period)
        st_capital_loss = max_(-st_capital_gains, 0)
        # Line 7a - Net capital gain or loss
        net_capital_gain = lt_capital_gains - st_capital_loss
        # Line 7b - capped net capital gain
        p = parameters(
            period
        ).gov.states.ar.tax.income.gross_income.capital_gains
        capped_net_cap_gain = min_(net_capital_gain, p.exempt.cap)
        # Line 8 - Tax rate applied to capital gain
        # 50% exempt if a gain, otherwise entire loss.
        exempt_fraction = where(capped_net_cap_gain > 0, p.exempt.rate, 0)
        taxable_amount = capped_net_cap_gain * (1 - exempt_fraction)
        # Lines 9-11: Arkansas short term capital gain if any.
        stcg_if_any = max_(st_capital_gains, 0)
        # Line 12: Total taxable gain or loss. Loss is capped.
        total_taxable_cap_gain_or_loss = taxable_amount + stcg_if_any
        filing_status = person.tax_unit("filing_status", period)
        loss_cap = p.loss_cap[filing_status]
        # In the joint filing case we allocate all of the capital gain or loss
        # to the head of the household to avoid double counting.
        joint = filing_status == filing_status.possible_values.JOINT
        head = person("is_tax_unit_head", period)
        total_gain_or_loss_allocated_to_head = (
            person.tax_unit.sum(total_taxable_cap_gain_or_loss) * head
        )
        redestributed_cap_gain_or_loss = where(
            joint,
            total_gain_or_loss_allocated_to_head,
            total_taxable_cap_gain_or_loss,
        )
        return max_(-loss_cap, redestributed_cap_gain_or_loss)
