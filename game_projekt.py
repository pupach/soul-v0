import pygame
import random
import math


class Supervisor:
    def __init__(self, width, height, begin_of_prohod, end_of_prohod,
                 granitca1, granitca2):
        self.width = width
        self.height = height
        self.govno = pygame.sprite.Group()
        self.begin_of_prohod = begin_of_prohod
        self.end_of_prohod = end_of_prohod
        self.level = 0
        self.igrok = igrok(self.govno, 0, 0)
        self.scorost = 450
        self.uroven = 1
        self.granitca1 = granitca1
        self.granitca2 = granitca2
        self.pole1 = random.randint(1, 3)
        self.pole2 = random.randint(1, 3)
        self.pole3 = random.randint(1, 3)

    def generate_osnov(self, min_mobs, max_mobs):
        self.print_to_file('generate_osnov')
        self.level += 1
        if self.level <= self.granitca1:
            self.uroven = (1, self.pole1)
        elif self.level <= self.granitca2:
            self.uroven = (2, self.pole2)
        else:
            self.uroven = (3, self.pole3)
        self.all = pygame.sprite.Group()
        self.number_izobraj = 0
        self.moving_objekt = pygame.sprite.Group()
        self.igrok_and_portal = pygame.sprite.Group()
        self.igrok.add(self.igrok_and_portal)
        self.igrok.add(self.moving_objekt)
        self.min_mobs = min_mobs
        self.max_mobs = max_mobs
        self.igrok.add(self.all)
        self.max_kolvo_room = 8
        self.all_room = pygame.sprite.Group()
        self.enemy = pygame.sprite.Group()

    def generate_window(self):
        self.print_to_file('generate_window')
        x = self.igrok.virt_coor_x - self.width // 2
        x += (self.igrok.rect.width // 2)
        y = self.igrok.virt_coor_y - self.height // 2
        y += (self.igrok.rect.height // 2)
        self.window = Window(self.all, x, y, self.height, self.width)

    def generate_rooms(self):
        self.print_to_file('generate_rooms')
        self.generate_room_of_spawn()
        t = random.randint(2, self.max_kolvo_room)
        for i in range(0, t):
            self.generate_coor_room(False, True)
        self.generate_coor_room(True)

    def generate_coor_room(self, room_of_end=False, room_aktiv=False):
        self.print_to_file('generate_coor_room')
        x1 = False
        while not x1:
            t1 = random.randint(0, len(self.all_room) - 1)
            t2 = random.randint(1, 4)
            a = 0
            for i in self.all_room:
                if a == t1:
                    coor_x = i.virt_coor_x
                    coor_y = i.virt_coor_y
                a += 1
            d = Room(self.govno, 0, 0, self.uroven)
            d.kill()
            if t2 == 1:
                coor_x -= d.rect.width
            elif t2 == 2:
                coor_y -= d.rect.height
            elif t2 == 3:
                coor_x += d.rect.width
            elif t2 == 4:
                coor_y += d.rect.height
            x = Room(self.all, coor_x, coor_y, self.uroven)
            self.do_draw(self.all)
            x1 = self.proverka_of_move(x)
            x.kill()
        self.generate_room(coor_x, coor_y, room_of_end, room_aktiv)

    def generate_room(self, coor_x, coor_y, room_of_end, room_aktiv):
        self.print_to_file('generate_room')
        if room_of_end:
            d = Room(self.all, coor_x, coor_y, self.uroven)
            d.add(self.all_room)
            self.generate_portal(d, coor_x, coor_y)
            self.generate_wall_on_perimetr(d)
        else:
            d = Room(self.all, coor_x, coor_y, self.uroven, room_aktiv)
            d.add(self.all_room)
            self.generate_wall_on_perimetr(d)
            self.generate_wall(d)

    def generate_wall(self, room):
        self.print_to_file('generate_wall')
        sp = self.choice_rastanovka_wall()
        if len(sp) == 0:
            return 0
        for i in range(0, len(sp)):
            for j in range(0, len(sp[i])):
                if sp[i][j] == '1':
                    s = Wall_in_room(self.all, 0, 0)
                    room.spisok.append(s)
                    s.virt_coor_y = room.virt_coor_y + i * s.rect.height
                    s.virt_coor_x = room.virt_coor_x + j * s.rect.width

    def choice_rastanovka_wall(self):
        self.print_to_file('choice_rastanovka_wall')
        f = open('шаблоныстен.txt')
        sp_osnov = []
        spisok = []
        a = 0
        for i in f:
            a += 1
            i = i.strip()
            if i == 'n':
                sp_osnov.append(spisok)
                spisok = []
            else:
                spisok.append(list(i))
        x = random.randint(0, len(sp_osnov))
        if x == len(sp_osnov):
            return []
        else:
            return sp_osnov[x]

    def kill_mobs(self):
        self.print_to_file('kill_mobs')
        for i in self.igrok.room.spisok:
            if i.name == 'zombi':
                i.health = -1000000
                self.proverka_of_live(i)

    def generate_mobs(self, room):
        self.print_to_file('generate_mobs')
        if room.aktiv:
            t = random.randint(self.min_mobs, self.max_mobs)
            room.kolvo_mob = t
            for i in range(0, t):
                self.generate_mob(room)

    def generate_mob(self, room):
        self.print_to_file('generate_mob')
        global spisok_of_mobs
        t = random.randint(0, len(spisok_of_mobs) - 1)
        if spisok_of_mobs[t] == 'zombi':
            h = zombi(self.all, 0, 0)
            room.spisok.append(h)
            h.add(self.moving_objekt)
            self.generate_coor_of_mob(room, h)
        elif spisok_of_mobs[t] == 'bomba':
            h = bomba(self.all, 0, 0)
            room.spisok.append(h)
            h.add(self.moving_objekt)
            self.generate_coor_of_mob(room, h)

    def generate_coor_of_mob(self, room, mob):
        self.print_to_file('generate_coor_of_mob')
        x1 = False
        while not x1:
            x = random.randint(room.virt_coor_x,
                               room.virt_coor_x + room.rect.width)
            y = random.randint(room.virt_coor_y,
                               room.virt_coor_y + room.rect.height)
            mob.pomen_coor(x, y)
            self.do_draw(self.all)
            x1 = self.proverka_of_move(mob)

    def generate_portal(self, room, coor_x, coor_y):
        self.print_to_file('generate_portal')
        k = Portal(self.govno, 0, 0)
        x = coor_x + room.rect.width // 2 - k.rect.width // 2
        y = coor_y + room.rect.height // 2 - k.rect.height // 2
        k1 = Portal(self.all, x, y)
        k1.add(self.igrok_and_portal)

    def do_draw(self, group):
        self.print_to_file('do_draw')
        spisok = []
        for i in group:
            spisok.append(i)
        spisok.sort(key=lambda a: a.z)
        for i in spisok:
            if not i.not_draw:
                p = pygame.sprite.Group()
                i.add(p)
                if type(i.virt_coor_x) != int:
                    i.virt_coor_x = i.virt_coor_x[0]
                if type(i.virt_coor_y) != int:
                    i.virt_coor_y = i.virt_coor_y[0]
                i.rect.x = i.virt_coor_x - self.window.virt_coor_x
                i.rect.y = i.virt_coor_y - self.window.virt_coor_y
                p.draw(self.window.screen)
                i.remove(p)

    def rastet_coor_of_prohod(self, room):
        self.print_to_file('rastet_coor_of_prohod')
        begin_width = room.virt_coor_x + room.rect.width * self.begin_of_prohod
        end_width = room.virt_coor_x + room.rect.width * self.end_of_prohod
        begin_height = room.virt_coor_y
        begin_height += room.rect.height * self.begin_of_prohod
        end_height = room.virt_coor_y + room.rect.height * self.end_of_prohod
        return begin_width, end_width, begin_height, end_height

    def generate_wall_on_perimetr(self, room):
        self.print_to_file('generate_wall_on_perimetr')
        lst = self.rastet_coor_of_prohod(room)
        begin_width, end_width = lst[0:2]
        begin_height, end_height = lst[2:]
        st = Wall(self.govno, 0, 0)
        coor = room.virt_coor_x + room.rect.width - st.rect.width
        a = room.virt_coor_y + room.rect.height
        for i in range(room.virt_coor_y, a, st.rect.height):
            if i == room.virt_coor_y:
                a = room.virt_coor_x + room.rect.width
                for j in range(room.virt_coor_x, a, st.rect.width):
                    if j >= begin_width and j <= end_width:
                        st1 = Wall(self.all, j, i - st.rect.width, False, True)
                        room.spisok.append(st1)
                    else:
                        st1 = Wall(self.all, j, i - st.rect.width, False)
                    room.spisok.append(st1)

            elif i == room.virt_coor_y + room.rect.height - st.rect.height:
                a = room.virt_coor_x + room.rect.width
                for j in range(room.virt_coor_x, a, st.rect.width):
                    if j >= begin_width and j <= end_width:
                        st1 = Wall(self.all, j, i + st.rect.width, False, True)
                        room.spisok.append(st1)
                    else:
                        st1 = Wall(self.all, j, i + st.rect.width, False)
                    room.spisok.append(st1)
            else:
                if i >= begin_height and i <= end_height:
                    st1 = Wall(self.all,
                               room.virt_coor_x - st.rect.width,
                               i, False, True)
                    st2 = Wall(self.all, coor + st.rect.height, i, False, True)
                else:
                    st1 = Wall(self.all,
                               room.virt_coor_x - st.rect.width,
                               i, False)
                    st2 = Wall(self.all, coor + st.rect.height, i, False)
                room.spisok.append(st1)
                room.spisok.append(st2)

    def steret_nekot_prohod(self, room):
        self.print_to_file('steret_nekot_prohod')
        for i in range(0, len(room.spisok)):
            if room.spisok[i].is_wall_on_prohod:
                d = pygame.sprite.Group()
                room.spisok[i].add(d)
                room.spisok[i].not_draw = False
                self.do_draw(d)
                spisok1 = pygame.sprite.spritecollide(room.spisok[i],
                                                      self.all_room,
                                                      False)
                room.spisok[i].not_draw = True
                room.spisok[i].kill()
                b = len(spisok1)
                if b == 0:
                    room.spisok[i].add(self.all)
                    room.spisok[i].not_draw = False
                    room.spisok[i].is_wall_on_prohod = False

    def hod_objekt(self, objekt, x, y):
        self.print_to_file('hod_objekt')
        x_objekt = objekt.virt_coor_x
        y_objekt = objekt.virt_coor_y
        gipot = math.sqrt(abs(x - x_objekt) ** 2 + abs(y - y_objekt) ** 2)
#        objekt.hod_in_one_napr -= 1
        if objekt.speed <= gipot:
            protent = objekt.speed / gipot
            k = [int(x_objekt + protent * (x - x_objekt))]
            k.append(int(y_objekt + protent * (y - y_objekt)))
            return k
        else:
            return x, y

    def hod_zombi(self, objekt):
        self.print_to_file('hod_zombi')
        x = False
        a = 0
        i = 0
        while not x:
            i += 1
            a += 1
            if i >= 10000:
                x = True
            elif a <= 3:
                x1, y1 = self.taktik_of_hod_to_igrok_around(100, 1)
                x1, y1 = self.hod_objekt(objekt, x1, y1)
                objekt.pomen_coor(x1, y1)
                x = self.proverka_of_move(objekt)
            else:
                self.print_to_file(objekt.name)
                x1, y1 = self.taktik_of_hod_to_igrok_random(objekt)
                self.print_to_file(str(x1) + str(y1))
                x1, y1 = self.hod_objekt(objekt, x1, y1)
                self.print_to_file(str(x1) + str(y1))
                objekt.pomen_coor(x1, y1)
                x = self.proverka_of_move(objekt)
            self.proverka_of_live(objekt)

    def taktik_of_hod_to_igrok_random(self, objekt, hod_in_one_napr=1):
        self.print_to_file('taktik_of_hod_to_igrok_random')
        x_objekt = objekt.virt_coor_x
        y_objekt = objekt.virt_coor_y
        x1 = random.randint((x_objekt - objekt.speed) * hod_in_one_napr,
                            (x_objekt + objekt.speed) * hod_in_one_napr)
        x2 = random.randint((x_objekt - objekt.speed) * hod_in_one_napr,
                            (x_objekt + objekt.speed) * hod_in_one_napr)
        y1 = random.randint((y_objekt - objekt.speed) * hod_in_one_napr,
                            (y_objekt + objekt.speed) * hod_in_one_napr)
        y2 = random.randint((y_objekt - objekt.speed) * hod_in_one_napr,
                            (y_objekt + objekt.speed) * hod_in_one_napr)
        f = random.randint(1, 4)
        if f == 1:
            x_nado = x1
            y_nado = (y_objekt - objekt.speed) * hod_in_one_napr
        elif f == 1:
            x_nado = x2
            y_nado = (y_objekt + objekt.speed) * hod_in_one_napr
        elif f == 1:
            x_nado = (x_objekt - objekt.speed) * hod_in_one_napr
            y_nado = y1
        else:
            x_nado = (x_objekt + objekt.speed) * hod_in_one_napr
            y_nado = y2
        return x_nado, y_nado

    def taktik_of_hod_to_igrok_around(self, razbros, koef):
        self.print_to_file('taktik_of_hod_to_igrok_around')
        global slovar_for_random
        x_of_igrok = self.igrok.virt_coor_x
        y_of_igrok = self.igrok.virt_coor_y
        g = slovar_for_random.get((razbros, koef), '0')
        if g == '0':
            sp = [0] * koef
            for i in range(0, razbros):
                d = razbros - i
                f = (d - 1) // koef + 1
                for j in range(0, f):
                    sp.append(d)
                    sp.append(0 - d)
            slovar_for_random[(razbros, koef)] = sp
        smej_x = random.choice(slovar_for_random[(razbros, koef)])
        smej_y = random.choice(slovar_for_random[(razbros, koef)])
        x_move = x_of_igrok + smej_x
        y_move = y_of_igrok + smej_y
        return x_move, y_move

    def move_camera_to_igrok(self):
        self.print_to_file('move_camera_to_igrok')
        coor_x = self.igrok.virt_coor_x - self.width // 2
        coor_x += (self.igrok.rect.width // 2)
        coor_y = self.igrok.virt_coor_y - self.height // 2
        coor_y += (self.igrok.rect.height // 2)
        self.window.virt_coor_x = coor_x
        self.window.virt_coor_y = coor_y

    def generate_room_of_spawn(self):
        self.print_to_file('generate_room_of_spawn')
        x = random.randint(0, self.max_kolvo_room + 9)
        y = random.randint(0, self.max_kolvo_room + 2)
        self.room_of_spawn = Room(self.all, x, y, self.uroven)
        self.room_of_spawn.add(self.all_room)
        self.generate_coor_igrok()
        self.generate_window()
        self.generate_wall_on_perimetr(self.room_of_spawn)

    def generate_coor_igrok(self):
        self.print_to_file('generate_coor_igrok')
        x_of_igrok = self.room_of_spawn.virt_coor_x
        x_of_igrok += self.room_of_spawn.rect.width // 2
        y_of_igrok = self.room_of_spawn.virt_coor_y
        y_of_igrok += self.room_of_spawn.rect.height // 2
        self.igrok.pomen_coor(x_of_igrok - self.igrok.rect.width // 2,
                              y_of_igrok - self.igrok.rect.height // 2)
        self.igrok.room = self.room_of_spawn

    def generate_level(self):
        self.generate_rooms()

    def next_level(self):
        self.print_to_file('next_level')
        spisok_of_pereset = pygame.sprite.spritecollide(self.igrok,
                                                        self.igrok_and_portal,
                                                        False)
        for i in range(0, len(spisok_of_pereset)):
            if spisok_of_pereset[i].name == 'portal':
                self.generate_osnov(self.min_mobs, self.max_mobs)
                self.begin_game()

    def smen_room_of_igrok(self, room):
        self.print_to_file('smen_room_of_igrok')
        self.igrok.room = room
        room.aktiv = False
        for i in range(0, len(room.spisok)):
            if room.spisok[i].name == 'Wall':
                room.spisok[i].up = False
                room.spisok[i].not_draw = False
                room.spisok[i].add(self.all)
            elif room.spisok[i].name_of_class == 'mob':
                room.spisok[i].sleep = False

    def stolknovenie(self, objekt1, igrok):
        self.print_to_file('stolknovenie')
        objekt1.health -= 3
        igrok.health -= objekt1.attack
        objekt1.hod_to_uron = objekt1.hod_to_uron_iznach
        objekt1.pomen_coor(objekt1.pred_coor_x, objekt1.pred_coor_y)

    def vost_hp_of_igrok(self, objekt1, zele):
        if objekt1.max_health > objekt1.health:
            objekt1.health += zele.kolvo_hp_of_regen
            zele.kill()

    def proverka_of_move(self, objekt, left=False,
                         right=False, up=False,
                         down=False):
        self.print_to_file('proverka_of_move')
        self.do_draw(self.moving_objekt)
        spisok_of_pereset = pygame.sprite.spritecollide(objekt,
                                                        self.all,
                                                        False)
        if objekt in self.moving_objekt and objekt.name_of_class != 'bullet':
            objekt.hod_to_uron -= 1
        st = 0
        for i in range(0, len(spisok_of_pereset)):
            if objekt.name == 'Room':
                if ((spisok_of_pereset[i].name == 'Room') and
                   (spisok_of_pereset[i] != objekt)):
                    objekt.pomen_coor(objekt.pred_coor_x, objekt.pred_coor_y)
                    return False
            elif ((objekt.name == 'bomba') and
                  (spisok_of_pereset[i].name == 'Wall_in_room')):
                return True
            elif ((objekt.name == 'bomba') and
                  ((spisok_of_pereset[i].name == 'igrok') or
                   (spisok_of_pereset[i].name_of_class == 'bullet'))):
                self.bomb_vzrav(objekt)
                return True
            elif ((objekt.name == 'zombi') and
                  (spisok_of_pereset[i].name == 'igrok') and
                  (objekt.hod_to_uron <= 0)):
                self.stolknovenie(objekt, spisok_of_pereset[i])
                self.proverka_of_live(self.igrok)
            elif ((objekt.name == 'zombi') and
                  (spisok_of_pereset[i].name_of_class == 'bullet')):
                objekt.get_damage(spisok_of_pereset[i].damage)
            elif ((objekt.name == 'igrok') and
                  (spisok_of_pereset[i].name == 'Room')):
                st += 1
                room = spisok_of_pereset[i]
            elif objekt.name == 'vzrav':
                if spisok_of_pereset[i].name_of_class == 'mob':
                    spisok_of_pereset[i].health -= objekt.attack
                    self.proverka_of_live(spisok_of_pereset[i])
            elif ((objekt.name == 'igrok') and
                  (spisok_of_pereset[i].name == 'zele_of_hp') and
                  (objekt.health > 0)):
                self.vost_hp_of_igrok(objekt, spisok_of_pereset[i])
            elif ((spisok_of_pereset[i].name != 'Room') and
                  (spisok_of_pereset[i].name != 'Window') and
                  (spisok_of_pereset[i].name != 'portal') and
                  (spisok_of_pereset[i].name != 'igrok') and
                  (spisok_of_pereset[i].name != 'zombi') and
                  (spisok_of_pereset[i].name != 'bomba') and
                  (spisok_of_pereset[i].name != 'vzrav') and
                  (spisok_of_pereset[i].name != 'zele_of_hp') and
                  (spisok_of_pereset[i].name_of_class != 'bullet')):
                objekt.pomen_coor(objekt.pred_coor_x, objekt.pred_coor_y)
                if objekt.name_of_class == 'bullet':
                    objekt.kill()
                return False
        if st == 1 and self.igrok.room != room and room.aktiv:
            self.smen_room_of_igrok(room)
        return True

    def random_shans_vupad_anywere(self, objekt):
        global shans_vupad_anywere_in_zombi, spisok_of_zele
        if objekt.name == 'zombi':
            for i in spisok_of_zele:
                a = shans_vupad_anywere_in_zombi[i]
                d = random.randint(1, 100)
                if a >= d:
                    if i == 'hp':
                        s = zele_of_hp(self.all, 20, 0, 0)
                        s.pomen_coor(objekt.virt_coor_x, objekt.virt_coor_y)
        elif objekt.name == 'bomba':
            for i in spisok_of_zele:
                a = shans_vupad_anywere_in_bomba[i]
                d = random.randint(1, 100)
                if a >= d:
                    if i == 'hp':
                        s = zele_of_hp(self.all, 20, 0, 0)
                        s.pomen_coor(objekt.virt_coor_x, objekt.virt_coor_y)

    def proverka_of_live(self, objekt):
        self.print_to_file('proverka_of_live')
        global spisok_of_mobs
        if objekt.health <= 0 and not objekt.killed and objekt.name != 'igrok':
            objekt.health -= 1000000000
            self.random_shans_vupad_anywere(objekt)
            objekt.kill()
            objekt.killed = True
            self.igrok.room.spisok.remove(objekt)
            x = list(filter(lambda a: a.name in spisok_of_mobs,
                            self.igrok.room.spisok))
            print(x)
            if len(x) == 0:
                for i in range(0, len(self.igrok.room.spisok)):
                    if ((self.igrok.room.spisok[i].name == 'Wall') and
                       (self.igrok.room.spisok[i].is_wall_on_prohod is True)):
                        self.igrok.room.spisok[i].kill()
        elif objekt.health <= 0 and objekt.name == 'igrok':
            GameOver()

    def proverka_of_animatia(self, ctet):
        if ctet == 3:
            self.ctet = 0
            for i in self.moving_objekt:
                if i.name_of_class != 'bullet':
                    i.pomen_izobraj(self.number_izobraj)
            self.number_izobraj += 1
            if self.number_izobraj == 5:
                self.number_izobraj = 0

    def draw_of_health(self):
        font = pygame.font.Font(None, 50)
        text = font.render(f"{self.igrok.health}/100", 1, (0, 0, 0))
        pygame.draw.rect(self.window.screen, (255, 0, 0), (0, 0, 200, 100))
        self.window.screen.blit(text, ((200 - text.get_width()) // 2,
                                (100 - text.get_height()) // 2))

    def hod_to_tochka_ignor_walls(self, x, y, objekt):
        x1, y1, = self.hod_objekt(objekt, x, y)
        objekt.pomen_coor(x1, y1)
        self.proverka_of_move(objekt)

    def bomb_vzrav(self, objekt):
        d = vzrav(self.all, objekt.virt_coor_x, objekt.virt_coor_y)
        d.add(self.moving_objekt)
        objekt.health = -10
        self.proverka_of_live(objekt)

    def hod_bomba(self, objekt):
        if objekt.hod_to_vzrav > 0:
            objekt.hod_to_vzrav -= 1
            if objekt.hod_in_one_napr == 0:
                objekt.hod_in_one_napr = objekt.hod_in_one_napr_iznach - 1
                d1 = random.randint(-60, 60)
                d2 = random.randint(-60, 60)
                objekt.coor_to_run_x = self.igrok.virt_coor_x + d1
                objekt.coor_to_run_y = self.igrok.virt_coor_y + d2
                self.hod_to_tochka_ignor_walls(objekt.coor_to_run_x,
                                               objekt.coor_to_run_y,
                                               objekt)
            else:
                if ((objekt.coor_to_run_x == objekt.virt_coor_x) and
                   (objekt.coor_to_run_y == objekt.virt_coor_y)):
                    objekt.hod_in_one_napr = 0
                    self.hod_bomba(objekt)
                else:
                    objekt.hod_in_one_napr -= 1
                    self.hod_to_tochka_ignor_walls(objekt.coor_to_run_x,
                                                   objekt.coor_to_run_y,
                                                   objekt)
        else:
            self.bomb_vzrav(objekt)

    def print_to_file(self, t):
        global logfile
        logfile.write(str(t))
        logfile.write('\n')

    def begin_game(self):
        self.print_to_file('begin_game')
        self.ctet = 0
        self.generate_level()
        self.do_draw(self.all)
        for i in self.all_room:
            self.generate_mobs(i)
            self.steret_nekot_prohod(i)
        clock = pygame.time.Clock()
        up, down, left, right = False, False, False, False
        fps = 25
        self.running = True
        while self.running:
            self.ctet += 1
            bullet_count = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.next_level()
                    if event.key == pygame.K_e:
                        self.kill_mobs()
                    if event.key == pygame.K_w:
                        up = True
                    if event.key == pygame.K_s:
                        down = True
                    if event.key == pygame.K_d:
                        right = True
                    if event.key == pygame.K_a:
                        left = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        up = False
                    elif event.key == pygame.K_s:
                        down = False
                    elif event.key == pygame.K_d:
                        right = False
                    elif event.key == pygame.K_a:
                        left = False
                elif ((event.type == pygame.MOUSEBUTTONDOWN) and
                      (bullet_count == 0)):
                    x, y = event.pos
                    eventpos = [x + self.window.virt_coor_x]
                    eventpos.append(y + self.window.virt_coor_y)
                    self.hit(eventpos)
                    bullet_count += 1
            self.proverka_of_animatia(self.ctet)
            x1 = self.igrok.virt_coor_x
            y1 = self.igrok.virt_coor_y
            if up and left:
                x1 = self.igrok.virt_coor_x - self.scorost // fps
                y1 = self.igrok.virt_coor_y - self.scorost // fps
            elif up and right:
                x1 = self.igrok.virt_coor_x + self.scorost // fps
                y1 = self.igrok.virt_coor_y - self.scorost // fps
            elif down and left:
                x1 = self.igrok.virt_coor_x - self.scorost // fps
                y1 = self.igrok.virt_coor_y + self.scorost // fps
            elif down and right:
                x1 = self.igrok.virt_coor_x + self.scorost // fps,
                y1 = self.igrok.virt_coor_y + self.scorost // fps
            elif up:
                x1 = self.igrok.virt_coor_x
                y1 = self.igrok.virt_coor_y - self.scorost // fps
            elif down:
                x1 = self.igrok.virt_coor_x
                y1 = self.igrok.virt_coor_y + self.scorost // fps
            elif right:
                x1 = self.igrok.virt_coor_x + self.scorost // fps
                y1 = self.igrok.virt_coor_y
            elif left:
                x1 = self.igrok.virt_coor_x - self.scorost // fps
                y1 = self.igrok.virt_coor_y
            self.igrok.pomen_coor(x1, y1)
            for i in self.moving_objekt:
                if i.name == 'igrok':
                    self.proverka_of_move(self.igrok, left, right, up, down)
                elif i.name == 'zombi' and not i.sleep:
                    self.hod_zombi(i)
                    self.proverka_of_live(i)
                elif i.name == 'bomba' and not i.sleep:
                    self.hod_bomba(i)
                    self.proverka_of_live(i)
                elif i.name == 'vzrav':
                    self.proverka_of_move(i, left, right, up, down)
            self.print_to_file(1)
            self.move_camera_to_igrok()
            self.do_draw(self.all)
            self.draw_of_health()
            clock.tick(fps)
            a = 0
            for i in self.all:
                if i.name == 'Room':
                    a += 1
                elif i.name_of_class == 'bullet':
                    self.proverka_of_move(i)
                    i.pred_coor_x = i.virt_coor_x
                    i.pred_coor_y = i.virt_coor_y
                    i.virt_coor_x += i.dx / fps
                    i.virt_coor_x = round(i.virt_coor_x)
                    i.virt_coor_y += i.dy / fps
                    i.virt_coor_y = round(i.virt_coor_y)
            self.print_to_file(a)
            pygame.display.flip()

    def hit(self, eventpos):
        bullet = Bullet(self.igrok.weapons[self.igrok.thistimeweapon],
                        self.igrok, eventpos)
        bullet.rect = bullet.image.get_rect()
        self.all.add(bullet)
        self.moving_objekt.add(bullet)


class Window(pygame.sprite.Sprite):
    def __init__(self, group, x, y, height, width, up=False):
        super().__init__(group)
        self.not_draw = up
        self.z = 1
        self.name = 'Window'
        self.image = pygame.image.load('t.jpg')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.virt_coor_x = x
        self.name_of_class = 'objekt'
        self.virt_coor_y = y
        self.generate_screen()

    def generate_screen(self):
        pygame.init()
        size = self.rect.width, self.rect.height
        self.screen = pygame.display.set_mode(size)
        self.screen.fill((0, 0, 0))


class Room(pygame.sprite.Sprite):
    def __init__(self, group, x, y, uroven, room_aktiv=False, up=False):
        super().__init__(group)
        self.z = 10
        self.not_draw = up
        self.kolvo_mob = 0
        a1 = 'фон'
        a2 = '.jpg'
        a = a1 + str(uroven[0]) + str(uroven[1]) + a2
        self.name = 'Room'
        self.aktiv = room_aktiv
        self.image = pygame.image.load(a)
        self.rect = self.image.get_rect()
        self.virt_coor_x = x
        self.virt_coor_y = y
        self.name_of_class = 'objekt'
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.spisok = []

    def pomen_coor(self, x, y):
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.virt_coor_x = x
        self.virt_coor_y = y


class Wall(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False, st=False):
        super().__init__(group)
        self.z = 20
        self.not_draw = up
        self.is_wall_on_prohod = st
        self.name_of_class = 'objekt'
        self.name = 'Wall'
        self.image = pygame.image.load('стена.jpg')
        self.rect = self.image.get_rect()
        self.virt_coor_x = x
        self.virt_coor_y = y


class Wall_in_room(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False, st=False):
        super().__init__(group)
        self.z = 20
        self.not_draw = up
        self.is_wall_on_prohod = st
        self.name_of_class = 'objekt'
        self.name = 'Wall_in_room'
        self.image = pygame.image.load('стена.jpg')
        self.rect = self.image.get_rect()
        self.virt_coor_x = x
        self.virt_coor_y = y


class Portal(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False):
        super().__init__(group)
        self.name = 'portal'
        self.z = 25
        self.not_draw = up
        self.name_of_class = 'objekt'
        self.image = pygame.image.load('портал.jpg')
        self.rect = self.image.get_rect()
        self.virt_coor_x = x
        self.virt_coor_y = y


class igrok(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False):
        super().__init__(group)
        self.z = 35
        self.name = 'igrok'
        self.health = 100
        self.a1 = 'игрок'
        self.a2 = '.jpg'
        self.d = '0'
        self.not_draw = up
        self.max_health = 100
        self.hod_to_uron = 10
        self.killed = False
        a = str(self.a1) + str(self.d) + str(self.a2)
        self.image = pygame.image.load(a)
        self.rect = self.image.get_rect()
        self.virt_coor_x = x
        self.name_of_class = 'mob'
        self.virt_coor_y = y
        self.room = None
        self.weapons = [Weapon(100, 400, 'f', '.png', 60)]
        self.thistimeweapon = 0

    def pomen_izobraj(self, d):
        self.d = d
        a = str(self.a1) + str(self.d) + str(self.a2)
        self.image = pygame.image.load(a)

    def pomen_coor(self, x, y):
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.virt_coor_x = x
        self.virt_coor_y = y

    def get_damage(self, count):
        self.health -= count

    def add_weapon(self, weapon):
        self.weapons.append(weapon)

    def next_weapon(self):
        if self.thistimeweapon is None and len(self.weapons) > 0:
            self.thistimeweapon = 0
        elif self.thistimeweapon is not None and len(self.weapons) > 0:
            self.thistimeweapon += 1
            self.thistimeweapon %= len(self.weapons)

    def previous_weapon(self):
        if self.thistimeweapon is None and len(self.weapons) > 0:
            self.thistimeweapon = len(self.weapons) - 1
        elif self.thistimeweapon is not None and len(self.weapons) > 0:
            self.thistimeweapon -= 1
            self.thistimeweapon %= len(self.weapons)


class zombi(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False):
        super().__init__(group)
        global hp_of_zombi, attack_of_zombi
        self.z = 29
        self.not_draw = up
        self.hod_to_uron = 4
        self.name = 'zombi'
        self.name_of_class = 'mob'
        self.speed = 15
        self.killed = False
        self.d = '0'
        self.a1 = 'zombi'
        self.a2 = '.jpg'
        self.image = pygame.image.load(self.a1 + str(self.d) + self.a2)
        self.rect = self.image.get_rect()
        self.health = hp_of_zombi
        self.attack = attack_of_zombi
        self.sleep = True
        self.is_wall_on_prohod = False
        self.hod_to_uron_iznach = 10
        self.virt_coor_x = x
        self.virt_coor_y = y

    def pomen_coor(self, x, y):
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.virt_coor_x = x
        self.virt_coor_y = y

    def get_damage(self, count):
        self.health -= count

    def pomen_izobraj(self, d):
        self.d = d
        a = str(self.a1) + str(self.d) + str(self.a2)
        self.image = pygame.image.load(a)


class bomba(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False):
        super().__init__(group)
        global hp_of_bomba, attack_of_bomba
        self.z = 30
        self.not_draw = up
        self.hod_to_uron = 0
        self.hod_to_uron_iznach = 0
        self.name = 'bomba'
        self.name_of_class = 'mob'
        self.speed = 25
        self.hod_to_vzrav = random.randint(100, 200)
        self.hod_in_one_napr_iznach = random.randint(9, 15)
        self.hod_in_one_napr = 0
        self.killed = False
        self.d = '0'
        self.a1 = 'bomba'
        self.a2 = '.jpg'
        self.coor_to_run_x = 0
        self.coor_to_run_y = 0
        self.image = pygame.image.load(self.a1 + str(self.d) + self.a2)
        self.rect = self.image.get_rect()
        self.health = hp_of_bomba
        self.attack = attack_of_bomba
        self.sleep = True
        self.is_wall_on_prohod = False
        self.virt_coor_x = x
        self.virt_coor_y = y

    def pomen_coor(self, x, y):
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.virt_coor_x = x
        self.virt_coor_y = y

    def get_damage(self, count):
        self.health -= count

    def pomen_izobraj(self, d):
        self.d = d
        a = str(self.a1) + str(self.d) + str(self.a2)
        self.image = pygame.image.load(a)


class zele_of_hp(pygame.sprite.Sprite):
    def __init__(self, group, kolvo_hp_of_regen, x, y, up=False):
        super().__init__(group)
        self.kolvo_hp_of_regen = kolvo_hp_of_regen
        self.image = pygame.image.load('зелье_здоровья.jpg')
        self.name = 'zele_of_hp'
        self.z = 10
        self.not_draw = up
        self.virt_coor_x = x
        self.virt_coor_y = y
        self.name_of_class = 'zele'
        self.rect = self.image.get_rect()

    def pomen_coor(self, x, y):
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.virt_coor_x = x
        self.virt_coor_y = y


class vzrav(pygame.sprite.Sprite):
    def __init__(self, group, x, y, up=False):
        super().__init__(group)
        global kolvo_uron_of_vzrav, kolvo_izobraj_of_vzrav
        self.attack = kolvo_uron_of_vzrav
        self.name_of_class = 'vzrav'
        self.a1 = 'взрыв'
        self.a2 = '.jpg'
        self.kolvo_izobraj = kolvo_izobraj_of_vzrav
        self.d = 0
        self.image = pygame.image.load(self.a1 + str(self.d) + self.a2)
        self.name = 'vzrav'
        self.z = 50
        self.not_draw = up
        self.hod_to_uron = 0
        self.hod_to_uron_iznach = 0
        self.virt_coor_x = x
        self.virt_coor_y = y
        self.rect = self.image.get_rect()

    def pomen_izobraj(self, k=0):
        self.d += 1
        if self.d < self.kolvo_izobraj:
            a = str(self.a1) + str(self.d) + str(self.a2)
            self.image = pygame.image.load(a)
        else:
            self.kill()


class Weapon(pygame.sprite.Sprite):
    def __init__(self, damage, v, name, ava, chance):
        super().__init__()
        self.damage = damage
        self.v = v
        self.name = name
        self.name_of_class = 'weapon'
        self.ava = ava
        self.chance = chance
        self.z = 100


class Bullet(pygame.sprite.Sprite):
    def __init__(self, weapon, igrok, mouse_pos):
        super().__init__()
        self.weapon = weapon
        self.v = self.weapon.v
        self.damage = self.weapon.damage
        self.igrok = igrok
        self.mouse_pos = mouse_pos
        self.name = f'bullet of {self.weapon.name}'
        self.name_of_class = 'bullet'
        self.pred_coor_x = igrok.virt_coor_x
        self.pred_coor_y = igrok.virt_coor_y
        self.virt_coor_x = igrok.virt_coor_x
        self.virt_coor_y = igrok.virt_coor_y
        self.to_coor_x = mouse_pos[0]
        self.to_coor_y = mouse_pos[1]
        self.z = 25
        self.not_draw = False
        dx = abs(self.virt_coor_x - self.to_coor_x)
        dy = abs(self.virt_coor_y - self.to_coor_y)
        if dx == 0:
            dx = 1
        if dy == 0:
            dy = 1
        tg = dy / dx
        y = math.atan(tg)
        py = math.sin(y) * self.v
        px = math.cos(y) * self.v
        if self.virt_coor_x >= self.to_coor_x:
            px = -px
        if self.virt_coor_y >= self.to_coor_y:
            py = -py
        self.dx, self.dy = px, py
        self.image = pygame.image.load('fireball.jfif')

    def pomen_coor(self, x, y):
        self.pred_coor_x = self.virt_coor_x
        self.pred_coor_y = self.virt_coor_y
        self.virt_coor_x = x
        self.virt_coor_y = y


class GameOver:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((600, 300))
        screen.fill((0, 0, 255))
        all_sprites = pygame.sprite.Group()
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load('gameover.png')
        sprite.rect = sprite.image.get_rect()
        all_sprites.add(sprite)
        clock = pygame.time.Clock()
        running = True
        sprite.rect.x = -600
        sprite.rect.y = 0
        fps = 50
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if sprite.rect.x < 0:
                sprite.rect.x += 200 // fps
            all_sprites.draw(screen)
            clock.tick(fps)
            pygame.display.flip()
        pygame.quit()


logfile = open('logfile.txt', 'w')
kolvo_izobraj_of_vzrav = 3
spisok_of_mobs = ['zombi', 'bomba']
spisok_of_zele = ['hp']
min_mobs = 5
max_mobs = 10
slovar_for_random = {}
shans_vupad_anywere_in_zombi = dict()
shans_vupad_anywere_in_zombi['hp'] = 50
shans_vupad_anywere_in_bomba = dict()
shans_vupad_anywere_in_bomba['hp'] = 60
hp_of_zombi = 25
kolvo_uron_of_vzrav = 20
attack_of_zombi = 10
hp_of_bomba, attack_of_bomba = 10, 20
skorost = 450
width, height = 1400, 800
begin_of_prohod = 2 / 5
end_of_prohod = 3 / 5
granitca1 = 2
granitca2 = 3
d = Supervisor(width, height, begin_of_prohod,
               end_of_prohod, granitca1, granitca2)
d.generate_osnov(min_mobs, max_mobs)
d.begin_game()
