# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:56:10 2024
App para facitar o controle de projetos sociais quanto a
alunos/pessoas atendidas e aulas/eventos realizados
@author: Luis Guimaraes
"""

# principais
from kivymd.app import MDApp
from kivy.lang import Builder

# containers
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen

# elementos
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.card import MDCard

# helpers
from kivy.metrics import dp


# KV file string for defining screens
KV = '''
ScreenManager:
    MainScreen:
    ProjectScreen:
    SubjectScreen:
    EventScreen:

<MainScreen>:
    name: 'mainscreen'

<ProjectScreen>:
    name: 'projectscreen'

<SubjectScreen>:
    name: 'subjectscreen'

<EventScreen>:
    name: 'eventscreen'
'''

#%% tela principal

# Main Screen Class
class MainScreen(Screen):
    initialized = False

    def on_enter(self, *args):
        if self.initialized:
            pass
        
        #constroi a tela
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)
        
        #card
        
        
        #titulo
        label = MDLabel(text="Main Screen", halign="center")
        layout.add_widget(label)
        
        #tabela de projetos
        
        
        #barra inferior
        
        
        #para nao adicionar de novo
        self.initialized = True

#%% tela do projeto

# Project Screen Class
class ProjectScreen(Screen):
    initialized = False
    
    def on_enter(self, *args):
        if self.initialized:
            pass
        
        #controi a tela
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)
        
        #titulo
        label = MDLabel(text="Project Screen", halign="center")
        layout.add_widget(label)

        #tabela
        data_table = MDDataTable(
            size_hint=(0.9, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            use_pagination=True,
            column_data=[
                ("No.", dp(30)),
                ("Name", dp(30)),
                ("Age", dp(30)),
            ],
            row_data=[
                ("1", "John Doe", "29"),
                ("2", "Jane Doe", "32"),
                ("3", "Sam Smith", "45"),
            ],
        )
        layout.add_widget(data_table)
        
        #barra inferior
        
        #para nao adicionar de novo
        self.initialized = True

#%% tela de alunos/pessoas

# Subject Screen Class
class SubjectScreen(Screen):
    initialized = False
    
    def on_enter(self, *args):
        if self.initialized:
            pass
        
        self.clear_widgets()
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)

        label = MDLabel(text="Subject Screen", halign="center")
        layout.add_widget(label)
        
        #para nao adicionar de novo
        self.initialized = True

#%% tela de aulas/eventos

# Event Screen Class
class EventScreen(Screen):
    initialized = False
    
    def on_enter(self, *args):
        if self.initialized:
            pass
        
        self.clear_widgets()
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)

        label = MDLabel(text="Event Screen", halign="center")
        layout.add_widget(label)
        
        #para nao adicionar de novo
        self.initialized = True

#%% app

# Main App Class
class ProjetoSocial(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Config
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        
    def build(self):
        # Load the main KV layout string and return it
        return Builder.load_string(KV)


# Run the app
if __name__ == '__main__':
    app = ProjetoSocial()
    app.run()