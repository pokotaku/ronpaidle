import tkinter as tk
from tkinter import Canvas
import threading
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

class IdleGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("モノクマクリッカー")

        self.coins = 1000000
        self.monokuma_points = 0
        self.generation_times = 0
        self.click_rate = 1
        self.generation_cost = 100000
        self.running = True
        self.lock = threading.Lock()
        self.cost_discount = 1
        self.start_time = time.time()
        self.purchase_modes = [1, 'max']
        self.purchase_mode_index = 0
        self.purchase_amount = self.purchase_modes[self.purchase_mode_index]

        self.goal = Goal("ゲームクリア", 2000000, self.complete_game)

        self.facilities = [
            Facility("クリック代行モノクマ", 50, 1),
            Facility("アルバイトモノクマ", 200, 5),
            Facility("会社員モノクマ", 500, 15),
            Facility("社長モノクマ", 1000, 35),
            Facility("株主モノクマ", 3000, 120),
            Facility("大地主モノクマ", 10000, 400),
            Facility("小説家モノクマ", 50000, 2300),
            Facility("アスリートモノクマ", 100000, 5000)
        ]

        self.artifacts = [
            Artifact("ロボットアーム", "クリックによるモノクマメダル2倍", self.double_click_rate, 5),
            Artifact("モノクマアウトレット", "施設購入コストが20%割引", self.apply_cost_discount, 10),
            Artifact("モノクマ教育センター", "モノクマメダルの生産が2倍", self.double_production_rate, 20)
        ]

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=200, bg="#000000")
        self.left_frame.pack(side="left", fill="y")

        self.center_frame = tk.Frame(self.main_frame, bg="white")
        self.center_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = tk.Frame(self.main_frame, width=200, bg="#e0e0e0")
        self.right_frame.pack(side="right", fill="y")

        self.coin_label = tk.Label(self.left_frame, text=f"モノクマメダル: {self.format_number(self.coins)}", font=("Helvetica", 14), fg="white", bg="#000000")
        self.coin_label.pack(pady=10)

        self.production_label = tk.Label(self.left_frame, text="生産量: 0 /s", fg="white", bg="#000000")
        self.production_label.pack(pady=2)

        self.monokuma_label = tk.Label(self.left_frame, text=f"モノクマ数: {self.format_number(self.monokuma_points)}", fg="white", bg="#000000")
        self.monokuma_label.pack(pady=5)

        self.coin_img = tk.Canvas(self.left_frame, width=120, height=120, bg="lightgray")
        self.coin_img.create_oval(20, 20, 100, 100, fill="gold")
        self.coin_img.pack()

        self.click_button = tk.Button(self.left_frame, text=f"クリックで{self.click_rate}コイン", command=self.click_coin)
        self.click_button.pack(pady=5)

        self.generation_label = tk.Label(self.left_frame, text=f"転生回数: {self.generation_times}", fg="white", bg="#000000")
        self.generation_label.pack(pady=5)

        self.generation_button = tk.Button(self.left_frame, text=f"転生（必要: {self.format_number(self.generation_cost)}）", command=self.generation)
        self.generation_button.pack(pady=5)
        
        self.goal_button = tk.Button(self.left_frame, text=f"{self.goal.name}（必要: {self.format_number(self.goal.cost)}）", command=self.buy_goal)
        self.goal_button.pack(pady=5)

        self.playtime_label = tk.Label(self.left_frame, text="プレイ時間: 00:00", fg="white", bg="#000000")
        self.playtime_label.pack(pady=5)

        self.artifact_frame = tk.Frame(self.left_frame, bg="#222222")
        self.artifact_labels = []
        for artifact in self.artifacts:
            label = tk.Button(self.artifact_frame, text=f"{artifact.name}：{artifact.effect_description}（{artifact.cost}モノクマ）", fg="white", bg="#222222", anchor="w", command=lambda a=artifact: self.buy_artifact(a))
            label.pack(fill="x", padx=5, pady=2)
            self.artifact_labels.append(label)
        self.artifact_frame.pack_forget()

        self.canvas = Canvas(self.center_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.amount_frame = tk.Frame(self.right_frame, bg="#e0e0e0")
        self.amount_frame.pack(pady=5)
        self.purchase_mode_btn = tk.Button(self.amount_frame, text="購入数: 1", command=self.toggle_purchase_amount)
        self.purchase_mode_btn.pack()

        self.facility_buttons = []
        for i, facility in enumerate(self.facilities):
            btn = tk.Button(self.right_frame, text="", command=lambda f=facility: self.buy_facility(f))
            btn.pack(pady=3)
            btn.pack_forget() if i != 0 else None
            self.facility_buttons.append(btn)

        self.update_thread = threading.Thread(target=self.generate_coins)
        self.update_thread.daemon = True
        self.update_thread.start()
        self.update_gui()

    def toggle_purchase_amount(self):
        self.purchase_mode_index = (self.purchase_mode_index + 1) % len(self.purchase_modes)
        self.purchase_amount = self.purchase_modes[self.purchase_mode_index]
        self.purchase_mode_btn.config(text=f"購入数: {self.purchase_amount}")

    def format_number(self, number):
        return f"{number:,}"

    def click_coin(self):
        with self.lock:
            self.coins += self.click_rate

    def generate_coins(self):
        while self.running:
            with self.lock:
                total_facility_production = sum(f.total_production() for f in self.facilities)
                self.coins += total_facility_production
            time.sleep(1)

    def generation(self):
        with self.lock:
            if self.coins >= self.generation_cost:
                self.coins = 0
                self.click_rate += 10
                self.generation_times += 1
                self.generation_cost = 100000 *((self.generation_times + 1) ** 2)
                self.monokuma_points = 0
                for facility in self.facilities:
                    facility.amount = 0
                    facility.total_purchased = 0
                    facility.rate *= 2
                if self.generation_times >= 1:
                    self.artifact_frame.pack(pady=10)
                for i, btn in enumerate(self.facility_buttons):
                    if i == 0:
                        btn.pack()
                    else:
                        btn.pack_forget()
                

    def buy_facility(self, facility):
        with self.lock:
            index = self.facilities.index(facility)
            if self.purchase_amount == 'max':
                count = 0
                total_cost = 0
                while True:
                    cost = int(facility.base_cost * (1.12 ** (facility.amount + count)) * self.cost_discount)
                    if self.coins >= total_cost + cost:
                        total_cost += cost
                        count += 1
                    else:
                        break
                if count > 0:
                    facility.amount += count
                    facility.total_purchased += count
                    self.monokuma_points += count
                    self.coins -= total_cost
            else:
                for _ in range(self.purchase_amount):
                    cost = int(facility.base_cost * (1.12 ** facility.amount) * self.cost_discount)
                    if self.coins >= cost:
                        self.coins -= cost
                        facility.amount += 1
                        facility.total_purchased += 1
                        self.monokuma_points += 1
                    else:
                        break
            if index + 1 < len(self.facilities):
                self.facility_buttons[index + 1].pack()

    def buy_artifact(self, artifact):
        if self.monokuma_points >= artifact.cost:
            self.monokuma_points -= artifact.cost
            artifact.count += 1
            artifact.apply_effect()
            artifact.cost = int(artifact.cost * 1.2)

    def double_production_rate(self):
        for facility in self.facilities:
            facility.rate *= 2

    def double_click_rate(self):
        self.click_rate *= 2

    def apply_cost_discount(self):
        self.cost_discount *= 0.8

    def update_gui(self):
        with self.lock:
            self.coin_label.config(text=f"モノクマメダル: {self.format_number(self.coins)}")
            self.monokuma_label.config(text=f"モノクマ数: {self.format_number(self.monokuma_points)}")
            self.click_button.config(text=f"クリックで{self.click_rate}コイン")
            self.generation_label.config(text=f"転生回数: {self.generation_times}")
            self.generation_button.config(text=f"転生（必要: {self.format_number(self.generation_cost)}）")
            total_production = 0
            for i, facility in enumerate(self.facilities):
                cost = int(facility.current_cost() * self.cost_discount)
                prod = facility.total_production()
                total_production += prod
                self.facility_buttons[i].config(
                    text=f"{facility.name}\n保有数: {facility.amount}\n購入費: {self.format_number(cost)}\n一体の生産: {self.format_number(facility.rate)} /s"
                )
            self.production_label.config(text=f"生産量: {self.format_number(total_production)} /s")
            for i, artifact in enumerate(self.artifacts):
                if artifact.count > 0:
                    self.artifact_labels[i].config(fg="lightgreen", text=f"{artifact.name}：{artifact.effect_description}（{artifact.cost}モノクマ）")
            self.canvas.delete("all")
            x = 10
            for f in self.facilities:
                for _ in range(f.amount):
                    self.canvas.create_oval(x, 50, x + 20, 70, fill="black")
                    x += 30
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.playtime_label.config(text=f"プレイ時間: {minutes:02d}:{seconds:02d}")
        self.root.after(200, self.update_gui)
        
    def buy_goal(self):
        with self.lock:
            if not self.goal.completed and self.coins >= self.goal.cost:
                self.coins -= self.goal.cost
                self.goal.completed = True
                self.goal.on_complete()

    def complete_game(self):
        self.click_button.config(state="disabled")
        self.generation_button.config(state="disabled")
        self.goal_button.config(text="ゲームクリア！", state="disabled")
        self.coin_label.config(text="おめでとう！ ゲームをクリアしました！")

if __name__ == "__main__":
    root = tk.Tk()
    game = IdleGameGUI(root)
    root.mainloop()