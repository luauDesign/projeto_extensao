# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:56:10 2024
app para facilitar o trabalho de acompanhar alunos e eventos em
projetos sociais voltados a arte ou esportes
@author: Luis
"""

#outros
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

# Main Screen Class
class MainScreen(Screen):
    data_table = None
    
    def on_enter(self, *args):
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
        data_table = MDDataTable(size_hint=(1, .9), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, use_pagination=False, rows_num=9999,
                                 column_data=[('nome', self.width),(f'', dp(0))], #a segunda coluna vazia evita um bug
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
    
    def cancel_row_creation(self, *args):
        self.new_row_dialog.dismiss()
    
    def confirm_row_creation(self, *args):
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
        print('---Pre-Entering ProjectAlunosScreen---')
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
        #tabela #TODO: carregar se ja existir, ou criar se nao existir
        alunos_df = app.curproject['alunos'].drop(columns=['frequencia'])
        data_table = MDDataTable(size_hint=(1, .9), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, use_pagination=False, rows_num=9999,
                                 column_data=[('id',dp(10)), ('nome',dp(200))],
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
                if type(app.root.transition) != FadeTransition:
                    app.root.transition = FadeTransition()
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
    
    def cancel_row_creation(self, *args):
        self.new_row_dialog.dismiss()
    
    def confirm_row_creation(self, *args):
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
        print('---Pre-Entering ProjectEventosScreen---')
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
        data_table = MDDataTable(size_hint=(1, .9), padding=5, elevation=2, pos_hint={'center_x': 0.5, 'center_y': 0.5}, use_pagination=False, rows_num=9999,
                                 column_data=[('id',dp(10)), ('ano',dp(200))],
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
        
        #botao para adicionar um novo evento
        event_button = MDIconButton(icon='clock-plus', theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='right', valign='center', icon_size='32sp')
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
        
        #TODO: cria a row na tabela do kivymd
        
        #TODO: cria a row no dataframe
        
        

#%% tela de alunos/pessoas

# Subject Screen Class
class SubjectScreen(Screen):
    
    def on_enter(self, *args):
        print('---Pre-Entering Subject Screen---')
        self.clear_widgets()
        
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)

        label = MDLabel(text="Subject Screen", halign="center")
        layout.add_widget(label)

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

class ProjetoSocial(MDApp):
    #stores the project list, each project is a dict with a name plus two pandas dataframes
    projetos = []
    curproject = None
    curpersonid = 0
    cureventid = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #config
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        Metrics.fontscale = .8
        
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
        alunos_df.columns = ['id', 'nome', 'frequencia']
        eventos_df = pd.DataFrame()
        eventos_df.columns = ['id', 'ano']
        
        #constroi o projeto
        projeto = {'nome':f'name', 'alunos':alunos_df, 'eventos':eventos_df}
        
        #adiciona
        self.projetos.append(projeto)
        self.curproject = self.projetos[-1]
        pass
    
    #TODO: TEMP
    def create_test_project(self, index=1):
        #alunos
        alunos_df = pd.DataFrame()
        alunos_df['id'] = [x+1 for x in range(10+index)]
        alunos_df['nome'] = [f'Aluno {x+1}' for x in range(10+index)]
        alunos_df['frequencia'] = [[] for x in range(10+index)]
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

#TODO: isso sao variaveis para debuggar, pode apagar depois
itable : MDDataTable = None
irow : CellRow = None
datepicker : MDDatePicker = None
timepicker : MDTimePicker = None


#%% run

# Run the app
if __name__ == '__main__':
    app = ProjetoSocial()
    app.run()
