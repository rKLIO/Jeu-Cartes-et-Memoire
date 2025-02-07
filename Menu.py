import kivy
import subprocess  # Importez le module subprocess
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.core.audio import SoundLoader

Config.set('graphics', 'width', '1500')
Config.set('graphics', 'height', '1000')

class RoundedPopup(Popup):
    pass

class MenuScreen(BoxLayout):
    def __init__(self):
        super(MenuScreen, self).__init__()
        self.orientation = "vertical"
        self.popup = None  # Initialiser self.popup à None dans le constructeur

        # Création des boutons
        jouer_button = Button(text="Jouer")
        niveaux_button = Button(text="Niveaux")
        quitter_button = Button(text="Quitter")

        # Définition des actions des boutons
        jouer_button.bind(on_press=self.jouer)
        niveaux_button.bind(on_press=self.choisir_niveau)
        quitter_button.bind(on_press=self.quitter)

    def jouer(self, instance):
        # Lancer le programme TestSystem.py
        subprocess.Popen(["python", "C:\\Users\\kenke\\Desktop\\BUT INFO\\Code BUT\\Mr.JEAN\\Dev App\\TestSystem.py"])
        App.get_running_app().stop()
    
    def choisir_niveau(self, instance):
        content = BoxLayout(orientation="vertical")
        facile_button = Button(text="Facile", background_color=(8/255, 84/255, 38/255, 1), on_press=self.jeu_facile, font_name="static/EBGaramond-Regular.ttf")
        moyen_button = Button(text="Moyen", background_color=(8/255, 84/255, 38/255, 1), on_press=self.jeu_moyen, font_name="static/EBGaramond-Regular.ttf")
        difficile_button = Button(text="Difficile", background_color=(8/255, 84/255, 38/255, 1), on_press=self.jeu_difficile, font_name="static/EBGaramond-Regular.ttf")
        
        content.add_widget(facile_button)
        content.add_widget(moyen_button)
        content.add_widget(difficile_button)
        
        self.popup = RoundedPopup(title="Choisir un niveau", content=content, size_hint=(None, None), size=(400, 300))
        self.popup.open()
    
    def jeu_facile(self, instance):
        self.write_level("facile")

    def jeu_moyen(self, instance):
        self.write_level("moyen")

    def jeu_difficile(self, instance):
        self.write_level("difficile")
        
    def write_level(self, level):
        with open('Niveaux.txt', 'w') as f:
            f.write(level)
            print(level)
        self.popup.dismiss()  # Ferme la fenêtre popup après avoir choisi un niveau
        
    def quitter(self, instance):
        # Fermer l'application
        with open('Niveaux.txt', 'w') as f:
            f.write("facile")
        App.get_running_app().stop()

    def write_style(self, style):
        with open('StyleCarte.txt', 'w') as f:
            f.write(style)
            print(style)
        self.popup.dismiss()

    def style(self, instance):
        content = BoxLayout(orientation="horizontal")
        style1_button = Button(background_normal="DosCarte.png", color= (1, 1, 1, 0) )
        style2_button = Button(background_normal="DosCarte1.png", color= (1, 1, 1, 0))
        style3_button = Button(background_normal="DosCarte2.png", color= (1, 1, 1, 0))
        
        # Utilisez des fonctions lambda pour retarder l'appel à write_style
        style1_button.bind(on_press=lambda instance: self.write_style("DosCarte.png"))
        style2_button.bind(on_press=lambda instance: self.write_style("DosCarte1.png"))
        style3_button.bind(on_press=lambda instance: self.write_style("DosCarte2.png"))
        
        content.add_widget(style1_button)
        content.add_widget(style2_button)
        content.add_widget(style3_button)
        
        self.popup = RoundedPopup(title="Choisir un style", content=content, size_hint=(None, None), size=(800, 500), background_color=(0/255, 0/255, 0/255, 1))
        self.popup.open()

class MenuJeuCartes(App):
    def build(self):
        music = SoundLoader.load('Waiting Room - Jazz Songs.mp3')
        if music:
            # Jouer la musique en boucle
            music.loop = True
            music.play()
        return MenuScreen()

MenuJeuCartes().run()