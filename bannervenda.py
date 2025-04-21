from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label


class BannerVenda(GridLayout):

    def __init__(self,**kwargs):
        self.rows = 1
        super().__init__()


        with self.canvas:
            Color(rgb=(0,0,0,1))
            self.rec = Rectangle(pos=self.pos,size=self.size)
        self.bind(pos=self.atualizar_rec,size=self.atualizar_rec)

        cliente = kwargs['cliente']
        foto_cliente = kwargs['foto_cliente']
        produto = kwargs['produto']
        foto_produto = kwargs['foto_produto']
        data = kwargs['data']
        quantidade = int(kwargs['quantidade'])
        preco = float(kwargs['preco'])


        esquerda = FloatLayout()
        erquerda_imagem = Image(pos_hint={'right': 1 , 'top': 0.9},size_hint=(1,0.7),source=f'icones/fotos_clientes/{foto_cliente}')
        esquerda_label = Label(pos_hint={'right':1,'top':0.2},size_hint=(1,0.2),text=cliente)
        esquerda.add_widget(erquerda_imagem)
        esquerda.add_widget(esquerda_label)

        meio = FloatLayout()
        meio_imagem = Image(pos_hint={'right': 1, 'top': 0.9}, size_hint=(1, 0.7),source=f'icones/fotos_produtos/{foto_produto}')
        meio_label = Label(pos_hint={'right': 1, 'top': 0.2}, size_hint=(1, 0.2), text=produto)
        meio.add_widget(meio_imagem)
        meio.add_widget(meio_label)

        direita =FloatLayout()
        direita_label_data = Label(pos_hint={'right': 1, 'top': 0.9}, size_hint=(1, 0.2), text=f'Data: {data}')
        direita_label_preco = Label(pos_hint={'right': 1, 'top': 0.6}, size_hint=(1, 0.2), text=f'Preço: {preco}')
        direita_label_quantidade = Label(pos_hint={'right': 1, 'top': 0.3}, size_hint=(1, 0.2), text=f'Quantidade: {quantidade}')
        direita.add_widget(direita_label_data)
        direita.add_widget(direita_label_preco)
        direita.add_widget(direita_label_quantidade)

        self.add_widget(esquerda)
        self.add_widget(meio)
        self.add_widget(direita)

    def atualizar_rec(self,*args):
        self.rec.pos = self.pos
        self.rec.size = self.size
