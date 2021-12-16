import pyxel
import random
import math

class Status:
    start_menu = 0
    playing = 1
    game_over = 2

def collision_detection(node_list):
    collision_list = []
    for node in node_list:
        if node.y + Node.RADIUS >= App.HEIGHT:
            collision_list.append(True)
            continue
        collision = False
        for other_node in node_list:
            if node is other_node:
                continue
            if other_node.y - node.y == Node.RADIUS*2 and node.x == other_node.x:
                collision = True
                break
        collision_list.append(collision)
    return collision_list

class Node:
    RADIUS = 10
    BASE = 2
    COLOR_LIST = [15,14,13,12,11,10,9,8,6,5,4,3,2]
    def __init__(self, x, y, multiplier):
        self.x = x
        self.y = y
        self.multiplier = multiplier
        self.num = Node.BASE ** multiplier
        self.digits = math.floor(math.log10(self.num)+1)
        self.color = Node.COLOR_LIST[self.multiplier]
    def move(self, x:int, node_list)->None:
        new_x = self.x + x*Node.RADIUS*2
        if new_x < Node.RADIUS:
            return
        elif new_x > App.WIDTH - Node.RADIUS:
            return
        for node in node_list:
            if self is node:
                continue
            if abs(node.x - new_x)**2 + abs(node.y - self.y)**2\
                 <= (Node.RADIUS*2)**2:
                return
        self.x = new_x
    def speed_up(self)->None:
        self.y += Node.RADIUS
    def update(self):
        if pyxel.frame_count % (App.FPS/2) == 0:
            self.y += Node.RADIUS
    def draw(self):
        pyxel.circ(self.x,self.y, Node.RADIUS-1, self.color)
        offset_x = int(float(self.digits)/2.0 * 3)
        pyxel.text(self.x-offset_x,self.y-2, str(self.num), pyxel.COLOR_WHITE)

class App:
    WIDTH = Node.RADIUS*2 * 5
    HEIGHT = Node.RADIUS*2 * 8
    FPS = 20
    TITLE = "ニノベキ2"

    def __init__(self):
        self.node_list = []
        self.status = Status.start_menu
        pyxel.init(App.WIDTH, App.HEIGHT, App.TITLE,App.FPS)
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.status == Status.start_menu:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.status = Status.playing
        elif self.status == Status.playing:
            self.playing_update()
        elif self.status == Status.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.status = Status.start_menu
    
    def playing_update(self):
        # ノードスポーン
        collision_list = collision_detection(self.node_list)
        if pyxel.frame_count % App.FPS == 0 and sum(collision_list) == len(collision_list):
            initial_x = random.randint(0, App.WIDTH/(Node.RADIUS*2)-1)*Node.RADIUS*2 + Node.RADIUS
            self.node_list.append(Node(initial_x, -Node.RADIUS, random.randint(1,5)))

        # ボタン操作処理
        collision_list = collision_detection(self.node_list)
        if len(self.node_list) != 0 and collision_list[-1] == False:
            if pyxel.btnp(pyxel.KEY_RIGHT):
                self.node_list[-1].move(1, self.node_list)
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.node_list[-1].move(-1, self.node_list)
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.node_list[-1].speed_up()
        
        # ノード結合
        collision_list = collision_detection(self.node_list)
        for node, collision in zip(self.node_list[::-1], collision_list):
            if collision == False:
                continue
            for other_node, other_collision in zip(self.node_list[::-1],collision_list):
                if other_collision == False:
                    continue
                if node is other_node:
                    continue
                if (node.num == other_node.num) and \
                    abs(node.x - other_node.x)**2 + \
                    abs(node.y - other_node.y)**2 <= (Node.RADIUS*2)**2:
                    self.draw()
                    self.node_list.remove(node)
                    new_node = Node(other_node.x, other_node.y,other_node.multiplier+1)
                    self.node_list.remove(other_node)
                    self.node_list.append(new_node)
                    return

        
        # ノード更新
        collision_list = collision_detection(self.node_list)
        for node, collision in zip(self.node_list, collision_list):
            if collision==False:
                node.update()
        if self.game_over_decision():
            self.status = Status.game_over

    def draw(self):
        pyxel.cls(pyxel.COLOR_NAVY)
        if self.status == Status.start_menu:
            pyxel.text(0,0,"Press Enter",pyxel.COLOR_WHITE)
        elif self.status == Status.playing:
            self.draw_nodes()
        elif self.status == Status.game_over:
            self.draw_nodes()
            pyxel.text(0,0,"Game Over",pyxel.COLOR_WHITE)

    def draw_nodes(self):
        for node in self.node_list:
            node.draw()
    
    def game_over_decision(self)->bool:
        lowest_y = App.HEIGHT 
        for node in self.node_list:
            if lowest_y > node.y:
                lowest_y = node.y
        if lowest_y < 0:
            return True
        else:
            return False


App()