# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:56:10 2024
app para facilitar o trabalho de acompanhar alunos e eventos em
projetos sociais voltados a arte ou esportes
@author: Luis
"""

#outros
import ctypes
import pandas as pd
from datetime import datetime, time

#principais
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window

#containers
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog

#elementos
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.datatables.datatables import CellRow
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.textfield import MDTextField
from kivymd.uix.pickers import MDDatePicker, MDTimePicker

#helpers
from kivy.metrics import dp, mm, Metrics
from kivy.properties import OptionProperty

#%%configs

CANCEL_BUTTON_COLOR = (1,.25,.2,1)

#%% telas

#define as telas pela kvlang #TODO: arrumar a ordem quando a navegação estiver pronta
KV = '''
MDScreenManager:
    MainScreen:
    ProjectAlunosScreen:
    ProjectEventosScreen:
    SubjectScreen:
    EventScreen: 
    PresenceScreen:

<MainScreen>:
    name: 'MainScreen'

<ProjectAlunosScreen>:
    name: 'ProjectAlunosScreen'

<ProjectEventosScreen>:
    name: 'ProjectEventosScreen'

<SubjectScreen>:
    name: 'SubjectScreen'

<EventScreen>:
    name: 'EventScreen'

<PresenceScreen>:
    name: 'PresenceScreen'
'''

from kivymd.uix.pickers.timepicker.timepicker import TimeInput

#%% helpers

'''
estrutura da tabela:
--------------------    
kivymd.uix.datatables.datatables.MDDataTable
    0: kivy.factory.TableContainer
        0: kivymd.uix.datatables.datatables.TableData
            0: kivymd.uix.datatables.datatables.TableRecycleGridLayout
                [i: kivymd.uix.datatables.datatables.CellRow]
                    0: kivymd.uix.card.card.MDSeparator
                    1: kivymd.uix.boxlayout.MDBoxLayout
                        0: kivymd.uix.boxlayout.MDBoxLayout
                            0: kivymd.uix.label.label.MDLabel
                            0: kivymd.uix.label.label.MDIcon
                                0: kivymd.uix.label.label.MDLabel
                        1: kivymd.uix.selectioncontrol.selectioncontrol.MDCheckbox
                            0: kivymd.uix.label.label.MDLabel

estrutura do timepicker:
------------------------
kivymd.uix.pickers.timepicker.timepicker.MDTimePicker
    0: kivymd.uix.relativelayout.MDRelativeLayout
        0: kivymd.uix.button.button.MDFlatButton ('OK')
        1: kivymd.uix.button.button.MDFlatButton ('CANCEL')
        2: kivymd.uix.button.button.MDIconButton (keyboard icon)
        3: kivymd.uix.pickers.timepicker.timepicker.CircularSelector
        4: kivymd.uix.pickers.timepicker.timepicker.AmPmSelector
        5: kivy.factory.TimeInputLabel ('Minute')
        6: kivy.factory.TimeInputLabel ('Hour')
        7: kivymd.uix.pickers.timepicker.timepicker.TimeInput ('HH:mm')
            0: kivymd.uix.pickers.timepicker.timepicker.TimeInputTextField (HH)
            1: kivymd.uix.label.label.MDLabel (':')
            2: kivymd.uix.pickers.timepicker.timepicker.TimeInputTextField (mm)
        8: kivymd.uix.label.label.MDLabel ('Escolha a Hora')
'''

#TODO: fazer isso funcionar
def adjust_row_heights(data_table, *args):
    #aparentemente, só as rows na tela e proximas da tale 'existem'
    print(len(data_table.children[0].children[0].children[0].children), ' rows')
    
    for row in data_table.children[0].children[0].children[0].children:
        print(type(row))
        row.adaptive_height = False
        row.minimum_height = mm(10)
        row.size_hint_y = None
        row.height = mm(10)
        row.padding = (0, 0)
        
        label = row.children[1].children[0]
        print(type(label))
        label.adaptive_height = False
        label.size_hint_y = None
        label.minimum_height = mm(10)
        label.height = mm(10)
        label.padding = (0, 0)

#%% tela principal

class MainScreen(Screen):
    data_table = None
    
    def on_pre_enter(self, *args):
        self.clear_widgets()
        
        #recipiente principal com cor de fundo
        layout = MDBoxLayout(orientation='vertical', md_bg_color='teal')
        self.add_widget(layout)
        
        #----------------------------------------------------------------------
        #cabeçalho
        header_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height = dp(50), minimum_height=0)
        layout.add_widget(header_line)
        
        #titulo
        label = MDLabel(text='Projetos', theme_text_color='Custom', font_style='H6', text_color='white', halign='center', valign='top', size_hint=(1, None) )
        label.bind(texture_size=lambda instance, value: instance.setter('height')(instance, instance.texture_size[1] + 30))
        header_line.add_widget(label)
        
        #----------------------------------------------------------------------
        #tabela #TODO: carregar se ja existir, ou criar se nao existir
        data_table = MDDataTable(size_hint=(1, dp(app.wsize[0])), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                                 use_pagination=False, rows_num=9999, background_color_cell="white", background_color_selected_cell="white",
                                 column_data=[('nome', dp(app.wsize[0])),(f'', 1)], #a segunda coluna vazia evita um bug
                                 row_data=[(app.projetos[x]['nome'], f'') for x in range(len(app.projetos))] )
        data_table.ids.container.remove_widget(data_table.header)
        data_table.sorted_on = "ID"
        data_table.sorted_order = "ASC" #"DSC"
        data_table.bind(on_row_press=self.on_row_press)
        self.data_table = data_table
        layout.add_widget(data_table)
        
        #----------------------------------------------------------------------
        #barra inferior #TODO: add filtros e busca
        
        bottom_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(bottom_line)
                
        #spacer 
        spacer = Widget(size_hint_x=1)
        bottom_line.add_widget(spacer)
        
        #botao para adicionar um novo projeto
        event_button = MDIconButton(icon='archive-plus', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        event_button.bind(on_release=self.on_add_row)
        bottom_line.add_widget(event_button)
    
    #--------------------------------------------------------------------------
    #quando o usuário toca numa celula da tabela
    def on_row_press(self, instance_table, instance_row):
        print(f'tela de projetos -> on_row_press: {instance_row.text}')
        
        #TODO: isso sao variaveis para debuggar, pode apagar depois
        global itable, irow 
        itable, irow = instance_table, instance_row
        
        #indentify which project the row belongs to #can't use the parent.children index because it loads and unloads rows dynamically
        for i in range(len(app.projetos)):
            if app.projetos[i]['nome']==irow.text:
                #set it as the current project and switch to the project screen
                app.curproject = app.projetos[i]
                if type(app.root.transition) != FadeTransition:
                    app.root.transition = FadeTransition()
                # self.clear_widgets() #limpa antes de sair para nao aparecer o antigo quando voltar pra essa tela
                app.root.current = 'ProjectAlunosScreen'
    
    #--------------------------------------------------------------------------
    #popup do botao de adicionar projeto
    def on_add_row(self, button):
        #campo de texto para o nome
        self.new_row_name_field = MDTextField(hint_text="Digite um nome para o projeto", required=True)
        
        #função para verificar se há texto no campo, para habilitar e desabilitar o botao confirmar
        self.new_row_name_field.bind(text=self.on_new_name_text_changed)
        
        #botão confirmar (inicialmente desabilitado
        self.new_row_confirm_button = MDFillRoundFlatButton(
            text="Confirmar", on_release=self.confirm_row_creation, disabled=True)
        
        #botao cancelar
        self.new_row_cancel_button = MDFillRoundFlatButton(
            text="Cancelar", on_release=self.cancel_row_creation, md_bg_color=CANCEL_BUTTON_COLOR)
        
        #monta e abre a caixa de dialogo
        self.new_row_dialog = MDDialog(
            title="Criar novo projeto",
            type="custom", elevation=1,
            content_cls=self.new_row_name_field,
            buttons=[self.new_row_cancel_button,
                     self.new_row_confirm_button],
            )
        self.new_row_dialog.open()
        
    def on_new_name_text_changed(self, instance, value):
        self.new_row_confirm_button.disabled = not value.strip()
    
    def cancel_row_creation(self, button):
        self.new_row_dialog.dismiss()
    
    def confirm_row_creation(self, button):
        print('criando novo projeto!')
        name_input = self.new_row_name_field.text
        
        #TODO: cria a row na tabela do kivymd
        
        #TODO: cria a row no dataframe
        
        
        #fecha a caixa
        self.new_row_dialog.dismiss()
   

#%% tela do projeto: alunos

class ProjectAlunosScreen(Screen):
    data_table = None
    
    def on_pre_enter(self, *args):
        self.clear_widgets()
        
        #recipiente principal com cor de fundo
        layout = MDBoxLayout(orientation='vertical', md_bg_color='teal')
        self.add_widget(layout)
        
        #----------------------------------------------------------------------
        #cabeçalho
        header_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(header_line)
        
        #botao para voltar pra tela principal
        home_button = MDIconButton(icon='home', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='left', valign='center', icon_size='32sp')
        home_button.bind(on_release=lambda x: setattr(app.root, 'current', 'MainScreen'))
        header_line.add_widget(home_button)
        
        #titulo
        label = MDLabel(text=f' \n{app.curproject["nome"]}',
                        theme_text_color='Custom', text_color='white', font_style='H6', halign='center', valign='center', size_hint=(1, None))
        label.bind(texture_size=lambda instance, value: instance.setter('height')(instance, instance.texture_size[1] + 30))
        header_line.add_widget(label)
        
        #botao para ir para a tela de eventos
        event_button = MDIconButton(icon='clipboard-clock', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='left', valign='center', icon_size='32sp')
        event_button.bind(on_release=lambda x: setattr(app.root, 'current', 'ProjectEventosScreen'))
        header_line.add_widget(event_button)
        
        #----------------------------------------------------------------------
        #tabela
        
        #dataframe dos alunos
        freq_cols = [col for col in app.curproject['alunos'].columns if '__freq__' in col]
        alunos_df = app.curproject['alunos'].drop(columns=freq_cols)
        
        #kivymd data table
        data_table = MDDataTable(size_hint=(1, dp(app.wsize[0])), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                                 use_pagination=False, rows_num=9999, background_color_cell="white", background_color_selected_cell="white",
                                 column_data=[('id', dp(app.wsize[0]//5+1)), ('nome', dp(app.wsize[0]*4//5+1))],
                                 row_data=[(x,y) for x,y in zip(alunos_df['id'].values, alunos_df['nome'].values)] )
        data_table.sorted_on = "ID"
        data_table.sorted_order = "ASC" #"DSC"
        data_table.bind(on_row_press=self.on_row_press)
        self.data_table = data_table
        layout.add_widget(data_table)
        
        #----------------------------------------------------------------------
        #barra inferior
        
        bottom_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(bottom_line)
        
        #spacer 
        spacer = Widget(size_hint_x=1)
        bottom_line.add_widget(spacer)
        
        #botao para adicionar um novo aluno
        event_button = MDIconButton(icon='account-plus', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        event_button.bind(on_release=self.on_add_row)
        bottom_line.add_widget(event_button)
    
    #--------------------------------------------------------------------------
    #quando o usuário toca numa celula da tabela
    def on_row_press(self, instance_table, instance_row):
        print(f'tela de projeto:pessoas -> on_row_press: {instance_row.text}')
        
        #TODO: isso sao variaveis para debuggar, pode apagar depois
        global itable, irow
        itable, irow = instance_table, instance_row
        
        #get the id of the row
        if (instance_row.index % 2) == 0:
            row_id = irow.parent.children[-irow.index-1].text
        else:
            row_id = irow.parent.children[-irow.index].text
        print('row_id:', row_id)
        
        #identify which person the row belongs to
        #por enquanto só para 2 colunas, com a primeira especificamente sendo 'id'
        idvalues = app.curproject['alunos']['id'].values
        for i in range(len(idvalues)):
            if f"{idvalues[i]}"==f'{row_id}':
                #set it as the current person and go to the screen
                app.curpersonid = i
                app.curpersonindex = app.curproject['alunos']['id'].values[i]
                if type(app.root.transition) != FadeTransition:
                    app.root.transition = FadeTransition()
                # self.clear_widgets() #limpa antes de sair para nao aparecer o antigo quando voltar pra essa tela
                app.root.current = 'SubjectScreen'
    
    #--------------------------------------------------------------------------
    #popup do botao de adicionar pessoa
    def on_add_row(self, button):
        #campo de texto para o nome
        self.new_row_name_field = MDTextField(hint_text="Digite um nome para a pessoa", required=True)
        
        #função para verificar se há texto no campo, para habilitar e desabilitar o botao confirmar
        self.new_row_name_field.bind(text=self.on_new_name_text_changed)
        
        #botão confirmar (inicialmente desabilitado
        self.new_row_confirm_button = MDFillRoundFlatButton(
            text="Confirmar", on_release=self.confirm_row_creation, disabled=True)
        
        #botao cancelar
        self.new_row_cancel_button = MDFillRoundFlatButton(
            text="Cancelar", on_release=self.cancel_row_creation, md_bg_color=CANCEL_BUTTON_COLOR)
        
        #monta e abre a caixa de dialogo
        self.new_row_dialog = MDDialog(
            title="Registrar nova pessoa",
            type="custom", elevation=1,
            content_cls=self.new_row_name_field,
            buttons=[self.new_row_cancel_button,
                     self.new_row_confirm_button],
            )
        self.new_row_dialog.open()
        
    def on_new_name_text_changed(self, instance, value):
        self.new_row_confirm_button.disabled = not value.strip()
    
    def cancel_row_creation(self, button):
        self.new_row_dialog.dismiss()
    
    def confirm_row_creation(self, button):
        print('criando novo aluno!')
        name_input = self.new_row_name_field.text
        
        #TODO: cria a row na tabela do kivymd
        
        #TODO: cria a row no dataframe
        
        
        #fecha a caixa
        self.new_row_dialog.dismiss()

#%% tela do projeto: eventos

class ProjectEventosScreen(Screen):
    data_table = None
    picked_date = None
    picked_time = None
    
    def on_pre_enter(self, *args):
        self.clear_widgets()
        
        #recipiente principal com cor de fundo
        layout = MDBoxLayout(orientation='vertical', md_bg_color='teal')
        self.add_widget(layout)
        
        #----------------------------------------------------------------------
        #cabeçalho
        header_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(header_line)
        
        #botao para voltar pra tela principal
        home_button = MDIconButton(icon='home', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='left', valign='center', icon_size='32sp')
        home_button.bind(on_release=lambda x: setattr(app.root, 'current', 'MainScreen'))
        header_line.add_widget(home_button)
        
        #titulo
        label = MDLabel(text=f'{app.curproject["nome"]}',
                        theme_text_color='Custom', text_color='white', font_style='H6', halign='center', valign='center', size_hint=(1, None))
        label.bind(texture_size=lambda instance, value: instance.setter('height')(instance, instance.texture_size[1] + 30))
        header_line.add_widget(label)
        
        #botao para ir para a tela de eventos
        btn0 = MDIconButton(icon='account-group', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        btn0.bind(on_release=lambda x: setattr(app.root, 'current', 'ProjectAlunosScreen'))
        header_line.add_widget(btn0)
        
        #----------------------------------------------------------------------
        #tabela #TODO: carregar se ja existir, ou criar se nao existir
        eventos_df = app.curproject['eventos']
        data_table = MDDataTable(size_hint=(1, .9), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                                 use_pagination=False, rows_num=9999, background_color_cell="white", background_color_selected_cell="white",
                                 column_data=[('id', dp(app.wsize[0]//5+1)), ('ano', dp(app.wsize[0]*4//5+1))],
                                 row_data=[(x,y) for x,y in zip(eventos_df['id'].values, eventos_df['ano'].values)] )
        # data_table.ids.container.remove_widget(data_table.header)
        data_table.sorted_on = "ID"
        data_table.sorted_order = "ASC" #"DSC"
        data_table.bind(on_row_press=self.on_row_press)
        self.data_table = data_table
        layout.add_widget(data_table)
        
        #----------------------------------------------------------------------
        #barra inferior
        bottom_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(bottom_line)
        
        #spacer 
        spacer = Widget(size_hint_x=1)
        bottom_line.add_widget(spacer)
        
        #botao para adicionar um novo evento(clock-plus, calendar-plus)
        event_button = MDIconButton(icon='calendar-plus', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        event_button.bind(on_release=self.on_add_row)
        bottom_line.add_widget(event_button)
    
    #--------------------------------------------------------------------------
    def on_row_press(self, instance_table, instance_row):
        print(f'tela de projeto:eventos -> on_row_press: {instance_row.text}')
        
        #TODO: isso sao variaveis para debuggar, pode apagar depois
        global itable, irow
        itable, irow = instance_table, instance_row
        
        #get the id of the row
        if (instance_row.index % 2) == 0:
            row_id = irow.parent.children[-irow.index-1].text
        else:
            row_id = irow.parent.children[-irow.index].text
        print('row_id:', row_id)
        
        #indentify which person the row belongs to
        #por enquanto só para 2 colunas, com a primeira especificamente sendo 'id'
        idvalues = app.curproject['eventos']['id'].values
        for i in range(len(idvalues)):
            #find the person
            if f"{idvalues[i]}"==f'{row_id}':
                print(idvalues[i], '==', row_id)
                # set it as the current person
                app.cureventid = i
                #config the transition if not already configured
                if type(app.root.transition) != FadeTransition:
                    app.root.transition = FadeTransition()
                #go to the person screen
                # self.clear_widgets() #limpa antes de sair para nao aparecer o antigo quando voltar pra essa tela
                app.root.current = 'EventScreen'
    
    #--------------------------------------------------------------------------
    #popups do botao de adicionar evento
    def on_add_row(self, button):
        self.show_date_picker()
        # self.show_time_picker() #TODO: TEMP enquanto debuga o time picker

    def show_date_picker(self):
        date_dialog = MDDatePicker(elevation=1)
        date_dialog.bind(on_save=self.on_confirm_date)
        date_dialog.open()
    
    def on_confirm_date(self, instance, value, date_range):
        '''
        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        '''
        self.show_time_picker()

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_change_time, on_save=self.on_confirm_time)
        
        #TODO: debug
        global timepicker
        timepicker = time_dialog
        
        #titulo
        time_dialog.title = 'ESCOLHA A HORA'
        
        #botoes OK e CANCEL #TODO: deixar todos no mesmo padrão
        ok_button = time_dialog.children[0].children[0]
        ok_button.text = 'OK'
        cancel_button = time_dialog.children[0].children[1]
        cancel_button.text = 'CANCELA'
        
        #label HORA e MINUTO
        time_dialog.children[0].children[5].text = 'Minuto'
        time_dialog.children[0].children[6].text = 'Hora'
        
        #TODO: modo 24 horas, precisa extender a classe
        
        #done
        time_dialog.open()
    
    def on_change_time(self, instance, time_obj):
        '''
        The method returns the set time.
        :type instance: <kivymd.uix.picker.MDTimePicker object>
        :type time: <class 'datetime.time'>
        '''
        return time_obj
    
    def on_confirm_time(self, instance, time_obj):
        print('criando novo evento!')
        print('on_confirm_time:')
        print('instance', type(instance), instance)
        print('time_obj', type(time_obj), time_obj)
        
        #TODO: cria a row na tabela
        
        #TODO: cria a row no dataframe
        
        

#%% tela de alunos/pessoas

class SubjectScreen(Screen):
    
    def on_pre_enter(self, *args):
        self.clear_widgets()
        
        #informacoes do aluno (o id e a frequencia são ignorados na tabela)
        aluno_df = pd.DataFrame()
        aluno_row =  [*app.curproject['alunos'].iloc(0)[app.curpersonid].values]
        aluno_id = aluno_row[0]
        aluno_name = aluno_row[1]
        freq_cols = [col for col in app.curproject['alunos'].columns if '__freq__' in col]
        aluno_df['column'] = [*app.curproject['alunos'].drop(columns=['id',*freq_cols]).columns]
        aluno_df['value'] = [*app.curproject['alunos'].drop(columns=['id',*freq_cols]).loc[app.curpersonindex].values]
        #recipiente principal com cor de fundo
        layout = MDBoxLayout(orientation='vertical', md_bg_color='teal')
        self.add_widget(layout)
        
        #----------------------------------------------------------------------
        #cabeçalho
        header_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(header_line)
        #botao para voltar pra tela principal
        home_button = MDIconButton(icon='home', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='left', valign='center', icon_size='32sp')
        home_button.bind(on_release=lambda x: setattr(app.root, 'current', 'MainScreen'))
        header_line.add_widget(home_button)
        #titulo
        label = MDLabel(text=f'{aluno_name}',
                        theme_text_color='Custom', text_color='white', font_style='H6', halign='center', valign='center', size_hint=(1, None))
        label.bind(texture_size=lambda instance, value: instance.setter('height')(instance, instance.texture_size[1] + 30))
        header_line.add_widget(label)
        #botao para voltar para a tela de alunos
        btn0 = MDIconButton(icon='account-group', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        btn0.bind(on_release=lambda x: setattr(app.root, 'current', 'ProjectAlunosScreen'))
        header_line.add_widget(btn0)
        
        #----------------------------------------------------------------------
        #tabela
        data_table = MDDataTable(size_hint=(1, .9), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                                 use_pagination=False, rows_num=9999, background_color_cell="white", background_color_selected_cell="white",
                                 column_data=[('', dp(app.wsize[0]//2+1)), ('', dp(app.wsize[0]//2+1))],
                                 row_data=[(x,y) for x,y in zip(aluno_df['column'].values, aluno_df['value'].values)] )
        data_table.ids.container.remove_widget(data_table.header)
        data_table.sorted_on = "ID"
        data_table.sorted_order = "ASC" #"DSC"
        data_table.bind(on_row_press=self.on_row_press)
        self.data_table = data_table
        layout.add_widget(data_table)
        
        #----------------------------------------------------------------------
        #barra inferior
        bottom_line = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), minimum_height=0)
        layout.add_widget(bottom_line)
        #botao para apagar o aluno
        delete_button = MDIconButton(icon='account-minus', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        delete_button.bind(on_release=self.open_delete_aluno_popup)
        bottom_line.add_widget(delete_button)
        #spacer
        bottom_line.add_widget( Widget(size_hint_x=1) )
        #botao para adicionar um novo aluno
        add_button = MDIconButton(icon='pen-plus', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
        add_button.bind(on_release=self.open_add_field_popup)
        bottom_line.add_widget(add_button)
    
    #--------------------------------------------------------------------------
    #popup de edicao de nome de campo ou valor de tabela
    
    def on_row_press(self, instance_table, instance_row):
        #rec row
        self.cur_row = instance_row
        #index par é a coluna, index impar é o valor
        self.is_campo = instance_row.index % 2 == 0
        #descobre o numero da linha (que no df é o id da coluna)
        self.col_id = instance_row.index // 2
        #a coluna 'id' e as colunas de frequencia nao aparecem na tabela
        alunos_df =  app.curproject['alunos']
        valid_columns = [col for col in alunos_df.columns if col != 'id' and not '__freq__' in col]
        self.col_name = valid_columns[self.col_id]
        #nao pode renomear ou apagar a coluna "nome", apenas seu valor
        if self.is_campo and (self.col_name=='id' or self.col_name=='nome'):
            return None
        #valor da coluna
        row_value = alunos_df.loc[app.curpersonindex, self.col_name]
        print('row value:', row_value)
        #valor da celula
        self.cur_value = self.col_name if self.is_campo else row_value
        
        #campo de texto para editar nome ou valor da coluna
        self.text_field = MDTextField(text=str(self.cur_value), required=False,
                                      helper_text='Deixe vazio para remover o campo', helper_text_mode="persistent",
                                      hint_text='Nome do campo' if self.is_campo else f'Valor do campo')
        #funções para verificar se há texto nos campos, para habilitar e desabilitar o botao confirmar
        self.text_field.bind(text=self.on_change_edit)
        #botoes confirmar e cancelar
        self.edit_confirm_button = MDFillRoundFlatButton(
            text="Confirmar", on_release=self.on_confirm_edit, disabled=False)
        self.edit_cancel_button = MDFillRoundFlatButton(
            text="Cancelar", on_release=self.on_cancel_edit, md_bg_color=CANCEL_BUTTON_COLOR)
        #monta e abre a caixa de dialogo
        self.edit_popup = MDDialog(
            title=('Editar nome do campo' if self.is_campo else f'Editar valor do campo'),
            type="custom", elevation=1, content_cls=self.text_field,
            buttons=[self.edit_cancel_button, self.edit_confirm_button],)
        self.edit_popup.open()
    
    def on_change_edit(self, instance, value):
        #nao pode ter outra coluna com o mesmo nome
        self.edit_confirm_button.disabled = self.text_field.text in app.curproject['alunos']
        
    def on_cancel_edit(self, button):
        self.edit_popup.dismiss()
        
    def on_confirm_edit(self, button):
        #se mudou o nome de uma coluna (mas nao deixou vazio)
        if self.is_campo and self.text_field.text != self.cur_value and self.text_field.text != '':
            print('mudou coluna de', self.cur_value, '/', app.curproject['alunos'].columns[self.col_id], 'para', self.text_field.text)
            self.data_table.update_row( #atualiza valor na tabela
                    self.data_table.row_data[self.col_id],                              # old row data
                    [self.text_field.text, self.data_table.row_data[self.col_id][1]],)  # new row data
            app.curproject['alunos'] = app.curproject['alunos'].rename(columns={self.col_name: self.text_field.text}) #atualiza nome da coluna no dataframe
            self.edit_popup.dismiss()   #fecha o popup
            
        #se mudou o valor de um campo
        if not self.is_campo and self.text_field.text != self.cur_value:
            #atualiza valor na tabela
            self.data_table.update_row(
                    self.data_table.row_data[self.col_id],                              #old row data
                    [self.data_table.row_data[self.col_id][0], self.text_field.text],)  #new row data
            #atualiza valor no dataframe
            app.curproject['alunos'].at[app.curpersonindex, self.col_name] = self.text_field.text
            self.edit_popup.dismiss() #fecha o popup
        
        #se deixou o nome da coluna vazio, abre a confirmação de apagar
        if self.is_campo and self.text_field.text == '':
            self.edit_popup.dismiss()   #fecha o popup
            self.open_delete_field_popup()  #abre popup para confirmar exclusao de campo
    
    #--------------------------------------------------------------------------
    #popup para deletar campo
    
    def open_delete_field_popup(self):
        #botoes confirmar (inicia desabilitado) e cancelar
        self.delete_confirm_button = MDFillRoundFlatButton(
            text='Confirmar', on_release=self.on_confirm_delete, disabled=False)
        self.delete_cancel_button = MDFillRoundFlatButton(
            text='Cancelar', on_release=self.on_cancel_delete, md_bg_color=CANCEL_BUTTON_COLOR)
        #texto informando que apaga de todos os alunos
        alert_message = MDLabel(
            text=f'Atenção! Você está prestes a apagar permanentemente o campo de dados "{self.col_name}". Todos os dados de "{self.col_name}" serão perdidos para todos os registros nesse projeto!',
            theme_text_color="Error", size_hint_y=None, height=dp(55), )
        #popup
        self.delete_popup = MDDialog(title='Confirmação de apagar campo', type='custom', elevation=1,
                                    content_cls=alert_message, buttons=[self.delete_cancel_button, self.delete_confirm_button], )
        self.delete_popup.open()
    
    def on_confirm_delete(self, button):
        self.data_table.remove_row( self.data_table.row_data[self.col_id] )     #remove da tabela
        app.curproject['alunos'].drop(columns=[self.col_name], inplace=True)    #remove do dataframe
        self.delete_popup.dismiss()
    
    def on_cancel_delete(self, button):
        self.delete_popup.dismiss()
    
    #--------------------------------------------------------------------------
    #popup do botao de adicionar campo
    
    def open_add_field_popup(self, button):
        self.text_field = MDTextField(text='', required=True, hint_text='Nome do novo campo')   #campo de texto para o nome do campo/coluna e para o valor
        self.text_field.bind(text=self.on_change_add)   #funcaos para verificar se há texto no campo para habilitar e desabilitar o botao confirmar
        #botoes confirmar (inicia desabilitado) e cancelar
        self.edit_confirm_button = MDFillRoundFlatButton(
            text='Confirmar', on_release=self.on_confirm_add, disabled=True)
        self.edit_cancel_button = MDFillRoundFlatButton(
            text='Cancelar', on_release=self.on_cancel_add, md_bg_color=CANCEL_BUTTON_COLOR)
        #campo de texto para o nome
        self.new_row_name_field = MDTextField(hint_text='Digite um nome para o novo campo', required=True)
        #popup
        self.add_popup = MDDialog( title='Criar novo campo', type='custom', elevation=1,
                                    content_cls=self.text_field, buttons=[self.edit_cancel_button, self.edit_confirm_button], )
        self.add_popup.open()
    
    def on_change_add(self, instance, value):
        #desabilita botao confirmar se nao tiver nome ou ja existir outra coluna com o mesmo nome
        self.edit_confirm_button.disabled = not value.strip() or self.text_field.text in app.curproject['alunos']
    
    def on_cancel_add(self, button):
        self.add_popup.dismiss()
    
    def on_confirm_add(self, button):
        self.data_table.add_row((self.text_field.text, ''))     #add na tabela
        app.curproject['alunos'][self.text_field.text] = ''     #add no dataframe
        self.add_popup.dismiss()
    
    #--------------------------------------------------------------------------
    #TODO: popup do botao de excluir aluno
    
    def open_delete_aluno_popup(self, button):
        debug(self, button)
        #botoes confirmar (inicia desabilitado) e cancelar
        self.delete_aluno_confirm_button = MDFillRoundFlatButton(
            text='Confirmar', on_release=self.on_confirm_delete_aluno, disabled=False)
        self.delete_aluno_cancel_button = MDFillRoundFlatButton(
            text='Cancelar', on_release=self.on_cancel_delete_aluno, md_bg_color=CANCEL_BUTTON_COLOR)
        #texto informando que apaga de todos os alunos
        nome_do_aluno = app.curproject['alunos'].loc[app.curpersonindex, 'nome']
        alert_message = MDLabel(
            text=f'Atenção! Você está prestes a apagar permanentemente o registro de "{nome_do_aluno}" no projeto "{app.curproject["nome"]}"! Não será possível desfazer esta ação!',
            theme_text_color="Error", size_hint_y=None, height=dp(55), )
        #popup
        self.delete_aluno_popup = MDDialog(title='Confirmação de apagar registro', type='custom', elevation=1,
                                    content_cls=alert_message, buttons=[self.delete_aluno_cancel_button, self.delete_aluno_confirm_button], )
        self.delete_aluno_popup.open()
    
    def on_cancel_delete_aluno(self, button):
        self.delete_aluno_popup.dismiss()
    
    def on_confirm_delete_aluno(self, button):
        app.curproject['alunos'] = app.curproject['alunos'].drop(app.curpersonindex)    #exclui no dataframe
        ### app.curproject['alunos'].reset_index(drop=True, inplace=True)               #reseta o index para não deixar buracos (cria outros problemas entao deixa sem)
        self.delete_aluno_popup.dismiss()                       #fecha popup       
        setattr(app.root, 'current', 'ProjectAlunosScreen')     #volta pra tela anterior
        
    
#%% tela de aulas/eventos

class EventScreen(Screen):
    
    def on_pre_enter(self, *args):
        self.clear_widgets()
    
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)

        label = MDLabel(text="Event Screen", halign="center")
        layout.add_widget(label)

#%% tela de chamada

class PresenceScreen(Screen):
    
    def on_pre_enter(self, *args):
        self.clear_widgets()
        
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)
        
        label = MDLabel(text="Presence Screen", halign="center")
        layout.add_widget(label)

#%% app

class ProjetoSocial(MDApp):
    #stores the project list, each project is a dict with a name plus two pandas dataframes
    projetos = []
    curproject = None
    curpersonid, curpersonindex = 0, 0
    cureventid, cureventindex = 0, 0
    wsize = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #config
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.device_orientation = 'portrait'
        Metrics.fontscale = .8
        
        #TODO: TEMP para testar com tamanho de telas de mobile, e centralizar na tela do computador (precisa do self.theme_cls.device_orientation = 'portrait')
        user32 = ctypes.windll.user32
        Window.size = (414, 896) #iphone 11 pro max
        Window.top = 100#(user32.GetSystemMetrics(1) - Window.height) // 2
        Window.left = 780#(user32.GetSystemMetrics(0) - Window.width) // 2
        
        #rec the screen size to adjust the table columns
        self.wsize = [Window.system_size[0]//5.8, Window.system_size[1]//5.8] #TODO: fazer pra qq aparelho
        
        #TODO: TEMP: using test data for now
        for i in range(4):
            self.create_test_project(index=i)
    
    def build(self):
        return Builder.load_string(KV)
    
    def create_project(self, name):
        if name==None:
            pass #TODO: handle it
        
        #cria tabelas de aluno e de eventos, com os campos fixos
        alunos_df = pd.DataFrame()
        alunos_df.columns = ['id', 'nome']
        eventos_df = pd.DataFrame()
        eventos_df.columns = ['id', 'ano']
        
        #constroi o projeto
        projeto = {'nome':f'name', 'alunos':alunos_df, 'eventos':eventos_df}
        
        #adiciona
        self.projetos.append(projeto)
        self.curproject = self.projetos[-1]
        pass
    
    #TODO: TEMP: cria dados de teste para começar com alguma coisa durante o desenvolvimento
    def create_test_project(self, index=1):
        #alunos
        alunos_df = pd.DataFrame()
        alunos_df['id'] = [x+1 for x in range(10+index)]
        alunos_df['nome'] = [f'Aluno {x+1}' for x in range(10+index)]
        alunos_df['__freq__1234'] = [[] for x in range(10+index)]
        for i in range(7):
            alunos_df[f'coluna{i}'] = [f'valor {i}' for x in range(10+index)]
        alunos_df.index = alunos_df.id
        #eventos
        eventos_df = pd.DataFrame()
        eventos_df['id'] = [x+1 for x in range(20+index)]
        eventos_df['ano'] = [2022 for x in range(20+index)]
        eventos_df.index = eventos_df.id
        #constroi o projeto
        if index==0:
            projeto = {'nome':f'Futsal Sub 16', 'alunos':alunos_df, 'eventos':eventos_df}
        elif index==1:
            projeto = {'nome':f'Futsal Sub 20', 'alunos':alunos_df, 'eventos':eventos_df}
        elif index==2:
            projeto = {'nome':f'Jiujitsu', 'alunos':alunos_df, 'eventos':eventos_df}
        else:
            projeto = {'nome':f'Projeto Exemplo {index+1}', 'alunos':alunos_df, 'eventos':eventos_df}
        #adiciona
        self.projetos.append(projeto)
        self.curproject = self.projetos[-1]
        pass

#%% data handling

#TODO: extrai as colunas do dataframe no formato que o kivymd usa

#TODO: extrai as linhas do dataframe no formato que o kivymd usa

#TODO: add new row to data table

#TODO: add new row to dataframe

#TODO: muito a fazer, salvar e carregar projetos, exportar/importar csv e json...

#%% debug

dvars = None

def debug(*args):
    global dvars
    dvars = args

#%% save and load

#------------------------------------------------------------------------------
#option 1: JSON

import json

def save_as_json(project, id):
    #cria json
    project_copy = project.copy()
    project_copy['alunos'] = project['alunos'].to_dict(orient='records')
    project_copy['eventos'] = project['eventos'].to_dict(orient='records')
    #salva
    file_name = f"{id}_{project['name']}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(project_copy, f, ensure_ascii=False, indent=4)

def load_from_json(file_path):
    #carrega
    with open(file_path, 'r', encoding='utf-8') as f:
        project_data = json.load(f)
    #recria projeto
    project_data['alunos'] = pd.DataFrame(project_data['alunos'])
    project_data['eventos'] = pd.DataFrame(project_data['eventos'])
    return {'name': file_path.split('_')[1].split('.')[0],
            'alunos': project_data['alunos'],
            'eventos': project_data['eventos'] }

#------------------------------------------------------------------------------
#option 2: combinar em um único CSV

import pandas as pd

def save_as_single_csv(project, file_id):
    #combina
    alunos = project['alunos'].copy()
    alunos['type'] = 'alunos'
    eventos = project['eventos'].copy()
    eventos['type'] = 'eventos'
    combined = pd.concat([alunos, eventos], ignore_index=True)
    #salva
    file_name = f"{file_id}_{project['name']}.csv"
    combined.to_csv(file_name, index=False)

def load_from_single_csv(file_path):
    #carrega e separa
    combined = pd.read_csv(file_path)
    alunos = combined[combined['type'] == 'alunos'].drop(columns=['type'])
    eventos = combined[combined['type'] == 'eventos'].drop(columns=['type'])
    #recria projeto
    return {'name': file_path.split('_')[1].split('.')[0],
            'alunos': alunos, 'eventos': eventos }

#------------------------------------------------------------------------------
#option 3: dois CSVs separados

import pandas as pd

def save_as_two_csvs(project, file_id):
    #nomes dos arquivos
    project_name = project['name']
    alunos_file = f"{file_id}_{project_name}_alunos.csv"
    eventos_file = f"{file_id}_{project_name}_eventos.csv"
    #salva
    project['alunos'].to_csv(alunos_file, index=False)
    project['eventos'].to_csv(eventos_file, index=False)

def load_from_two_csvs(file_id, project_name):
    #nomes dos arquivos
    alunos_file = f"{file_id}_{project_name}_alunos.csv"
    eventos_file = f"{file_id}_{project_name}_eventos.csv"
    #carrega
    alunos = pd.read_csv(alunos_file)
    eventos = pd.read_csv(eventos_file)
    #recria projeto
    return {'name': project_name, 'alunos': alunos, 'eventos': eventos }

#------------------------------------------------------------------------------
#option 4: pickle

import pickle

def save_as_pickle(project, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(project, f)

def load_from_pickle(file_path):
    with open(file_path, 'rb') as f:
        project = pickle.load(f)
    return project

#------------------------------------------------------------------------------
#option 5: excel

import pandas as pd

def save_as_excel(project, file_id):
    #salva em arquivo excel com duas sheets
    file_name = f"{file_id}_{project['name']}.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        project['alunos'].to_excel(writer, sheet_name='Alunos', index=False)
        project['eventos'].to_excel(writer, sheet_name='Eventos', index=False)

def load_from_excel(file_path):
    #carrega
    with pd.ExcelFile(file_path) as xls:
        alunos = pd.read_excel(xls, 'Alunos')
        eventos = pd.read_excel(xls, 'Eventos')
    #recria projeto
    return {'name':file_path.split('_')[1].split('.')[0],
            'alunos':alunos, 'eventos':eventos }


#------------------------------------------------------------------------------
#option 6: sincroniza com google docs na nuvem (TODO: fica pra depois)



#%% run

# Run the app
if __name__ == '__main__':
    app = ProjetoSocial()
    app.run()
