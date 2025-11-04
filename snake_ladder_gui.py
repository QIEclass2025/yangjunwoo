import tkinter as tk
from tkinter import messagebox
import random
import argparse
import json
import urllib.request
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

# Pillow 라이브러리 필요 (pip install Pillow)
try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("라이브러리 오류", "Pillow 라이브러리가 필요합니다. 'pip install Pillow'를 실행해주세요.")
    exit()

# 게임의 핵심 로직을 담당하는 클래스
class SnakeLadderGameLogic:
    def __init__(self, num_players=2, num_snakes=8, num_ladders=8, seed=None):
        self.board_size = 100
        self.num_players = num_players
        self.player_positions = {i: 1 for i in range(1, self.num_players + 1)}
        self.snakes = {}
        self.ladders = {}
        if seed is not None:
            random.seed(seed)
        self._place_snakes_and_ladders(num_snakes, num_ladders)

    def _place_snakes_and_ladders(self, num_snakes, num_ladders):
        occupied_positions = {1, self.board_size}
        for _ in range(num_snakes):
            while True:
                head = random.randint(11, self.board_size - 1)
                tail = random.randint(2, head - 1)
                if (head - tail < 30) and head not in occupied_positions and tail not in occupied_positions:
                    self.snakes[head] = tail
                    occupied_positions.add(head)
                    occupied_positions.add(tail)
                    break
        for _ in range(num_ladders):
            while True:
                start = random.randint(2, self.board_size - 10)
                end = random.randint(start + 1, self.board_size - 1)
                if (end - start < 30) and start not in occupied_positions and end not in occupied_positions:
                    self.ladders[start] = end
                    occupied_positions.add(start)
                    occupied_positions.add(end)
                    break

    def roll_die(self):
        return random.randint(1, 6)

# GUI를 담당하는 메인 애플리케이션 클래스
class SnakeLadderGUI(tk.Tk):
    def __init__(self, num_players, num_snakes, num_ladders, seed):
        super().__init__()
        self.title("포켓몬 뱀 사다리 게임")
        self.geometry("750x800")

        # --- 게임 로직 및 상태 초기화 ---
        self.game_logic = SnakeLadderGameLogic(num_players, num_snakes, num_ladders, seed)
        self.turn_count = 1
        self.current_player = 1
        self.player_colors = ["red", "blue", "green", "purple"]
        self.player_pokemon = {}
        self.pokemon_image_references = [] # ★ 이미지 참조를 저장할 리스트

        # --- UI 요소 생성 ---
        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack(pady=20)

        self.info_frame = tk.Frame(self)
        self.info_frame.pack()
        self.turn_label = tk.Label(self.info_frame, text=f"턴: {self.turn_count}", font=("Helvetica", 14))
        self.turn_label.grid(row=0, column=0, padx=10)
        self.player_label = tk.Label(self.info_frame, text="포켓몬 로딩 중...", font=("Helvetica", 14))
        self.player_label.grid(row=0, column=1, padx=10)

        self.roll_button = tk.Button(self, text="주사위 굴리기", font=("Helvetica", 14), command=self.play_turn, state="disabled")
        self.roll_button.pack(pady=10)

        self.message_label = tk.Label(self, text="플레이어의 포켓몬을 불러오고 있습니다...", font=("Helvetica", 12))
        self.message_label.pack()
        self.update()

        # --- 초기화 작업 ---
        self._fetch_player_pokemon()
        self.cell_coords = self._draw_board()
        self._draw_snakes_and_ladders()
        self._draw_players()
        
        self.message_label.config(text="게임을 시작하려면 '주사위 굴리기' 버튼을 누르세요.")
        self.player_label.config(text=f"{self.player_pokemon[self.current_player]['name']}의 차례", fg=self.player_colors[self.current_player-1])
        self.roll_button.config(state="normal")

    def _fetch_pokemon_data(self, pokemon_id):
        """단일 포켓몬 데이터를 API에서 가져와 PIL Image 객체로 반환합니다."""
        try:
            with urllib.request.urlopen(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}") as response:
                data = json.loads(response.read())
            name = data['name'].capitalize()
            sprite_url = data['sprites']['front_default']
            with urllib.request.urlopen(sprite_url) as response:
                image_data = response.read()
            # PIL Image 객체로 변환하여 반환
            image_obj = Image.open(BytesIO(image_data)).resize((40, 40), Image.Resampling.LANCZOS)
            return {'id': pokemon_id, 'name': name, 'image_obj': image_obj}
        except Exception as e:
            print(f"Error fetching Pokemon ID {pokemon_id}: {e}")
            return None

    def _fetch_player_pokemon(self):
        """플레이어 수만큼 포켓몬 데이터를 가져와 Tkinter 이미지로 변환하고 참조를 저장합니다."""
        num_players = self.game_logic.num_players
        pokemon_ids = random.sample(range(1, 899), num_players)

        with ThreadPoolExecutor(max_workers=num_players) as executor:
            results = list(executor.map(self._fetch_pokemon_data, pokemon_ids))

        for i, pokemon_data in enumerate(results):
            player_num = i + 1
            if pokemon_data and pokemon_data['image_obj']:
                # ★ PIL Image를 ImageTk.PhotoImage로 변환
                photo_image = ImageTk.PhotoImage(pokemon_data['image_obj'])
                self.player_pokemon[player_num] = {
                    'id': pokemon_data['id'],
                    'name': pokemon_data['name'],
                    'image': photo_image # PhotoImage 객체를 저장
                }
                # ★ 리스트에 PhotoImage 참조를 추가하여 가비지 컬렉션 방지
                self.pokemon_image_references.append(photo_image)
            else:
                self.player_pokemon[player_num] = {'id': 0, 'name': f'Player {player_num}', 'image': None}

    def _draw_board(self):
        cell_size = 60
        coords = {}
        for i in range(100):
            row, col = 9 - (i // 10), (i % 10) if (9 - (i // 10)) % 2 != 0 else 9 - (i % 10)
            x1, y1 = col * cell_size, row * cell_size
            self.canvas.create_rectangle(x1, y1, x1 + cell_size, y1 + cell_size, outline="black")
            cell_num = i + 1
            self.canvas.create_text(x1 + 15, y1 + 15, text=str(cell_num))
            coords[cell_num] = (x1 + cell_size / 2, y1 + cell_size / 2)
        return coords

    def _draw_snakes_and_ladders(self):
        for head, tail in self.game_logic.snakes.items():
            self.canvas.create_line(self.cell_coords[head], self.cell_coords[tail], fill="red", width=4, arrow=tk.LAST)
        for start, end in self.game_logic.ladders.items():
            self.canvas.create_line(self.cell_coords[start], self.cell_coords[end], fill="green", width=4, dash=(4, 4))

    def _draw_players(self):
        self.canvas.delete("player")
        for p_num, pos in self.game_logic.player_positions.items():
            if p_num in self.player_pokemon and self.player_pokemon[p_num]['image']:
                pokemon_image = self.player_pokemon[p_num]['image']
                x, y = self.cell_coords[pos]
                offset = (p_num - 1) * 10 - (self.game_logic.num_players - 1) * 5
                self.canvas.create_image(x + offset, y, image=pokemon_image, tags="player")

    def play_turn(self):
        roll = self.game_logic.roll_die()
        p_name = self.player_pokemon[self.current_player]['name']
        message = f"{p_name}이(가) {roll}을(를) 굴렸습니다. "
        
        current_pos = self.game_logic.player_positions[self.current_player]
        next_pos = current_pos + roll

        if next_pos >= self.game_logic.board_size:
            if next_pos == self.game_logic.board_size:
                self.game_logic.player_positions[self.current_player] = self.game_logic.board_size
                self._draw_players()
                self.message_label.config(text=message)
                messagebox.showinfo("게임 종료!", f"축하합니다! {p_name}이(가) 승리했습니다!")
                self.roll_button.config(state="disabled")
                return
            else:
                 message += f"{self.game_logic.board_size}을(를) 초과하여 이동할 수 없습니다."
        else:
            self.game_logic.player_positions[self.current_player] = next_pos
            message += f"{current_pos}에서 {next_pos}로 이동. "
            if next_pos in self.game_logic.snakes:
                dest = self.game_logic.snakes[next_pos]
                self.game_logic.player_positions[self.current_player] = dest
                message += f"뱀을 만나 {dest}으로 미끄러집니다!"
            elif next_pos in self.game_logic.ladders:
                dest = self.game_logic.ladders[next_pos]
                self.game_logic.player_positions[self.current_player] = dest
                message += f"사다리를 타고 {dest}으로 올라갑니다!"

        self.current_player = (self.current_player % self.game_logic.num_players) + 1
        self.turn_count += 1
        next_p_name = self.player_pokemon[self.current_player]['name']

        self.turn_label.config(text=f"턴: {self.turn_count // self.game_logic.num_players}")
        self.player_label.config(text=f"{next_p_name}의 차례", fg=self.player_colors[self.current_player-1])
        self.message_label.config(text=message)
        self._draw_players()

def main():
    parser = argparse.ArgumentParser(description="GUI 뱀 사다리 게임")
    parser.add_argument("--players", type=int, default=2, choices=range(2, 5), help="플레이어 수 (2-4, 기본값: 2)")
    parser.add_argument("--snakes", type=int, default=8, help="뱀의 수 (기본값: 8)")
    parser.add_argument("--ladders", type=int, default=8, help="사다리의 수 (기본값: 8)")
    parser.add_argument("--seed", type=int, default=None, help="랜덤 시드")
    args = parser.parse_args()

    app = SnakeLadderGUI(num_players=args.players, num_snakes=args.snakes, num_ladders=args.ladders, seed=args.seed)
    app.mainloop()

if __name__ == "__main__":
    main()