import streamlit as st
import time

class Facility:
    def __init__(self, name, base_cost, rate):
        self.name = name
        self.base_cost = base_cost
        self.rate = rate
        self.amount = 0
        self.total_purchased = 0

    def current_cost(self):
        return int(self.base_cost * (1.12 ** self.amount))

    def total_production(self):
        return self.rate * self.amount

class Artifact:
    def __init__(self, name, effect_description, apply_effect, cost):
        self.name = name
        self.effect_description = effect_description
        self.apply_effect = apply_effect
        self.count = 0
        self.cost = cost

class Goal:
    def __init__(self, name, cost, on_complete):
        self.name = name
        self.cost = cost
        self.on_complete = on_complete
        self.completed = False

def double_click_rate(state):
    state['click_rate'] *= 2

def apply_cost_discount(state):
    state['cost_discount'] *= 0.8

def double_production_rate(state):
    for f in state['facilities']:
        f.rate *= 2

def multiply_monokuma_points(state):
    state['monokuma_points'] *= 2

def percent_boost_production(state):
    for f in state['facilities']:
        boost = 1 + (f.total_purchased / 100)
        f.rate *= boost

def reset_state(state):
    state['coins'] = 0
    state['monokuma_points'] = 0
    state['click_rate'] = 1
    state['generation_times'] = 0
    state['generation_cost'] = 100000
    state['cost_discount'] = 1
    for f in state['facilities']:
        f.amount = 0
        f.total_purchased = 0
        f.rate = f.base_cost // 10 or 1
    for a in state['artifacts']:
        a.count = 0
        a.cost = a.costs[0] if hasattr(a, 'costs') else a.cost
    state['goal'].completed = False

def main():
    st.title("モノクマクリッカー")

    if 'coins' not in st.session_state:
        st.session_state.update({
            'coins': 0,
            'monokuma_points': 0,
            'click_rate': 1,
            'generation_times': 0,
            'generation_cost': 100000,
            'cost_discount': 1,
            'facilities': [
                Facility("クリック代行モノクマ", 50, 1),
                Facility("アルバイトモノクマ", 200, 5),
                Facility("会社員モノクマ", 500, 15),
            ],
            'artifacts': [
                Artifact("ロボットアーム", "クリック2倍", double_click_rate, 5),
                Artifact("モノクマ教育センター", "生産2倍", double_production_rate, 20),
            ],
            'goal': Goal("ゲームクリア", 100000000, lambda: st.success("ゲームクリア！"))
        })

    state = st.session_state

    st.metric("モノクマメダル", f"{state['coins']:,}")
    st.metric("モノクマ数", f"{state['monokuma_points']:,}")
    st.metric("転生回数", state['generation_times'])

    if st.button(f"クリックで {state['click_rate']} 獲得"):
        state['coins'] += state['click_rate']

    for f in state['facilities']:
        cost = int(f.current_cost() * state['cost_discount'])
        if st.button(f"{f.name}（{cost:,}）購入"):
            if state['coins'] >= cost:
                state['coins'] -= cost
                f.amount += 1
                f.total_purchased += 1
                state['monokuma_points'] += 1

    if st.button(f"転生（{state['generation_cost']:,}必要）"):
        if state['coins'] >= state['generation_cost']:
            state['coins'] = 0
            state['click_rate'] += 10
            state['generation_times'] += 1
            state['generation_cost'] = 100000 ** (state['generation_times'] + 1)
            state['monokuma_points'] = 0
            for f in state['facilities']:
                f.amount = 0
                f.total_purchased = 0
                f.rate *= 2
            for a in state['artifacts']:
                a.count = 0
            state['cost_discount'] = 1

    for a in state['artifacts']:
        if st.button(f"{a.name}：{a.effect_description}（{a.cost}モノクマ）"):
            if state['monokuma_points'] >= a.cost:
                state['monokuma_points'] -= a.cost
                a.count += 1
                a.apply_effect(state)
                a.cost = int(a.cost * 1.3)

    if st.button(f"{state['goal'].name}（{state['goal'].cost:,}必要）"):
        if not state['goal'].completed and state['coins'] >= state['goal'].cost:
            state['coins'] -= state['goal'].cost
            state['goal'].completed = True
            state['goal'].on_complete()

if __name__ == '__main__':
    main()
