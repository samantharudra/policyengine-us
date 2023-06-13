from policyengine_us.model_api import *


class co_chp_physician_services_saving(Variable):
    value_type = float
    entity = Person
    label = "Child Health Plan Plus physician services expense reduction"
    definition_period = YEAR

    def formula(person, period, parameters):
        income_level = person("medicaid_income_level", period)
        is_pregnant = person("is_pregnant", period)
        p = parameters(period).gov.states.co.hcpf.chp.copays.physician_services
        copay = where(is_pregnant, 0, p.calc(income_level))
        expense = person("physician_services_expense", period)
        return max_(0, expense - copay)
