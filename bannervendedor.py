import requests
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from botoes import ImageButton, LabelButton
from functools import partial
from kivy.app import App


class BannerVendedor(FloatLayout):

    def __init__(self,**kwargs):
        super().__init__()
        self.rows = 1


        with self.canvas:
            Color(rgb=(0,0,0,1))
            self.rec = Rectangle(pos=self.pos,size=self.size)
        self.bind(pos=self.atualizar_rec,size=self.atualizar_rec)


        id_vendedor = kwargs['id_vendedor']
        link = f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/.json?orderBy="id_usuario"&equalTo="{id_vendedor}"'
        requisicao2 = requests.get(link)
        requisicao_dict = requisicao2.json()
        valor = list(requisicao_dict.values())[0]
        avatar = valor['avatar']
        total_vendas = valor['total_vendas']

        meu_aplicativo = App.get_running_app()

        imagem = ImageButton(source=f'icones/fotos_perfil/{avatar}',pos_hint={'right':0.4,'top':0.95},size_hint=(0.4,0.9),
                             on_release=partial(meu_aplicativo.carregar_vendas_vendedor,valor))
        label_id = LabelButton(text=f'ID Vendedor : {id_vendedor}',pos_hint={'right':0.9,'top':0.9},size_hint=(0.4,0.5),
                               on_release=partial(meu_aplicativo.carregar_vendas_vendedor,valor))
        label_total = LabelButton(text=f'Total de Vendas: R${total_vendas}',pos_hint={'right':0.9,'top':0.5},size_hint=(0.4,0.5),
                                  on_release=partial(meu_aplicativo.carregar_vendas_vendedor,valor))
        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total)

    def atualizar_rec(self,*args):
        self.rec.pos = self.pos
        self.rec.size = self.size
