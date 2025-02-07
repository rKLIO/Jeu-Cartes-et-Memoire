from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.uix.relativelayout import RelativeLayout
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
import subprocess
import random

Config.set('graphics', 'width', '1500')
Config.set('graphics', 'height', '1000')
Config.set('graphics', 'resizable', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class Cartesdejeu:
    def __init__(self, nom):
        self.nom = nom
        
    def __str__(self):
        return f'({self.nom})'

    def __repr__(self):
        return f'({self.nom})'

class RoundedPopup(Popup):
    pass

class Fenetre(BoxLayout):
    cliked1 = None
    cliked2 = None
    grille_cartes = None
    score = 0
    carte_valide = []
    score_label = None
    moyen = False
    difficile = False
    temps = 0
    temps_label = None
    with open('StyleCarte.txt', 'r') as f:
        val_doscarte = f.read()
    carte_verif = []
    click_locked = False  # Verrou pour gérer les clics multiples
    son = True

    def Generation(self):
        with open('Niveaux.txt', 'r') as f:
            self.valniv = f.read()
        print(f"Niveau lu : {self.valniv}")
        
        if self.valniv == 'moyen':
            self.moyen = True
        elif self.valniv == 'difficile':
            self.difficile = True
        elif self.valniv == 'facile':
            self.moyen = False
            self.difficile = False

        liste_symbole = ["carreau", "trefle", "coeur", "pic"]
        liste_types = ["roi", "dame"]
        if self.moyen == True:
            liste_types.append('valet')
        elif self.difficile == True:
            liste_types.append('valet')
            liste_types.append('as')
        deck_carte = []

        combinaisons = [(symbole, type_carte) for symbole in liste_symbole for type_carte in liste_types]
        combinaisons_doublees = combinaisons * 2
        random.shuffle(combinaisons_doublees)
        print(f"Combinaisons doublées et mélangées : {combinaisons_doublees}")

        for nom_carte in combinaisons_doublees:
            carte = Cartesdejeu(" ".join(nom_carte)) 
            deck_carte.append(carte)

        if self.moyen == False and self.difficile == False:
            layout_grid = GridLayout(cols=4, spacing=10, padding=[-270, -325], size_hint=(None, None), size=(800, 600))
        elif self.moyen == True:
            layout_grid = GridLayout(cols=6, spacing=10, padding=[-450, -315], size_hint=(None, None), size=(800, 600))
        elif self.difficile == True:
            layout_grid = GridLayout(cols=8, spacing=10, padding=[-620, -315], size_hint=(None, None), size=(800, 600))

        for carte in deck_carte:
            button = Button(background_normal=self.val_doscarte, text=str(carte), on_press=self.on_button_click,
                            color=(0, 0, 0, 0),
                            size=(160, 210), size_hint=(None, None))
            layout_grid.add_widget(button)

        self.grille_cartes = layout_grid
        return layout_grid

    def animate_button(self, button):
        button.opacity = 0
        animation = Animation(opacity=1, duration=1)
        animation.start(button)

    def on_button_click(self, instance):
        print(f"Button clicked: {instance.text}")
        print(f"Click locked: {self.click_locked}")
        
        if self.click_locked:
            print("Clicks are locked. Ignoring click.")
            return
        
        if self.son:
            sound = SoundLoader.load("flipcard-91468.mp3")
            if sound:
                sound.play()
                
        instance.background_normal = instance.text + ".png"
        self.verification(instance)
        self.update_score_label()
        self.check_victoire_condition()

    def verification(self, instance):
        print(f"Verification called with instance: {instance.text}")
        
        if self.click_locked:
            print("Clicks are locked. Ignoring verification.")
            return
        
        if self.cliked1 is None:
            self.cliked1 = instance
            print(f"First card clicked: {self.cliked1.text}")
        else:
            self.cliked2 = instance
            print(f"Second card clicked: {self.cliked2.text}")

        if self.cliked1 is not None and self.cliked2 is not None:
            index1 = self.grille_cartes.children.index(self.cliked1)
            index2 = self.grille_cartes.children.index(self.cliked2)
            print(f"Indices des cartes cliquées : {index1}, {index2}")

            if index1 == index2:
                print("Same card clicked twice. Hiding card.")
                self.hide_cards()
                self.cliked1 = None
                self.cliked2 = None
                return
            
            if index1 in self.carte_valide or index2 in self.carte_valide:
                print("One of the clicked cards is already validated.")
                if index1 not in self.carte_valide:
                    self.cliked1.background_normal = self.val_doscarte
                    self.cliked2 = None
                if index2 not in self.carte_valide:
                    self.cliked2.background_normal = self.val_doscarte
                    self.cliked1 = None
                return
            
            else:
                if self.cliked1.text == self.cliked2.text:
                    print(f"Cards match: {self.cliked1.text} == {self.cliked2.text}")
                    self.carte_valide.append(index1)
                    self.carte_valide.append(index2)
                    self.score += 100
                    self.check_victoire_condition()
                    self.cliked1 = None
                    self.cliked2 = None
                else:
                    print(f"Cards do not match: {self.cliked1.text} != {self.cliked2.text}")
                    if self.score > 0:
                        self.score -= 20
                    if self.valniv == 'moyen':
                        self.disable_clicks_temporarily(.4)
                        Clock.schedule_once(lambda dt: self.hide_cards(), .4)
                    elif self.valniv == 'difficile':
                        self.disable_clicks_temporarily(.3)
                        Clock.schedule_once(lambda dt: self.hide_cards(), .3)
                    elif self.valniv == 'facile':
                        self.disable_clicks_temporarily(.5)
                        Clock.schedule_once(lambda dt: self.hide_cards(), .5)

    def hide_cards(self):
        print("Hiding cards")
        if self.cliked1:
            self.cliked1.background_normal = self.val_doscarte
        if self.cliked2:
            self.cliked2.background_normal = self.val_doscarte
        self.cliked1 = None
        self.cliked2 = None
        self.update_score_label()

    def update_score_label(self):
        if self.score_label:
            self.score_label.text = f"Score: {self.score}"
        print(f"Score updated: {self.score}")

    def check_victoire_condition(self):
        if len(self.carte_valide) == len(self.grille_cartes.children):
            print("Victory condition met")
            content = RelativeLayout()
            image = AsyncImage(source="C:/Users/kenke/Desktop/BUT INFO/Code BUT/Mr.JEAN/Dev App/Yes_check.png")
            content.add_widget(image)
            self.popup = RoundedPopup(title="Félicitations !!! Vous avez gagné ", content=content, size_hint=(None, None), size=(800, 600), background_color=(0/255, 0/255, 0/255, 1))
            self.popup.open()
            if self.son:
                music = SoundLoader.load('Small Group Clapping - Sound Effect.mp3')
                if music:
                    music.play()
            Clock.schedule_once(lambda dt: self.add_buttons_to_popup(self.popup), 1.5)

    def add_buttons_to_popup(self, popup):
        bouton1 = Button(text="Recommencer", size_hint=(None, None), size=(750, 90), pos_hint={'x': 0.015, 'y': 0.5}, on_press=self.popup_recommencer, font_name="static/EBGaramond-Regular.ttf", background_color=(8/255, 84/255, 38/255, 1))
        bouton2 = Button(text="Menu Principal", size_hint=(None, None), size=(750, 90), pos_hint={'x': 0.015, 'y': 0.3}, on_press=self.bouton_quitter, font_name="static/EBGaramond-Regular.ttf", background_color=(8/255, 84/255, 38/255, 1))
        popup.content.add_widget(bouton1)
        popup.content.add_widget(bouton2)
        self.animate_button(bouton1)
        self.animate_button(bouton2)

    def popup_recommencer(self, instance):
        print("Restart button clicked")
        self.bouton_recommencer(instance)
        self.popup.dismiss()
    
    def bouton_quitter(self, instance):
        print("Quit button clicked")
        subprocess.Popen(["python", "C:\\Users\\kenke\\Desktop\\BUT INFO\\Code BUT\\Mr.JEAN\\Dev App\\Menu.py"])
        App.get_running_app().stop()

    def bouton_recommencer(self, instance):
        print("Recommencer function called")
        if self.cliked1 is not None:
            self.cliked1.background_normal = self.val_doscarte
        self.cliked1 = None
        self.cliked2 = None
        self.score = 0

        for index in self.carte_valide:
            button = self.grille_cartes.children[index]
            button.background_normal = self.val_doscarte

        self.carte_valide = []
        random.shuffle(self.grille_cartes.children)
        
        self.update_score_label()

    def disable_clicks_temporarily(self, duration):
        print(f"Disabling clicks for {duration} seconds")
        self.click_locked = True
        Clock.schedule_once(lambda dt: self.enable_clicks(), duration)

    def enable_clicks(self):
        print("Enabling clicks")
        self.click_locked = False

    if son:
        music = SoundLoader.load('Pasadas las 12.mp3')
        if music:
            music.volume = .3
            music.loop = True
            music.play()
        music2 = SoundLoader.load('crowd_talking-6762.mp3')
        if music2:
            music2.loop = True
            music2.play()

class CartesApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        fenetre = Fenetre()
        grille_cartes = fenetre.Generation()
        fenetre.add_widget(grille_cartes)
        fenetre.score_label = Label(text=f"Score: {fenetre.score}", font_size=30, size_hint_y=None, height=50, font_name="static\EBGaramond-Regular.ttf")
        layout.add_widget(fenetre.score_label)
        layout.add_widget(fenetre)
        return layout

CartesApp().run()