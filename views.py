from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from . import config

"""
Principal maintainer: Rachel Chen <me@rachelchen.me>
Contributors:
    Kristian Lopez Vargas <kristianlvargas@gmail.com>
    Eli Pandolfo
"""

class InitialInstructions(Page):
    form_model = models.Player
    form_fields = ['time_InitialInstructions']
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {'participation_fee': self.session.config['participation_fee']}


class TaskInstructions(Page):
    form_model = models.Player
    form_fields = ['time_TaskInstructions']
    def vars_for_template(self):
        mode = Constants.dynamic_values[self.round_number - 1]['mode']
        return {'mode': mode}

    def is_displayed(self):
        mode = Constants.dynamic_values[self.round_number - 1]['mode']
        if self.round_number > 1:
            prevmode = Constants.dynamic_values[self.round_number - 2]['mode']
        return self.round_number == 1 or mode != prevmode

    def vars_for_template(self):
        mode = Constants.dynamic_values[self.round_number - 1]['mode']
        # this will be used in the conditional display of instructions
        return {'mode': mode,
                'sec1': mode.split('_')[1],
                'sec2': mode.split('_')[2]
                }

class Graph(Page):
    form_model = models.Player

    def get_form_fields(self):
        current_round = self.round_number
        dynamic_values = config.getDynamicValues()
        round_data = dynamic_values[current_round - 1]
        if round_data is not None and round_data['mode'] is not None:
            if round_data['mode'] == 'det_giv':
                return ['mode', 'me_a', 'time_Graph']
            elif round_data['mode'] == 'probability':
                return ['mode', 'prob_a', 'prob_b', 'time_Graph']
            elif round_data['mode'] == 'sec_ownrisk':
                return ['mode', 'me_a', 'me_b', 'prob_a', 'prob_b', 'time_Graph']
            else:
                return ['mode', 'partner_a', 'partner_b', 'me_a', 'me_b', 'prob_a', 'prob_b', 'time_Graph']
        else:
            return ['mode', 'partner_a', 'partner_b', 'me_a', 'me_b', 'prob_a', 'prob_b', 'time_Graph']

    def vars_for_template(self):
        mode = Constants.dynamic_values[self.round_number - 1]['mode']
        if self.round_number > 1:
            counter = 1
            prevmode = Constants.dynamic_values[self.round_number - 2]['mode']
            while mode == prevmode:
                counter += 1;
                if counter == self.round_number:
                    break
                prevmode = Constants.dynamic_values[self.round_number - (counter + 1)]['mode']
        else:
            counter = 1
        return {'mode': mode,
                'counter': counter,
                'sec1': mode.split(_)[1],
                'sec2': mode.split(_)[2]
                }

    def before_next_page(self):
        current_round = self.round_number
        dynamic_values = config.getDynamicValues()
        round_data = dynamic_values[current_round - 1]
        if round_data['mode'] == 'single':
            self.group.set_payoffs()
        elif self.player.id_in_group == 1:
            self.group.set_payoffs()

class ResultsWaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def after_all_players_arrive(self):
        pass

class Results(Page):
    form_model = models.Player
    form_fields = ['time_Results']

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        # variables:
        mode = Constants.dynamic_values[self.session.vars['paying_round'] - 1]['mode']
        decision = self.group.get_player_by_id(1).me_a if mode != 'probability' else self.group.get_player_by_id(1).prob_a
        decision = str(round(decision, 1)) + '% for A'
        return {'mode': mode.capitalize(), 'decision': decision}


page_sequence = [
    InitialInstructions,
    TaskInstructions,
    Graph,
    ResultsWaitPage,
    Results
]


# yes | otree resetdb && otree runserver
