import json
import os
from datetime import date
from functools import partial
import requests
from kivy.app import App
from kivy.lang import Builder
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
from botoes import *
from telas import *
from myFirebase import FireBase


GUI = Builder.load_file('main.kv')
class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    def __init__(self):
        super().__init__()
        self.vendedor = None
        self.equipe = None
        self.total_vendas = None
        self.id_usuario = None
        self.localId = None
        self.firebase = None
        self.foto_perfil = None
        self.vendas = None
        self.idToken = None

    def build(self):
        self.firebase = FireBase()
        return GUI


    def on_start(self):
        self.carregar_infos_usuario()
        #Carregar fotos do perfil
        arquivos = os.listdir('icones/fotos_perfil')
        foto_perfil = self.root.ids['fotoperfil']
        fotos = foto_perfil.ids['lista_fotos_perfil']
        for foto in arquivos:
            imagem = ImageButton(source=f'icones/fotos_perfil/{foto}',on_release=partial(self.mudar_foto_perfil,foto))
            fotos.add_widget(imagem)

        #Carregar Fotos Clientes
        arquivos = os.listdir('icones/fotos_clientes')
        tela_adicionar_vendas = self.root.ids['adicionarvendas']
        adicionar_clientes = tela_adicionar_vendas.ids['lista_clientes']
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f'icones/fotos_clientes/{foto_cliente}',on_release=partial(self.selecionar_cliente,foto_cliente))
            texto = LabelButton(text=foto_cliente.replace('.png','').capitalize(),on_release=partial(self.selecionar_cliente,foto_cliente))
            adicionar_clientes.add_widget(imagem)
            adicionar_clientes.add_widget(texto)

        #Carregar Fotos Produtos
        arquivos = os.listdir('icones/fotos_produtos')
        tela_adicionar_produtos = self.root.ids['adicionarvendas']
        adicionar_produtos = tela_adicionar_produtos.ids['lista_produtos']
        for foto_produto in arquivos:
            imagem = ImageButton(source=f'icones/fotos_produtos/{foto_produto}',on_release=partial(self.selecionar_produto,foto_produto))
            texto = LabelButton(text=foto_produto.replace('.png', '').capitalize(),on_release=partial(self.selecionar_produto,foto_produto))
            adicionar_produtos.add_widget(imagem)
            adicionar_produtos.add_widget(texto)

        #Carregar Data Atual
        tela_adicionar_vendas = self.root.ids['adicionarvendas']
        tela_adicionar_vendas.ids['label_data'].text = f"Data: {date.today().strftime('%d/%m/%y')}"



    def mudar_tela(self,id_tela,*args):
        gerenciador_telas = self.root.ids['screen_manager']
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self,foto,*args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'
        info = f'{{"avatar":"{foto}"}}'
        requests.patch(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}.json',data=info)
        self.mudar_tela('ajustes')


    def carregar_infos_usuario(self):
        try:
            with open('refresh.txt','r') as arquivo:
                refreshToken = arquivo.read()
                if refreshToken == '':
                    self.mudar_tela('loginpage')
            idToken = self.firebase.trocarToken(refreshToken)
            self.idToken = idToken[1]
            localId = self.firebase.trocarToken(refreshToken)
            self.localId = localId[0]
        except Exception as erro:
            print(erro)
            self.mudar_tela('loginpage')
            pass
        else:
            requisicao = requests.get(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}.json')
            requisicao_dic = requisicao.json()
            print(requisicao_dic)
            # preencher foto do perfil
            avatar = requisicao_dic['avatar']
            self.foto_perfil = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'
            homepage = self.root.ids['homepage']
            lista_vendas = homepage.ids['lista_vendas']

            # preencher Id_Unico do usuario
            id_usuario = requisicao_dic['id_usuario']
            self.id_usuario = id_usuario
            pagina_ajustes = self.root.ids['ajustes']
            pagina_ajustes.ids['label_vendedor'].text = f'Seu ID Único : {id_usuario}'

            # preencher Total Vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            pagina_homepage = self.root.ids['homepage']
            pagina_homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas: [/color] [b]R$ {total_vendas}[/b]'

            # preencher Equipe Vendas
            self.equipe = requisicao_dic['equipe']

            # preencher lista vendas
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                for venda in vendas:
                    if not isinstance(vendas,dict):
                        continue
                    venda = vendas[venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto=venda['produto'],
                                         foto_produto=venda['foto_produto'], unidade=venda.get('unidade'),
                                         quantidade=venda['quantidade'], preco=venda['preco'], data=venda['data'])
                    lista_vendas.add_widget(banner)
            except Exception as erro:
                print(erro)
                pass
            self.mudar_tela('homepage')
        finally:
            self.listar_vendedores()

    # lista de vendedores
    def listar_vendedores(self):
        try:
            requisicao = requests.get(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}.json')
            requisicao_dic = requisicao.json()
            equipe = requisicao_dic['equipe']
            self.equipe = equipe
            lista_equipe = equipe.split(',')
            listar_vendedores = self.root.ids['listarvendedores']
            lista_vendedores = listar_vendedores.ids['lista_vendedores']
            for id_vendedor in lista_equipe:
                if id_vendedor != '':
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor)
                    lista_vendedores.add_widget(banner_vendedor)
        except Exception as erro:
            print(erro)
            pass


    def adicionar_vendedor(self,id_vendedor):
        self.vendedor = id_vendedor
        adicionar_vendedor = self.root.ids['adicionarvendedor']
        mensagem_id_vendedor = adicionar_vendedor.ids['mensagem_id_vendedor']
        link = f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/.json?orderBy="id_usuario"&equalTo="{id_vendedor}"'
        requisicao = requests.get(link)
        requisicao_dict = requisicao.json()
        if requisicao_dict == {}:
            mensagem_id_vendedor.text = 'Vendedor não foi Encontrado!'
        else:
            equipe = self.equipe.split(',')
            if id_vendedor in equipe:
                mensagem_id_vendedor.text = 'Esse Vendedor já Esta na sua Equipe!'
            else:
                print(equipe)
                equipe = self.equipe + f',{id_vendedor}'
                info = {"equipe":equipe}
                requests.patch(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}.json',data=json.dumps(info))
                mensagem_id_vendedor.text = 'Vendedor Adicionado com Sucesso!'
                listar_vendedores = self.root.ids['listarvendedores']
                lista_vendedores = listar_vendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self,foto,*args):
        self.cliente = foto.replace('.png', '')
        tela_adicionar_vendas = self.root.ids['adicionarvendas']
        adicionar_clientes = tela_adicionar_vendas.ids['lista_clientes']
        #pintar todos de branco
        for item in list(adicionar_clientes.children):
            item.color = (1,1,1,1)
            #pintar de azul o item selecionado
            try:
                texto = item.text
                texto = texto.lower()+'.png'
                if texto == foto:
                    item.color = (0,207/255,219/255,1)
            except Exception as erro:
                print(erro)
                pass

    def selecionar_produto(self,foto,*args):
        self.produto = foto.replace('.png','')
        tela_adicionar_produtos = self.root.ids['adicionarvendas']
        adicionar_produtos = tela_adicionar_produtos.ids['lista_produtos']
        #pintar todos de branco
        for item in list(adicionar_produtos.children):
            item.color = (1,1,1,1)
            #pintar de azul o item selecionado
            try:
                texto = item.text
                texto = texto.lower()+'.png'
                if texto == foto:
                    item.color = (0,207/255,219/255,1)
            except Exception as erro:
                print(erro)
                pass


    def selecionar_unidade(self,id_label,*args):
        self.unidade = id_label.replace('unidade_','')
        tela_adicionar_vendas = self.root.ids['adicionarvendas']
        tela_adicionar_vendas.ids['unidade_kilos'].color = (1,1,1,1)
        tela_adicionar_vendas.ids['unidade_unidades'].color = (1, 1, 1, 1)
        tela_adicionar_vendas.ids['unidade_litros'].color = (1, 1, 1, 1)
        tela_adicionar_vendas.ids[id_label].color = (0,20/255,219/255,1)

    def selecionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        adicionar_vendas = self.root.ids['adicionarvendas']
        data = adicionar_vendas.ids['label_data'].text.replace('Data: ','')
        preco = adicionar_vendas.ids['input_preco_total'].text
        quantidade = adicionar_vendas.ids['input_quantidade'].text
        if not cliente:
            adicionar_vendas.ids['label_selecionar_cliente'].color = (1,0,0,1)
        if not produto:
            adicionar_vendas.ids['label_selecionar_produto'].color = (1,0,0,1)
        if not unidade:
            adicionar_vendas.ids['unidade_kilos'].color = (1, 0, 0, 1)
            adicionar_vendas.ids['unidade_unidades'].color = (1, 0, 0, 1)
            adicionar_vendas.ids['unidade_litros'].color = (1, 0, 0, 1)
        if not preco:
            adicionar_vendas.ids['input_preco_total'].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except Exception as erro:
                print(erro)
                adicionar_vendas.ids['input_preco_total'].color = (1, 0, 0, 1)

        if not quantidade:
            adicionar_vendas.ids['input_quantidade'].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except Exception as erro:
                print(erro)
                adicionar_vendas.ids['input_quantidade'].color = (1, 0, 0, 1)

        # Considerando que o Usuario digitou tudo Corretamente
        if cliente and produto and cliente and type(preco == float) and type(quantidade == float):
            foto_cliente = cliente + '.png'
            foto_produto = produto + '.png'
            info = {'cliente':cliente,'produto':produto,'foto_cliente':foto_cliente,'foto_produto':foto_produto,'data':data,'preco':preco,'quantidade':quantidade,'unidade':unidade}
            requests.post(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}/vendas.json',data=json.dumps(info))
            homepage = self.root.ids['homepage']
            lista_vendas = homepage.ids['lista_vendas']
            banner = BannerVenda(cliente=cliente,produto=produto,foto_cliente=foto_cliente,foto_produto=foto_produto,data=data,preco=preco,quantidade=quantidade,unidade=unidade)
            lista_vendas.add_widget(banner)
            requisicao = requests.get(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}/total_vendas.json')
            total_vendas = requisicao.json()
            print(total_vendas)
            total_vendas = total_vendas + preco
            #total_vendas = {'total_vendas': total_vendas}

            requests.put(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{self.localId}/total_vendas.json',json=total_vendas)
            self.carregar_infos_usuario()
            self.mudar_tela('homepage')

    def carregar_todas_vendas(self):
        listarvendas = self.root.ids['listarvendas']
        lista_vendas = listarvendas.ids['lista_vendas']
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        requisicao = requests.get(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/.json?orderBy="id_usuario"')
        requisicao_dic = requisicao.json()

        # preencher foto do perfil
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/hash.png'

        listarvendas = self.root.ids['listarvendas']
        lista_vendas = listarvendas.ids['lista_vendas']
        total_vendas = 0
        for id_usuario in requisicao_dic:
            usuario = requisicao_dic[id_usuario]
            if not isinstance(usuario,dict ):
                continue
            vendas = requisicao_dic[id_usuario]['vendas']
            if not isinstance(vendas,dict ):
                continue
            try:
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas = total_vendas + venda['preco']
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                         produto=venda['produto'],
                                         foto_produto=venda['foto_produto'], unidade=venda.get('unidade',''),
                                         quantidade=venda['quantidade'], preco=venda['preco'], data=venda['data'])
                    lista_vendas.add_widget(banner)
            except Exception as erro:
                print(erro)
                pass

        #preencher Total Vendas
        listarvendas.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas: [/color] [b]R$ {total_vendas}[/b]'

        self.mudar_tela('listarvendas')

    def sair_listar_vendas(self,id_tela):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.foto_perfil}'
        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self,dict_infos_vendedor,*args):
        listarvendas = self.root.ids['vendas_outro_vendedor']
        lista_vendas = listarvendas.ids['lista_vendas']
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)
        try:
            total_vendas = dict_infos_vendedor['total_vendas']
            vendas_outro_vendedor = self.root.ids['vendas_outro_vendedor']
            lista_vendas = vendas_outro_vendedor.ids['lista_vendas']
            label_total_vendas = vendas_outro_vendedor.ids['label_total_vendas']
            label_total_vendas.text = f'[color=#000000]Total de Vendas: [/color] [b]R$ {total_vendas}[/b]'

            infos = dict_infos_vendedor
            vendas = infos['vendas']
            for venda in vendas.values():
                if not isinstance(vendas,dict):
                    continue
                banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                     produto=venda['produto'],
                                     foto_produto=venda['foto_produto'], unidade=venda.get('unidade',''),
                                     quantidade=venda['quantidade'], preco=venda['preco'], data=venda['data'])
                lista_vendas.add_widget(banner)
        except Exception as erro:
            print(erro)
            pass
        avatar = dict_infos_vendedor['avatar']
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{avatar}'

        self.mudar_tela('vendas_outro_vendedor')

MainApp().run()
