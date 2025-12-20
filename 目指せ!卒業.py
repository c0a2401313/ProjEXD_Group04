import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),     
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = 0

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

            #加速イベント
            if key_lst[pg.K_LSHIFT]: #スペース
                self.speed = 20 #加速化処理
            else: #通常時
                self.speed = 10

        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]

        #追加機能4:無敵状態
        if self.state == "hyper":
            self.hyper_life -= 1
            self.image = pg.transform.laplacian(self.image)
            if self.hyper_life < 0:
                self.state = "normal"
                self.image = self.imgs[self.dire]

        screen.blit(self.image, self.rect)

class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird,angle0=0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))

        #機能６
        angle += angle0


        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 1.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

class Gravity(pg.sprite.Sprite):
    """
    重力フィールドに関するクラス
    発動時に画面を黒くし、決めセリフを表示する
    """
    def __init__(self, life: int):
        """
        引数：持続時間の整数型
        """
        super().__init__()
        self.life = life
        self.alpha = 250
        
        # 1. ベースとなる黒い画面を作成
        self.image = pg.Surface((WIDTH, HEIGHT))
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect()

        # 2. 決めセリフの準備（追加箇所）
        # フォントサイズ80, 赤色(255, 0, 0) で文字を作成
        self.font = pg.font.Font(None, 100) 
        self.text_img = self.font.render("Gravity Zero!", True, (255, 255, 255))
        self.text_rect = self.text_img.get_rect()
        self.text_rect.center = (WIDTH // 2, HEIGHT // 2)

    def update(self):
        """
        時間経過で透明度を上げ、徐々に明るくする
        """
        self.alpha -= 0.5
        if self.alpha < 0:
            self.alpha = 0

        # 1. 毎回画面を黒く塗りつぶす（前のフレームの絵を消す）
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        
        # 2. 黒い画面の上に文字を重ねる（追加箇所）
        self.image.blit(self.text_img, self.text_rect)

        # 3. 透明度をセット（背景と文字、両方が薄くなる）
        self.image.set_alpha(self.alpha)

        self.life -= 1
        if self.life < 0:
            self.kill()

#機能６
class NeoBeam:
    def __init__(self,bird: Bird,num):
        """
        __init__ の Docstring

        :bird : こうかとん
        num : ビームの本数
        """
        self.bird = bird
        self.num = num
    def gen_beams(self):
        beams_list = []
        step = 100 // (self.num -1)
        for angle in range(-50,51,step):
            beams_list.append(Beam(self.bird,angle))
        return beams_list

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10 % 2]
        if self.life < 0:
            self.kill()

#スコアをデバック用にレベルとして代用
class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 13
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class EMP(pg.sprite.Sprite):
    """
    電磁パルス（EMP）に関するクラス
    """
    def __init__(self, emys: pg.sprite.Group, bombs: pg.sprite.Group, screen: pg.Surface):
        """
        EMPを生成し，敵機と爆弾を無効化する
        引数1 emys：敵機グループ
        引数2 bombs：爆弾グループ
        引数3 screen：画面Surface
        """
        super().__init__()
        self.emys = emys
        self.bombs = bombs
        self.screen = screen
        self.lifetime = 3#黄色画面表示時間

        # 敵機を無効化
        for emy in emys:
            emy.interval = float("inf")
            emy.image = pg.transform.laplacian(emy.image)

        # 爆弾を無効化
        for bomb in bombs:
            bomb.speed = bomb.speed // 2
            bomb.state = "inactive"

        # 画面全体に透明な黄色矩形を表示
        self.image = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        self.image.fill((255, 255, 0, 100))  # RGBA (alpha=100)
        self.rect = self.image.get_rect()

    def update(self):
        """
        EMP効果の継続時間を管理
        """
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


# ===================== ここから追加：Shieldクラス =====================

class Shield(pg.sprite.Sprite):
    """
    防御壁（Shield）に関するクラス
    青い矩形（横幅20 / 高さ こうかとんの身長の2倍）
    life フレーム経過で消滅
    """
    def __init__(self, bird: Bird, life: int):
        super().__init__()
        width = 20
        height = bird.rect.height * 2

        # 手順1：空のSurfaceを生成（アルファ付き）
        base_image = pg.Surface((width, height), pg.SRCALPHA)

        # 手順2：青いrectを描画
        pg.draw.rect(base_image, (0, 0, 255), (0, 0, width, height))

        # 手順3：こうかとんの向きを取得
        vx, vy = bird.dire
        if vx == 0 and vy == 0:
            vx = 1  # 万一(0,0)なら右向き扱い

        # 手順4：角度を求める
        angle = math.degrees(math.atan2(-vy, vx))

        # 手順5：Surfaceを回転
        self.image = pg.transform.rotozoom(base_image, angle, 1.0)

        # Rectを取得
        self.rect = self.image.get_rect()

        # 手順6：向いている方向に、こうかとん1体分ずらして配置
        offset = max(bird.rect.width, bird.rect.height)
        self.rect.centerx = bird.rect.centerx + vx * offset
        self.rect.centery = bird.rect.centery + vy * offset

        # 寿命
        self.life = life

    def update(self):
        """
        残り寿命を1減らし、0未満になったら消滅
        """
        self.life -= 1
        if self.life < 0:
            self.kill()

# ===================== ここまで追加：Shieldクラス =====================


class Enemy(pg.sprite.Sprite):
    """
    Enemy の Docstring
    """

    def __init__(self, lv):
        """
        Enemy の Docstring
        """
        super().__init__()
        
        wave = lv // 3
        if lv >= 15:wave = 4
        enemy_fid_dic = {0: "fig/report.png", 1: "fig/clock.png", 2: "fig/ai.png", 3: "fig/guard.png", 4: "fig/teacher.png"}
        enemy_stats = [[100,100,100,2],[100,100,100,2],[100,100,100,2],[100,100,100,2],[100,100,100,2]]
        self.image = pg.transform.rotozoom(pg.image.load(enemy_fid_dic[wave]), 0, 0.1)
        self.rect = self.image.get_rect()
        #HP,attack,defense,speed
        self.stats = enemy_stats[wave]
        if random.choice([True, False]):
            self.rect.centerx = random.choice([0, WIDTH])
            self.rect.centery = random.randint(0, HEIGHT)
        else:
            self.rect.centerx = random.randint(0, WIDTH)
            self.rect.centery = random.choice([0, HEIGHT])

        self.pos = pg.Vector2(self.rect.center)
        self.speed = self.stats[3]

    def update(self, bird_pos):
        target_vector = pg.math.Vector2(bird_pos)
        direction = target_vector - self.pos

        if direction.length() != 0:
            velocity  = direction.normalize() * self.speed
            self.pos += velocity
        self.rect.center = self.pos

class LastBoss(Enemy):
    """
    ラスボスに関するクラス
    画面を埋め尽くす巨大な敵で、上から徐々に降りてくる
    """
    def __init__(self):
        super().__init__(15)  # レベル設定（画像決定用、中身は何でも良い）
        
        # 画面を埋め尽くすサイズに画像を拡大 (元の画像を2倍にするなど)
        original_img = pg.image.load(f"fig/fantasy_maou_devil.png")
        self.image = pg.transform.rotozoom(original_img, 0, 2.5) 
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2  # 横位置は画面中央
        self.rect.bottom = 0           # 初期位置は画面の上外
        
        self.pos = pg.Vector2(self.rect.center)
        self.speed = 1  # じりじりと襲ってくる（低速）

    def update(self, bird_pos):
        """
        こうかとんの位置に関係なく、じりじりと下に降りてくる
        """
        self.pos.y += self.speed
        self.rect.centery = int(self.pos.y)
        
        # 画面下まで来たら止まる（あるいはゲームオーバー判定など）
        if self.rect.top > HEIGHT:
            self.rect.top = HEIGHT  # とりあえず止める処理


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    bg_img = pg.image.load(f"fig/back_ground.png")
    bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))
    
    score = Score()

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    gravity = pg.sprite.Group()
    emys = pg.sprite.Group()
    shields = pg.sprite.Group()  # 防御壁グループ（1つだけ存在）
    emps = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()
    ending = False
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                #機能６
                if key_lst[pg.K_LSHIFT]:
                    nb = NeoBeam(bird, 3) #第２引数がビームの本数
                    beams.add(nb.gen_beams())
                else:
                    #下のbeams.add(Beam(bird))を0つ分タブで上げる。


                    beams.add(Beam(bird))
            if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT and score.value > 100:
                bird.state = "hyper"
                bird.hyper_life = 500
                score.value -= 100
            if event.type == pg.KEYDOWN and event.key== pg.K_e:
                if score.value >= 20:
                    emps.add(EMP(emys,bombs,screen))
                    score.value -=20
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                if score.value >= 200:
                    gravity.add(Gravity(400))
                    score.value -= 200
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    beams.add(Beam(bird))
                # 防御壁：Sキー押下で発動
                if event.key == pg.K_s:
                    # スコア50以上＆既に壁がないときだけ発動
                    if score.value >= 50 and len(shields) == 0:
                        shields.add(Shield(bird, life=400))
                        score.value -= 50  # 消費スコア

        screen.blit(bg_img, [0, 0])

        if score.value >= 15 and not ending:
            for enemy in emys:enemy.kill()
            gravity.add(Gravity(400))
            ending = True
            emys.add(LastBoss())
        
        if tmr % 50 == 0 and not ending:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy(score.value))

        if tmr % 500 == 0:score.value += 1 #500フレームごとに50点加算



        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():  # ビームと衝突した爆弾リスト
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ

        # Shieldと爆弾の衝突（ここではスコアは増やさない）
        hit_dict = pg.sprite.groupcollide(shields, bombs, False, True)
        for sh, hit_bombs in hit_dict.items():
            for bomb in hit_bombs:
                exps.add(Explosion(bomb, 50))

        # # こうかとんと爆弾の衝突
        # for bomb in pg.sprite.spritecollide(bird, bombs, True):
        #     bird.change_img(8, screen)  # こうかとん悲しみエフェクト
        #     score.update(screen)
        #     pg.display.update()
        #     time.sleep(2)
        #     return
        for bomb in pg.sprite.groupcollide(bombs, gravity, True, False).keys():  # 力場と衝突した爆弾リスト
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ

            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
            if bird.state == "hyper":
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.value += 1  # 1点アップ
            else:
                if bomb.state == "inactive":
                    bomb.kill()
                    continue
                else:
                    bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                    score.update(screen)
                    pg.display.update()
                    time.sleep(2)
                    return

        gravity.update()
        gravity.draw(screen)
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update(bird.rect.center)
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        shields.update()
        shields.draw(screen)
        exps.update()
        exps.draw(screen)

        emps.update()
        emps.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()