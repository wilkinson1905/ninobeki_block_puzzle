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
                 < (Node.RADIUS*2)**2:
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
        self.restart()
        pyxel.init(App.WIDTH, App.HEIGHT, App.TITLE,App.FPS)
        pyxel.run(self.update, self.draw)
    def restart(self):
        self.node_list = []
        self.status = Status.start_menu
        self.score = 0
        self.during_binding = False
        self.binding_count = 0
        self.max_binding_count = 0
        self.max_node_num = 0
        self.spawn_range = [1,3]
        self.next_node_multi = self.spawn_range[0]

    def update(self):
        if self.status == Status.start_menu:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.status = Status.playing
        elif self.status == Status.playing:
            self.playing_update()
        elif self.status == Status.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.restart()
                self.status = Status.start_menu
    
    def playing_update(self):
        # ノードスポーン
        collision_list = collision_detection(self.node_list)
        if pyxel.frame_count % App.FPS == 0 and sum(collision_list) == len(collision_list)\
                and self.during_binding == False:
            self.binding_count = 0
            initial_x = 2*Node.RADIUS*2 + Node.RADIUS
            self.node_list.append(Node(initial_x, Node.RADIUS, self.next_node_multi))
            self.next_node_multi = random.randint(self.spawn_range[0] , self.spawn_range[1])
            sp_range = list(range(self.spawn_range[0],self.spawn_range[1]+1))
            self.next_node_multi = random.choices(sp_range,weights=sp_range[::-1])[0]

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
        if len(collision_list) != 0 and collision_list[-1] == True:
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
                        self.during_binding = True
                        self.binding_count += 1
                        #スコア計算
                        self.score += new_node.num * self.binding_count
                        if new_node.multiplier > self.spawn_range[1] and \
                            new_node.num > self.max_node_num:
                            self.max_node_num = new_node.num
                            self.spawn_range[1] = new_node.multiplier-2
                        if self.binding_count > self.max_binding_count:
                            self.max_binding_count = self.binding_count
                        return
        self.during_binding = False
        
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
            pyxel.text(App.WIDTH/2-20,App.HEIGHT/2,"Press Enter",pyxel.COLOR_WHITE)
        elif self.status == Status.playing:
            self.draw_nodes()
        elif self.status == Status.game_over:
            self.draw_nodes()
            pyxel.text(App.WIDTH/2-20,App.HEIGHT/2,"GAME OVER",pyxel.COLOR_WHITE)
        #スコア等表示
        width_offset = App.WIDTH/2 + 3*3
        height_offset = 2
        pyxel.rect(0,0,App.WIDTH,Node.RADIUS*2,pyxel.COLOR_DARK_BLUE)

        pyxel.text(0,height_offset,"score :"+str(self.score),pyxel.COLOR_WHITE)
        pyxel.text(width_offset,height_offset,"chain:"+str(self.max_binding_count),pyxel.COLOR_WHITE)
        pyxel.text(0,Node.RADIUS+height_offset,"maxnum:"+str(self.max_node_num),pyxel.COLOR_WHITE)
        pyxel.text(width_offset,Node.RADIUS+height_offset,"next :"+str(Node.BASE**self.next_node_multi),\
            pyxel.COLOR_WHITE)

    def draw_nodes(self):
        for node in self.node_list:
            node.draw()
    
    def game_over_decision(self)->bool:
        lowest_y = App.HEIGHT 
        for node in self.node_list:
            if lowest_y > node.y:
                lowest_y = node.y
        if lowest_y < Node.RADIUS*2:
            return True
        else:
            return False


App()