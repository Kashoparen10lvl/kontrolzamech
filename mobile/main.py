from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.network.urlrequest import UrlRequest
import json
import os

# Убираем настройки окна для WSL
# from kivy.core.window import Window

# === КОНФИГУРАЦИЯ ===
# Замените на IP вашего ноутбука!
SERVER_URL = "http://127.0.1.1:5000"
# ======================

current_user = None

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        self.username = TextInput(hint_text='Логин', size_hint=(1, 0.25), multiline=False)
        self.password = TextInput(hint_text='Пароль', password=True, size_hint=(1, 0.25), multiline=False)
        
        btn_login = Button(text='Войти', size_hint=(1, 0.2))
        btn_login.bind(on_press=self.login)
        
        btn_register = Button(text='Регистрация', size_hint=(1, 0.2))
        btn_register.bind(on_press=self.register)
        
        btn_recover = Button(text='Восстановить пароль', size_hint=(1, 0.2))
        btn_recover.bind(on_press=self.recover)
        
        btn_demo = Button(text='Демо-режим', size_hint=(1, 0.2))
        btn_demo.bind(on_press=self.demo)
        
        layout.add_widget(Label(text='Контроль замечаний', size_hint=(1, 0.3), bold=True))
        layout.add_widget(Label(text=f'Сервер: {SERVER_URL}', size_hint=(1, 0.1), font_size=dp(10)))
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(btn_login)
        layout.add_widget(btn_register)
        layout.add_widget(btn_recover)
        layout.add_widget(btn_demo)
        
        self.add_widget(layout)
    
    def login(self, instance):
        global current_user
        username = self.username.text
        password = self.password.text
        
        def on_success(req, result):
            global current_user
            if result.get('success'):
                current_user = result['user']
                self.manager.current = 'objects'
                self.manager.get_screen('objects').load_objects()
            else:
                popup = Popup(content=Label(text=result.get('error', 'Ошибка')), size_hint=(0.8, 0.3))
                popup.open()
        
        def on_error(req, result):
            popup = Popup(content=Label(text='Ошибка соединения с сервером'), size_hint=(0.8, 0.3))
            popup.open()
        
        data = json.dumps({'username': username, 'password': password})
        UrlRequest(f'{SERVER_URL}/api/login', req_data=data, on_success=on_success, on_error=on_error, method='POST', req_headers={'Content-Type': 'application/json'})
    
    def register(self, instance):
        popup = RegisterPopup()
        popup.open()
    
    def recover(self, instance):
        popup = RecoverPopup()
        popup.open()
    
    def demo(self, instance):
        global current_user
        current_user = {'username': 'demo', 'role': 'Демо'}
        self.manager.current = 'objects'
        self.manager.get_screen('objects').load_objects()

class RegisterPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        self.username = TextInput(hint_text='Логин', size_hint=(1, 0.3), multiline=False)
        self.password = TextInput(hint_text='Пароль', password=True, size_hint=(1, 0.3), multiline=False)
        
        btn_register = Button(text='Зарегистрироваться', size_hint=(1, 0.3))
        btn_register.bind(on_press=self.do_register)
        
        btn_cancel = Button(text='Отмена', size_hint=(1, 0.3))
        btn_cancel.bind(on_press=lambda x: self.dismiss())
        
        layout.add_widget(Label(text='Регистрация', size_hint=(1, 0.2)))
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(btn_register)
        layout.add_widget(btn_cancel)
        
        self.content = layout
        self.size_hint = (0.8, 0.5)
    
    def do_register(self, instance):
        def on_success(req, result):
            if result.get('success'):
                popup = Popup(content=Label(text='Регистрация успешна!'), size_hint=(0.8, 0.3))
                popup.open()
                self.dismiss()
            else:
                popup = Popup(content=Label(text=result.get('error', 'Ошибка')), size_hint=(0.8, 0.3))
                popup.open()
        
        def on_error(req, result):
            popup = Popup(content=Label(text='Ошибка соединения'), size_hint=(0.8, 0.3))
            popup.open()
        
        data = json.dumps({'username': self.username.text, 'password': self.password.text})
        UrlRequest(f'{SERVER_URL}/api/register', req_data=data, on_success=on_success, on_error=on_error, method='POST', req_headers={'Content-Type': 'application/json'})

class RecoverPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        self.username = TextInput(hint_text='Логин', size_hint=(1, 0.3), multiline=False)
        
        btn_recover = Button(text='Восстановить', size_hint=(1, 0.3))
        btn_recover.bind(on_press=self.do_recover)
        
        btn_cancel = Button(text='Отмена', size_hint=(1, 0.3))
        btn_cancel.bind(on_press=lambda x: self.dismiss())
        
        layout.add_widget(Label(text='Восстановление пароля', size_hint=(1, 0.2)))
        layout.add_widget(self.username)
        layout.add_widget(btn_recover)
        layout.add_widget(btn_cancel)
        
        self.content = layout
        self.size_hint = (0.8, 0.4)
    
    def do_recover(self, instance):
        def on_success(req, result):
            if result.get('success'):
                popup = Popup(content=Label(text=f'Ваш пароль: {result["password"]}'), size_hint=(0.8, 0.3))
                popup.open()
                self.dismiss()
            else:
                popup = Popup(content=Label(text=result.get('error', 'Ошибка')), size_hint=(0.8, 0.3))
                popup.open()
        
        def on_error(req, result):
            popup = Popup(content=Label(text='Ошибка соединения'), size_hint=(0.8, 0.3))
            popup.open()
        
        data = json.dumps({'username': self.username.text})
        UrlRequest(f'{SERVER_URL}/api/recover', req_data=data, on_success=on_success, on_error=on_error, method='POST', req_headers={'Content-Type': 'application/json'})

class ObjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = ScrollView()
        self.add_widget(self.layout)
    
    def load_objects(self):
        def on_success(req, result):
            content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
            content.add_widget(Label(text=f'Пользователь: {current_user["username"]} ({current_user["role"]})', size_hint=(1, 0.1)))
            
            for obj in result:
                btn = Button(text=obj["name"], size_hint=(1, 0.15))
                btn.bind(on_press=lambda x, o=obj: self.open_object(o))
                content.add_widget(btn)
            
            btn_add = Button(text='+ Добавить объект', size_hint=(1, 0.15))
            btn_add.bind(on_press=self.add_object)
            content.add_widget(btn_add)
            
            btn_logout = Button(text='Выйти', size_hint=(1, 0.1))
            btn_logout.bind(on_press=lambda x: self.logout())
            content.add_widget(btn_logout)
            
            self.layout.clear_widgets()
            self.layout.add_widget(content)
        
        def on_error(req, result):
            content = BoxLayout(orientation='vertical', padding=dp(15))
            content.add_widget(Label(text='Ошибка загрузки объектов', size_hint=(1, 0.3)))
            btn_retry = Button(text='Повторить', size_hint=(1, 0.2))
            btn_retry.bind(on_press=lambda x: self.load_objects())
            content.add_widget(btn_retry)
            self.layout.clear_widgets()
            self.layout.add_widget(content)
        
        UrlRequest(f'{SERVER_URL}/api/objects', on_success=on_success, on_error=on_error)
    
    def open_object(self, obj):
        self.manager.get_screen('object_detail').current_object = obj
        self.manager.get_screen('object_detail').load_remarks()
        self.manager.current = 'object_detail'
    
    def add_object(self, instance):
        popup = AddObjectPopup()
        popup.open()
    
    def logout(self, instance):
        global current_user
        current_user = None
        self.manager.current = 'login'

class AddObjectPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        self.name = TextInput(hint_text='Название объекта', size_hint=(1, 0.3), multiline=False)
        self.address = TextInput(hint_text='Адрес', size_hint=(1, 0.3), multiline=False)
        
        btn_add = Button(text='Добавить', size_hint=(1, 0.25))
        btn_add.bind(on_press=self.do_add)
        
        btn_cancel = Button(text='Отмена', size_hint=(1, 0.25))
        btn_cancel.bind(on_press=lambda x: self.dismiss())
        
        layout.add_widget(Label(text='Новый объект', size_hint=(1, 0.2)))
        layout.add_widget(self.name)
        layout.add_widget(self.address)
        layout.add_widget(btn_add)
        layout.add_widget(btn_cancel)
        
        self.content = layout
        self.size_hint = (0.8, 0.5)
    
    def do_add(self, instance):
        def on_success(req, result):
            popup = Popup(content=Label(text='Объект добавлен!'), size_hint=(0.8, 0.3))
            popup.open()
            self.dismiss()
            App.get_running_app().root.get_screen('objects').load_objects()
        
        data = json.dumps({'name': self.name.text, 'address': self.address.text})
