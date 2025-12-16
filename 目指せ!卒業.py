import os
import pygame
import sys

"""
定数宣言
"""
#カレントディレクトリへの移動
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#デフォルトGUIサイズ
DEFAULT_SIZE: tuple[int, int] = (0, 0)

"""
オブジェクトクラス群
"""
class Chara(pygame.sprite.Sprite):
    """
    プレイヤー
    """
    def __init__(self):
        """
        初期化
        """
        super().__init__()
        
        self.image = "path"
        
        #ステータス
        self.spd = 0
        self.atk = 0
        self.hp = 0
        self.level = 0        
        self.exp = 0
        
        #座標
        self.x = 0
        self.y = 0
        
        #所持武器
        #制約：最大5, インスタンス
        self.weapons = []
    def update(self):
        """
        描画処理
        """
        pass
    
    def level_up(self):
        """
        レベルアップイベント
        """
        pass

"""
敵
"""
class Enemy1(pygame.sprite.Sprite):
    """
    敵
    """
    def __init__(self):
        """
        初期化処理
        """
        super().__init__()

        self.image = "path"

        self.spd = 0
        self.atk = 0
        self.hp = 0
        self.exp = 0
        
        self.drops = []

    def update(self):
        """
        画面描画
        """        
        pass
    
    def atk_effect(self):
        """
        攻撃挙動
        """
        pass
    
"""
武器
"""
class Weapon1(pygame.sprite.Sprite):
    """
    武器
    """
    def __init__(self):
        """
        初期化
        """
        super().__init__()
        
        self.level = 0
        self.atk = 0
        
    def behavior(self):
        """
        武器の挙動
        """
        pass

"""
アイテムオブジェクトクラス
"""
class Item1(pygame.sprite.Sprite):
    def __init__(self):
        """
        初期化
        """
        super().__init__()
        
        self.image = "path"
    
    def update(self):
        """
        描画処理
        """
        pass
    
    def behavior(self):
        """
        挙動
        """
        pass

"""
実行
"""
class Application():
    """
    実行処理クラス
    """
    def __init__(self):
        """
        初期化処理
        """
        pygame.init()

        self.screen = pygame.display.set_mode(DEFAULT_SIZE, pygame.FULLSCREEN)
        pygame.display.set_caption("目指せ！卒業")
        
        self.bg_img = pygame.image.load(f"images/back_ground.png")
        w = self.screen.get_width()
        h = self.screen.get_height()
        self.bg_img = pygame.transform.scale(self.bg_img, (w, h))
               
        self.clock = pygame.time.Clock()
        self.running = True
    
    def run(self):
        """
        画面描画
        """
        while self.running:
            self.handle_events()

            #背景色描画
            self.screen.blit(self.bg_img, [0, 0])
            
            self.clock.tick(60) #FPS制御
            pygame.display.update() #画面更新

        #ゲーム終了
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """
        イベント処理
        """
        #単発系イベント
        for event in pygame.event.get():
            
            #終了処理
            #閉じるボタン判定
            if event.type == pygame.QUIT:
                self.running = False
            #キー押下判定
            elif event.type == pygame.KEYDOWN:
                #ESC判定
                if event.key == pygame.K_ESCAPE:
                    self.running = False 
        
        #継続系イベント
        key_state = pygame.key.get_pressed()

if __name__ == "__main__":
    app = Application()
    app.run()